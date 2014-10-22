import twython
import codecs
import simplejson
import datetime, time
import sys
import os
from apscheduler.schedulers.background import BackgroundScheduler

#To run this file, parameters are -w keywords -o output_file_name -i interval (minutes, default 30) -d duration(days, default 1), multiple keywords are connected with +
#and the tweets that contain keywords will constantly flow in and be written to the output_file_name, until you manually kill this process

def GetLastLine(input_file) :
	file = codecs.open(input_file, "r+", encoding = "utf-8")
	file.seek(0, os.SEEK_END)
	pos = file.tell() - 1
	while pos > 0 and file.read(1) != "\n":
		pos -= 1
		file.seek(pos, os.SEEK_SET)

	if pos > 0:
		file.seek(pos, os.SEEK_SET)
		line = file.readlines()
		file.seek(pos, os.SEEK_SET)
		file.truncate()
		file.write('\n')

	file.close()
	return line[1]

#=============Twitter Search API===============================
def TweetSearch(keywords, output_file, interval):
	#find the latest tweet that have been crawled before
	print output_file
	if os.path.exists(output_file):
		last_line = GetLastLine(output_file)
		since_id = last_line.split('\t')[0]
		print since_id
	else:
		since_id = '0'

	output = codecs.open(output_file, 'a', encoding = 'utf-8')

	#open twython
	twitter = twython.Twython('jh7TUj0nNaOSWnRnel8toUvdi', 'L0G0L5pKxA1BjDAc2sTLMTVVxy1tbSvBNo0r0B41l9LjqxmItV', '2802589467-icYj3gXB0vShXtDSsJogTbVZwHqWeGmC3AK1cjS', 'N9n47iYU8wUwM5EC9Qv3PPOmDn1JDfPbV6Bjs921Sl1W4')
	results = twitter.search(q=keywords, result_type = 'recent', count = '100', since_id = since_id)
	max_id = results.get('search_metadata').get('max_id')

	#search until the publish time is earlier than interval
	while 1:
		if results.get('search_metadata').get('count') == 0:
			break
		tweets = results.get('statuses')
		if len(tweets) == 0:
			break

		#check publish time
		time = results.get('statuses')[0].get('created_at')[4:]
		time = time[:15] + ' ' + time[-4:]
		published_time = datetime.datetime.strptime(time, '%b %d %H:%M:%S %Y')	
		now = datetime.datetime.now() + datetime.timedelta(hours=5)
		if now - published_time > datetime.timedelta(minutes = interval):
			break
	
		#write data
		for tweet in tweets:
			if tweet.get('lang') != 'en':
				continue
			#write tweet id, text, and created time
			output.write(tweet.get('id_str') + '\t')
			output.write(tweet.get('text').replace('\t', ' ').replace('\n', ' ') + '\t')
			output.write(tweet.get('created_at') + '\t')

			#write urls contained in the tweet, connected by ','
			urls = tweet.get('entities').get('urls')
			url_text = ''
			if len(urls) > 0:
				for url in urls:
					url_text += url.get('url') + ','
				url_text = url_text[:-1]
			output.write(url_text + '\t')

			#write hashtags contained in the tweet, connected by ','
			hashtags = tweet.get('entities').get('hashtags')
			tag_text = ''
			if len(hashtags) > 0:
				for tag in hashtags:
					tag_text += tag.get('text') + ','
				tag_text = tag_text[:-1]
			output.write(tag_text + '\t')

			#write retweeted status
			retweeted = tweet.get('retweeted_status')
			if retweeted is not None:
				output.write(retweeted.get('id_str') + '\t')
				output.write(str(retweeted.get('favorited')) + '\t')
				output.write(str(retweeted.get('favorite_count')) + '\t')
				output.write(str(retweeted.get('retweeted')) + '\t')
				output.write(str(retweeted.get('retweet_count')) + '\t')
			else:
				output.write('\t\t\t\t\t')

			#write the favorite and retweet counts of this tweet
			output.write(str(tweet.get('favorited')) + '\t')
			output.write(str(tweet.get('favorite_count')) + '\t')
			output.write(str(tweet.get('retweeted')) + '\t')
			output.write(str(tweet.get('retweet_count')) + '\t')

			#write user information
			user = tweet.get('user')
			output.write(user.get('id_str') + '\t')
			output.write(str(user.get('verified')) + '\t')
			output.write(str(user.get('followers_count')) + '\t')
			output.write(str(user.get('statuses_count')) + '\t')
			output.write(str(user.get('friends_count')) + '\t')
			output.write(str(user.get('favorites_count')) + '\t')
			output.write(user.get('created_at') + '\n')

		#query for the next 100 tweets before
		next = results.get('search_metadata').get('next_results')
		if next == None:
			break
		results = twitter.search(q=keywords, result_type = 'recent', count = '100', max_id=next[8:26], since_id = since_id)
	
	#write the latest tweet id for further collecting data
	output.write(str(max_id))
	output.close()


def TweetSearchForNewsGroup(keywords, interval):
	for (news, words) in keywords.items():
		TweetSearch(words, news, interval)

#===================Twitter Streaming API================================	
class MyStreamer(twython.TwythonStreamer):
	output = None
	def __init__(self, app_key, app_secret, token, token_secret, output_file):
		twython.TwythonStreamer.__init__(self, app_key, app_secret, token, token_secret)
		self.output = codecs.open(output_file, 'w', encoding = 'utf-8')
		
	def on_success(self, data):
		self.output.write(simplejson.dumps(data, indent = 4*' '))

	def on_error(self, status_code, data):
		print status_code
	
def TweetStreaming(keywords, output_file):
	stream = MyStreamer('jh7TUj0nNaOSWnRnel8toUvdi', 'L0G0L5pKxA1BjDAc2sTLMTVVxy1tbSvBNo0r0B41l9LjqxmItV', '2802589467-icYj3gXB0vShXtDSsJogTbVZwHqWeGmC3AK1cjS', 'N9n47iYU8wUwM5EC9Qv3PPOmDn1JDfPbV6Bjs921Sl1W4', output_file)
	stream.statuses.filter(track=keywords)	


#===================Search Tweets in Cron-Style, i.e., execute every 30 minutes=======================
def CronTweetSearch(keywords, interval, duration):

	scheduler = BackgroundScheduler()
	scheduler.daemonic = False
	start_time = datetime.datetime.now()

	scheduler.add_job(lambda:TweetSearchForNewsGroup(keywords, interval), 'interval', minutes = interval)
	scheduler.start()

	while True:
		time.sleep(5000)
		now = datetime.datetime.now()
		if now - start_time > datetime.timedelta(days = duration):
			scheduler.shutdown()
			return

	
#====================Main===============================================
if __name__ == '__main__':
	output_file = 'twitter.txt'
	keywords[output_file] = 'hong kong protester'
	interval = 30
	duration = 1
	
	for i in range(1, len(sys.argv), 2):
		if sys.argv[i] == '-w':
			keywords = ''
			keyword_list = (sys.argv[i+1]).split('+')
			for keyword in keyword_list:
				keywords = keywords + keyword + ' '
			keywords = keywords[:-1]
			
		if sys.argv[i] == '-o':
			output_file = sys.argv[i+1]

		if sys.argv[i] == '-i':
			interval = int(sys.argv[i+1])

		if sys.argv[i] == '-d':
			duration = int(sys.argv[i+1])

	
	CronTweetSearch(keywords, interval, duration)

