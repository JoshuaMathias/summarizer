#!/bin/python3
# To run successfully, use the command below from the home directory of this project:
# $ python3 src/summarizer.py -c config_un.yml

import local_util as u
logger = u.get_logger( __name__ ) # will call setup_logging() if necessary

## note: logger uses % style formatting.
# --- end logging ---


import argparse
import topic_index_reader
import sum_config
import position_weight_summarizer
import nltk
import os
import sys


# import fss
import qrmatrix
import train_counts

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
        for para in article.paragraphs:
            self.__add_summary_sentence__(para.strip())

        footer = '\n--- end summary: "{}" ---\n'.format(article.id)
        return header + self.summary + footer

    def summarize_docset(self, docset):
        self.__init_summary__()
        for article in docset.articles:
            para1 = article.paragraphs[0]
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
    argparser.add_argument('-f', '--final', action="store_true", help='Run final evaluation on evaltest data')
    args = argparser.parse_args()

    u.eprint('Hello from "summarizer.py" version '+version+' (by team "#e2jkplusplus").')
    logger.info('\n\n------------------------------\n')
    logger.info('summarizer.py begin, parsed args=%s', args)

    config = sum_config.SummaryConfig(args.config)
    logger.info('config.TEAM_ID                  ="%s"', config.TEAM_ID )
    logger.info('config.RELEASE_TITLE            ="%s"', config.RELEASE_TITLE )
    logger.info('config.MAX_WORDS                ="%s"', config.MAX_WORDS )
    logger.info('config.OUTPUT_SUMMARY_DIRECTORY ="%s"', config.OUTPUT_SUMMARY_DIRECTORY )
    logger.info('config.AQUAINT                  ="%s"', config.AQUAINT )
    logger.info('config.AQUAINT1_DIRECTORY       ="%s"', config.AQUAINT1_DIRECTORY )
    logger.info('config.AQUAINT2_DIRECTORY       ="%s"', config.AQUAINT2_DIRECTORY )
    logger.info('config.ARTICLE_FILE             ="%s"', config.ARTICLE_FILE )
    logger.info('config.WORD_COUNTS_FILE         ="%s"', config.WORD_COUNTS_FILE )

    logger.info('config.ARTICLE_WEIGHT_FILE      ="%s"', config.ARTICLE_WEIGHT_FILE )
    logger.info('config.SENTENCE_WEIGHT_FILE     ="%s"', config.SENTENCE_WEIGHT_FILE )

    if config.QRMATRIX:
        logger.info('config.QRMATRIX          = TRUE')
    else:
        logger.info('config.QRMATRIX          = FALSE')

    if config.SENTENCE_LOCATION:
        logger.info('config.SENTENCE_LOCATION = TRUE')
    else:
        logger.info('config.QRMATRIX          = FALSE')

    summary_word_counts = { }

    source_description = "*unkown*" # set this to a suitable label for our statistics summary.

    if config.AQUAINT:
        if args.final:
            test_index_reader = topic_index_reader.TopicIndexReader(config.AQUAINT_TEST_TOPIC_INDEX_FILE,
                                                               aquaint1 = config.AQUAINT1_DIRECTORY,
                                                               aquaint2 = config.AQUAINT2_DIRECTORY,
                                                               dbname = config.SHELVE_DB_TEST)
        else:
            test_index_reader = topic_index_reader.TopicIndexReader(config.AQUAINT_TEST_TOPIC_INDEX_FILE,
                                                               aquaint1 = config.AQUAINT1_DIRECTORY,
                                                               aquaint2 = config.AQUAINT2_DIRECTORY,
                                                               dbname = config.SHELVE_DB_DEV)
        train_index_reader = topic_index_reader.TopicIndexReader(config.AQUAINT_TRAIN_TOPIC_INDEX_FILE,
                                                           aquaint1 = config.AQUAINT1_DIRECTORY,
                                                           aquaint2 = config.AQUAINT2_DIRECTORY,
                                                           dbname = config.SHELVE_DB_TRAIN)
        # todo: move shelve_db into config.yaml ? (jgreve)
        #u.eprint('index_reader={}'.format(index_reader) )
        logger.info('test_index_reader=%s', test_index_reader )

        logger.info('config.MAX_WORDS=%s', config.MAX_WORDS)
        smry = Summarizer(config.MAX_WORDS)

        #logger.info('config.topic_file_path()="%s"', config.aquaint_topic_file_path())
        test_topic_index = test_index_reader.read_topic_index_file(docset_type = 'docseta')
        logger.info( 'test_topic_index=%s', test_topic_index )

        train_topic_index = train_index_reader.read_topic_index_file()
        # Only train counts if the word counts file is not found
        if not os.path.exists(config.WORD_COUNTS_FILE):
            logger.debug('\n\n--- Writing word frequencies of training set to '+config.WORD_COUNTS_FILE+' ---')
            trained_word_counts, num_trained_docsets = train_counts.train_counts(train_topic_index.documentSets(), config.WORD_COUNTS_FILE)
        else:
            trained_word_counts, num_trained_docsets = train_counts.read_train_counts(config.WORD_COUNTS_FILE)

        logger.debug( '\n\n--- for docset in topic_index.... ---' )
        source_description = str(test_topic_index)
        logger.info('Reading weights from "%s" and "%s"', config.ARTICLE_WEIGHT_FILE, config.SENTENCE_WEIGHT_FILE )
        summary_weights = position_weight_summarizer.PositionWeights(config.ARTICLE_WEIGHT_FILE, config.SENTENCE_WEIGHT_FILE)
        for docset in test_topic_index.documentSets(docset_type='docseta'):
            msg = 'processing %s' % docset
            u.eprint( msg  ) # high level summary to stdout for our user.
            logger.info( msg )
            print('%s : %s' % (docset.id, docset.topic_title)) # requried in stdout
            smry.summary = ''
            smry.summary_size = 0
            if config.QRMATRIX:
                summary_text = qrmatrix.qr_sum(docset, config, trained_word_counts, num_trained_docsets)
                summary_word_count = len( summary_text.split() )
                logger.info('qrmatrix.qr_sum(docset=%s): summary_word_count=%d, summary_text="%s"', docset, summary_word_count, summary_text )
                summary_word_counts[summary_word_count] = 1 + summary_word_counts.get(summary_word_count,0)
            elif config.SENTENCE_LOCATION:
                logger.info('summary_weights.position_sum(docset (%s))', docset.id)
                summary_text = summary_weights.position_sum(docset)
                summary_word_count = len(summary_text.split())
                logger.info('summary_weights.position_sum(docset=%s): summary_word_count=%d, summary_text="%s"', docset, summary_word_count, summary_text)
                print('summary_weights.position_sum(docset=%s): summary_word_count=%d, summary_text="%s"' % (docset, summary_word_count, summary_text))

                summary_word_counts[summary_word_count] = 1 + summary_word_counts.get(summary_word_count, 0)

    # qrmatrix.write_statistics( source_description ) # write some output for what happened.
    u.write_values( sys.stderr, "summary_word_counts", summary_word_counts)
    print('Done.')
