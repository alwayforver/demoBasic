from django import template
from overviews.models import *

register = template.Library()

def get_dict_item(dictionary,key):
	return dictionary.get(key)

def get_dict_keys(dictionary):
	return dictionary.keys()

def get_range(num):
	return range(1,num+1,1)

def plus(num1,num2):
	return num1+num2

def NoURLTweets(tweet):
	if "http://" in tweet:
		return False
	else:
		return True

def replace_mark(content):
	return content.replace('::::', '\n')

def replace_empty(content):
	if content == '':
		return "[Empty]"
	else:
		return content
		
register.filter('get_dict_item',get_dict_item)
register.filter('get_dict_keys',get_dict_keys)
register.filter('get_range',get_range)
register.filter('plus',plus)
register.filter('NoURLTweets',NoURLTweets)
register.filter('replace_mark', replace_mark)
register.filter('replace_empty', replace_empty)
