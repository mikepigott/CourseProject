# ExpertSearch

To run the code, run the following command from `ExpertSearch` (tested with Python2.7 on MacOS and Linux):

`gunicorn server:app -b 127.0.0.1:8095` 

The site should be available at http://localhost:8095/

> *Note:* This server requires Python 2.x.  For running on a Mac with both Python 2.7 and Python 3.x, see the `start_expertsearch.sh` script.

>If you are using Windows OS, please install Windows Subsystem for Linux (WSL) and install all the required modules. You can then run the gunicorn command specified above.
You could also use Docker or Cygwin to run the code on Windows OS. 

## Installation

### Python

Running the ExpertSearch server and the following extraction scripts requires Python 2.x:

* `extraction/extract_email.py`
* `extraction/extract_names.py`
* `extraction/get_location.py`

Running the topic generator requires Python 3.x:

* `extraction/extract_topics.py`

### ExpertSearch Server

The following (Python 2.x) modules are needed to run the server:

* `gunicorn`
* `flask`
* `metapy`
* `requests`
* `json`

### Topic Extractor

The following (Python 3.x) modules are needed to run the topic extractor:

* `numpy`
* `nltk`
* `spacy`
* `gensim`
* `pyldavis`
* `wordcloud`

Once NLTK is installed, you will also need to download `wordnet` and `stopwords`:

```python
nltk.download('wordnet')
nltk.download('stopwords')
```

### Name Extractor
The provided NER script is installed in name_NER.py. You can simply run python name_NER.py to retreieve 
names from the bio files or any files if you want

new_names.txt stores all names extracted from bio files. It's eliminate all names are not present fully in the articles, having high weight on retrieving full name of the article rather than capture any names seen in the article

The script itself has high precision more than recall on retrieving names

### Email Extractor

The following (Python 3.x) modules are needed to run the email extractor:

* `os`
* `codecs`
* `re`


## Generating Topics

Regenerating the LDA topic model, word clouds, and index will require the following steps:

1. Running `extraction/extract_topics.py` with the number of topics to generate. (The default is 10.)
2. Running the `write_file_names.py` script to recreate the following files:
    * `data/compiled_bios/dataset-full-corpus.txt`: The list of all files in the search index.
    * `data/compiled_bios/metadata.dat`: Metadata about each file in the corpus.
    * `data/filter_data/unis.json`: The set of universities to filter on.
    * `data/filter_data/locs.json`: The set of locations to filter on.
3. Deleting the contents of the `data/FacultyDataset` directory so the index can be recreated.
4. Starting the server.

### Extracting Topics

The `extraction/extract_topics.py` has five arguments:

1. The number of topics.  Defaults to 10.
2. The location to save the generated LDA topic model.  Defaults to `topics_lda_model.gensim`.
3. The directory containing the files to generate topics from.  Defaults to `../data/copiled_bios/`.
4. The location of the file to output the tab-delimited topic rankings to.  Defaults to `../data/topics.dat`.  (This is the location that `write_file_names.py` expects it to be, so do not change it if you plan to run that script.)
5. The directory to write the word clouds to.  Defaults to `../static/topics`.  (This is the location that the server expects them to be, so do not change it if you plan to run the server.)

Example usage:
```sh
cd extraction
# This will generate an LDA model of 10 topics and store the result in topics_lda_model.gensim.
python3 extract_topics.py
# This will generate an LDA model of 16 topics and store the result in 16topics_model.gensim
python3 extract_topics.py 16 16topics_model.gensim
```

### Rebuilding the Metadata

This is straightforward; the `write_file_names.py` script does not take any arguments, and looks for the files in predefined locations:

Input:
* Corpus: `data/compiled_bios`
* Departments: `data/depts`
* Universities: `data/unis`
* Names: `data/names.txt`
* URLs: `data/urls`
* Locations: `data/location`
* Emails: `data/emails`
* Topics: `data/topics.dat`

Output:
* `data/compiled_bios/dataset-full-corpus.txt`
* `data/compiled_bios/metadata.dat`
* `data/filter_data/unis.json`
* `data/filter_data/locs.json`
* `data/topics/*.json`

Example usage:
```sh
# From the ExpertSearch root directory
python2 write_file_names.py
```

### Removing the cached index and starting the server

```sh
rm -rf data/FacultyDataset
gunicorn server:app -b 127.0.0.1:8095 # or your favorite way of starting the server
```

## Browsing Topics

When visiting http://localhost:8095 for the first time, you will be presented with a set of word clouds, one for each topic.  Each of these is clickable, and will fetch all of the documents associated with that topic, in decreasing order of relevance.

You will also be able to click the topic word-cloud in the search results to view the same data.

Searching will work the same.

### Topic Result Generation

These search results were generated as part of the `write_file_names.py` script, and deposited in the `data/topics/` directory.  Each JSON file is a list of documents in the format returned by the search engine.  When a topic word-cloud is clicked on, the server fetches the file from disk and returns it, as-is, back to the browser.  The JavaScript code then converts the JSON to the list of search results viewable on the screen.