import numpy as np
import nltk
from nltk.util import ngrams
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

def make_ngrams(tokens, n):
    return(list(ngrams(tokens, n)))

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
            summary_line_4_grams = make_ngrams(summary.line_tokens[summary_line_index], 4)
            summary_index = summary_line_index if summary_line_index < 10 else 9
            for para_index in range(len(self.paragraphs)):
                for line_index in range(len(self.paragraphs[para_index])):
                    sim = cosine_similarity_ngrams(summary_line_4_grams, make_ngrams(self.paragraphs[para_index][line_index], 4))
                    self.statistics[para_index, line_index, summary_index] += sim

    def len(self):
        length = 0
        for paragraph in self.paragraphs:
            length += len(paragraph)

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
        self.line_count = list()

        for article in docset.articles:
            self.articles.append(TokenizedArticle(article))

    def add_summary_line(self, line_number):
        if len(self.line_count) <= line_number:
            for n in range(len(self.line_count), line_number + 1):
                self.line_count.append(0)

        try:
            self.line_count[line_number] += 1
        except IndexError:
            logger.error('self.line_count has length %d, but accessing line %d' % (len(self.line_count), line_number))
            raise IndexError()

class PeerSummaries():
    def __init__(self, docset, peer_directory):
        self.summaries = list()
        summary_count = 0
        for file in os.listdir(peer_directory):
            if fnmatch.fnmatch(file, summary_file_pattern(docset)):
                self.summaries.append(Summary(os.path.join(peer_directory, file)))
                summary_count += 1

        logger.info('Found %d summary files in %s' % (summary_count, summary_file_pattern(docset)))

class WeightAverages():
    def __init__(self):
        self.value_table = list()
        self.count_table = list()

    def add_value(self, line_index, horiz_index, value, weight):
        if len(self.value_table) <= line_index:
            for n in range(len(self.value_table), line_index + 1):
                self.value_table.append(list())
                self.count_table.append(list())

        horiz_list = self.value_table[line_index]
        count_list = self.count_table[line_index]
        if len(horiz_list) <= horiz_index:
            for m in range(len(horiz_list), horiz_index + 1):
                horiz_list.append(0.0)
                count_list.append(0)

        horiz_list[horiz_index] += value
        count_list[horiz_index] += weight

    def output_averages(self, outfile):
        for l in range(len(self.value_table)):
            for h in range(len(self.value_table[l])):
                if self.count_table[l][h] > 0:
                    outfile.write('%s' % (self.value_table[l][h] / self.count_table[l][h]))
                else:
                    outfile.write('0.0')
                if h < len(self.value_table[l]) - 1:
                    outfile.write (',')
            outfile.write('\n')
        outfile.flush()
        outfile.close()

class SentenceOrderTable(WeightAverages):
    def __init__(self):
        super().__init__()

    def addDocSet(self, docset):
        for article in docset.articles:
            line_count = 0
            paragraph_count = 0
            for paragraph in article.paragraphs:
                sentence_count = 0
                for sentence in paragraph:
                    for summary_line in range(10):
                        if len(docset.line_count) > summary_line and docset.line_count[summary_line] > 0:
                            self.add_value(summary_line, line_count,
                                           article.statistics[paragraph_count, sentence_count, summary_line],
                                           docset.line_count[summary_line])
                    sentence_count += 1
                    line_count += 1
                paragraph_count += 1

class ArticleOrderTable(WeightAverages):
    def __init__(self):
        super().__init__()

    def addDocSet(self, docset):
        for summary_line in range(10):
            if len(docset.line_count) > summary_line and docset.line_count[summary_line] > 0:
                for article_index in range(len(docset.articles)):
                    article_value = 0.0
                    line_count = 0
                    paragraph_count = 0
                    article = docset.articles[article_index]
                    for paragraph in article.paragraphs:
                        sentence_count = 0
                        for sentence in paragraph:
                            article_value += article.statistics[paragraph_count, sentence_count, summary_line]
                            sentence_count += 1
                            line_count += 1
                        paragraph_count += 1

                    self.add_value(summary_line, article_index, article_value, docset.line_count[summary_line])

class ParagraphOrderTable(WeightAverages):
    def __init__(self):
        super().__init__()

    def addDocSet(self, docset):
        for summary_line in range(10):
            if len(docset.line_count) > summary_line and docset.line_count[summary_line] > 0:
                for article_index in range(len(docset.articles)):
                    line_count = 0
                    paragraph_count = 0
                    article = docset.articles[article_index]
                    for paragraph in article.paragraphs:
                        paragraph_value = 0.0
                        sentence_count = 0
                        for sentence in paragraph:
                            paragraph_value += article.statistics[paragraph_count, sentence_count, summary_line]
                            sentence_count += 1
                            line_count += 1

                        self.add_value(summary_line, paragraph_count, paragraph_value, docset.line_count[summary_line])
                        paragraph_count += 1

def summary_file_pattern(docset):
    return docset.topic_id.upper()[0:-1] + "*"

if __name__ == '__main__':
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    version = "0.4"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    argparser = argparse.ArgumentParser(description='sentence_distance.py v. '+version+' by team #e2jkplusplus')
    argparser.add_argument('-c', '--config', metavar='CONFIG', default=os.path.join(dir_path, 'config.yml'), help='Config File(s)')
    argparser.add_argument('-p', '--peers', metavar='PEER', default='/opt/dropbox/17-18/573/Data/peers/training/')
    args = argparser.parse_args()

    config = sum_config.SummaryConfig(args.config)
    reader = topic_index_reader.TopicIndexReader(config.aquaint_topic_file_path(),
                                                 aquaint1=config.AQUAINT1_DIRECTORY,
                                                 aquaint2=config.AQUAINT2_DIRECTORY,
                                                 dbname='shelve_db')

    topic_index = reader.read_topic_index_file(docset_type = 'docseta')

    sentence_order_table = SentenceOrderTable()
    article_order_table = ArticleOrderTable()
    paragraph_order_table = ParagraphOrderTable()
    total_article_lines = 0.0
    num_articles = 0
    for docset in topic_index.documentSets(docset_type='docseta'):
        peer_summaries = PeerSummaries(docset, args.peers)
        tokenized_docset = TokenizedDocSet(docset)
        for summary in peer_summaries.summaries:
            for n in range(len(summary.line_tokens)):
                tokenized_docset.add_summary_line(n)

            for article in tokenized_docset.articles:
                article.compare_summary(summary)
                total_article_lines += article.len()
                num_articles += 1

        sentence_order_table.addDocSet(tokenized_docset)
        article_order_table.addDocSet(tokenized_docset)
        paragraph_order_table.addDocSet(tokenized_docset)

    logger.info('Average article length = %s' % (total_article_lines / num_articles))

    sentence_outfile = open('SentenceOrder.csv', 'w')
    sentence_order_table.output_averages(sentence_outfile)

    article_outfile = open('ArticleOrder.csv', 'w')
    article_order_table.output_averages(article_outfile)

    paragraph_outfile = open('ParagraphOrder.csv', 'w')
    paragraph_order_table.output_averages(paragraph_outfile)
