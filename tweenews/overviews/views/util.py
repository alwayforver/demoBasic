from django.conf import settings
import sys,os
import Queue
from overviews.models import News

def read_source(sourcefile):
	id_map = {}
	relations = []
	state = 0
	n_samples = 0
	with open(sourcefile, 'r') as source:
		for line in source:
			if "ind to newsID:" in line: ## id mapping
				state = 1
				continue
			elif "children_ array in scikit-learn aggl clustering array:" in line:
				state = 2
				idx = 0
				n_samples = len(id_map.keys())
				continue
			if state == 1:
				entries = line.strip().split(' ')
				try:
					id_map[int(entries[0])] = int(entries[1])
				except:
					print "reading error"
					exit()

			if state == 2:
				line = line.replace('[', '').replace(']', '')
				node = str(n_samples + idx)
				children = [tmp for tmp in line.strip().split(' ') if tmp != '']
				for child in children:
					relations.append([node, child])
				idx += 1
	node_children = {}
	if len(relations) == 0:
		print "No relations"
		exit()
	root = str(n_samples + idx - 1)
	for r in  relations:
		if not node_children.has_key(r[0]):
			node_children[r[0]] = [r[1]]
		else:
			node_children[r[0]].append(r[1])
	return [id_map, node_children, root]

def draw_json(node_children, root, id_map, outputfile):
	print outputfile
	output = open(outputfile, 'w')
	output_data = '{"name":"' + root + '"}\n'
	q = Queue.Queue()
	q.put(root)
	while not q.empty():
		node = q.get()
		node_text = '{"name":"'+node+'"}'
		if node_children.has_key(node):
			replace_text = '{"name":"'+node+'",\n'
			replace_text = replace_text+'"children":[\n'
			tmp = []
			for child in node_children[node]:
				child_name = ''
				if int(child) in id_map:
					try:
						#print id_map[int(child)]
						news = News.objects.get(ID =  id_map[int(child)])
						child_name = str(id_map[int(child)]) + ' ' + str(news.title) + ' ' + str(news.created_at)
						#print child_name
					except:
						#print "No such News"
						pass
				else:
					child_name = child

				tmp.append('{"name":"'+child_name+'"}')
				q.put(child)
			replace_text = replace_text+',\n'.join(tmp)+'\n'
			replace_text = replace_text+']\n}'
			output_data = output_data.replace(node_text,replace_text)

	for line in output_data:
		output.write(line)
	output.close()

def test():
	[id_map, temp_relation, root] = read_source(settings.MEDIA_ROOT + '/tmp_noknn.txt')
	draw_json(temp_relation , root, id_map, settings.MEDIA_ROOT+'/' +'test.json')
	print settings.MEDIA_ROOT
	print settings.STATIC_ROOT

#if __name__ == '__main__':
	#[temp_relation, root] = read_source('tmp_noknn.txt')
	#draw_json(temp_relation , root, 'test.json')
	
