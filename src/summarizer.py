#!/bin/python3
# To run successfully, use the command below from the home directory of this project:
# $ python3 src/summarizer.py -c config_un.yml
import argparse
import content_provider
import sum_config
import nltk
import os
import fss
import local_util as u
# "local_util" mainly for u.eprint() which is like print but goes to stderr.

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
            self.__add_summary_sentence__(sentences[0].replace('\n',' '))
        return self.summary


def read_config(cfg, label, default):
    if label in cfg:
        return cfg[label]
    else:
        return default


if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    version = "1.0"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    argparser = argparse.ArgumentParser(description='summarizer.py v. '+version+' by team #e2jkplusplus')
    argparser.add_argument('-c', '--config', metavar='CONFIG', default=os.path.join(dir_path, 'config.yml'), help='Config File(s)')
    args = argparser.parse_args()

    u.eprint('Hello from "summarizer.py" version '+version+' (by team "#e2jkplusplus").')
    u.eprint('parsed args={}'.format(args))

    config = sum_config.SummaryConfig(args.config)

    if config.AQUAINT:
        u.eprint('config.AQUAINT1_DIRECTORY={}'.format(config.AQUAINT1_DIRECTORY))
        u.eprint('config.AQUAINT2_DIRECTORY={}'.format(config.AQUAINT2_DIRECTORY))
        reader = content_provider.ContentReader(aquaint=config.AQUAINT1_DIRECTORY,
                                                aquaint2=config.AQUAINT2_DIRECTORY)

        u.eprint('config.MAX_WORDS={}'.format(config.MAX_WORDS))
        smry = Summarizer(config.MAX_WORDS)

        u.eprint('config.topic_file_path()="{}"'.format(config.aquaint_topic_file_path()))
        for docset in reader.read_topic_index(config.aquaint_topic_file_path()):
            u.eprint('%s : %s' % (docset.id, docset.topic_title))
            print('%s : %s' % (docset.id, docset.topic_title))
            smry.summary = ''
            smry.summary_size = 0
            print(fss.first_sent_sum(docset, config) + "\n\n")

    elif config.ONE_FILE:
        smry = Summarizer(config.MAX_WORDS)

        u.eprint('config.ARTICLE_FILE="{}"'.format( config.ARTICLE_FILE ))
        articles = content_provider.ContentReader().read_raw_files(config.ARTICLE_FILE)

        for article in articles:
            print(smry.summarize(article))

    print('Done.')
