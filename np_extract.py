from textblob import TextBlob
from newspaper import Article


# Best to use headlines or breaking news
def get_np(news_url):
    article = Article(url, language='en')
    article.download()
    article.parse()
    title = article.title.lower()
    print "Retrieved Title ","\"", title, "\""
    blob = TextBlob(title)
    return blob.noun_phrases

if __name__ == "__main__":
    url = raw_input("Please enter news url: ")
    key_phrases = get_np(url)
    print key_phrases
