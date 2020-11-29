from os import listdir
from os.path import isfile, join
import sys

# USAGE: python extract_topics.py [number of topics (default: 10)] [corpus directory (default: ../data/compiled_bios/)] [output file (default: ../data/topics.dat)] [output word clouds directory (default: ../static/topics/)]

num_topics = 10
corpus_dir = "../data/compiled_bios/"
topics_output_file = "../data/topics.dat"
wordclouds_output_dir = "../static/topics/"

if len(sys.argv) > 1:
    num_topics = int(sys.argv[1])

if len(sys.argv) > 2:
    corpus_dir = sys.argv[2]

if len(sys.argv) > 3:
    topics_output_file = sys.argv[3]

if len(sys.argv) > 4:
    wordclouds_output_dir = sys.argv[4]

print("# of Topics: %d\nCorpus Directory: %s\nTopics OutputFile: %s\nWord Clouds Output Directory: %s" % (num_topics, corpus_dir, topics_output_file, wordclouds_output_dir))
