from GoogleNewsCrawler import GoogleNewsCrawler
from twitter import CronTweetSearch, TweetSearchForNewsGroup
import sys
import time
import datetime
import thread
import os


#Crawler for both news and tweets.
#To run, you need to give the parameters by -o output_news_file -t output_folder_for_related_tweets -i interval_for_crawler -d duration_of_searching_tweets
#news are written into a single file output_news_file, tweets are written into a folder, where its file name corresponds to the related news (title + source)
#news and tweets are crawled every 'interval' minutes, and tweets crawler will last for 'duration' time. News crawler will be running until a manual kill.

def Crawler(news_output, twitter_output_folder, interval, duration):
	keywords = GoogleNewsCrawler(10, news_output, twitter_output_folder)
	CronTweetSearch(keywords, interval, duration)

if __name__ == '__main__':
	news_output = 'news.txt'
	twitter_output_folder = 'tweets'
	interval = 30
	duration = 1

	#parse input
	for i in range(1, len(sys.argv), 2):
		if sys.argv[i] == '-o':
			news_output = sys.argv[i+1]
		if sys.argv[i] == '-t':
			twitter_output_folder = sys.argv[i+1]
		if sys.argv[i] == '-i':
			interval = int(sys.argv[i+1])
		if sys.argv[i] == '-d':
			duration = int(sys.argv[i+1])

	if not os.path.exists('news'):
		os.makedirs('news')
	if not os.path.exists(twitter_output_folder):
		os.makedirs(twitter_output_folder)

	while True:
		today = str(datetime.date.today())
		news_output = 'news/' + today + '.txt'
		twitter_output = twitter_output_folder + '/' + today
		if not os.path.exists(twitter_output):
			os.makedirs(twitter_output)
		thread.start_new_thread(Crawler, (news_output, twitter_output, interval, duration))
		time.sleep(interval * 60)

