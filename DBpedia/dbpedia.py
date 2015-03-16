import codecs
import os
import requests
import json

def EntityExtraction(text):

    url = 'http://localhost:2222/rest/annotate'    #local service
    params = {'confidence': 0.5, 'support': 10, 'text': text}
    reqheaders = {'accept': 'application/json'}

    response = requests.post(url, data=params, headers=reqheaders)

    results = response.json()

    entities = {}

    if 'Resources' in results:
        for result in results['Resources']:
            entity = result['@surfaceForm']
            types = result['@types']

            if 'DBpedia:Person' in types:
                entity += ':person'
            elif 'DBpedia:Place' in types:
                entity += ':place'
            elif 'DBpedia:Organisation' in types:
                entity += ':org'

            if entity in entities:
                entities[entity] += 1
            else:
                entities[entity] = 1

    entities_string = ''
    for (entity, count) in entities.items():
        entities_string += entity + ':' + str(count) + '\t'
        
    return entities_string


if __name__ =='__main__':


    for i in range(10):
        text = 'President Obama called Wednesday on Congress to extend a tax break for students included in last year\'s economic stimulus package, arguing that the policy provides more generous assistance.'
        print EntityExtraction(text)
        if i%1000==1:
            print i

