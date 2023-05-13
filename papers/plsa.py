import numpy as np
import math
import os
import re
import sys
import platform

# For Windows
delimiter = "\\"

def normalize(input_matrix):

    row_sums = input_matrix.sum(axis=1)
    try:
        assert (np.count_nonzero(row_sums)==np.shape(row_sums)[0])
    except Exception:
        raise Exception("Error while normalizing. Row(s) sum to zero")
    new_matrix = input_matrix / row_sums[:, np.newaxis]
    return new_matrix


def txtlist(dict_path):
    file_list = []
    for files in os.walk(dict_path):
        for file in files[2]:
            file_list.append(dict_path + delimiter + file)
    # print(file_list)
    return file_list


class Corpus(object):

    def __init__(self, documents_path):

        self.documents = []
        self.vocabulary = []
        self.likelihoods = []
        self.documents_path = documents_path
        self.term_doc_matrix = None 
        self.document_topic_prob = None  # P(z | d)
        self.topic_word_prob = None  # P(w | z)
        self.topic_prob = None  # P(z | d, w)

        self.number_of_documents = 0
        self.vocabulary_size = 0
        self.p_w = 0

    def build_corpus(self):

        for doc in self.documents_path:
            file = open(doc, 'r', encoding='utf-8')
            document_content = []
            counter = 0
            for line in file.readlines():
                if counter > 100:
                    break
                line = line.strip('\n')
                line = line.split()
                document_content += line
                counter += 1
            self.documents.append(document_content)
            self.number_of_documents += 1

        

    def build_vocabulary(self):

        for line in self.documents:
            for word in line:
                if word not in self.vocabulary and word != ' ' and word != '':
                    self.vocabulary.append(word)
                    self.vocabulary_size += 1
        print(self.vocabulary_size)


    def build_term_doc_matrix(self):

        self.term_doc_matrix = [[0]*(len(self.documents))]*len(self.vocabulary)
        for i in range(len(self.documents)):
            for j in range(len(self.documents[i])):
                for k in range(len(self.vocabulary)):
                    if self.documents[i][j] == self.vocabulary[k]:
                        self.term_doc_matrix[k][i] += 1
        # self.term_doc_matrix = np.array(self.term_doc_matrix)
        # print(self.term_doc_matrix.shape)


    def initialize_randomly(self, number_of_topics):

        self.document_topic_prob = np.random.random((self.number_of_documents, number_of_topics))
        self.document_topic_prob = normalize(self.document_topic_prob)

        self.topic_word_prob = np.random.random((number_of_topics, len(self.vocabulary)))
        self.topic_word_prob = normalize(self.topic_word_prob)

        # print(self.document_topic_prob.shape)
        # print(self.topic_word_prob.shape)
        

    def initialize_uniformly(self, number_of_topics):

        self.document_topic_prob = np.ones((self.number_of_documents, number_of_topics))
        self.document_topic_prob = normalize(self.document_topic_prob)

        self.topic_word_prob = np.ones((number_of_topics, len(self.vocabulary)))
        self.topic_word_prob = normalize(self.topic_word_prob)

    def initialize(self, number_of_topics, random=False):

        print("Initializing...")

        if random:
            self.initialize_randomly(number_of_topics)
        else:
            self.initialize_uniformly(number_of_topics)

    def expectation_step(self):

        print("E step:")
        P_z_d = self.document_topic_prob.reshape((self.document_topic_prob.shape[0], self.document_topic_prob.shape[1], 1))
        P_w_z = self.topic_word_prob.reshape((1, self.document_topic_prob.shape[1], self.vocabulary_size))
        self.p_w = P_z_d * P_w_z
        D, T, W = self.p_w.shape
        temp = self.p_w.sum(axis=1)
        temp[temp == 0] = 1
        self.topic_prob = self.p_w / temp.reshape(D, 1, W)
        # print(self.topic_prob)
            

    def maximization_step(self, number_of_topics):
        print("M step:")
        
        td_matrix = np.array(self.term_doc_matrix)
        count_w_d = td_matrix.T.reshape((self.number_of_documents, 1, self.vocabulary_size))
        topic_word_prob_top = count_w_d * self.topic_prob
        topic_word_prob_top = topic_word_prob_top.sum(axis=0)
        temp = topic_word_prob_top.sum(axis=1)
        temp[temp == 0] = 1
        self.topic_word_prob = topic_word_prob_top / temp.reshape(number_of_topics, 1)
        # print(self.topic_word_prob.shape)
        # update P(z | d)

        document_topic_top = count_w_d * self.topic_prob
        document_topic_top = document_topic_top.sum(axis=2)
        temp2 = document_topic_top.sum(axis=1)
        temp2[temp2 == 0] = 1
        self.document_topic_prob = document_topic_top / temp2.reshape(self.number_of_documents, 1)
        # print(self.document_topic_prob.shape)


    def calculate_likelihood(self, number_of_topics):

        td_matrix = np.array(self.term_doc_matrix)
        count_w_d = td_matrix.T.reshape((self.number_of_documents, 1, self.vocabulary_size))
        P_z_d = self.document_topic_prob.reshape((self.document_topic_prob.shape[0], self.document_topic_prob.shape[1], 1))
        P_w_z = self.topic_word_prob.reshape((1, self.document_topic_prob.shape[1], self.vocabulary_size))
        likelihood = count_w_d * np.log(np.sum(P_z_d * P_w_z, axis=1) + 1e-5)
        self.likelihoods.append(likelihood.sum())

        return

    def plsa(self, number_of_topics, max_iter, epsilon):

        print ("EM iteration begins...")
        
        # build term-doc matrix
        self.build_term_doc_matrix()
        
        # Create the counter arrays.
        
        # P(z | d, w)
        self.topic_prob = np.zeros([self.number_of_documents, number_of_topics, self.vocabulary_size], dtype=np.float)

        # P(z | d) P(w | z)
        self.initialize(number_of_topics, random=True)

        # Run the EM algorithm
        current_likelihood = 0.0
        diff = []
        for iteration in range(max_iter):
            print("Iteration #" + str(iteration + 1) + "...")

            self.expectation_step()
            self.maximization_step(number_of_topics)
            self.calculate_likelihood(number_of_topics)
            if len(self.likelihoods) == 1:
                diff.append(self.likelihoods[0] - current_likelihood)
                if abs(self.likelihoods[0] - current_likelihood) <= epsilon:
                    break
            else:
                diff.append(self.likelihoods[-1] - self.likelihoods[-2])
                if abs(self.likelihoods[-1] - self.likelihoods[-2]) <= epsilon:
                    # print(self.likelihoods[-1] - self.likelihoods[-2])
                    break
        # print("likelihoods:\n", self.likelihoods)
        # print(self.topic_word_prob)
        # print(self.document_topic_prob)
        # print(np.array(self.term_doc_matrix).shape)
        # print(self.document_topic_prob.shape)
        # print(self.topic_word_prob.shape)
        # print(self.topic_prob.shape)
        # print(diff)

def main(selection):
    # Check the current platform to use corresponding styles of paths
    # For Mac OS / Linux
    if platform.system().lower() != "windows":
        global delimiter 
        delimiter = "/"
        documents_path = txtlist('./papers/data')
        documents_path = documents_path[:100]
    else:
        # For Windows
        documents_path = txtlist(r'.\papers\data')
        documents_path = documents_path[:100]

    with open('paper_lists.txt', 'w') as f:
        for item in documents_path:
            f.write("%s\n" % item)
        
    corpus = Corpus(documents_path)
    corpus.build_corpus()
    corpus.build_vocabulary()
    print("Vocabulary size:" + str(len(corpus.vocabulary)))
    print("Number of documents:" + str(len(corpus.documents)))
    number_of_topics = 10
    max_iterations = 100
    epsilon = 0.01
    corpus.plsa(number_of_topics, max_iterations, epsilon)

    # print(corpus.p_w.sum(axis=1).shape)
    prob_matrix = corpus.p_w.sum(axis=1)
    vocab = np.array(corpus.vocabulary)
    # np.savetxt("prob_matrix.txt", prob_matrix)
    # np.savetxt("vocabulary.txt", vocab, fmt='%s', encoding='utf-8')
    # print(corpus.vocabulary[0])
    print(vocab.shape)
    print(prob_matrix.shape)
    # print(corpus.documents)
if __name__ == '__main__':
    # selection = sys.argv[1]
    selection = "machine learning"
    main(selection)
