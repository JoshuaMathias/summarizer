import sys  # stderr
import scipy.sparse


#-----------------------------------------
# utility functions
#-----------------------------------------
def eprint(*args, **kwargs):
   print(*args, file=sys.stderr, **kwargs)

def makeIndent( depth ):
   return '|   ' * depth

def dumpArray( a, label ):
   print('\n--- {} :: shape={} type={} ---'.format( label, a.shape, type(a) ))
   if isinstance( a, scipy.sparse.csr_matrix ) \
   or isinstance( a, scipy.sparse.csc_matrix ) :
      print( a.A )  # show in normal form, vs. serialized list of number
   else:
      print(a)

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

