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

# USAGE: python extract_topics.py [number of topics (default: 10)] [corpus directory (default: ../data/compiled_bios/)] [output file (default: ../data/topics.dat)] [output word clouds directory (default: ../static/topics/)]

num_topics = 10
corpus_dir = "../data/compiled_bios/"
topics_output_file = "../data/topics.dat"
wordclouds_output_dir = "../static/topics"

if len(sys.argv) > 1:
    num_topics = int(sys.argv[1])

if len(sys.argv) > 2:
    corpus_dir = sys.argv[2]

if len(sys.argv) > 3:
    topics_output_file = sys.argv[3]

if len(sys.argv) > 4:
    wordclouds_output_dir = sys.argv[4]

print("# of Topics: %d\nCorpus Directory: %s\nTopics OutputFile: %s\nWord Clouds Output Directory: %s" % (num_topics, corpus_dir, topics_output_file, wordclouds_output_dir))

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

corpusfiles = [f for f in listdir(corpus_dir) if isfile(join(corpus_dir, f))]

for file in corpusfiles:
    print(file)
    with open(join(corpus_dir, file)) as inf:
        words = []
        for line in inf:
            words.extend(line.split())

        tokens = prepare_text_for_lda(' '.join(words))
        text_data.append(tokens)

        if random.random() > .99:
            print(tokens)

# -- Generate the LDA Model
dictionary = corpora.Dictionary(text_data)
corpus = [dictionary.doc2bow(text) for text in text_data]

lda_model = gensim.models.ldamodel.LdaModel(corpus, num_topics = num_topics, id2word=dictionary, passes=15)

# -- Decide Topics for Profiles --
with open(topics_output_file, "w") as o:
    for tokens in text_data:
        new_doc_bow = dictionary.doc2bow(tokens)
        o.write('\t'.join(convert_topics_to_list(ldamodel.get_document_topics(new_doc_bow))) + str("\n")) 

# -- Generate the Word Clouds --
topics = ldamodel.show_topics(num_topics=num_topics, num_words=25, formatted=False)

for topic in topics:
	topic_dict = {}
	for record in topic[1]:
		topic_dict[record[0]] = record[1]
	word_cloud = wordcloud.WordCloud().generate_from_frequencies(topic_dict)
	word_cloud.to_file(wordclouds_output_dir + "/" + str(topic[0]) + ".png")

# -- Display the LDA Model --
lda_display = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary, sort_topics=False)
pyLDAvis.show(lda_display)
