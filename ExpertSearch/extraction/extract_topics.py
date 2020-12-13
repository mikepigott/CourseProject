from os import listdir
from os.path import isfile, join
import sys
import random
import numpy
import nltk
import spacy
from spacy.lang.en import English
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora
import gensim
import wordcloud
import pyLDAvis.gensim

# USAGE: python extract_topics.py [number of topics (default: 10)] [LDA Model path (default: topics_lda_model.gensim)] [corpus directory (default: ../data/compiled_bios/)] [output file (default: ../data/topics.dat)] [output word clouds directory (default: ../static/topics/)]

num_topics = 10
lda_model_output_file = "topics_lda_model.gensim"
corpus_dir = "../data/compiled_bios/"
topics_output_file = "../data/topics.dat"
wordclouds_output_dir = "../static/topics"

if len(sys.argv) > 1:
    num_topics = int(sys.argv[1])

if len(sys.argv) > 2:
    lda_model_output_file = sys.argv[2]

if len(sys.argv) > 3:
    corpus_dir = sys.argv[3]

if len(sys.argv) > 4:
    topics_output_file = sys.argv[4]

if len(sys.argv) > 5:
    wordclouds_output_dir = sys.argv[5]

print("# of Topics: %d\nCorpus Directory: %s\nTopics OutputFile: %s\nWord Clouds Output Directory: %s\nLDA Model Output Path: %s" % (num_topics, corpus_dir, topics_output_file, wordclouds_output_dir, lda_model_output_file))

# -- Preprocess the Bios --

spacy.load('en')
parser = English()

# nltk.download('wordnet')
# nltk.download('stopwords')

en_stop = set(nltk.corpus.stopwords.words('english'))

def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens

def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma

def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)

def prepare_text_for_lda(text):
    tokens = tokenize(text)
    tokens = [token for token in tokens if len(token) > 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens

text_data = []

corpusfiles = [f for f in listdir(corpus_dir) if isfile(join(corpus_dir, f)) and f.endswith(".txt") and not f.startswith("dataset-full-corpus") ]
corpusfiles.sort()

print("Reading the corpus files.")
count = 0

for file in corpusfiles:
    with open(join(corpus_dir, file)) as inf:
        words = []
        for line in inf:
            words.extend(line.split())

        tokens = prepare_text_for_lda(' '.join(words))
        text_data.append(tokens)

        count = count + 1
        if count % 250 == 0:
            print("Processed %s, file %d of %d." % (file, count, len(corpusfiles)))

print("Processed %d files of %d." % (len(corpusfiles), len(corpusfiles)))

# -- Generate the LDA Model
print("Creating the LDA model with %d topics." % num_topics)

dictionary = corpora.Dictionary(text_data)
corpus = [dictionary.doc2bow(text) for text in text_data]

lda_model = gensim.models.ldamodel.LdaModel(corpus, num_topics = num_topics, id2word=dictionary, passes=15)

print("Created the LDA model.")

lda_model.save(lda_model_output_file)

# -- Decide Topics for Profiles --
print("Creating the topics file: %s" % topics_output_file)

def convert_topics_to_list(corpus_file_name, topics):
    list = [corpus_file_name]
    topic_dict = {}
    for topic in topics:
        topic_dict[topic[0]] = topic[1]

    for topic in range(num_topics):
        list.append(str(topic_dict.get(topic, 0)))

    return list

count = 0

with open(topics_output_file, "w") as o:
    for idx in range(len(text_data)):
        corpus_file_name = corpusfiles[idx]
        tokens = text_data[idx]
        new_doc_bow = dictionary.doc2bow(tokens)
        topic_list = lda_model.get_document_topics(new_doc_bow)
        o.write('\t'.join(convert_topics_to_list(corpus_file_name, topic_list)) + str("\n")) 

        count = count + 1
        if count % 250 == 0:
            print("Processed %s, file %d of %d. Topic List: %s" % (corpus_file_name, count, len(text_data), topic_list))

print("Created the topics file.")

# -- Generate the Word Clouds --
print("Creating the word clouds: %s" % wordclouds_output_dir)

topics = lda_model.show_topics(num_topics=num_topics, num_words=25, formatted=False)

for topic in topics:
	topic_dict = {}
	for record in topic[1]:
		topic_dict[record[0]] = record[1]
	word_cloud = wordcloud.WordCloud().generate_from_frequencies(topic_dict)
	word_cloud.to_file(wordclouds_output_dir + "/" + str(topic[0]) + ".png")

print("Created the word clouds.")

print("Displaying the LDA model.  Please wait for it to appear in your browser.")

# -- Display the LDA Model --
lda_display = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary, sort_topics=False)
pyLDAvis.show(lda_display)
