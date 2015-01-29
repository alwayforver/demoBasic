import MySQLdb
import os
import sys
import time
import codecs
import datetime
import threading

#The code works in two ways.
#You can specify the starting and ending dates you want to dump, for example, python DB.py 2014-12-01 2014-12-03 will dump data of the opening three days in Dec.
#If you don't specify the dates, the program will first dump data of the day before yesterday, and then dump data once every day.


def DumpTweets(username, password, dbname, date, tmp_file, tweet_files):
	dbconnection = MySQLdb.connect('localhost', username, password, dbname)
	cursor = dbconnection.cursor()

	tmp_file = os.getcwd().replace('\\', '/') + '/tmp/' + tmp_file
	output = codecs.open(tmp_file, 'w', encoding = 'utf-8')

	for file in tweet_files:
		tweet_file = os.getcwd().replace('\\', '/') + '/tweets/' + date + '/' + file
		if os.path.getsize(tweet_file) < 30:
			continue

		sql = 'LOAD DATA INFILE \'' + tweet_file + '\' IGNORE INTO TABLE overviews_tweet CHARACTER SET utf8mb4 (ID, raw_text, @var_tweet_time, tweet_urls, hash_tags, retweet_id, @var_retweet_favorited, retweet_favorite_count, @var_retweet_retweeted, retweet_retweet_count, @var_tweet_favorited, favorite_count, @var_tweet_retweeted, retweet_count, user, @var_user_verified, followers_count, status_count, friends_count, user_favorites_count, @var_user_time, location, coordinates, source, mentions, reply_user_id, reply_status_id) SET created_at = CONVERT_TZ(STR_TO_DATE(CONCAT(SUBSTR(@var_tweet_time, 1, 19), SUBSTR(@var_tweet_time, 26, 5)), \'%a %b %d %T %Y\'), CONCAT(SUBSTR(@var_tweet_time, 21, 3), \':00\'), \'+00:00\'), user_created_at = CONVERT_TZ(STR_TO_DATE(CONCAT(SUBSTR(@var_user_time, 1, 19), SUBSTR(@var_user_time, 26, 5)), \'%a %b %d %T %Y\'), CONCAT(SUBSTR(@var_user_time, 21, 3), \':00\'), \'+00:00\'), retweet_is_favorited = IF(@var_retweet_favorited = \'True\', 1, 0), retweet_is_retweeted = IF(@var_retweet_retweeted = \'True\', 1, 0), is_favorited = IF(@var_tweet_favorited = \'True\', 1, 0), is_retweet = IF(@var_tweet_retweeted = \'True\', 1, 0), verified = IF(@var_user_verified = \'True\', 1, 0)'
		cursor.execute(sql)
		dbconnection.commit()

		news_id = file.split('_')[0]
		input = codecs.open(tweet_file, encoding = 'utf-8')
		lines = input.readlines()[:-1]

		for line in lines:
			tweet_id = line.split('\t')[0]
			if len(tweet_id) > 0 and tweet_id[0].isdigit() and tweet_id[-1].isdigit():
				output.write(tweet_id + '\t' + news_id + '\n')
		input.close()
	
	output.close()

	sql = 'LOAD DATA INFILE \'' + tmp_file + '\' IGNORE INTO TABLE overviews_tweet_related_news CHARACTER SET utf8mb4 (tweet_id, news_id)'
	cursor.execute(sql)
	dbconnection.commit()
	dbconnection.close()


def Dump(date, username, password, dbname):
	start = datetime.datetime.now()
	print 'Starting Dump Data for ', date, 'at', start

	dbconnection = MySQLdb.connect('localhost', username, password, dbname)
	cursor = dbconnection.cursor()

	news_file = os.getcwd().replace('\\', '/') + '/news/' + date + '.txt'
	sql = 'LOAD DATA INFILE \'' + news_file + '\' IGNORE INTO TABLE overviews_news CHARACTER SET utf8mb4 (ID, url, title, source, @var_news_date, authors,  key_word, snippet, raw_text, @temp) SET created_at = CONVERT_TZ(STR_TO_DATE(SUBSTR(@var_news_date, 1, 25), \'%a, %d %b %Y %T\'), CONCAT(SUBSTR(@var_news_date, 27, 3), \':00\'), \'+00:00\')'
	cursor.execute(sql)
	dbconnection.commit()
	dbconnection.close()

#	tweets_folder = 'tweets/' + date
#	tweet_files = os.listdir(tweets_folder)
#	tweet_partition = [[], [], [], []]
#	threads = []
#	
#	for i in xrange(0, len(tweet_files)):
#		tweet_partition[i % 4].append(tweet_files[i])
#
#	for i in xrange(0, 4):
#		thread = threading.Thread(target = DumpTweets, args = (username, password, dbname, date, 'temp' + str(i), tweet_partition[i]))
#		threads.append(thread)
#		thread.start()
#
#	for thread in threads:
#		thread.join()

	tweets_folder = 'tweets/' + date
	tweet_files = os.listdir(tweets_folder)
	DumpTweets(username, password, dbname, date, 'temp', tweet_files)


	print 'Finished at', datetime.datetime.now()
	print 'Time elapsed ', datetime.datetime.now() - start


if __name__ == '__main__':
	username = 'hcai6'
	password = 'haoyan'
	dbname = 'NewsTwitter0128'

	if not os.path.exists('tmp'):
		os.makedirs('tmp')


	if len(sys.argv) > 1:
		start = sys.argv[1]
		end = sys.argv[2]

		files = os.listdir('news')
		for file in files:
			date = file.split('.')[0]
			if date >= start and date <= end:
				Dump(date, username, password, dbname)

	else:
		daytime = 60 * 60 * 24
		while True:
			today = datetime.date.today()
			before_yesterday = str(today - datetime.timedelta(days=2))
			Dump(before_yesterday, username, password, dbname)
			time.sleep(daytime)






