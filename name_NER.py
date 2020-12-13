from re import search
import re
import nltk
from nltk.tag.stanford import StanfordNERTagger

jar = './stanford-ner-2018-10-16/stanford-ner.jar'
model = './stanford-ner-2018-10-16/classifiers/4_class_2020_11.gz'


# Prepare NER tagger with english model
ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')

for i in range(1):
    indexOfFile = i
    with open('data/compiled_bios/' + str(93) + '.txt', 'r') as file:
        data = file.read().replace('\n', '')
        isOutOfIndex = False
        dic = {}
        # Tokenize: Split sentence into words
        words = nltk.word_tokenize(data)
        res = ""
        results = ner_tagger.tag(words)
        # print(results)
        # Run NER tagger on words
        for i in range(len(results)):
            if i != 0 and i != len(results) - 1 and isOutOfIndex == False:
                formerWord = results[i - 1]
                latterWord = results[i + 1]
                currentWord = results[i]            
                if currentWord[1] == 'PERSON' and latterWord[1] != 'PERSON':
                    fullName = currentWord[0]
                    index = i
                    # wordCount = 1
                    while formerWord[1] == 'PERSON':
                        fullName = formerWord[0] + ' ' + fullName
                        index = index - 1
                        # wordCount = wordCount + 1
                        if index == 0: 
                            isOutOfIndex = True
                            res = fullName
                            break
                        formerWord = results[index - 1]
                    
                    fullName = fullName.replace(")", "")
                    fullName = fullName.replace("(", "")
                    fullName = fullName.replace("]", "")
                    fullName = fullName.replace("[", "")
                    fullName = fullName.replace("\\", "")
                    fullName = fullName.replace("\(\(\(", ">>")
                    fullName = fullName.strip()
                    dic[fullName] = dic.get(fullName, 0) + 1
        if (isOutOfIndex == True):
            f = open("names.txt", "a")
            f.write(res + "\n")
            f.close()
        if (isOutOfIndex == False):
            keys = sorted(dic.keys(), key=len)
            keys.reverse()


            # print(keys)
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    cur = keys[i]
                    comparedKey = keys[j]
                    if comparedKey in cur:
                        dic[cur] = dic.get(cur) + 1
            
            highestFrequency = 0
            
            
            for item in dic.items():
                if item[1] > highestFrequency:
                    res = item[0]
                    highestFrequency = item[1]
                if item[1] == highestFrequency:
                    if len(item[0]) > len(res):
                        res = item[0]
            print(dic)
            # print(res)
            # print(indexOfFile)
            # Cleanup phase
            if (res != ""):
                res = res.replace('Professor', '')
                if ('Goodwin' in res):
                    res = ""
            # print(cleanedUpRes)
            
            f = open("names.txt", "a")
            f.write(res + "\n")
            f.close()
    file.close()

