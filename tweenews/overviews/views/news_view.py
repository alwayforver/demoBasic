from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from overviews.models import News, Tweet
import math
import time
from overviews.forms import SearchForm

def news(request, pos = 1, rank_method = 0):
    news_set = None
    form = SearchForm()
    query = None
    if(request.method == 'POST' and 'q' in request.POST):
        query =  request.POST['q']
        news_set = News.objects.filter(title__icontains=query)
        #print new_set
        print 'Post ' + str(news_set.count())
    elif(request.method == 'POST'):
        string_type = ['key_word', 'source', 'main_article', 'title']
        manytomany_type = ['ID']
        timetype = ['created_at']
        kwargs = {}
        form = SearchForm(request.POST)
        if form.is_valid():
            print 'Get in Form'
            all_empty = True
            for field in form.cleaned_data:
                if form.cleaned_data[field]:
                    all_empty = False
                    #    if field == 'year' and form.cleaned_data['year_opt']:
                    #        if form.cleaned_data['year_opt'] == '=':
                    #            kwargs['year'] = str('%s' % form.cleaned_data[field])
                    #        elif form.cleaned_data['year_opt'] in year_query_map:
                    #            kwargs[str('year__%s' % year_query_map[form.cleaned_data['year_opt']])] = str('%s' % form.cleaned_data[field])
                        #if field == 'ID':

                    if field in string_type:
                        kwargs[str('%s__icontains' % field)] = str('%s' % form.cleaned_data[field].strip())
                    elif field in manytomany_type:
                        kwargs[str('%s' % field)] = form.cleaned_data[field]
            if all_empty!= True:
                news_set = News.objects.select_related().filter(**kwargs)
                print len(news_set)
        print 'Advanced Search'

    ## check search
    if request.method == 'GET' and 'q' in request.GET :
        #print q
        query = request.GET.get('q', '')
        query = query.strip()
        if len(query) > 0:
            news_set = News.objects.select_related().filter(title__icontains=query)
            print "Search Result Move On"

    base_page = 1
    pos = max(int(pos),base_page)
    rank_method = int(rank_method)
    SearchFlag = False
    if news_set != None and len(news_set)!= 0:
        total_num = news_set.count()
        SearchFlag = True
    else:
        total_num = News.objects.count()
    one_page = 100
    default_pagenum = 10
    end_pos = min( pos + default_pagenum , int(math.ceil(float(total_num)/float(one_page))))
    end_pos = max( pos , end_pos)
    print total_num, pos, end_pos
    if rank_method == 0:
        #all_news_list = News.objects.filter(ID__range = ((pos-1)*one_page+1, pos*one_page))
        if SearchFlag:
            all_news_list = news_set.order_by('ID')[(pos-1)*one_page:pos*one_page]
        else:
            all_news_list = News.objects.all().order_by('ID')[(pos-1)*one_page:pos*one_page]
    elif rank_method == 1: 
        if SearchFlag:    
            all_news_list = news_set.order_by('created_at')[(pos-1)*one_page : pos*one_page]
        else:
            all_news_list = News.objects.all().order_by('created_at')[(pos-1)*one_page : pos*one_page]
    elif rank_method == 2:
        if SearchFlag:
            all_news_list = news_set.order_by('-created_at')[(pos-1)*one_page : pos*one_page]
        else:
            all_news_list = News.objects.all().order_by('-created_at')[(pos-1)*one_page : pos*one_page]
    start_pos = min(pos, end_pos-10)
    start_pos = max(0, start_pos)    
    page_index = range(start_pos, end_pos+1)
    last_pos = int(math.ceil(float(total_num)/float(one_page)))
    prev = max(1, pos - 1)
    nextPos = min(end_pos, pos+1)
    context = {'all_news_list':all_news_list, 'search_form': form, 'page_index':page_index, 'nextPos': nextPos,'prevPos': prev, 'rankmethod': rank_method, 'last_pos': last_pos}
    if request.method == 'POST' and news_set != None and SearchFlag == False:
        context['search_fail'] = True
    if query:
        context['q'] = query
    return render(request, 'news.html', context)


