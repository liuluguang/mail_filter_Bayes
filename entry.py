import re
import os
import math
from Word import *



LOWER_LENGTH = 2
UPPER_LENGTH = 9

training_ham_dict = dict()
training_spam_dict = dict()
vocabulary = set()

model = dict()
prob_ham = 0
prob_spam = 0

stop_words_vocabulary = set()


filter_mode = 0


def change_vocabulary(mode):
    if mode == '1':
        # 倒序遍历
        for i in range(len(vocabulary) - 1, -1, -1):
            if training_spam_dict[vocabulary[i]] + training_ham_dict[vocabulary[i]] == 0:
                del vocabulary[i]
    elif mode == '2':
        for i in range(len(vocabulary) - 1, -1, -1):
            if training_spam_dict[vocabulary[i]] + training_ham_dict[vocabulary[i]] <= 5:
                del vocabulary[i]
    elif mode == '3':
        for i in range(len(vocabulary) - 1, -1, -1):
            if training_spam_dict[vocabulary[i]] + training_ham_dict[vocabulary[i]] <= 10:
                del vocabulary[i]
    elif mode == '4':
        for i in range(len(vocabulary) - 1, -1, -1):
            if training_spam_dict[vocabulary[i]] + training_ham_dict[vocabulary[i]] <= 15:
                del vocabulary[i]
    elif mode == '5':
        for i in range(len(vocabulary) - 1, -1, -1):
            if training_spam_dict[vocabulary[i]] + training_ham_dict[vocabulary[i]] <= 20:
                del vocabulary[i]





def length_good(lower, upper, word):
    if len(word) < upper and len(word) > lower:
        return True
    else:
        return False



def init_stop_word_vocabulary(path):
    file = open(path,'r')
    for line in file:
        word = line.strip()
        word = word.lower()
        stop_words_vocabulary.add(word)





def generate_file(ham_dic, spam_dic, smooth, path):
    lines = []

    file = open(path,'w')

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
        word_prob_ham = word_in_ham_smooth/total_count_ham_smooth
        word_prob_spam = word_in_spam_smooth/total_count_spam_smooth


        line = str(i) + "  "+ word +"  " + str(word_in_ham_smooth) + "  " \
               + str(word_prob_ham) + "  "\
               + str(word_in_spam_smooth) + "  "+str(word_prob_spam) +'\n'
        w = Word(word, word_in_ham_smooth, word_prob_ham,
                 word_in_spam_smooth, word_prob_spam)
        lines.append(line)
        file.write(line)
        model[word] = w

        i = i+1










def trainning_ham(file, mode):
    with open(file, encoding='latin-1') as f:
        for line in f:
            res = re.split('[^a-zA-Z]',line)
            for word in res:
                if word == '' or word == ' ':
                    continue
                word = word.lower()
                if mode == '2' and word in stop_words_vocabulary:
                    continue
                elif mode =='3' and not length_good(LOWER_LENGTH,UPPER_LENGTH,word):
                    continue
                vocabulary.add(word)

                if training_ham_dict.__contains__(word):
                    count = training_ham_dict.get(word)
                    training_ham_dict[word] = count+1
                else:
                    training_ham_dict[word] = 1



def trainning_spam(file, mode):
    with open(file, encoding='latin-1') as f:
        for line in f:
            res = re.split('[^a-zA-Z]',line)
            for word in res:
                if word == '' or word == ' ':
                    continue
                word = word.lower()
                if mode == '2' and word in stop_words_vocabulary:
                    continue
                elif mode == '3' and not length_good(LOWER_LENGTH,UPPER_LENGTH,word):
                    continue



                vocabulary.add(word)
                if training_spam_dict.__contains__(word):
                    count = training_spam_dict.get(word)
                    training_spam_dict[word] = count+1
                else:
                    training_spam_dict[word] = 1


def testing_file(file,mode):
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
                if mode == '2' and word in stop_words_vocabulary:
                    continue
                elif mode == '3' and not length_good(LOWER_LENGTH, UPPER_LENGTH, word):
                    continue
                words_in_file.append(word)
                s_ham, s_spam = calculate_score(word)
                score_ham = score_ham + s_ham
                score_spam = score_spam + s_spam

    return score_ham, score_spam


def calculate_score(word):
    w = model.get(word,-1)
    if w == -1:
        return 0,0
    score_ham =  math.log10(w.prob_ham)
    score_spam = math.log10(w.prob_spam)
    return score_ham, score_spam


def training(path, mode):
    global prob_spam
    global  prob_ham
    count_of_ham_files = 0
    count_of_spam_files = 0
    files = os.listdir(path)
    for file in files:
        # print("file ...")
        if 'ham' in file:
            trainning_ham(path+'/'+file, mode)
            count_of_ham_files = count_of_ham_files + 1
        else:
            trainning_spam(path+'/'+file, mode)
            count_of_spam_files = count_of_spam_files + 1
    prob_ham = count_of_ham_files / (count_of_ham_files + count_of_spam_files)

    prob_spam = count_of_spam_files / (count_of_ham_files + count_of_spam_files)


def testing(path, mode):

    files = os.listdir(path)
    i = 1
    if mode == '1':
        output = open('baseline-result.txt', 'w')
    elif mode == '2':
        output = open('stopword-result.txt', 'w')
    elif mode == '3':
        output = open('wordlength-result.txt', 'w')

    for file in files:


        f_type = file.split('-')[1]
        h_score, sp_score = testing_file(path+"/"+file, mode)
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





filter_mode = input("Please choose running mode. 1. normal 2. Stop words filter 3. Length filter")

if filter_mode is '2':
    init_stop_word_vocabulary('English-Stop-Words.txt')

training('train',filter_mode)
if filter_mode == '1':
    generate_file(training_ham_dict, training_spam_dict, 0.5, 'model.txt')
elif filter_mode == '2':
    generate_file(training_ham_dict, training_spam_dict, 0.5, 'stopword-model.txt')
elif filter_mode == '3':
    generate_file(training_ham_dict, training_spam_dict, 0.5, 'wordlength-model.txt')



testing('test',filter_mode)
print(training_ham_dict)
print(training_spam_dict)