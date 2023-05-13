# Main.py has the query sentences as input and print the relative paper titles, a part of content related to query, 
# and the paper links to the backend program. We segment the query sentences into word level, and compute the 
# probability of combination of these words utilizing the probability matrix produced by our PLSA model. Then 
# we will choose one or two papers which have the highest relevance scores as relative papers. Then we find 
# the context of the query sentence appearing in the paper content. We print the titles, the context content, 
# and paper links to our server to let it show on our extension.
import numpy as np
import platform
import re
import json
import sys
import csv
# For Windows
delimiter = "\\"
dict_path = r'.\pdfs'
txt_path = r'.\data'
def main(selection):
    content = ''
    content2 = ''
    if platform.system().lower() != "windows":
        global dict_path 
        dict_path = "./pdfs"
        global txt_path
        txt_path = "./data"
        global delimiter 
        delimiter = "/"

    prob_matrix = np.loadtxt("prob_matrix.txt")
    vocab = np.loadtxt("vocabulary.txt", dtype= 'str', delimiter=' ', encoding='utf-8')
    vocab = list(vocab)
    # print(len(vocab))
    # print(prob_matrix.shape)
    query_words = selection.split()
    paper_index = []
    flag = 0
    for word in query_words:
        for i in range(len(vocab)):
            if word in vocab[i]:
                paper_index.append(np.argmax(prob_matrix[:, i]))
                # print(prob_matrix[1,i], np.argmax(prob_matrix[:, i]))
                flag = 1
                break
    if flag == 0:
        j = {
            "papers":
                    [
                        { "paperTitle":'No relative papers', "abstract":'', "link":''}
                    ]
            }
        print(json.dumps(j), end="")
        return

    file_list = []
    file = open(dict_path + delimiter + 'links.txt', 'r', encoding='utf-8')
    for line in file.readlines():
        line = line.strip('\n')
        file_list.append(line)
    # print(len(file_list), paper_index[0] * 2)
    # doc_name1 = file_list[paper_index[0] * 2] + '.txt'
    with open('paper_lists.txt', 'r') as file:
        for index, line in enumerate(file, start=1):
            if index == paper_index[0]:
                p_index = line.strip()
                pdf_position = p_index.find('pdf')
                pdf_number = p_index[pdf_position:p_index.rfind('.txt')]
            if len(paper_index) >= 2:
                if index == paper_index[1]:
                    p_index = line.strip()
                    pdf_position = p_index.find('pdf')
                    pdf_number2 = p_index[pdf_position:p_index.rfind('.txt')]
    doc_name1 = pdf_number
    if len(paper_index) > 1:
        doc_name2 = pdf_number2

    relative_paper = open(txt_path + delimiter + doc_name1 + '.txt', 'r', encoding='utf-8')
    paper_content = ''
    for line in relative_paper.readlines():
        line = line.strip('\n')
        paper_content += line
    # with open(txt_path + delimiter + doc_name1, 'r', encoding='utf-8') as f:
    #     paper_content = f.read().replace('\n', '')
    
    num = 200
    for m in re.finditer(query_words[0], paper_content):
        start = m.start()
        end = m.end()
        if (m.start() - num) < 0:
            start = 0
            content = paper_content[start:end+num]
        elif (m.end() + num) > len(paper_content):
            end = len(paper_content) - 1
            content = paper_content[start-num:end]
        else:
            content = paper_content[start-num:end+num]
    # print(paper_content)
    if content == '':
        for i in range(15):
            with open(txt_path + delimiter + doc_name1 + '.txt', 'r', encoding='utf-8') as f:
                paper_cont = f.read().replace('\n', '')
                if query_words[0] in paper_cont:
                    paper_index[0] = i
                    for m in re.finditer(query_words[0], paper_cont):
                        start = m.start()
                        end = m.end()
                        if (m.start() - num) < 0:
                            start = 0
                            content = paper_cont[start:end+num]
                        elif (m.end() + num) > len(paper_cont):
                            end = len(paper_cont) - 1
                            content = paper_cont[start-num:end]
                        else:
                            content = paper_cont[start-num:end+num]
                    # print(content)
                    break



    if len(paper_index) > 1:
        # doc_name2 = file_list[paper_index[1] * 2] + '.txt'
        relative_paper2 = open(txt_path + delimiter + doc_name2 + '.txt', 'r', encoding='utf-8')
        paper_content2 = ''
        for line in relative_paper2.readlines():
            line = line.strip('\n')
            paper_content2 += line
        
        for m in re.finditer(query_words[1], paper_content2):
            start = m.start()
            end = m.end()
            if (m.start() - num) < 0:
                start = 0
                content2 = paper_content2[start:end+num]
            elif (m.end() + num) > len(paper_content2):
                end = len(paper_content2) - 1
                content2 = paper_content2[start-num:end]
            else:
                content2 = paper_content2[start-num:end+num]
    
    title = [0, 0]
    link = [0, 0]
    file_path = 'pdf_record.csv'
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    # Create a CSV reader object
        csv_reader = csv.DictReader(file, delimiter=',')

        # Iterate through each row in the CSV file
        for row in csv_reader:
            # Check if the index in the current row matches the desired index
            if row['pdf_index'] == doc_name1 + '.pdf':
                # Store the matched ref and title in the dictionary
                title[0] = row['title']
                link[0] = row['ref']
            if len(paper_index) > 1:
                if row['pdf_index'] == doc_name2 + '.pdf':
                    # Store the matched ref and title in the dictionary
                    title[1] = row['title']
                    link[1] = row['ref']

    # dictionary
    if len(paper_index) == 1 and content != '':
        j = {
            "papers":
                    [
                        { "paperTitle":title[0], "abstract":content, "link":link[0]}
                    ]
        }

        # print out json
        print(json.dumps(j), end="")
    elif len(paper_index) > 1 and content2 == '':
        if content != '':
            j = {
                "papers":
                        [
                            { "paperTitle":title[0], "abstract":content, "link":link[0]}
                        ]
            }
            print(json.dumps(j), end="")
    elif len(paper_index) > 1 and content2 != '':
        if content != '':
            j = {
                "papers":
                        [
                            { "paperTitle":title[0], "abstract":content, "link":link[0]},
                            { "paperTitle":title[1], "abstract":content2, "link":link[1]}
                        ]
            }
            print(json.dumps(j), end="")
        if content == '':
            j = {
                "papers":
                        [
                            { "paperTitle":title[1], "abstract":content2, "link":link[1]}
                        ]
            }
            print(json.dumps(j), end="")
    elif content == '' and content2 == '':
        j = {
            "papers":
                    [
                        { "paperTitle":'No relative papers', "abstract":'', "link":''}
                    ]
        }
        print(json.dumps(j), end="")
    return

if __name__ == '__main__':
    selection = sys.argv[1]
    # selection = "Machine"
    main(selection)

    