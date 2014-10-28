import twython
import codecs
import simplejson
import datetime, time
import sys
import os
import thread
import string
import random

#To run this file, parameters are -w keywords -o output_file_name -i interval (minutes, default 30) -d duration(days, default 1), multiple keywords are connected with +
#and the tweets that contain keywords will constantly flow in and be written to the output_file_name, until you manually kill this process

def GetLastLine(input_file) :
	input = codecs.open(input_file, 'r+', encoding = 'utf-8')
	lines = input.readlines()
	if lines:
		line = (lines[-1].split('\t')[0]).replace('\n', '')
	else:
		return None

	input.seek(0, os.SEEK_END)
	pos = input.tell() - 21
	
	if pos < 0:
		input.seek(0, os.SEEK_SET)
		input.truncate()
	else:
		input.seek(pos, os.SEEK_SET)
		c = input.read(1)
		if (c == '\n'):
			input.truncate()
	
	input.close()
	return line

#=============Twitter Search API===============================
def TweetSearch(keywords, output_file, interval):
	if keywords == '':
		return

	#find the latest tweet that have been crawled before
	since_id = '0'
	if os.path.exists(output_file):
		last_line = GetLastLine(output_file)
		if last_line is None:
			since_id = '0'
		else:
			since_id = last_line
	else:
		since_id = '0'
	max_id = since_id

	try:
		output = codecs.open(output_file, 'a', encoding = 'utf-8')
	except Exception:
		return

	#open twython
	try:
		rand = random.randint(0, 2)
		if rand == 0:
			twitter = twython.Twython('jh7TUj0nNaOSWnRnel8toUvdi', 'L0G0L5pKxA1BjDAc2sTLMTVVxy1tbSvBNo0r0B41l9LjqxmItV', '2802589467-icYj3gXB0vShXtDSsJogTbVZwHqWeGmC3AK1cjS', 'N9n47iYU8wUwM5EC9Qv3PPOmDn1JDfPbV6Bjs921Sl1W4')
		elif rand == 1:
			twitter = twython.Twython('HLrxMgREPf045FIJtRz3WQAb8', ' atZvODDN2gysB61gfKBsCEnqBe1TV1jbSGvnleaUAoqx7ewGsg', '2257147508-SuL04e6ZNka4zfYug4siBoOxTGfjXGoSkGU2knC', 'wvBGZHgV60zUSmRfrmE2oljKZIv9ZixaooHYNDxU1sTsN')
		else:
			twitter = twython.Twython('bvYzhYPQY7YaHXcORdFtzwNKw', 'F6xzVB8Ev3DWzfr8Dl4xv22eKe54fq2bcG8xn79T38mzMNlwmd', '505759082-7xbt6KcsKv7v0lTOoWmReIom7msd5j8HbXcT2DGp', 'Qr65Me3wzQYZA81PmA6FcLngb5hTMzOZTSqgcr2HaD33X')
	except Exception:
		output.write(max_id + '\n')
		output.close()
		return

	try:
		results = twitter.search(q=keywords, result_type = 'recent', count = '100', since_id = since_id)
	except Exception:
		output.write(max_id + '\n')
		output.close()
		return

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
		if since_id == '0' and now - published_time > datetime.timedelta(minutes = interval):
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
	output.write(str(max_id) + '\n')
	output.close()


def TweetSearchForNewsGroup(keywords, interval):
	for (news, words) in keywords.items():
		TweetSearch(words, news, interval)

#===================Twitter Streaming API================================	
#class MyStreamer(twython.TwythonStreamer):
#	output = None
#	def __init__(self, app_key, app_secret, token, token_secret, output_file):
#		twython.TwythonStreamer.__init__(self, app_key, app_secret, token, token_secret)
#		self.output = codecs.open(output_file, 'w', encoding = 'utf-8')
#		
#	def on_success(self, data):
#		self.output.write(simplejson.dumps(data, indent = 4*' '))
#
#	def on_error(self, status_code, data):
#		print status_code
#	
#def TweetStreaming(keywords, output_file):
#	stream = MyStreamer('jh7TUj0nNaOSWnRnel8toUvdi', 'L0G0L5pKxA1BjDAc2sTLMTVVxy1tbSvBNo0r0B41l9LjqxmItV', '2802589467-icYj3gXB0vShXtDSsJogTbVZwHqWeGmC3AK1cjS', 'N9n47iYU8wUwM5EC9Qv3PPOmDn1JDfPbV6Bjs921Sl1W4', output_file)
#	stream.statuses.filter(track=keywords)	


#===================Search Tweets in Cron-Style, i.e., execute every 30 minutes=======================
def CronTweetSearch(keywords, interval, duration):

	if len(keywords) == 0:
		return

	start_time = datetime.datetime.now()

	while True:
		rand = random.randint(0, interval * 60)
		time.sleep(rand)

		thread.start_new_thread(TweetSearchForNewsGroup, (keywords, interval * 2))
		now = datetime.datetime.now()
		if now - start_time > datetime.timedelta(days = duration):
			return

		time.sleep(interval * 60 - rand)

	
#====================Main===============================================
if __name__ == '__main__':
	title = 'twitter'
	source = ''

	output_file = ("".join(c for c in title if c not in (string.punctuation))).replace(' ', '_') + '-' + source.replace(' ', '_')

	keywords = 'update 5-pro-europe parties big election ukraine exit poll'
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

	
	TweetSearch(keywords, output_file, interval)

