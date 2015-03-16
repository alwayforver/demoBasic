from django import forms
from django.utils.html import mark_safe, escape
from django.utils.encoding import force_unicode
from django.contrib.admin import widgets
from django.contrib.auth.models import User
import datetime
#from overviews.models import News, Tweet

#TIME_FILERS_CHOICES = (('', '---------'), ('=', '='), ('>', '>'), ('>=', '>='), ('<', '<'), ('<=', '<='))
#TIME_FORM_CHOICES.insert(0, ('', '---------'))
class SearchForm(forms.Form):
	ID = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': 'ID', 'class': 'form-control'}), required=False)
	key_word = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Keywods', 'class': 'form-control'}), required=False)
    #year_opt = forms.ChoiceField(choices=YEAR_FILERS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    #year = forms.ChoiceField(choices=YEARS_FORM_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=False)
	title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title', 'class': 'form-control'}), required=False)
	main_article = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Description', 'class': 'form-control'}), required=False)
	source = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Source', 'class': 'form-control'}), required=False)
    #source = forms.ModelMultipleChoiceField(queryset=Venue.objects.all().order_by('name'), widget=forms.SelectMultiple(attrs={'class': 'form-control'}), required=False)
class StartEndDateForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()