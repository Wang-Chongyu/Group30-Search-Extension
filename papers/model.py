import torch
from torch.utils.data import DataLoader, Dataset
import os
import re
from random import sample
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from transformers import BertModel, BertTokenizer
from tqdm import tqdm
import pickle
import json
import sys
import csv

# create dataset class

class MyDataset(Dataset):

    # load all files
    def __init__(self,base_path,chunk_len=512):
        super(MyDataset, self).__init__()
        self.chunk_len = chunk_len
        self.all_file_paths = []
        base_file_names = os.listdir(base_path)
        base_file_names.sort(key=self.sort_key)
        self.all_file_paths.extend([os.path.join(base_path,i) for i in base_file_names])
        # print(len(self.all_file_paths))
    
    def sort_key(self,filename):
        return int(re.search(r'\d+', filename).group())

    # filter out the bad tokens
    def tokenize(self, text):

        fileters = ['!', '"', '#', '$', '%', '&', '\(', '\)', '\*', '\+', ',', '-', '\.', '/', ':', ';', '<', '=', '>',
                    '\?', '@', '\[', '\\', '\]', '^', '_', '`', '\{', '\|', '\}', '~', '\t', '\n', '\x97', '\x96', '”', '“', ]
        text = re.sub("<.*?>", " ", text, flags=re.S)
        text = re.sub("|".join(fileters), " ", text, flags=re.S)
        return text  
    

    def __getitem__(self, index):
        # we have to seperate each file into 512-length chunks
        # and then we can use bert to encode them
        if index < 0 or index >= len(self.all_file_paths):
            return None
        cur_file = self.all_file_paths[index]
        filtered_text = self.tokenize(open(cur_file,encoding='utf-8').read().strip().lower())

        # split into chunks
        chunks = []
        for i in range(0,len(filtered_text),self.chunk_len):
            chunks.append(filtered_text[i:i+self.chunk_len])
        
        return len(chunks),chunks
    
    def __len__(self):
        return len(self.all_file_paths)


# create model class
class BertClassifier():
    def __init__(self,model_name = 'distilbert-base-uncased' ,hiden_size=768):
        super(BertClassifier, self).__init__()
        self.model_name = model_name
        self.hidden_size = hiden_size

        # load bert tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.bert = BertModel.from_pretrained(self.model_name).to('cuda')

        # froze the bert parameter
        for param in self.bert.parameters():
            param.requires_grad = False
    
    def get_vector(self,sentence):
        bert_cls_hidden_state = self.bert(
            **sentence).last_hidden_state[:, 0, :]

        return bert_cls_hidden_state
    
    def classify(self,query,text_chunks):

        # encode the text chunks
        encoded_texts = text_chunks
       
        # encode the query
        encoded_query = self.tokenizer(query, return_tensors="pt")
        query_output = self.get_vector(encoded_query)


        joint_similarity = 0
        for encoded_text in encoded_texts:

            # convert to tensor
            encoded_text = self.tokenizer(encoded_text, return_tensors="pt")
            # get the bert output
            text_output = self.get_vector(encoded_text)

            # get the similarity
            similarity = F.cosine_similarity(text_output,query_output)
            joint_similarity += similarity   
        

        return joint_similarity/len(encoded_texts)


if __name__ == "__main__":

    # hyperparameters
    # cur_query = 'Information retrieval'
    cur_query = sys.argv[1]
    data_root = r".\data"
    output_size = 3

    # load the model
    model = BertClassifier()

    # load dataset
    dataset = MyDataset(data_root)
   
    try:  
        # predict the similarity
        # load the file_embedding_dict
        with open('file_embedding_dict.pkl','rb') as f:
            file_embedding_dict = pickle.load(f)
    except:
        file_embedding_dict = {}
        for idx in tqdm(range(len(dataset))):
            _,chunks = dataset[idx]
            cur_embddings = []
            for chunk in chunks:
                e1 = model.tokenizer(chunk, return_tensors="pt")
                # put e1 into gpu
                e1 = {key: value.to('cuda') for key, value in e1.items()}
                e2 = model.get_vector(e1)
                # put e2 into cpu
                e2 = e2.detach().cpu().numpy()
                cur_embddings.append(e2)
            
            file_embedding_dict[idx] = cur_embddings

    
            
        # using pickle to save file_embedding_dict
        with open('file_embedding_dict.pkl','wb') as f:
            pickle.dump(file_embedding_dict,f)


    encoded_query = model.tokenizer(cur_query, return_tensors="pt").to('cuda')
    query_output = model.get_vector(encoded_query).detach().cpu().numpy()

    # get the similarity
    similarities = {}
    for idx in tqdm(file_embedding_dict):
        cur_embeddings = file_embedding_dict[idx]
        joint_similarity = 0
        for cur_embedding in cur_embeddings:
            similarity = F.cosine_similarity(torch.from_numpy(cur_embedding),torch.from_numpy(query_output))
            joint_similarity += similarity
        similarities[idx] = joint_similarity/len(cur_embeddings) + len(cur_embeddings)/1000000

    # sort the similarities
    sorted_similarities = sorted(similarities.items(),key=lambda x:x[1],reverse=True)

    # get the bottom 10
    bottom = sorted_similarities[:output_size]
    paper_list = []
    for idx in bottom:
        paper_list.append(dataset.all_file_paths[idx[0]])
        # print(dataset.all_file_paths[idx[0]])
        # print(idx[0])
        # print('-----------------------')


    # get the information of related papers
    file_path = 'pdf_record.csv'
    title = [0, 0, 0]
    link = [0, 0, 0]
    pdf_num = []

    for item in paper_list:
        pdf_position = item.find('pdf')
        pdf_number = item[pdf_position:item.rfind('.txt')]
        pdf_num.append(pdf_number)

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    # Create a CSV reader object
        csv_reader = csv.DictReader(file, delimiter=',')

        # Iterate through each row in the CSV file
        for row in csv_reader:
            # Check if the index in the current row matches the desired index
            if row['pdf_index'] == pdf_num[0] + '.pdf':
                # Store the matched ref and title in the dictionary
                title[0] = row['title']
                link[0] = row['ref']
            if row['pdf_index'] == pdf_num[1] + '.pdf':
                # Store the matched ref and title in the dictionary
                title[1] = row['title']
                link[1] = row['ref']
            if row['pdf_index'] == pdf_num[2] + '.pdf':
                # Store the matched ref and title in the dictionary
                title[2] = row['title']
                link[2] = row['ref']

    
    j = {
        "papers":
                [
                    { "paperTitle":title[0], "abstract":paper_list[0], "link":link[0]},
                    { "paperTitle":title[1], "abstract":paper_list[1], "link":link[1]},
                    { "paperTitle":title[2], "abstract":paper_list[2], "link":link[2]}
                ]
        }
    print(json.dumps(j), end="")
            

        



