class Word:
    def __init__(self, word, count_ham, prob_ham, count_spam, prob_spam):
        self.word = word
        self.count_ham = count_ham
        self.prob_ham = prob_ham
        self.prob_spam = prob_spam
        self.count_spam = count_spam