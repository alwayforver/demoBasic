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
		
register.filter('get_dict_item',get_dict_item)
register.filter('get_dict_keys',get_dict_keys)
register.filter('get_range',get_range)
register.filter('plus',plus)