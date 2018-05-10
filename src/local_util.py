import sys  # stderr
#import scipy.sparse  # jgreve: seems we're not using this, re-enable if dumpArray() helpful.

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
