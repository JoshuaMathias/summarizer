import numpy as np
import nltk
import re
import math
import argparse
import os
import fnmatch
from collections import Counter

import article_content
import sum_config
import topic_index_reader

import local_util as u
logger = u.get_logger('sentence_distance.py') # will call setup_logging() if necessary


def sentence_tokens_with_alpha_only(sentence):
    return [t for t in nltk.word_tokenize(sentence.lower()) if re.search("[a-z]", t)]

def reverse_jaccard_distance_value(tokens1, tokens2):
    return 1.0 - nltk.jaccard_distance(tokens1, tokens2)

def ngrams(tokens, n):
    return(list(nltk.util.ngrams(tokens, n)))

def cosine_similarity_ngrams(a, b):
    vec1 = Counter(a)
    vec2 = Counter(b)
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator:
        return 0.0
    return float(numerator) / denominator

class TokenizedArticle():
    def __init__(self, article):
        self.num_paragraphs = len(article.paragraphs)
        self.max_sentences = 0
        self.paragraphs = list()

        for paragraph_text in article.paragraphs:
            paragraph_tokens = list()
            for line in nltk.sent_tokenize(paragraph_text):
                paragraph_tokens.append(sentence_tokens_with_alpha_only(line))

            self.paragraphs.append(paragraph_tokens)
            self.max_sentences = max(self.max_sentences, len(paragraph_tokens))

        self.statistics = np.zeros((len(self.paragraphs), self.max_sentences, 10))

    def compare_summary(self, summary):
        for summary_line_index in range(len(summary.line_tokens)):
            summary_line_set = set(summary.line_tokens[summary_line_index])
            summary_line_4_grams = ngrams(summary.line_tokens, 4)
            summary_index = summary_line_index if summary_line_index < 10 else 9
            for para_index in range(len(self.paragraphs)):
                for line_index in range(len(self.paragraphs[para_index])):
                    self.statistics[para_index, line_index, summary_index] += reverse_jaccard_distance_value(summary_line_set, set(self.paragraphs[para_index][line_index]))


class Summary():
    def __init__(self, summary_filename):
        summary_file = open(summary_filename, 'r')
        self.line_tokens = list()
        for line in summary_file:
            if len(line.strip()) > 0:
                self.line_tokens.append(sentence_tokens_with_alpha_only(line))

class TokenizedDocSet():
    def __init__(self, docset):
        self.articles = list()

        for article in docset.articles:
            self.articles.append(TokenizedArticle(article))

class PeerSummaries():
    def __init__(self, docset, peer_directory):
        self.summaries = list()
        for file in os.listdir(peer_directory):
            if fnmatch.fnmatch(file, docset.topic_id + "*"):
                self.summaries.append(Summary(os.path.join(peer_directory, file)))

if __name__ == '__main__':
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    version = "1.0"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    argparser = argparse.ArgumentParser(description='summarizer.py v. '+version+' by team #e2jkplusplus')
    argparser.add_argument('-c', '--config', metavar='CONFIG', default=os.path.join(dir_path, 'config.yml'), help='Config File(s)')
    argparser.add_argument('-p', '--peers', metavar='PEER', default='/opt/dropbox/17-18/573/Data/peers/')
    args = argparser.parse_args()

    config = sum_config.SummaryConfig(args.config)
    reader = topic_index_reader.TopicIndexReader(config.aquaint_topic_file_path(),
                                                 aquaint1=config.AQUAINT1_DIRECTORY,
                                                 aquaint2=config.AQUAINT2_DIRECTORY,
                                                 dbname='shelve_db')

    for docset in reader.documentSets(docset_type='docseta'):
        peer_summaries = PeerSummaries(docset, args.p)

