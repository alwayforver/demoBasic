import MySQLdb
import os
import sys
import time
import codecs
import datetime


def CreateTables(username, password, dbname):
	dbconnection = MySQLdb.connect('localhost', username, password, dbname)
	cursor = dbconnection.cursor()

	cursor.execute("DROP TABLE IF EXISTS News")
	sql = 'Create Table News (news_id INT NOT NULL, news_url VARCHAR(300), news_title VARCHAR(200), news_source VARCHAR(50), news_date VARCHAR(40), news_authors VARCHAR(300), news_keywords VARCHAR(200), news_snippets VARCHAR(500), news_content VARCHAR(20000), PRIMARY KEY (news_id) )'
	cursor.execute(sql)

	cursor.execute("DROP TABLE IF EXISTS Tweets")
	sql = 'CREATE TABLE Tweets (tweet_id CHAR(20) NOT NULL, tweet_text VARCHAR(200), tweet_time CHAR(30), tweet_urls VARCHAR(100), tweet_hashtags VARCHAR(50), retweeted_id CHAR(20), retweeted_favorited CHAR(5), retweeted_favorite_count VARCHAR(10), retweeted_retweeted CHAR(5), retweeted_retweeted_count VARCHAR(10), tweet_favorited CHAR(5), tweet_favorite_count VARCHAR(10), tweet_retweeted CHAR(5), tweet_retweet_count VARCHAR(10), user_id CHAR(10), user_verified CHAR(5), user_followers_count VARCHAR(10), user_status_count VARCHAR(10), user_friends_count VARCHAR(10), user_favorites_count VARCHAR(10), user_created_time CHAR(30), user_location VARCHAR(100), tweet_coordinates VARCHAR(40), tweet_source VARCHAR(30), tweet_mentions VARCHAR(100), tweet_reply_user_id CHAR(10), tweet_reply_status_id CHAR(20), PRIMARY KEY (tweet_id) )'
	cursor.execute(sql)

	cursor.execute("DROP TABLE IF EXISTS Connections")
	sql = 'CREATE TABLE Connections (news_id INT NOT NULL, tweet_id CHAR(20) NOT NULL, PRIMARY KEY (news_id, tweet_id) )'
	cursor.execute(sql)


def Dump(date, username, password, dbname):
	start = datetime.datetime.now()
	print 'Starting Dump Data for ', date, 'at', start

	dbconnection = MySQLdb.connect('localhost', username, password, dbname)
	cursor = dbconnection.cursor()

	news_file = os.getcwd().replace('\\', '/') + '/news/' + date + '.txt'
	sql = 'LOAD DATA LOCAL INFILE \'' + news_file + '\' IGNORE INTO TABLE News CHARACTER SET utf8 (news_id, news_url, news_title, news_source, news_date, news_authors,  news_keywords, news_snippets, news_content, @temp)'
	cursor.execute(sql)
	dbconnection.commit()

	output = codecs.open('temp.txt', 'w', encoding = 'utf-8')
	tweets_folder = 'tweets/' + date
	tweet_files = os.listdir(tweets_folder)
	for file in tweet_files:
		tweet_file = 'tweets/' + date + '/' + file
		if os.path.getsize(tweet_file) < 30:
			continue

		print file
		sql = 'LOAD DATA LOCAL INFILE \'' + tweet_file + '\' IGNORE INTO TABLE Tweets CHARACTER SET utf8 '
		cursor.execute(sql)
		dbconnection.commit()

		news_id = file.split('_')[0]
		input = codecs.open(tweet_file, encoding = 'utf-8')
		lines = input.readlines()[:-1]
		for line in lines:
			tweet_id = line.split('\t')[0]
			output.write(news_id + '\t' + tweet_id + '\n')
		input.close()
	
	output.close()

	sql = 'LOAD DATA LOCAL INFILE \'temp.txt\' INTO TABLE Connections CHARACTER SET utf8 '
	cursor.execute(sql)
	dbconnection.commit()

	dbconnection.close()
	print 'Finished at', datetime.datetime.now()
	print 'Time elapsed ', datetime.datetime.now() - start

def Test(username, password, dbname):
	dbconnection = MySQLdb.connect('localhost', username, password, dbname)
	cursor = dbconnection.cursor()

	sql = 'SELECT * FROM Tweets WHERE tweet_id LIKE "53937"'
	cursor.execute(sql)
	data = cursor.fetchone()
	print data

	dbconnection.close()

if __name__ == '__main__':
	username = 'tong'
	password = '123456'
	dbname = 'news_twitter'

#	Test(username, password, dbname)

	CreateTables(username, password, dbname)
#
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






