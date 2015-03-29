import sys
import os
import pickle
from nltk.tokenize import sent_tokenize
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.tag import *
from nltk.corpus import treebank
import math
import csv
from twokenize import tokenize
import time
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import random

class MySentiWordExtractor:
    def __init__(self):
        # print "haha",os.listdir('')
        f = open("./static/script/SentiWordNet_1.0.1.txt")
        self.term_sent = {}
        for line in f.readlines():
            if line[0]!='#':
                cols = line.split('\t')
                pos = cols[0]
                # print cols[2],"!",cols[3]
                score = float(cols[2]) -float(cols[3])
                words = cols[4].split(' ')
                for word_rank in words:
                    word = word_rank.split('#')[0]
                    rank = int(word_rank.split('#')[2])
                    synterm = word+"#"+pos
                    if synterm not in self.term_sent:
                        self.term_sent[synterm] = {}
                    self.term_sent[synterm][rank] = score
    def get_score(self, (word,pos)):
        query = word+'#'+pos
        if query not in self.term_sent:
            return 0
        else:
            score = 0.0;
            denominator = 0.0;
            for k, v in self.term_sent[query].iteritems():

                denominator+=1.0/k
                score+= v* 1.0/k
                # print k, denominator, score
            score = score / denominator
            return score

    def get_second_score(self, (word,pos)):
        poss = ['a','r','v','n']
        poss.remove(pos)
        candidates = []
        for each in poss:

            if self.get_score((word,each))!=0:
                return self.get_score((word,each))
        return 0
    def get_first_score(self,(word,pos)):
        query = word+'#'+pos
        if query not in self.term_sent:
            return 0
        else:
            score = 0.0;
            denominator = 0.0;
            for k, v in self.term_sent[query].iteritems():
                if k<3:
                    denominator+=1.0/k
                    score+= v* 1.0/k
                # print k, denominator, score
            score = score / denominator
            return score


# tokenizer = TreebankWordTokenizer()
# english_stops = set(stopwords.words('english'))
# lemmatizer = WordNetLemmatizer()
# sentiextractor = MySentiWordExtractor()

def normalization(raw_text):
    # to implement normalizaion of tweet text including \xe elimination, RT elimination, http elimination
    # now only easiest way for normalization
    text = raw_text[3:] if raw_text[:3]=="RT " or raw_text[:3]=="rt " else raw_text
    text_fields = text.split()
    text = ' '.join([each for each in text_fields if "http" not in each and "@" not in each])
    text = text.strip()
    return text

class SentiTweet:
    def __init__(self,text):
        self.text = normalization(text)
        tokens = tokenize(self.text)
        self.tokens = tokens
        tokens_postag = nltk.pos_tag(tokens)
        wordnet_tag = []
        for each_pair in tokens_postag:
            if 'NN' in each_pair[1]:
                wordnet_tag.append( (each_pair[0],'n'))
            if 'JJ' in each_pair[1]:
                wordnet_tag.append( (each_pair[0],'a'))
            elif 'RB' in each_pair[1]:
                wordnet_tag.append( (each_pair[0],'r'))
            elif 'VB' in each_pair[1]:
                wordnet_tag.append( (each_pair[0],'v'))

        # lemmatized tokens are lemmatized and lowered
        self.ltoken_tag = []
        for each_pair in wordnet_tag:
            lword = lemmatizer.lemmatize(each_pair[0],each_pair[1])
            self.ltoken_tag.append((lword.lower(), each_pair[1]))

        self.tweet_senti_score = []

        for each_pair in self.ltoken_tag:
            each_score = sentiextractor.get_score(each_pair)
            if abs(each_score)>0.02:
                self.tweet_senti_score.append(each_score)
            else:
                self.tweet_senti_score.append(0)
    def getRawSentiScore(self):
        return abs(sum(self.tweet_senti_score))

class TrainTweet:
    def __init__(self,line):
        fields = line.split('","')
        print fields
        if fields[0]=='"0':
            self.senti = -1
        elif fields[0]=='"2':
            self.senti = 0
        elif fields[0]=='"4':
            self.senti = 1
        self.id = fields[1]
        self.date = fields[2]
        # self.text = fields[5][1:-1]
        self.text = normalization(fields[5][:-1])
        tokens = tokenize(self.text)
        self.tokens = tokens
        tokens_postag = nltk.pos_tag(tokens)
        wordnet_tag = []
        for each_pair in tokens_postag:
            if 'NN' in each_pair[1]:
                wordnet_tag.append( (each_pair[0],'n'))
            if 'JJ' in each_pair[1]:
                wordnet_tag.append( (each_pair[0],'a'))
            elif 'RB' in each_pair[1]:
                wordnet_tag.append( (each_pair[0],'r'))
            elif 'VB' in each_pair[1]:
                wordnet_tag.append( (each_pair[0],'v'))

        # lemmatized tokens are lemmatized and lowered
        self.ltoken_tag = []
        for each_pair in wordnet_tag:
            lword = lemmatizer.lemmatize(each_pair[0],each_pair[1])
            self.ltoken_tag.append((lword.lower(), each_pair[1]))

        self.tweet_senti_score = []

        for each_pair in self.ltoken_tag:
            each_score = sentiextractor.get_score(each_pair)
            if abs(each_score)>0.02:
                self.tweet_senti_score.append(each_score)
            else:
                self.tweet_senti_score.append(0)
    def getRawSentiScore(self):
        return sum(self.tweet_senti_score)


class LRSentiClassifier():
    def __init__(self):

        # polarity_file = open('./polarityClassifier')
        # posneg_file = open('./posnegClassifier')

        polarity_file = open('./overviews/lib/polarityClassifier')
        posneg_file = open('./overviews/lib/posnegClassifier')

        self.polarity_vectorizer, self.polarity_lr = pickle.load(polarity_file)
        self.posneg_vectorizer, self.posneg_lr = pickle.load(posneg_file)
        polarity_file.close()
        posneg_file.close()

    def getPolarityScore(self, text):
        text = normalization(text)
        X = self.polarity_vectorizer.transform([text])
        # print text
        # print X
        # print self.polarity_lr.predict_proba(X)
        return self.polarity_lr.predict_proba(X)[0][1]
        # print self.polarity_lr.predict(X)
        
    def getSentiScore(self, text):
        text = normalization(text)
        polarity_X = self.polarity_vectorizer.transform([text])
        # print type(self.polarity_lr.predict(polarity_X))
        if self.polarity_lr.predict(polarity_X)[0]==0:
            return 0
        else:
            posneg_X = self.posneg_vectorizer.transform([text])
            result = self.posneg_lr(posneg_X)[0]
            if result == 1:
                return 1
            else:
                return -1

# def computeSentiPercentage(sentiCL, tweets, tweets_rele, tweets_po)


if __name__ == '__main__':

    cl = LRSentiClassifier()
    cl.getSentiScore('this is good')
    #   cl.getPolarityScore('this is good')

    # lines = train_file.readlines()

    # print len(lines)
    # trainset = []

    # csv.reader(train_file)

    # line = '"0","1468055262","Mon Apr 06 23:28:39 PDT 2009","NO_QUERY","LarryEisner","@dkoenigs thanks man.  I\'m so very grateful.  I feel unworthy of such attention, though, because I\'m in this because of myself... "'
    # t = TrainTweet(line)
    # print t.text


    # t0 = time.time()
    # # print t.tokens
    # print tokenize('@dkoenigs thanks man.  I\'m so very grateful.  I feel unworthy of such attention, though, because I\'m in this because of myself... ')


    # t1 = time.time()
    # print t1-t0

    # t2 = time.time()
    # print tokenizer.tokenize('@dkoenigs thanks man.  I\'m so very grateful.  I feel unworthy of such attention, though, because I\'m in this because of myself... ')
    # t3 = time.time()

    # print t3-t2
    # print t.ltoken_tag


    # lines = random.shuffle(lines)

    # count = 0

    # for line in lines[:5000]:
    #     line = line.strip()
    #     t = TrainTweet(line)
    #     if t.text!="":
    #         trainset.append(t)
    #         print t.text
    #         print t.ltoken_tag
    #         print t.tweet_senti_score
    #         print "#############"

    # senti = MySentiWordExtractor()


