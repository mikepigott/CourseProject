import os,codecs,re

def main(dir_,out_path):
	emails = []
	#print(len(os.listdir(dir_)))
	for i in range(len(os.listdir(dir_))-5):
		#print(i)
		content = codecs.open(os.path.join(dir_,str(i)+'.txt'), 'r',encoding='utf-8',errors='ignore').readlines()
		for line in content:
			#print(line)
			#match = re.findall(r'[\w\.-]+@[\w\.-]+', line)
			#match = re.findall(r'[\w\.-]+(?:@|at)+[\w\.-]+', line)

			#trying an approach
			rgx = r'(?:\.?)([\w\-_+#~!$&\'\.]+(?<!\.)(@|[ ]?\(?"?[ ]?(at|AT)[ ]?\)?"?[ ]?)(?<!\.)[\w]+[\w\-\.]*(\.|[ ]?(\(|")dot("|\))[ ]?)[a-zA-Z-]{2,3})(?:[^\w])'
			matches1 = re.findall(rgx, line)
			get_first_group = lambda y: list(map(lambda x: x[0], y))
			match = get_first_group(matches1)

			#Ends trial
			

			if len(match) > 0:
				emailval=match[0].lower().strip()
				if "www" in emailval or emailval=="iastate.edu" or emailval=="eecs-info@utk.edu" or emailval=="statcounter.com": 
					emails.append('')
				else:
					dots= [" dot ",' "dot" '," (dot) "]
					ats= [" at "," (at) ",' "at" ']
					for d in dots:
						if d in emailval:
							emailval=emailval.replace(d,".")
					for a in ats:
						if a in emailval:
							emailval=emailval.replace(a,"@")		
					emails.append(emailval)
			else:
				emails.append('')

	with codecs.open(out_path,'w',encoding='utf-8',errors='ignore') as f:
		for email in emails[:-1]:
			f.write(email+'\n')
		if emails[-1]=='':
			f.write('\n')
		else:
			f.write(emails[-1])

if __name__ == '__main__':
	main('../data/compiled_bios/','../data/emails2')


	   
