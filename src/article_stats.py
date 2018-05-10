#!/bin/python3
#     $ clear; rm *.log; src/foo.py -c bin/config_patas_D3.yml 

# jgreve Wed May  9 2018
# Write some stats about our aritcles, some shallow data profilng
# and pattern checks.

import local_util as u
logger = u.get_logger( __name__ ) # will call setup_logging() if necessary

## note: logger uses % style formatting.
# --- end logging ---


import math
import argparse
import topic_index_reader
import sum_config
import nltk
import os


# import fss
# import qrmatrix

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
        for article in docset.articles:
            para1 = article.body[0]
            sentences = nltk.sent_tokenize(para1)
            self.__add_summary_sentence__(sentences[0].replace('\n',' '))
        return self.summary


def read_config(cfg, label, default):
    if label in cfg:
        return cfg[label]
    else:
        return default



def write_stats_details( label, d, depth=0 ):
    indent = '|   '*depth
    logger.debug( '%s: label=%s', indent, label )
    keys = sorted( d )
    if not keys:
        logger.debug( '%s: key=%s is empty, returning', indent, label )
        return
    thing = d[keys[0]]
    if isinstance( thing, dict ):
        logger.debug( '%s: key=%s has #%d items', indent, label, len(keys) )
        for key in keys:
            write_stats_details( label + ':' + key, d[key], depth+1 )
        logger.debug( '%s: key=%s ---end---', indent, label )
        return
    logger.debug( '%s: key=%s has #%d items ---begin details---', indent, label, len(keys) )
    for key in keys:
        logger.debug( '%s: %s=%s', indent, key, d[key] )
    logger.debug( '%s: key=%s ---end details---', indent, label )
    


track_dict = dict( )
def write_stats( ):
    global track_dict
    for bucket_key in sorted( track_dict ):
        logger.debug( '\n\n------ write_stats_details: bucket="%s" ------', bucket_key )
        write_stats_details( bucket_key, track_dict[bucket_key] )

def track_internal( bucket, tokens, value ):
    global track_dict
    if bucket not in track_dict:
        track_dict[ bucket ] = dict( )
    d = track_dict[ bucket ]
    for token in tokens:
        if token not in d:
            d[token] = dict( ) # start a new dictionary.
        d = d[token]
    # at this point d references the correct value-counter dict.
    d[value] = 1 + d.get( value, 0 )

def track( path,  value, bucket = None ):
    tokens = path.split( '.' )
    if bucket:
        track_internal( bucket, tokens, value )
    track_internal( '*ALL*', tokens, value )

def log_ten( n ):
    if n == 0:
        return -1
    return round( math.log10( n ), 1 )

def scan_article( article ):
    logger.debug( '\t-------+' )
    logger.debug( '\tarticle:%02d.%02d: %s',   docset_idx, article_idx, article )
    logger.debug( '\t       : headline="%s"',  article.headline )
    logger.debug( '\t       : datetime ="%s"', article.datetime )
    logger.debug( '\t       : dateline ="%s"', article.dateline )
    logger.debug( '\t       : agency   ="%s"', article.agency )
    logger.debug( '\t       : #paragraphs = %d', len(article.paragraphs) )
    track( "length.headline",  len(article.headline),  bucket=article.agency)
    track( "length.datetime",  len(article.datetime),  bucket=article.agency)
    track( "article.cnt",      1 )
    track( "article.agency",   article.agency )
    track( "length.datetime",  len(article.datetime),  bucket=article.agency)
    track( "article.para_cnt", len(article.paragraphs),  bucket=article.agency)
    text_size = 0
    for pidx, p in enumerate( article.paragraphs ):
        logger.debug( '\t       : para[%03d]: <%s>', pidx, p )
        #ps = article.scrubbed_paragraphs()[pidx]
        #logger.debug( '\t       : scrb[%03d]: <%s>', pidx, ps )
        #max_idx = max( len(p), len(ps) )
        #for idx in range( max_idx ):
        #    text_size = 0
        text_size += len(p)
        track( "article.text_sizeLog10_para", log_ten(len(p)),   bucket=article.agency )
        for c in p:
            track( "article.char_freq", c,   bucket=article.agency)
    track( "article.text_sizeLog10_total", log_ten(text_size),   bucket=article.agency )

def dump_paragraphs( article ):
    for pidx, p in enumerate( article.paragraphs ):
        logger.debug( '\t       : para[%03d]: <%s>', pidx, p )
        ps = article.scrubbed_paragraphs()[pidx]
        logger.debug( '\t       : scrb[%03d]: <%s>', pidx, ps )
        max_idx = max( len(p), len(ps) )
        for idx in range( max_idx ):
            c  = p[idx]  if idx < len(p)  else chr(0)
            cs = ps[idx] if idx < len(ps) else chr(0)
            # display chars
            d  = c  if c  >= ' ' else '<%02X>' % ord(c)
            ds = cs if cs >= ' ' else '<%02X>' % ord(cs)
            flag = ' ' if c == cs else '*'
            logger.debug( '\t       : %spara/scrb[%03d]: %-4.4ss 0x%02X | %-4.4ss 0x%02X',
                flag, idx, d, ord(c), ds, ord(cs) )


if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    version = "1.0"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    argparser = argparse.ArgumentParser(description='summarizer.py v. '+version+' by team #e2jkplusplus')
    argparser.add_argument('-c',
                           '--config',
                           metavar='CONFIG',
                           default=os.path.join(dir_path, 'config.yml')
                           , help='Config File(s)')
    args = argparser.parse_args()

    #u.eprint('Hello from "{}" version '+version+' (by team "#e2jkplusplus").'.format(sys.argv[0]))
    logger.info('parsed args=%s', args)
    config = sum_config.SummaryConfig(args.config)

    logger.info('config.AQUAINT1_DIRECTORY=%s', config.AQUAINT1_DIRECTORY)
    logger.info('config.AQUAINT2_DIRECTORY=%s', config.AQUAINT2_DIRECTORY)
    index_reader = topic_index_reader.TopicIndexReader(config.aquaint_topic_file_path(),
                                                       aquaint1 = config.AQUAINT1_DIRECTORY,
                                                       aquaint2 = config.AQUAINT2_DIRECTORY,
                                                       dbname = 'shelve_db')
    # todo: move shelve_db into config.yaml ? (jgreve)
    #u.eprint('index_reader={}'.format(index_reader) )
    logger.info('index_reader=%s', index_reader )

    logger.info('config.MAX_WORDS=%s', config.MAX_WORDS)
    smry = Summarizer(config.MAX_WORDS)
    #logger.info('config.topic_file_path()="%s"', config.aquaint_topic_file_path())

    topic_index = index_reader.read_topic_index_file(docset_type = 'docseta')
    logger.info( '\n\n---main loop in foo.py---\ntopic_index=%s', topic_index )
    for docset_idx, docset in enumerate( topic_index.documentSets(docset_type='docseta') ):
        msg = 'processing #%d: %s' % (docset_idx, docset)
        u.eprint( msg  ) # high level summary to stdout for our user.
        logger.debug( msg )
        # lets dump a little more info about the docset....
        logger.debug( '\tdocset:%02d: type=<%s>', docset_idx, docset.type )
        logger.debug( '\tdocset:%02d: topic_title=<%s>', docset_idx, docset.topic_title )
        logger.debug( '\tdocset:%02d: topic_id=<%s>', docset_idx, docset.topic_id )
        for article_idx, article in enumerate(docset.articles):
            scan_article( article )
            if article.id == 'APW19990421.0284':
                dump_paragraphs( article )
                #quit()
    write_stats( )
    print('Done.')
