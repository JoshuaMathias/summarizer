import argparse
import os
import nltk
import re

import topic_index_reader
import sum_config

def __sentence_tokens_with_alpha_only__(sentence):
    return [t for t in nltk.word_tokenize(sentence) if re.search("[a-zA-Z]", t)]

def __tokenize_docset__(docset):
    for article in docset.articles:
        article.tok_paras = list()
        for paragraph in article.paragraphs:
            tok_para = list()
            for sentence in nltk.sent_tokenize(paragraph):
                tok_para.append(__sentence_tokens_with_alpha_only__(sentence))
            article.tok_paras.append(tok_para)

if __name__ == "__main__":
    # Similar to summarizer -- loads all articles, but then checks
    delivery_no = 'D4'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    argparser = argparse.ArgumentParser(description='position_weight_training.py %s by team #e2jkplusplus' % delivery_no)
    argparser.add_argument('-c', '--config', metavar='CONFIG', default=os.path.join(dir_path, 'config.yml'), help='Config File(s)')
    args = argparser.parse_args()
    config = sum_config.SummaryConfig(args.config)

    docsets = list()
    reader = topic_index_reader.TopicIndexReader(config.aquaint_topic_file_path(),
                                                 aquaint1 = config.AQUAINT1_DIRECTORY,
                                                 aquaint2 = config.AQUAINT2_DIRECTORY,
                                                 dbname = 'shelve_db')

    for docset in reader.read_topic_index_file(docset_type = 'docseta').documentSets(docset_type='docseta'):
        for article in docset.articles:
            article.tok_paras = list()
            for paragraph in article.paragraphs:
                tok_para = list()
                for sentence in nltk.sent_tokenize(paragraph):
                    tok_para.append(__sentence_tokens_with_alpha_only__(sentence))