import sys
import urllib2
import re
import datetime
import newspaper
import codecs
import os
from textblob import TextBlob
import string
import simplejson

# This file crawls news (including full article) from Google News feed
# To run, you need to give the parameters by -n num_of_news -o output_file -t output_folder_for_related_tweets
# where num_of_news is no larger than 10 (default 10), and the news will be appended into the output_file

def GetLastLines(input_file) :
	filesize = os.path.getsize(input_file)
	blocksize = 102400
	input = codecs.open(input_file, 'rb', encoding = 'utf-8')
	last_lines = []

	if filesize > blocksize :
		maxseekpoint = (filesize // blocksize)
		input.seek((maxseekpoint-1)*blocksize)
	elif filesize :
		input.seek(0, 0)

	lines =  input.readlines()
	if lines :
		if len(lines) > 10:
			last_lines = lines[-10:]
		else:
			last_lines = lines

	input.close()
	return last_lines

def GetLatestNews(input_file):
#	latest_news = []
#	if os.path.exists(input_file):
#		lines = GetLastLines(input_file)
#		for line in lines:
#			latest_news.append(line.split('\t')[1])
#	return latest_news
	latest_news = {}
	if os.path.exists(input_file):
		input = codecs.open(input_file, encoding = 'utf-8')
		lines = input.readlines()
		for line in lines:
			latest_news[line.split('\t')[1]] = 0
		input.close()

	folder = input_file.split('/')[0]
	date = input_file.split('/')[1].split('.')[0]
	today = datetime.datetime.strptime(date, '%Y-%m-%d').date()
	yesterday = str(today - datetime.timedelta(days=1))
	input_file = folder + '/' + yesterday + '.txt'

	if os.path.exists(input_file):
		input = codecs.open(input_file, encoding = 'utf-8')
		lines = input.readlines()
		for line in lines:
			latest_news[line.split('\t')[1]] = 0
		input.close()

	return latest_news


def GoogleNewsCrawler(num_news, output_file, twitter_folder):
	new_news = {}

	latest_news = GetLatestNews(output_file)

	news_id = codecs.open('news_id.txt', encoding = 'utf-8')
	id = int(news_id.readline())
	news_id.close()

	#download news feed
#	#=============Google News===============================
	s = 'http://news.google.com/?output=rss'
	feed = urllib2.quote(s.encode("utf-8"))
	url = ('https://ajax.googleapis.com/ajax/services/feed/load?v=1.0&q='+ feed + '&num=' + str(num_news))


	#=============USA Today====================================
#	url = 'http://api.usatoday.com/open/breaking?api_key=ytrgp8a45h9rg6pj9f7nd6dc'
	
	#============New York Times================================
#	today = datetime.date.today()
#	date = today.isoformat().split('-')
#	url = 'http://api.nytimes.com/svc/news/v3/content/all/all/24.json?api-key=2475992e2d45f4e52a642998cd8aba2f:8:69891353'
	
	#=============BBC==========================================
#	url = 'http://feeds.bbci.co.uk/news/rss.xml'
	
	#============CNN===========================================
#	url = 'http://rss.cnn.com/rss/edition.rss'

	#=============FOX==========================================
#	url = 'http://feeds.foxnews.com/foxnews/latest'

	#=============Reuters======================================
#	url = 'http://feeds.reuters.com/reuters/topNews'

	log = codecs.open('log.txt', 'a', encoding = 'utf-8')
	
	response = urllib2.urlopen(url)
	content = response.read().decode('utf-8')
	content = content.replace('\\u0026', '&')
	content = content.replace('\\u200b', '')
	results = simplejson.loads(content)
	results = results.get('responseData').get('feed').get('entries')

	output = codecs.open(output_file, 'a', encoding='utf-8')
	
	#parse content to find titles and urls etc.
	titles = []
	dates = []
	news_urls = []

	for result in results:
		titles.append(result.get('title'))
		dates.append(result.get('publishedDate'))
		news_urls.append(result.get('link'))

	snippets = re.findall(r'font size\\u003d\\\"-1\\\"\\u003e([^\\].+?)\\u003c', content)
	
	for news_url in news_urls:
		#get the full article via the url
		url = 'http://' + news_url.split('//')[2]
		url = url.replace('%3D', '=')

		#ignore existing news
		if url in latest_news:
			titles.pop(0)
			dates.pop(0)
			snippets.pop(0)
			continue

		
		try:
			article = newspaper.Article(url, language='en')
			article.download()
			article.parse()
		except Exception:
			google_title = titles.pop(0).split(' - ')
			source = google_title.pop(len(google_title) - 1).replace('\\u0026', '&')
			title = ' '.join(google_title).replace('\t', ' ')
			blob = TextBlob(title)
			keywords = blob.noun_phrases
			authors = ''
			text = ''
			date = dates.pop(0)

			output.write(str(id) + '\t')
			output.write(url + '\t')
			output.write(title.replace('\t', ' ').replace('\n', '::::').replace('\r', '::::') + '\t')
			output.write(source + '\t')
			output.write(date.replace('\t', ' ') + '\t')
			output.write(authors + '\t')
			output.write(';'.join(keywords) + '\t')
			if len(snippets) == 0:
				log.write('Write Error\n')
				log.write(content)
				output.write('\t')
			else:
				output.write(snippets.pop(0).replace('\\u0026', '&').replace('&amp;', '&').replace('&#39;', '\'').replace('&quot;', '\"') + '\t')
			output.write(text + '\t')
			output.write('\n')

			twitter_file = twitter_folder + '/' + str(id) + '_' + ("".join(c for c in title if c not in (string.punctuation))).replace(' ', '_') + '-' + ("".join(c for c in source if c not in (string.punctuation))).replace(' ', '_')
			new_news[twitter_file] = ' OR '.join(keywords)
			id += 1

			continue

		#extract necessary information
		google_title = titles.pop(0).split(' - ')
		source = google_title.pop(len(google_title) - 1).replace('\\u0026', '&')
		title = ' '.join(google_title).replace('\t', ' ')
		if title[:-5] in article.title:
			title = article.title


		blob = TextBlob(title)
		keywords = blob.noun_phrases
		authors = article.authors
		text = article.text.replace('\t', ' ')
		date = dates.pop(0)


		#write the information
		output.write(str(id) + '\t')
		output.write(url + '\t')
		output.write(title.replace('\t', ' ').replace('\n', '::::').replace('\r', '::::') + '\t')
		output.write(source + '\t')
		output.write(date.replace('\t', ' ') + '\t')
		output.write(';'.join(authors)+ '\t')
		output.write(';'.join(keywords) + '\t')
		if len(snippets) == 0:
			log.write('Write Error\n')
			log.write(content)
			output.write('\t')
		else:
			output.write(snippets.pop(0).replace('\\u0026', '&').replace('&amp;', '&').replace('&#39;', '\'').replace('&quot;', '\"') + '\t')
		output.write(text.replace('\t', ' ').replace('\n', '::::').replace('\r', '::::') + '\t')
		output.write('\n')

		twitter_file = twitter_folder + '/' + str(id) + '_' + ("".join(c for c in title if c not in (string.punctuation))).replace(' ', '_') + '-' + ("".join(c for c in source if c not in (string.punctuation))).replace(' ', '_')
		new_news[twitter_file] = ' OR '.join(keywords)
		id += 1

	output.close()

	news_id = codecs.open('news_id.txt', 'w', encoding='utf-8')
	news_id.write(str(id))
	news_id.close()

	return new_news
		
			
if __name__ == '__main__':
	output_file = 'news.txt'
	num_news = 10
	twitter_folder = 'tweets'
	#parse input
	for i in range(1, len(sys.argv), 2):
		if sys.argv[i] == '-n':
			num_news = int(sys.argv[i+1])
		if sys.argv[i] == '-o':
			output_file = sys.argv[i+1]
		if sys.argv[i] == '-t':
			twitter_folder = sys.argv[i+1]
	
	GoogleNewsCrawler(num_news, output_file, twitter_folder)