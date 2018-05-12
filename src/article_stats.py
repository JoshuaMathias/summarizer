#!/bin/python3
# to run use:
#  bin/article_stats
#

# see logs and output under the run/ directory.
#-------------------------------------------------
# jgreve Wed May  9 2018
# Write some stats about our articles, some data profilng
# and pattern checks.

import local_util as u
logger = u.get_logger( __name__ ) # will call setup_logging() if necessary

## note: logger uses % style formatting.
# --- end logging ---


from nltk.tokenize import sent_tokenize, word_tokenize # for tokenizing sentences and words
import math
import argparse
import topic_index_reader
import sum_config
import nltk
import os
import re


# import fss
# import qrmatrix


def read_config(cfg, label, default):
    if label in cfg:
        return cfg[label]
    else:
        return default


def gather_stats( label, d, key_hdr='', val_hdr='' ):
    stats = { }
    stats['total'] = sum( d.values() )
    stats['cnt'] = len( d )
    stats['key_width'] = max( [ len(str(key)) for key in d.keys() ]  )
    stats['key_width'] = max( stats['key_width'], len(key_hdr) )
    stats['val_width'] = max( [ len(str(value)) for value in d.values() ]  )
    stats['val_width'] = max( stats['val_width'], len(val_hdr) )
    stats['min'] = min( d.values() )
    stats['max'] =  max( d.values() )
    stats['types'] = set( [ type( value ) for value in d.values() ] )
    stats['type'] = None
    stats['type_flag'] = 's' # assume string.
    if 1 == len( stats['types'] ):
        t = list( stats['types'] )[0] # grab first type, all the same.
        stats['type'] = t
        if t == int:
            stats['type'] = 'd'
        elif t == float:
            stats['type'] = 'f'
        elif t == str:
            stats['type'] = 's'
        else:
            logger.warning( '%s: unknown type %s', label, str(t) )
    #----------------
    return stats

def write_char_freqs( indent, f, label, d ):
    key_hdr = 'char: hex '
    val_hdr = 'freq'
    stats = gather_stats( label, d, key_hdr=key_hdr, val_hdr=val_hdr )
    msg='write_char_freqs(): label={} has #{} items, key_hdr={} val_hdr={}'.format( label, len(d), key_hdr, val_hdr )
    logger.debug( '%s: %s', indent, msg )
    f.write('{}\n'.format( msg ) )
    f.write('stats={}\n'.format( stats ) )
    f.write('\n')
    f.write('| {:^{key_width}} | {:^{val_width}} | {:^7s} | {:^7s} |\n'.format(
        key_hdr, val_hdr, '%ge', 'cum%',
        key_width=stats['key_width'],
        val_width=stats['val_width'] ) )
    keys = sorted( d.keys() )
    cum_percent = 0.0 # cummulative %
    for key in keys:
        #logger.debug( '%s: %s=%s', indent, key, d[key] )
        val = d[key]
        percent = (val / stats['total']) * 100
        cum_percent += percent
        histo = '#'  * int(round(percent/2))
        if key >= ' ':
            display =  '<{}> : 0x{:02X}'.format( key, ord(key) )
        else:
            display = '--- : 0x{:02X}'.format( ord(key) )
        f.write('| {:{key_width}} | {:{val_width}} | {:6.2f}% | {:6.2f}% | {}\n'.format(
            display, val, percent, cum_percent, histo,
            key_width=stats['key_width'],
            val_width=stats['val_width'] ) )
    logger.debug( '%s: key=%s ---end details---', indent, label )
    f.write('\n\ntotal items:    {:10,d}\n'.format( stats['total'] ) )
    f.write(    'distinct items: {:10,d}\n'.format( stats['cnt'] ) )
    f.write(    'ratio: {:6.2f}\n'.format( stats['total']/stats['cnt'] ) )





def write_values( indent, f, label, d, descending_freq=False ):
    key_hdr = label.split('-')[-1]
    val_hdr = 'freq'
    msg='write_values(): label={} has #{} items, key_hdr={} val_hdr={}'.format( label, len(d), key_hdr, val_hdr )
    a = 'char_freq'
    if key_hdr[-len(a):] == a:
        return write_char_freqs( indent, f, label, d ) # ends with char_freq

    stats = gather_stats( label, d, key_hdr=key_hdr, val_hdr=val_hdr )
    stats['key_width'] = max( stats['key_width'], len(key_hdr) )
    stats['val_width'] = max( stats['val_width'], len(val_hdr) )

    msg='write_values(): ---begin details---'.format( label, len(d) )
    logger.debug( '%s: %s', indent, msg )
    f.write('{}\n'.format( msg ) )
    f.write('stats={}\n'.format( stats ) )
    f.write('\n')
    f.write('| {:^{key_width}} | {:^{val_width}} | {:^7s} | {:^7s} |\n'.format(
        key_hdr, val_hdr, '%ge', 'cum%',
        key_width=stats['key_width'],
        val_width=stats['val_width'] ) )
    if descending_freq:
        items = sorted( d.items(), key=lambda x: ( -x[1], x[0] ) ) # negate counts to effect largest value first.
        # otherwise reverse=True will yield things like: (100, 'C' ), (100, 'B' ), (100, 'A')
    else:
        #keys = sorted( d.keys() )
        items = sorted( d.items() )
    cum_percent = 0.0 # cummulative %
    for item in items:
        #logger.debug( '%s: %s=%s', indent, key, d[key] )
        #val = d[key]
        key, val = item
        #logger.debug( '%s: %s=%s', indent, key, val )
        percent = (val / stats['total']) * 100
        cum_percent += percent
        histo = '#'  * int(round(percent/2))
        f.write('| {:{key_width}} | {:{val_width}} | {:6.2f}% | {:6.2f}% | {}\n'.format(
            key, val, percent, cum_percent, histo,
            key_width=stats['key_width'],
            val_width=stats['val_width'] ) )
    logger.debug( '%s: key=%s ---end details---', indent, label )
    f.write('\n\ntotal items:    {:10,d}\n'.format( stats['total'] ) )
    f.write(    'distinct items: {:10,d}\n'.format( stats['cnt'] ) )
    f.write(    'ratio: {:10.4f}\n'.format( stats['total']/stats['cnt'] ) )

def write_stats_details( label, dir, d, depth=0 ):
    indent = '|   '*depth
    logger.debug( '%s: label=%s', indent, label )
    if len(d) == 0:
        logger.debug( '%s: label=%s is empty, returning', indent, label )
        return
    thing = next( iter( d.values() ) )  # grab any item, see if it is a dictionary.
    if isinstance( thing, dict ):
        logger.debug( '%s: key=%s has #%d items', indent, label, len(d) )
        for key in sorted( d.keys() ):
            longer_label = label + '-' + key
            write_stats_details( longer_label, dir, d[key], depth+1 )
        logger.debug( '%s: key=%s ---end---', indent, label )
        return
    filename = '{}/{}.txt'.format( dir,  label )
    with open( filename, 'w' ) as f:
        write_values( indent, f, label, d )
    #----------------------------------------------
    if re.search( r'(word)|(pattern)$', label ):
        # need a cleaner way to control formatting, for now if ends with .*word or .*pattern
        # we get both:
        #    ascending:   Alpha:1 Beta:1  Gamma:3 Delta:5 Epsilon:1  (ordered by key)
        #    descending:  Delta:5 Gamma:3 Alpha:1 Beta:1  Epsilon:1  (ordered by higher-freq(major), ascending key(minor))
        filename = '{}/{}__rev.txt'.format( dir,  label )
        with open( filename, 'w' ) as f:
            write_values( indent, f, label, d, descending_freq=True )

track_dict = dict( )
def write_stats( label, dir ):
    global track_dict
    u.eprint('write_state(): label="{}" dir="{}"'.format( label, dir))
    for bucket_key in sorted( track_dict ):
        bucket_dir = '{}/{}'.format( dir, bucket_key )
        if not os.path.exists( bucket_dir ):
            os.makedirs( bucket_dir )
            u.eprint('created bucket directory "{}"'.format( bucket_dir ) )
        logger.debug( '\n\n------ write_stats_details: bucket="%s"  bucket_dir="%s"------', bucket_key, bucket_dir )
        write_stats_details( bucket_key, bucket_dir, track_dict[bucket_key] )

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
    track_internal( 'ALL', tokens, value )

def log_ten( n ):
    if n == 0:
        return -1
    return round( math.log10( n ), 1 )


pattern_examples = dict( ) # put a limit on how many "examples" of a given pattern we show.
def track_word( label, word, bucket=None ):
    global pattern_examples
    if label not in pattern_examples:
        pattern_examples[label] = dict()
    pattern_limit = pattern_examples[label]
    track( label+"_word", word,  bucket=article.agency)
    pattern = word
    pattern = re.sub( r'[0-9]', r'9', pattern )
    pattern = re.sub( r'[a-z]', r'A', pattern )
    pattern = re.sub( r'AAA+', r'T', pattern )
    pattern = re.sub( r'T T( T)+', r'T+', pattern )
    track( label+"_pattern", pattern,  bucket=article.agency)
    pattern_limit[pattern] = 1 + pattern_limit.get( pattern, 0 )
    if pattern_limit[pattern] <= 50:
        logger.debug('%-15s: pattern<%-20s> word=<%s>', label, pattern, word )
            

def track_sentence( s, label, bucket = None ):
    for word in word_tokenize(s): # as used in qrmatrix.py, ln# 88
        # all words (lower-cased) in paragaph
        word = word.lower()
        track_word( label, word, bucket )

def track_paragraph( p, label, bucket = None ):
    # all words (lower-cased) in paragaph
    for word in p.lower().split():
        track_word( label, word, bucket )


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
        logger.debug( '\t       : para[%03d]: len=%d: <%s>%s', pidx, len(p), p, (' *' if len(p) == 0 else '') )
        #ps = article.scrubbed_paragraphs()[pidx]
        #logger.debug( '\t       : scrb[%03d]: <%s>', pidx, ps )
        #max_idx = max( len(p), len(ps) )
        #for idx in range( max_idx ):
        #    text_size = 0
        text_size += len(p)
        track( "article.text_sizeLog10_para", log_ten(len(p)),   bucket=article.agency )
        # all characters in paragaph
        for c in p:
            track( "article.char_freq", c,   bucket=article.agency)

        # track "words" twice, once raw and once "scrubbed"
        track_paragraph( p, label="article_raw", bucket=article.agency )
        paragraph = p # bend a copy...

        #--- logic from qrmatrix.py, ln# 81 - 83
        paragraph = re.sub("(\n|\t)", " ", paragraph)
        paragraph = re.sub("  +", " ", paragraph)
        paragraph = re.sub("^ ", "", paragraph)
        track_paragraph( paragraph, label="article_scrub", bucket=article.agency )

        sentences = sent_tokenize(paragraph) # as used in qrmatrix.py, ln# 85
        track( "nltk_sent-per-para", len(sentences), bucket=article.agency )
        for sidx, s in enumerate(sentences):
            logger.debug( '\t       :    : sent[%02d]: <%s>', sidx, s )
            track_sentence( s, label="sent_nltk", bucket=article.agency )
    #--- end for...paragraphs ---
    logger.debug( '\t       : text_size = %d%s', text_size, (' **' if text_size <= 5 else '') )
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
    argparser = argparse.ArgumentParser(description='article stats')
    argparser.add_argument('-c',
                           '--config',
                           metavar='CONFIG',
                           default=os.path.join(dir_path, 'config.yml'),
                           help='Config File(s)')
    args = argparser.parse_args()

    logger.info('parsed args=%s', args)
    config = sum_config.SummaryConfig(args.config)

    logger.info('config.AQUAINT1_DIRECTORY=%s', config.AQUAINT1_DIRECTORY)
    logger.info('config.AQUAINT2_DIRECTORY=%s', config.AQUAINT2_DIRECTORY)
    index_reader = topic_index_reader.TopicIndexReader(config.aquaint_topic_file_path(),
                                                       aquaint1 = config.AQUAINT1_DIRECTORY,
                                                       aquaint2 = config.AQUAINT2_DIRECTORY,
                                                       dbname = config.SHELVE_DBNAME ) #'shelve_db')
    # note: moved shelve_db into config.yml, see runtime:  shelve_dbname:
    # in "conf/config_patas_D3.yml"
    #u.eprint('index_reader={}'.format(index_reader) )
    logger.info('index_reader=%s', index_reader )

    logger.info('config.MAX_WORDS=%s', config.MAX_WORDS)
    #logger.info('config.topic_file_path()="%s"', config.aquaint_topic_file_path())

    topic_index = index_reader.read_topic_index_file(docset_type = 'docseta')
    logger.info( '\n\n---main loop in foo.py---\ntopic_index=%s', topic_index )
    for docset_idx, docset in enumerate( topic_index.documentSets(docset_type='docseta') ):
        msg = 'processing #%d: %s' % (docset_idx, docset)
        u.eprint( msg  ) # high level summary to stdout for our user.
        #if docset_idx >= 3:
        #    break
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
    write_stats( str(topic_index), config.STATS_DIR )
    print('Done.')
