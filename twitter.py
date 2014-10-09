import twython
import codecs
import simplejson
import datetime, pytz
import sys

#To run this file, parameters are -w keywords -o output_file_name, multiple keywords are connected with +
#and the tweets that contain keywords will constantly flow in and be written to the output_file_name, until you manually kill this process

#=============Twitter Search API===============================
def TweetSearch(keywords, output_file):
	output = codecs.open(output_file, 'w', encoding = 'utf-8')

	twitter = twython.Twython('jh7TUj0nNaOSWnRnel8toUvdi', 'L0G0L5pKxA1BjDAc2sTLMTVVxy1tbSvBNo0r0B41l9LjqxmItV', '2802589467-icYj3gXB0vShXtDSsJogTbVZwHqWeGmC3AK1cjS', 'N9n47iYU8wUwM5EC9Qv3PPOmDn1JDfPbV6Bjs921Sl1W4')
	results = twitter.search(q=keywords, count = '100')

	while 1:
		if results.get('search_metadata').get('count') == '0':
			break
		time = results.get('statuses')[0].get('created_at')[4:]
		time = time[:15] + ' ' + time[-4:]
		published_time = datetime.datetime.strptime(time, '%b %d %H:%M:%S %Y')
		print published_time
	
		now = datetime.datetime.now() + datetime.timedelta(hours=5)
		if now - published_time > datetime.timedelta(days=1):
			break
	
		output.write(simplejson.dumps(results, indent = 4*' '))
		next = results.get('search_metadata').get('next_results')
		if next == None:
			break
		results = twitter.search(q=keywords, count = '100', max_id=next[8:26])
	
	output.close()

#===================Twitter Streaming API================================	
class MyStreamer(twython.TwythonStreamer):
	output = None
	def __init__(self, app_key, app_secret, token, token_secret, output_file):
		MyStreamer.__init__(self, app_key, app_secret, token, token_secret)
		self.output = codecs.open(output_file, 'w', encoding = 'utf-8')
		
    def on_success(self, data):
        self.output.write(simplejson.dumps(data, indent = 4*' '))

    def on_error(self, status_code, data):
        print status_code
	
def TweetStreaming(keywords, output_file):
	stream = MyStreamer('jh7TUj0nNaOSWnRnel8toUvdi', 'L0G0L5pKxA1BjDAc2sTLMTVVxy1tbSvBNo0r0B41l9LjqxmItV', '2802589467-icYj3gXB0vShXtDSsJogTbVZwHqWeGmC3AK1cjS', 'N9n47iYU8wUwM5EC9Qv3PPOmDn1JDfPbV6Bjs921Sl1W4', output_file)
	stream.statuses.filter(track=keywords)	

	
#====================Main===============================================
if __name__ == '__main__':
	output_file = 'twitter.txt'
	keywords = 'hong kong protester'
	
	for i in range(1, len(sys.argv), 2):
		if sys.argv[i] == '-w':
			keywords = ''
			keyword_list = (sys.argv[i+1]).split('+')
			for keyword in keyword_list:
				keywords = keywords + keyword + ' '
			keywords = keywords[:-1]
			
		if sys.argv[i] == '-o':
			output_file = sys.argv[i+1]
	
	TweetStreaming(keywords, output_file)

