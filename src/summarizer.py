#!/bin/python3
import sys
import argparse
import yaml
import content_provider
import nltk


class Summarizer():
    def __init__(self, nwords):
        self.nwords = nwords

    def __init_summary__(self):
        self.summary = ''
        self.summary_size = 0

    def __add_summary_sentence__(self, sentence):
        sentence_tokens = sentence.split()
        if len(sentence_tokens) > self.nwords - self.summary_size:
            for i in range(self.nwords - self.summary_size):
                self.summary += ' ' + sentence_tokens[i]
                self.summary_size += 1
        else:
            self.summary += sentence
            self.summary_size += len(sentence_tokens)

        self.summary += '\n'


    def summarize(self, article):
        self.__init_summary__()
        header = '--- begin summary: "{}" ---\n'.format(article.id)
        for para in article.body:
            self.__add_summary_sentence__(para.strip())

        footer = '\n--- end summary: "{}" ---\n'.format(article.id)
        return header + self.summary + footer

    def summarize_docset(self, docset):
        self.__init_summary__()
        for article in docset.docs:
            para1 = article.body[0]
            sentences = nltk.sent_tokenize(para1)
            self.__add_summary_sentence__(sentences[0])
        return self.summary


def read_config(cfg, label, default):
    if label in cfg:
        return cfg[label]
    else:
        return default

if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    argparser = argparse.ArgumentParser(description = 'summarizer.py v. 0.0 by team #e2jkplusplus')
    argparser.add_argument('config', metavar='CONFIG', default='config.yml', help='Config File(s)')
    args = argparser.parse_args()

    print('Hello from "summarizer.py" version 0.0 (by team "#e2jkplusplus").')

    with open(args.config, 'r') as  ymlfile:
        cfg = yaml.load(ymlfile)

    if 'aquaint' in cfg:
        aquaint_cfg = cfg['aquaint']
        aquaint1_directory = read_config(aquaint_cfg, 'aquaint1_directory', '/opt/dropbox/17-18/573/AQUAINT')
        aquaint2_directory = read_config(aquaint_cfg, 'aquaint2_directory', '/opt/dropbox/17-18/573/AQUAINT-2')
        aquaint_topic_index = read_config(aquaint_cfg, 'aquaint_topic_index', '/opt/dropbox/17-18/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml')

        reader = content_provider.ContentReader(aquaint=aquaint1_directory, aquaint2=aquaint2_directory)

        smry = Summarizer(100)

        for docset in reader.read_topic_index(aquaint_topic_index):
            print('%s : %s' % (docset.id, docset.topic_title))
            smry.summary = ''
            smry.summary_size = 0
            print(smry.summarize_docset(docset))

    elif 'one_file' in cfg:
        file_cfg = cfg['one_file']
        nwords = read_config(cfg, 'word_count', 100)
        raw_file = read_config(cfg, 'article_file', 'aquaint_test1/nyt/1999/19990330_NYT')

        smry = Summarizer(nwords)

        articles = content_provider.ContentReader().read_raw_files(args.filename)

        for article in articles:
            print(smry.summarize(article))

    print('Done.')