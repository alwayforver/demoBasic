import sys
import urllib2
import re
import datetime
import newspaper
import codecs

# This file crawls news (including full article) from Google News feed
# To run, you need to give the parameters by -n num_of_news -o output_file
# where num_of_news is no larger than 10 (default 10), and the news will be appended into the output_file

def GoogleNewsCrawler(num_news, output_file):
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
	
	response = urllib2.urlopen(url)
	content = response.read().decode('utf-8')
	output = codecs.open(output_file, 'a', encoding='utf-8')
	
	#parse content to find titles and urls etc.
	titles = re.findall(r'{\"title\":\"[^\"]+\"', content)
	dates = re.findall(r'\"publishedDate\":\"[^\"]+\"', content)
	snippets = re.findall(r'font size\\u003d\\\"-1\\\"\\u003e([^\\].+?)\\u003c', content)
	
	news_urls = re.findall(r'\"link\":\"[^\"]+\"', content)
	news_urls.pop(0)
	
	for news_url in news_urls:
		#get the full article via the url
		url = 'http://' + news_url.split('//')[2][:-1]
		article = newspaper.Article(url, language='en')
		article.download()
		article.parse()
		
		#extract necessary information
		title = article.title.replace('\t', ' ')
		authors = article.authors
		text = article.text.replace('\t', ' ')
		date = dates.pop(0).split('\"')[3]
		google_title = titles.pop(0).split('-')
		source = google_title[len(google_title) - 1][1:-1]

		#write the information
		output.write(title.replace('\t', ' ').replace('\n', '::::') + '\t')
		output.write(source + '\t')
		output.write(date.replace('\t', ' ') + '\t')
		author_str = ''
		for author in authors:
			author_str = author + ';'
		output.write(author_str[:-1] + '\t')
		output.write(snippets.pop(0).replace('\\u0026', '&').replace('&amp;', '&').replace('&#39;', '\'').replace('&quot;', '\"') + '\t')
		output.write(text.replace('\t', ' ').replace('\n', '::::') + '\t')
		output.write('\n')
		
			
if __name__ == '__main__':
	output_file = 'news.txt'
	num_news = 10
	#parse input
	for i in range(1, len(sys.argv), 2):
		if sys.argv[i] == '-n':
			num_news = int(sys.argv[i+1])
		if sys.argv[i] == '-o':
			output_file = sys.argv[i+1]
	
	GoogleNewsCrawler(num_news, output_file)