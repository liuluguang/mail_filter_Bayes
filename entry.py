import re
import os
import math
import numpy
import matplotlib.pyplot as plt
from Word import *



LOWER_LENGTH = 2
UPPER_LENGTH = 9

training_ham_dict = dict()
training_spam_dict = dict()

total_dict = dict()

removed_vocabulary = set()

origin_vocabulary = set()
vocabulary = set()

model = dict()
prob_ham = 0
prob_spam = 0

stop_words_vocabulary = set()


filter_mode = 0



def change_vocabulary_demo(condition,value):
    global vocabulary
    global training_ham_dict
    global training_spam_dict

    if condition is '>=':
        for word in vocabulary:
            if total_dict.get(word,0) >= value[0]:
                removed_vocabulary.add(word)
    elif condition is '<=':
        for word in vocabulary:
            if total_dict.get(word,0) <= value[0]:
                removed_vocabulary.add(word)
    elif condition is '=':
        for word in vocabulary:
            if total_dict.get(word,0) == value[0] :
                removed_vocabulary.add(word)
    if condition is '>=,<=':
        for word in vocabulary:
            if total_dict.get(word,0) >= value[0] and total_dict.get(word,0) <= value[1] :
                removed_vocabulary.add(word)

    vocabulary = vocabulary - removed_vocabulary
    for word in removed_vocabulary:
        if word in training_ham_dict:
            training_ham_dict.pop(word)
        if word in training_spam_dict:
            training_spam_dict.pop(word)


def change_vocabulary(mode):
    global vocabulary
    global training_ham_dict
    global training_spam_dict

    if mode == '1':
        for word in vocabulary:
            if total_dict.get(word,0) == 1 :
                removed_vocabulary.add(word)
    elif mode == '2':
        for word in vocabulary:
            if total_dict.get(word,0)  <= 5:
                removed_vocabulary.add(word)
    elif mode == '3':
        for word in vocabulary:
            if total_dict.get(word,0) <= 10:
                removed_vocabulary.add(word)
    elif mode == '4':
        for word in vocabulary:
            if total_dict.get(word,0)  <= 15:
                removed_vocabulary.add(word)
    elif mode == '5':
        for word in vocabulary:
            if total_dict.get(word,0)  <= 20:
                removed_vocabulary.add(word)
    else:
        #sort by value. decreased.
        temp_pair = sorted(total_dict.items(), key=lambda x: x[1], reverse=True)
        if mode == '6':
            reduce_count = round(len(temp_pair) * 0.05)
        elif mode == '7':
            reduce_count = round(len(temp_pair) * 0.10)
        elif mode == '8':
            reduce_count = round(len(temp_pair) * 0.15)
        elif mode == '9':
            reduce_count = round(len(temp_pair) * 0.20)
        elif mode == '10':
            reduce_count = round(len(temp_pair) * 0.25)

        for i in range(0, reduce_count):
            word = temp_pair[i][0]
            removed_vocabulary.add(word)

    vocabulary = vocabulary - removed_vocabulary
    for word in removed_vocabulary:
        if word in training_ham_dict:
            training_ham_dict.pop(word)
        if word in training_spam_dict:
            training_spam_dict.pop(word)



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
                elif mode == '3' and not length_good(LOWER_LENGTH,UPPER_LENGTH,word):
                    continue
                vocabulary.add(word)

                if total_dict.__contains__(word):
                    count = total_dict.get(word)
                    total_dict[word] = count + 1
                else:
                    total_dict[word] = 1

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

                if total_dict.__contains__(word):
                    count = total_dict.get(word)
                    total_dict[word] = count+1
                else:
                    total_dict[word] = 1

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
        score_ham = math.log10(prob_ham)
        score_spam = math.log10(prob_spam)
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

                if math.isinf(s_ham) is True:
                    score_ham = -math.inf
                else:
                    if math.isinf(score_ham) is False:
                        score_ham = score_ham + s_ham

                if math.isinf(s_spam) is True:
                    score_spam = -math.inf
                else:
                    if math.isinf(score_spam) is False:
                        score_spam = score_spam + s_spam




    return score_ham, score_spam


def calculate_score(word):
    w = model.get(word,-1)
    if w == -1:
        return 0,0
    try:
        score_ham =  math.log10(w.prob_ham)
    except:
        score_ham = -math.inf

    try:
        score_spam = math.log10(w.prob_spam)
    except:
        score_spam = -math.inf

    return score_ham, score_spam


def read_and_count(path, mode):
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


def testing(path, mode, test_mode):

    # accuracy = right_count / (model_ham_count + model_spam_count)
    # recall ham =  real_ham_count / file_ham_count (max == 1)
    # precision ham = real_ham_count / model_ham_count

    right_count = 0.0

    model_ham_count = 0.0
    model_spam_count = 0.0
    file_ham_count = 0.0
    file_spam_count = 0.0

    real_ham_count = 0.0
    real_spam_count = 0.0


    files = os.listdir(path)
    i = 1
    if mode == '1':
        output = open('baseline-result.txt', 'w')
    elif mode == '2':
        output = open('stopword-result.txt', 'w')
    elif mode == '3':
        output = open('wordlength-result.txt', 'w')
    else:
        output = open('test-'+test_mode+'-result.txt', 'w')

    for file in files:
        f_type = file.split('-')[1]
        if f_type == 'ham':
            file_ham_count = file_ham_count+1
        elif f_type =='spam':
            file_spam_count = file_spam_count+1

        h_score, sp_score = testing_file(path+"/"+file, mode)

        if h_score>=sp_score:
            res = 'ham'
            model_ham_count = model_ham_count +1
        else:
            res = 'spam'
            model_spam_count = model_spam_count +1

        matched = 'wrong'
        if res == f_type and f_type == 'ham':
            matched = 'right'
            real_ham_count = real_ham_count + 1
            right_count = right_count + 1
        elif res == f_type and f_type == 'spam':
            matched = 'right'
            real_spam_count = real_spam_count + 1
            right_count = right_count + 1

        string = str(i) + "  "+ file+"  "+res + "  "+ str(h_score) +"  "+str(sp_score)+"  "+f_type+"  "+matched+'\n'
        print(string)
        output.write(string)
        i = i + 1

    accuracy = right_count / (model_ham_count + model_spam_count)
    recall_ham = real_ham_count / file_ham_count
    if recall_ham > 1:
        recall_ham == 1
    if model_ham_count == 0.0 and real_ham_count != 0.0:
        precision_ham = 0.0
    elif model_ham_count == 0.0 and real_ham_count ==0.0:
        precision_ham = 1.0
    else:
        precision_ham = real_ham_count / model_ham_count

    recall_spam = real_spam_count / file_spam_count
    if recall_spam > 1:
        recall_spam == 1
    if model_spam_count == 0.0 and real_spam_count != 0.0:
        precision_spam = 0.0
    elif model_spam_count == 0.0 and real_spam_count == 0.0:
        precision_spam = 1.0
    else:
        precision_spam = real_spam_count / model_spam_count

    f_measure_ham = (2*recall_ham*precision_ham)/(precision_ham+recall_ham)
    f_measure_spam = (2 * recall_spam * precision_spam) / (precision_spam + recall_spam)
    return accuracy, precision_ham, recall_ham, precision_spam, recall_spam, f_measure_ham, f_measure_spam







filter_mode = input("Please choose running mode. 1. normal 2. Stop words filter 3. Length filter 4. Test 5. Test2 6. Demo 1")
test_mode = ""
if filter_mode is '2':
    init_stop_word_vocabulary('English-Stop-Words.txt')
elif filter_mode == '4':
    test_mode = input("Please input the filter mode. 1. =1 2. <=5 3. <=10 4. <=15 5. <=20 \n "
                      "6. 5% 7. 10% 8. 15% 9. 20% 10. 25%")

read_and_count('train',filter_mode)

if filter_mode == '1':
    generate_file(training_ham_dict, training_spam_dict, 0.5, 'model.txt')
    res = testing('test', filter_mode, test_mode)
    print("Accuracy: " + str(res[0]))
    print("Ham performance:")
    print("Recall: " + str(res[2]) + "  Precision: " + str(res[1]) + "  F-measure: " + str(res[5]))
    print("Spam performance:")
    print("Recall: " + str(res[4]) + "  Precision: " + str(res[3]) + "  F-measure: " + str(res[6]))
elif filter_mode == '2':
    generate_file(training_ham_dict, training_spam_dict, 0.5, 'stopword-model.txt')
    res =testing('test', filter_mode, test_mode)
    print("Accuracy: "+str(res[0]))
    print("Ham performance:")
    print("Recall: " +str(res[2]) +"  Precision: "+str(res[1]) +"  F-measure: "+str(res[5]))
    print("Spam performance:")
    print("Recall: " +str(res[4]) +"  Precision: "+str(res[3]) +"  F-measure: "+str(res[6]))
elif filter_mode == '3':
    generate_file(training_ham_dict, training_spam_dict, 0.5, 'wordlength-model.txt')
    res = testing('test', filter_mode, test_mode)
    print("Accuracy: " + str(res[0]))
    print("Ham performance:")
    print("Recall: " + str(res[2]) + "  Precision: " + str(res[1]) + "  F-measure: " + str(res[5]))
    print("Spam performance:")
    print("Recall: " + str(res[4]) + "  Precision: " + str(res[3]) + "  F-measure: " + str(res[6]))



elif filter_mode == '4':
    origin_vocabulary = vocabulary.copy()
    origin_ham_dict = training_ham_dict.copy()
    origin_spam_dict = training_spam_dict.copy()
    res_list = list()


    for i in range(1,11):
        test_mode = str(i)
        change_vocabulary(test_mode)
        generate_file(training_ham_dict, training_spam_dict, 0.5, 'test-'+test_mode+'-model.txt')
        res = testing('test', filter_mode, test_mode)
        res_list.append(res)
        #recover

        vocabulary = origin_vocabulary.copy() # recover origin vocabulary
        model.clear()
        removed_vocabulary.clear()
        training_spam_dict = origin_spam_dict.copy()
        training_ham_dict = origin_ham_dict.copy()


        #recover
    for result in res_list:
        print("Result: ")
        for item in result:
            print(item)



    x = [0.05,0.10,0.15,0.20,0.25]
    for i in range(0,7):
        plt.figure(figsize=(8, 4))
        plt.title("Test Result")
        plt.xlabel("frequency drop rate%")
        if i == 0:
            name = "2."+"Accuracy"
            plt.ylabel("Accuracy")
        elif i ==1:
            name = "2."+"Precision for HAM"
            plt.ylabel("Precision for HAM")
        elif i ==2:
            name = "2." + "Recall for HAM"
            plt.ylabel("Recall for HAM")
        elif i ==3:
            name = "2." + "Precision for SPAM"
            plt.ylabel("Precision for SPAM")
        elif i ==4:
            name = "2." + "Recall for SPAM"
            plt.ylabel("Recall for SPAM")
        elif i == 5:
            name = "1." + "F-measure for HAM"
            plt.ylabel("F-measure for HAM")
        elif i == 6:
            name = "1." + "F-measure for SPAM"
            plt.ylabel("F-measure for SPAM")
        y = [res_list[5][i],res_list[6][i],res_list[7][i],res_list[8][i],res_list[9][i]]
        plt.plot(x, y)
        plt.savefig(name+".png")

    x = [1,5,10,15,20]
    for i in range(0,7):
        y = [res_list[0][i],res_list[1][i],res_list[2][i],res_list[3][i],res_list[4][i]]
        plt.figure(figsize=(8, 4))
        plt.title("Test Result")
        plt.xlabel("frequency drop count")
        if i == 0:
            name = "1."+"Accuracy"
            plt.ylabel("Accuracy")
        elif i ==1:
            name = "1."+"Precision for HAM"
            plt.ylabel("Precision for HAM")
        elif i ==2:
            name = "1." + "Recall for HAM"
            plt.ylabel("Recall for HAM")
        elif i ==3:
            name = "1." + "Precision for SPAM"
            plt.ylabel("Precision for SPAM")
        elif i ==4:
            name = "1." + "Recall for SPAM"
            plt.ylabel("Recall for SPAM")
        elif i == 5:
            name = "1." + "F-measure for HAM"
            plt.ylabel("F-measure for HAM")
        elif i == 6:
            name = "1." + "F-measure for SPAM"
            plt.ylabel("F-measure for SPAM")
        plt.plot(x, y)
        plt.savefig(name+".png")

elif filter_mode == '5':
    origin_vocabulary = vocabulary.copy()
    origin_ham_dict = training_ham_dict.copy()
    origin_spam_dict = training_spam_dict.copy()
    res_list = list()
    array = numpy.arange(0.0, 1.1, 0.1)

    for i in array:
        test_mode = str(i)
        generate_file(training_ham_dict, training_spam_dict, i, 'test-'+test_mode+'-model.txt')
        res = testing('test', filter_mode, test_mode)
        res_list.append(res)
        #recover
        vocabulary = origin_vocabulary.copy() # recover origin vocabulary
        model.clear()
        removed_vocabulary.clear()
        training_spam_dict = origin_spam_dict.copy()
        training_ham_dict = origin_ham_dict.copy()
        #recover

    print(res_list)
    x = array
    for i in range(0, 7):
        plt.figure(figsize=(8, 4))
        plt.title("Test Result")
        plt.xlabel("Delta value (smooth)")
        if i == 0:
            name = "3." + "Accuracy"
            plt.ylabel("Accuracy")
        elif i == 1:
            name = "3." + "Precision for HAM"
            plt.ylabel("Precision for HAM")
        elif i == 2:
            name = "3." + "Recall for HAM"
            plt.ylabel("Recall for HAM")
        elif i == 3:
            name = "3." + "Precision for SPAM"
            plt.ylabel("Precision for SPAM")
        elif i == 4:
            name = "3." + "Recall for SPAM"
            plt.ylabel("Recall for SPAM")
        elif i == 5:
            name = "3." + "F-measure for HAM"
            plt.ylabel("F-measure for HAM")
        elif i == 6:
            name = "3." + "F-measure for SPAM"
            plt.ylabel("F-measure for SPAM")

        y = [res_list[0][i], res_list[1][i], res_list[2][i], res_list[3][i], res_list[4][i], res_list[5][i],
             res_list[6][i], res_list[7][i], res_list[8][i], res_list[9][i], res_list[10][i]]
        plt.plot(x, y)
        plt.savefig(name + ".png")
elif filter_mode == '6':
    filter_condition = input("Please input the filter condition ( >=  <= =   >=&&<=)")
    filter_value = input("Please input the filter value ( 5    5,9 )")
    change_vocabulary_demo(filter_condition, filter_value.split(','))
    generate_file(training_ham_dict, training_spam_dict, 0.5, 'demo-model-exp4.txt')
    res = testing('test', filter_mode, test_mode)





