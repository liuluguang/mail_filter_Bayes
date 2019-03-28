import re
import os
import math
from Word import *



training_ham_dict = dict()
training_spam_dict = dict()
vocabulary = set()
model = dict()
prob_ham = 0
prob_spam = 0


def generate_file(ham_dic, spam_dic, smooth, path):
    lines = []
    file = open(path,'a')

    total_count_ham = 0
    total_count_spam = 0
    for value in ham_dic.values():
        total_count_ham = total_count_ham + value
    for value in spam_dic.values():
        total_count_spam = total_count_spam + value

    total_count_ham_smooth = total_count_ham + smooth * len(vocabulary)
    total_count_spam_smooth = total_count_spam + smooth * len(vocabulary)
    i = 1
    for word in sorted(vocabulary):
        word_in_ham_smooth = ham_dic.get(word,0) + smooth
        word_in_spam_smooth = spam_dic.get(word, 0) + smooth

        line = str(i) + "  "+ word +"  " + str(word_in_ham_smooth) + "  " \
               + str(word_in_ham_smooth/total_count_ham_smooth) + "  "\
               + str(word_in_spam_smooth) + "  "+str(word_in_spam_smooth/total_count_spam_smooth) +'\n'
        w = Word(word, word_in_ham_smooth, word_in_ham_smooth/total_count_ham_smooth,
                 word_in_spam_smooth, word_in_spam_smooth/total_count_spam_smooth)
        lines.append(line)
        file.write(line)
        model[word] = w

        i = i+1










def trainning_ham(file):
    with open(file, encoding='latin-1') as f:
        for line in f:
            res = re.split('[^a-zA-Z]',line)
            for word in res:
                if word == '' or word == ' ':
                    continue

                word = word.lower()
                vocabulary.add(word)

                if training_ham_dict.__contains__(word):
                    count = training_ham_dict.get(word)
                    training_ham_dict[word] = count+1
                else:
                    training_ham_dict[word] = 1



def trainning_spam(file):
    with open(file, encoding='latin-1') as f:
        for line in f:
            res = re.split('[^a-zA-Z]',line)
            for word in res:
                if word == '' or word == ' ':
                    continue

                word = word.lower()
                vocabulary.add(word)
                if training_spam_dict.__contains__(word):
                    count = training_spam_dict.get(word)
                    training_spam_dict[word] = count+1
                else:
                    training_spam_dict[word] = 1


def testing_file(file):
    words_in_file = list()
    score_ham = 0.0
    score_spam = 0.0
    with open(file, encoding='latin-1') as f:
        for line in f:
            res = re.split('[^a-zA-Z]',line)
            for word in res:
                if word == '' or word == ' ':
                    continue
                word = word.lower()
                words_in_file.append(word)
                s_ham, s_spam = calculate_score(word)
                score_ham = score_ham + s_ham
                score_spam = score_spam + s_spam

    return score_ham, score_spam


def calculate_score(word):
    score_ham = math.log10(prob_ham)
    score_spam = math.log10(prob_spam)
    w = model.get(word,-1)
    if w == -1:
        return 0,0
    score_ham = score_ham + math.log10(w.prob_ham)
    score_spam = score_spam + math.log10(w.prob_spam)
    return score_ham, score_spam








def training(path):
    global prob_spam
    global  prob_ham
    count_of_ham_files = 0
    count_of_spam_files = 0
    files = os.listdir(path)
    for file in files:
        if 'ham' in file:
            trainning_ham(path+'/'+file)
            count_of_ham_files = count_of_ham_files + 1
        else:
            trainning_spam(path+'/'+file)
            count_of_spam_files = count_of_spam_files + 1
    prob_ham = count_of_ham_files / (count_of_ham_files + count_of_spam_files)
    prob_spam = count_of_spam_files / (count_of_ham_files + count_of_spam_files)

def testing(path):

    files = os.listdir(path)
    i = 1
    output = open('baseline-result.txt', 'a')
    for file in files:


        f_type = file.split('-')[1]
        h_score, sp_score = testing_file(path+"/"+file)
        if h_score>=sp_score:
            res = 'ham'
        else:
            res = 'spam'
        matched = 'wrong'
        if res == f_type:
            matched = 'right'
        string = str(i) + "  "+ file+"  "+res + "  "+ str(h_score) +"  "+str(sp_score)+"  "+f_type+"  "+matched+'\n'
        print(string)
        output.write(string)
        i = i + 1







training('train')
generate_file(training_ham_dict, training_spam_dict, 0.5, 'model.txt')

testing('test')
print(training_ham_dict)
print(training_spam_dict)