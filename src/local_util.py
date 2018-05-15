import sys  # stderr
#import scipy.sparse  # jgreve: seems we're not using this, re-enable if dumpArray() helpful.
#import HTMLParser as html    # https://stackoverflow.com/a/925630/5590742

#-----------------------------------------
# utility functions
#-----------------------------------------

def eprint(*args, **kwargs):
   print(*args, file=sys.stderr, **kwargs)

def makeIndent( depth ):
   return '|   ' * depth

#def dumpArray( a, label ):
#   print('\n--- {} :: shape={} type={} ---'.format( label, a.shape, type(a) ))
#   if isinstance( a, scipy.sparse.csr_matrix ) \
#   or isinstance( a, scipy.sparse.csc_matrix ) :
#      print( a.A )  # show in normal form, vs. serialized list of number
#   else:
#      print(a)

def writeConfusionMatrix( title, actual, bestGuess ):
   print('Confusion matrix for the {} data:'.format(title) )
   print('row is the truth, column is the system output')
   if len(actual) != len(bestGuess):
      eprint('WARNING: writeConfusionMatrix( "{}" ): len(actual)={}, len(bestGuess)={}'.format( title, len(actual), len(bestGuess)) )
   labels = set( actual )
   labels |= set( bestGuess )
   labels = sorted( labels )
   maxIndex = len(actual)
   rowIndex = { }
   for rowIdx, label in enumerate( labels ):
      rowIndex[label] = rowIdx
   colIndex = { }
   for colIdx, label in enumerate( labels ):
      colIndex[label] = colIdx
   cm = [ [0 for x in range( len(labels ) ) ] for y in range( len(labels) ) ]
   total = 0
   for idx, t in enumerate( actual ):
      g = bestGuess[idx] # same location
      r = rowIndex[t]
      c = colIndex[g]
      cm[r][c] += 1
      total += 1
   diagSum =  0
   # print header (column labels, the system output (our 'guess'))
   print( '\n{:13s}{}'.format( '',    ' '.join(labels) ) )
   for rowIdx, rowLabel in enumerate( labels ):
      msg = '{}'.format( rowLabel )
      for colIdx, colLabel in enumerate( labels ):
         msg += ' {}'.format( cm[rowIdx][colIdx] )
      print( msg )
   for idx in range( len(labels) ):
      diagSum += cm[idx][idx]
   accuracy = diagSum / total
   print('\n {} accuracy={:.10f}'.format(title.capitalize(), accuracy) )


# --- begin logging ---
# logging example from here (see: yaml recipe)
#      https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
import logging
import os
import logging.config
import yaml

__LOGGING_SETUP_FLAG__ = False
def setup_logging(
        default_path='logging.yaml',
        default_level=logging.INFO,
        env_key='LOG_CFG'
    ):
    """Setup logging configuration
       Attempts to read ENV-VAR "LOG_CFG", allows override of log.yaml

    """
    global __LOGGING_SETUP_FLAG__
    __LOGGING_SETUP_FLAG__ = True
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
        eprint('setup_logging(): env_key={}, value="{}"'.format(env_key, value))
    else:
        eprint('setup_logging(): env_key={} undefined, using path="{}"'.format(env_key, path))
    if os.path.exists(path):
        eprint('setup_logging(): loading path="{}"...')
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        eprint('setup_logging(): WARNING! path="{}" does not exist? using default_level...')
        logging.basicConfig(level=default_level)

def get_logger( name ):
    """usage: logger = u.get_logger( __name__ ), will call u.setup_logging() if needed"""
    global __LOGGING_SETUP_FLAG__
    if not __LOGGING_SETUP_FLAG__:
        setup_logging( ) # lazy init
    return logging.getLogger( name )



#class HtmlStripper(html.HTMLParser):
#    def __init__(self):
#        self.reset()
#        self.fed = [ ] 
#    def hanlde_data( self, d ):
#        self.fed.append( d )
#        print('handle_data(): d="{}"'.format(d))
#    def get_data(self):
#        return ''.join( self.fed )

#class HTMLTextExtractor(html.HTMLParser):
#    def __init__(self):
#        html.HTMLParser.__init__(self)
#        self.result = [ ]
#
#    def handle_data(self, d):
#        self.result.append(d)
#
#    def handle_charref(self, number):
#        codepoint = int(number[1:], 16) if number[0] in (u'x', u'X') else int(number)
#        self.result.append(unichr(codepoint))
#
#    def handle_entityref(self, name):
#        codepoint = htmlentitydefs.name2codepoint[name]
#        self.result.append(unichr(codepoint))
#
#    def get_text(self):
#        return u''.join(self.result)
#
#def html_strip( html_text ):
#    h = HTMLTextExtractor( )
#    #print('html_strip: input="{}"'.format(html_text) )
#    h.feed( html_text )
#    result = h.get_text( )
#    #print('html_strip: output ="{}"'.format(result) )
#    return result

#---------------------------

def gather_stats( label, d, key_hdr='', val_hdr='' ):
    stats = { }
    stats['total'] = sum( d.values() )
    stats['cnt'] = len( d )
    # need a string representation of our key...
    stats['key_width'] = max( [ len( str(key) ) for key in d.keys() ]  )
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

def write_char_freqs( f, label, d ):
    key_hdr = 'char: .hex...'
    val_hdr = 'freq'
    stats = gather_stats( label, d, key_hdr=key_hdr, val_hdr=val_hdr )
    msg='write_char_freqs(): label={} has #{} items, key_hdr={} val_hdr={}'.format( label, len(d), key_hdr, val_hdr )
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
        val = d[key]
        percent = ( float(val) / stats['total']) * 100 # I kind of hate python2's variable handling as well.
        cum_percent += percent
        histo = '#'  * int(round(percent/2))
        if key >= ' ':
            display =  '<{}> : 0x{:04X}'.format( key, ord(key) )
        else:
            display = '--- : 0x{:04X}'.format( ord(key) )
        f.write('| {:{key_width}} | {:{val_width}} | {:6.2f}% | {:6.2f}% | {}\n'.format(
            display, val, percent, cum_percent, histo,
            key_width=stats['key_width'],
            val_width=stats['val_width'] ) )
    f.write('\n\ntotal items:    {:10,d}\n'.format( stats['total'] ) )
    f.write(    'distinct items: {:10,d}\n'.format( stats['cnt'] ) )
    f.write(    'ratio: {:6.2f}\n'.format( stats['total']/stats['cnt'] ) )

def write_values( f, label, d, descending_freq=False ):
    logger = get_logger( __name__ )
    logger.debug('write_values(): label=%s', label )
    key_hdr = label.split('-')[-1]
    val_hdr = 'freq'
    stats = gather_stats( label, d, key_hdr=key_hdr, val_hdr=val_hdr )
    stats['key_width'] = max( stats['key_width'], len(key_hdr) )
    stats['val_width'] = max( stats['val_width'], len(val_hdr) )
    msg='write_values(): label={} has #{} items, key_hdr={} val_hdr={}'.format( label, len(d), key_hdr, val_hdr )
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
        #val = d[key]
        key, val = item
        percent = (float(val) / stats['total']) * 100
        cum_percent += percent
        histo = '#'  * int(round(percent/2))
        
        f.write('| {:{key_width}} | {:{val_width}} | {:6.2f}% | {:6.2f}% | {}\n'.format(
            key, val, percent, cum_percent, histo,
            key_width=stats['key_width'],
            val_width=stats['val_width'] ) )
    f.write('\n\ntotal items:    {:10,d}\n'.format( stats['total'] ) )
    f.write(    'distinct items: {:10,d}\n'.format( stats['cnt'] ) )
    f.write(    'ratio: {:10.4f}\n'.format( stats['total']/stats['cnt'] ) )


