import codecs
import string
import nltk
import math
import scipy
import numpy as np
import sys
from datetime import datetime
from tweetAnalysis import SentiTweet, LRSentiClassifier, normalization
from utility import get_ticks
import pickle
import time

# note the relevance score of BM25 is about 3-4 times smaller than cosine,
# so the first weight need to be larger.
# for content relevance, time relevance, content similarity, time diversity
news_weight = [0.4, 1.0, -0.5, 1.0]
# news_threshold = 0.005
news_threshold_damping_ratio = 0.3  # 0.35
tweets_threshold = -500
# for content relevance, sentiment, content similarity with news (pos or
# neg), and content similarity
tweets_weight = [1.0, 1.0, 0.5, -1.6]
beta = 1.0
cohits_mu = 10.0


def summarization(sentiCL, news, tweets, word_distribution, vectorizer, mu, sigma, topk, debug=0):
    # with open('testtime','w') as f:
    #     pickle.dump([sentiCL, news, tweets, word_distribution, vectorizer, mu, sigma, topk, debug ],f)
    #     exit(0)
    word_distribution = word_distribution / np.linalg.norm(word_distribution)

    t1 = time.time()
    news_titles_vec = vectorizer.transform([n.title for n in news])
    tweets_content_vec = vectorizer.transform([t.raw_text for t in tweets])
    news, news_titles_vec = removeZeroVector(news, news_titles_vec)
    tweets, tweets_content_vec = removeZeroVector(tweets, tweets_content_vec)
    t2 = time.time()
    # print 'vectorize', (t2 - t1)

    news_rele, tweets_rele = computeBM25(
        news_titles_vec, tweets_content_vec, word_distribution)
    # print time.time()-t2
    # news_rele, _ = computeContentRelevance(news_titles_vec, tweets_content_vec, word_distribution)
    tweets, tweets_content_vec, tweets_rele = getRelevantTweets(
        tweets, tweets_content_vec, tweets_rele)
    t3 = time.time()
    # print 'cosine', (t3 - t2)
    # news, tweets, news_titles_vec, tweets_content_vec, news_rele, tweets_rele = coHits(news, tweets, news_titles_vec, tweets_content_vec, news_rele, tweets_rele)
    t4 = time.time()
    # print 'cohits', (t4 - t3)
    print
    print "News Summary"
    news_summary, news_summary_vec = getNewsSummary(
        news, news_rele, news_titles_vec, mu, sigma, topk)
    t5 = time.time()
    print "=========="
    print "Tweet Summary"
    # print 'news summary time', (t5 - t4)
    # print '======================'

    # print "t5-t6 tweets length", len(tweets)
    tweets_summary, sentiment = getTweetsSummary(
        sentiCL, tweets, tweets_rele, tweets_content_vec, news_summary_vec, topk)
    t6 = time.time()
    # print 'tweets summary time', (t6 - t5)

    # news_summary is a list of news objects, and the tweets_summary is a list
    # of tweet text.
    return news_summary, tweets_summary, tweets, tweets_rele, sentiment


# compute relevance score
def computeBM25(news_vec, tweets_vec, word_distribution):
    # k1=1.6
    # b=0.75
    # top_count = 100
    # top_words = word_distribution.argsort()[::-1][:top_count]

    # dist = word_distribution[top_words]
    # top_news_vec = np.ceil(news_vec[:, top_words]).toarray()
    # top_tweets_vec = np.ceil(tweets_vec[:, top_words]).toarray()

    # nNews = news_vec.shape[0]
    # nTweets = tweets_vec.shape[0]
    # avg_doc_len_n = float(news_vec.data.size) / nNews
    # avg_doc_len_t = float(tweets_vec.data.size) / nTweets

    # t1=time.time()

    # news_len = np.tile((news_vec!=0).sum(axis = 1).A1*b/avg_doc_len_n, (top_count,1)).T
    # tweets_len = np.tile((tweets_vec!=0).sum(axis = 1).A1*b/avg_doc_len_t, (top_count,1)).T
    # t2=time.time()
    # print 'new0',t2-t1
    # news_score = ( dist*top_news_vec*(k1+1)/ (top_news_vec + k1*(1-b+news_len)) ).sum(axis=1)
    # tweets_score = ( dist*top_tweets_vec*(k1+1)/ (top_tweets_vec + k1*(1-b+tweets_len)) ).sum(axis=1)
    # t3=time.time()
    # print 'new1',t3-t2
    ######
    top_count = word_distribution.size
    top_count = 100
    top_words = word_distribution.argsort()[::-1][:top_count]
    dist = word_distribution[top_words]
    avg_doc_len_n = float(news_vec.data.size) / news_vec.shape[0]
    avg_doc_len_t = float(tweets_vec.data.size) / tweets_vec.shape[0]
    top_news_vec = news_vec[:, top_words].T
    top_tweets_vec = tweets_vec[:, top_words].T

    news_score = np.zeros(news_vec.shape[0])
    news_len = np.ceil(news_vec).sum(axis=1).T.A1

    tweets_score = np.zeros(tweets_vec.shape[0])
    tweets_len = np.ceil(tweets_vec).sum(axis=1).T.A1

    top_news_vec = np.ceil(top_news_vec).toarray()
    top_tweets_vec = np.ceil(top_tweets_vec).toarray()

    for i in xrange(len(top_words)):
        # news_score += dist[i] * idf[i] * ((2.6 * top_news_vec[i, :]) / (top_news_vec[i, :] + 1.6 * (0.25 + 0.75 / avg_doc_len * news_len )))
        news_score += dist[i] * ((2.6 * top_news_vec[i, :]) / (
            top_news_vec[i, :] + 1.6 * (0.25 + 0.75 / avg_doc_len_n * news_len)))

        # tweets_freq = np.ceil(top_tweets_vec[i, :])

        tweets_score += dist[i] * ((2.6 * top_tweets_vec[i, :]) / (
            top_tweets_vec[i, :] + 1.6 * (0.25 + 0.75 / avg_doc_len_t * tweets_len)))
        # tweets_score += dist[i] * idf[i] * ((2.6 * top_tweets_vec[i, :]) / (top_tweets_vec[i, :] + 1.6 * (0.25 + 0.75 / avg_doc_len * tweets_len )))
    # print 'old',time.time()-t3

    return news_score, tweets_score


def computeContentRelevance(news_vec, tweets_vec, word_distribution):
    dist_len = np.linalg.norm(word_distribution)

    news_score = []
    for i in xrange(news_vec.shape[0]):
        news_score.append(
            computeCosSim(news_vec[i, :].toarray()[0], word_distribution, dist_len))

    tweets_score = []
    for i in xrange(tweets_vec.shape[0]):
        tweets_score.append(
            computeCosSim(tweets_vec[i, :].toarray()[0], word_distribution, dist_len))

    return np.array(news_score), np.array(tweets_score)


def computeCosSim(text_vec, word_distribution, dist_len):
    return (np.dot(text_vec, word_distribution) / dist_len)


# get relevant news and tweets
def removeZeroVector(text, vec):
    nonzeros = list(set(vec.tocoo().row))
    nonzero_vec = vec[nonzeros, :]
    nonzero_text = [text[i] for i in nonzeros]
    return nonzero_text, nonzero_vec


def getRelevantTweets(tweets, tweets_content_vec, tweets_rele):
    length = min(len(tweets), 2000)
    top_tweets = (tweets_rele.argsort())[::-1][:length]
    top_tweets_vec = tweets_content_vec[top_tweets, :]
    top_tweets_rele = tweets_rele[top_tweets]
    top_tweets_content = [tweets[i].raw_text for i in top_tweets]

    return top_tweets_content, top_tweets_vec, top_tweets_rele


# get news summary based on relevance & diversity of content & time
def getNewsSummary(news, news_rele, news_titles_vec, mu, sigma, topk):
    time_rele = computeTimeRelevance(news, mu, sigma)
    score = news_weight[0] * news_rele + news_weight[1] * time_rele
    div = np.zeros(len(news))
    time_div = np.zeros(len(news))

    summary = []
    summary_vec = []
    news_threshold = 0
    highest_news_rele = 0
    for i in xrange(0, topk):
        updated_score = score + \
            news_weight[2] * div + news_weight[3] * time_div
        selected = np.argmax(updated_score)

        # threshold
        if updated_score[selected] < news_threshold:
            break
        if news_threshold == 0:
            news_threshold = updated_score[
                selected] * news_threshold_damping_ratio

        # should at least half as relevent as highest
        if highest_news_rele == 0:
            highest_news_rele = news_rele[selected]
        elif news_rele[selected] < highest_news_rele * 0.6:
            break
        summary.append(news[selected])
        summary_vec.append(news_titles_vec[selected, :])
        print news[selected].title.encode('utf-8')
        print 'weighted=', updated_score[selected], 'content rele=', news_rele[selected], 'content sim=', div[selected], 'time rele=', time_rele[selected], 'time div=', time_div[selected]
        print
        div = updateDiversity(
            news_titles_vec[selected, :], i, news_titles_vec, div)
        updateTimeDiversity(
            news[selected].created_at, news, time_div, mu, sigma)

    return summary, summary_vec


def computeTimeRelevance(news, mu, sigma):
    news_score = []
    for n in news:
        timestamp = get_ticks(n.created_at)
        news_score.append(scipy.stats.norm(mu, sigma).pdf(timestamp))
    return np.array(news_score)


def updateDiversity(selected_vec, num_summary, news_titles_vec, div):
    selected_vec = selected_vec.toarray()[0]
    ###
    div_new = news_titles_vec.dot(selected_vec)
    div = np.maximum(div_new, div)
    return div
    # print 'div0',div0
    ###
    # for i in xrange(news_titles_vec.shape[0]):
    #     sim = computeCosSim(news_titles_vec[i, :].toarray()[0], selected_vec, 1.0)
    # div[i] = (float(div[i]) * (num_summary) + sim) / float(num_summary + 1) #average similarity
    #     if sim > div[i] :
    # div[i] = sim #maximum similarity
    # print 'div',div


def updateTimeDiversity(sel_time, news, time_div, mu, sigma):
    sel_time = get_ticks(sel_time)
    norm = scipy.stats.norm(mu, sigma)
    sel_cdf = norm.cdf(sel_time)

    for i in xrange(0, len(news)):
        timestamp = get_ticks(news[i].created_at)
        time_dif = math.fabs(norm.cdf(timestamp) - sel_cdf)
        if time_dif < time_div[i]:
            time_div[i] = time_dif


# get tweets summary based on tweets relevance, sentiment and diversity
def getTweetsSummary(sentiCL, tweets, tweets_rele, tweets_content_vec, news_summary_vec_list, topk):
    sentiment = computeSentiment(sentiCL, tweets)  # provided by Min
    news_sim = np.zeros(len(tweets))
    for i in xrange(len(news_summary_vec_list)):
        news_sim = updateTweetsDiversity(
            news_summary_vec_list[i], i, tweets_content_vec, news_sim)
    div = np.zeros(len(tweets))

    for i in xrange(len(tweets)):
        if tweets[i]=="MacBook &amp; Apple Watch":
            tweets_rele[i]=-50

    score = tweets_weight[0] * tweets_rele + tweets_weight[1] * sentiment + tweets_weight[2] * news_sim

    
    summary = []
    highest_tweets_rele = 0
    for i in xrange(0, topk):

        updated_score = score + tweets_weight[3] * div
        selected = np.argmax(updated_score)
        if highest_tweets_rele == 0:
            highest_tweets_rele = tweets_rele[selected]
        # elif tweets_rele[selected] < 0.2 * highest_tweets_rele:
        #     break

        if updated_score[selected] < tweets_threshold:
            print "deleted"
            print tweets[selected].encode('utf-8')
            print 'weighted=', updated_score[selected], 'content rele=', tweets_rele[selected], 'senti=', sentiment[selected], 'news sim=', news_sim[selected], 'tweets sim=', div[selected]
            print
            break
        
        summary.append(tweets[selected])
        print tweets[selected].encode('utf-8')
        print 'weighted=', updated_score[selected], 'content rele=', tweets_rele[selected], 'senti=', sentiment[selected], 'news sim=', news_sim[selected], 'tweets sim=', div[selected]
        print
        div = updateTweetsDiversity(
            tweets_content_vec[selected, :], i, tweets_content_vec, div)

    return summary, sentiment


def computeSentiment(sentiCL, tweets):
    sentiment = []
    for t in tweets:
        sentiment.append(sentiCL.getPolarityScore(t))
    return np.array(sentiment)


def updateTweetsDiversity(selected_vec, num_summary, tweets_content_vec, div):
    selected_vec = selected_vec.toarray()[0]
    ####
    div_new = tweets_content_vec.dot(selected_vec)
    div = np.maximum(div_new, div)
    return div
    ####
    # for i in xrange(tweets_content_vec.shape[0]):
    #     sim = computeCosSim(tweets_content_vec[i, :].toarray()[0], selected_vec, 1.0)
    # div[i] = (float(div[i]) * (num_summary) + sim) / float(num_summary + 1) #average similarity
    #     if sim > div[i] :
    # div[i] = sim #maximum similarity


# co-HITS algorithm
def coHits(news, tweets, news_vec, tweets_vec, news_rele, tweets_rele):
    network = getNetwork(news_vec, tweets_vec)
    network, diag, news_nonzeros, tweets_nonzeros = getDiagonalMat(network)

    news_rele = news_rele[news_nonzeros]
    tweets_rele = tweets_rele[tweets_nonzeros]
    news_vec = news_vec[news_nonzeros, :]
    tweets_vec = tweets_vec[tweets_nonzeros, :]
    news = [news[i] for i in news_nonzeros]
    tweets = [tweets[i] for i in tweets_nonzeros]

    full_network = np.concatenate(
        (network.dot(network.T), beta * network), axis=1)
    full_network = np.concatenate((full_network, np.concatenate(
        (beta * network.T, network.T.dot(network)), axis=1)), axis=0)

    score = np.concatenate((news_rele, tweets_rele), axis=1).T

    score = cohits_mu / (1.0 + cohits_mu) * np.linalg.inv(
        (np.eye(score.size) - 1.0 / (1.0 + cohits_mu) * diag * full_network * diag)).dot(score)
    return news, tweets, news_vec, tweets_vec, score[:news_rele.size], score[news_rele.size:]


def getNetwork(news_vec, tweets_vec):
    network = []
    for i in xrange(news_vec.shape[0]):
        row = []
        n_vec = news_vec[i, :].toarray()[0]
        for j in xrange(tweets_vec.shape[0]):
            row.append(
                computeCosSim(tweets_vec[j, :].toarray()[0], n_vec, 1.0))
        network.append(row)

    return np.array(network)


def getDiagonalMat(network):
    news_diag_values = np.sum(network, axis=1).T
    tweets_diag_values = np.sum(network, axis=0)
    news_nonzeros = np.nonzero(news_diag_values)[0]
    tweets_nonzeros = np.nonzero(tweets_diag_values)[0]

    network = network[news_nonzeros, :]
    network = network[:, tweets_nonzeros]

    diag_values = np.concatenate(
        (news_diag_values[news_nonzeros], tweets_diag_values[tweets_nonzeros]), axis=1)

    diag_values = np.sqrt(diag_values)
    diag_values = 1.0 / diag_values

    return network, np.diag(diag_values), news_nonzeros, tweets_nonzeros


if __name__ == '__main__':
    f = open('testtime')
    [sentiCL, news, tweets, word_distribution, vectorizer,
        mu, sigma, topk, debug] = pickle.load(f)

    summarization(sentiCL, news, tweets, word_distribution,
                  vectorizer, mu, sigma, topk, debug)
