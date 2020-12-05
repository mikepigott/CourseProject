import os,codecs,json
import collections

def create_topics_list(topics_path):
	topics_list = []
	count = 0
	with open(topics_path, 'r') as tf:
		for line in tf:
			primary_topic = 0
			primary_topic_idx = 0
			topic_list = line.strip().split('\t')
			for idx in range(1, len(topic_list)):
				topic = float(topic_list[idx])
				if topic > primary_topic:
					primary_topic = topic
					primary_topic_idx = idx - 1
			topics_list.append(primary_topic_idx)

			count = count + 1
			if count % 250 == 0:
				print("Processed file %s (# %d).  Primary topic: %d (Rank: %f)" % (topic_list[0], count, primary_topic_idx, primary_topic))

	return topics_list

def _sort_by_topic_relevance(record):
	return record[-1]

def create_browsable_topics(topics_path, unis, depts, corrected_names, urls, locs, emails, topics_list, topics_json_dir):
	docs_by_topic = collections.defaultdict(list)

	# Construct a dictionary of relevant documents by topic.
	with open(topics_path, 'r') as tf:
		doc_num = 0
		for line in tf:
			topic_list = line.strip().split('\t')
			for topic_idx in range(1, len(topic_list)):
				topic_relevance = float(topic_list[topic_idx])
				if topic_relevance > 0:
					docs_by_topic[topic_idx - 1].append([
						topic_list[0],                                    # Document Name
						'Relevance: ' + str(topic_relevance * 100) + '%', # Document Preview
						emails[doc_num],                                  # Email
						unis[doc_num],                                    # University
						depts[doc_num],                                   # Department
						corrected_names[doc_num],                         # Faculty Name
						urls[doc_num],                                    # Faculty URL
						locs[doc_num].split()[0],                         # State
						locs[doc_num].split()[1],                         # Country
						emails[doc_num],                                  # Email
						topics_list[doc_num],                             # Primary Topic
						topic_relevance                                   # Current Topic Relevance
					])
			doc_num = doc_num + 1

	for topic_num in docs_by_topic.keys():
		# Sort the per-topic documents by relevance, descending.
		relevant_docs = docs_by_topic[topic_num] 
		relevant_docs.sort(reverse=True, key=_sort_by_topic_relevance)

		print("Topic %d document 0 relevance index: %f" % (topic_num, _sort_by_topic_relevance(relevant_docs[0])))

		# Write the documents as JSON search results.
		json.dump({"docs": relevant_docs}, open(topics_json_dir + str(topic_num) + '.json', 'w'))

	return

def main(dir_,out_file1,out_file2,dept_path,uni_path,names_path,url_path,loc_path,email_path,topics_path,filter_file1,filter_file2,topics_json_dir):

	with open(uni_path,'r') as f:
		unis = f.readlines()

	with open(dept_path,'r') as f:
		depts = f.readlines()

	with open(names_path,'r') as f:
		names = f.readlines()

	with open(url_path,'r') as f:
		urls = f.readlines()

	with codecs.open(loc_path,'r',encoding='utf-8',errors='ignore') as f:
		locs = f.readlines()

	with codecs.open(email_path,'r',encoding='utf-8',errors='ignore') as f:
		emails = f.readlines()

	topics_list = create_topics_list(topics_path)

	max_len = 15
	max_parts = 3
	non_names = ['curriculum','vitae','bio','professor','assistant',')','(','--','nat','center','sitemap','u.','2002','washington']

	corrected_names = []

	for name in names:
		parts = name.strip().split()
		corrected_name = ''
		for part in parts[:max_parts]:
			if len(part)<=max_len and part.lower() not in non_names and part.title() not in corrected_name.split():
				corrected_name += ' '+part.title()
		corrected_names.append(corrected_name)


	num_bios = len(os.listdir(dir_))-5

	print(emails[-2:],len(emails),len(corrected_names),len(locs),len(depts),len(unis),num_bios)

	with open(out_file1,'w') as f1:
		with codecs.open(out_file2,'w',encoding='utf-8',errors='ignore') as f2:
			for i in range(num_bios)[:-1]:
				f1.write('[None] '+str(i)+'.txt')
				f1.write('\n')
				if emails[i]=='\n':
					emails[i]='None'
				f2.write(str(i)+'.txt'+'\t'
					+unis[i].strip()+'\t'+depts[i].strip()+'\t'+corrected_names[i]+'\t'+urls[i].strip()+'\t'+locs[i].strip()+'\t'+emails[i].strip()+'\t'+str(topics_list[i]))
				f2.write('\n')

			f1.write('[None] '+str(num_bios-1)+'.txt')
			if emails[num_bios-1]=='\n':
					emails[num_bios-1]='None'
			f2.write(str(num_bios-1)+'.txt'+'\t'
				+unis[num_bios-1].strip()+'\t'+depts[num_bios-1].strip()+'\t'+corrected_names[num_bios-1]+'\t'+urls[num_bios-1].strip()+'\t'+locs[num_bios-1].strip()+'\t'+emails[num_bios-1].strip()+'\t'+str(topics_list[num_bios-1]))

	unis_dict = {"unis":sorted([uni.strip() for uni in list(set(unis))])}
	all_countries = set()
	all_locs = set()

	for loc in locs:
		country = loc.split('\t')[1]
		all_countries.add(country.strip())
		all_locs.add(loc.replace('\t',', ').strip())

	all_countries = sorted(list(all_countries))
	all_locs = sorted(list(all_locs))
	all_locs = all_countries + all_locs

	locs_dict = {"locs":all_locs}

	json.dump(unis_dict,open(filter_file1,'w'))
	json.dump(locs_dict,open(filter_file2,'w'))

	create_browsable_topics(topics_path, unis, depts, corrected_names, urls, locs, emails, topics_list, topics_json_dir)
	

if __name__ == '__main__':
	main('./data/compiled_bios','./data/compiled_bios/dataset-full-corpus.txt','./data/compiled_bios/metadata.dat','./data/depts','./data/unis','./data/names.txt','./data/urls','./data/location','./data/emails','./data/topics.dat','./data/filter_data/unis.json','./data/filter_data/locs.json', './data/topics/')




