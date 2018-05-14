#!/bin/python3

# rouge_tableize.py
# ------------------------------------------------------------------------
# Convert the perl-style rougue score results into a tableized form.
# Writes formatted data to stdout, status messages to stderr.
# note: If a table cell value is missing it will write '?'
# example usage:
#        $ src/rouge_tableize.py results/D2_rouge_scores.out.QRM > run.dat
# ------------------------------------------------------------------------
# jgreve  Mon Apr 23 18:47:31 PDT 2018
# ------------------------------------------------------------------------
# jgreve  Mon added logging.

import local_util as u
logger = u.get_logger( __name__ ) # will call setup_logging() if necessary

import sys
import re
import collections
import time

DELIM=',' # '\t' # something to make excel happy.

def verify_prefix_value( prefix, raw ):
    logger.debug( 'verify_prefix_value( prefix=%s, raw=%s)', prefix, raw )
    if( not raw.startswith( prefix ) ):
        raise ValueError('Expected prefix="{}" not found at beginning of raw="{}"'.format(prefix,raw))
    # Given prefix='FOO:' and raw='FOO:3.14159' answer the float.
    # offset=0123456789+
    #    raw=FOO:3.4159
    # len(prefix)=4, so raw[ 4: ] is everything from the
    # 4th char to end of string.
    return float( raw[ len(prefix) : ] )


def add_table_cell( table,  row_label, col_label, value, pref_cols = None ):
    if row_label not in table:
        table[row_label] = dict( )
    row = table[row_label]
    pref_label = col_label
    if pref_cols is not None:
        if col_label in pref_cols:
            pref_label = pref_cols.get( col_label )
            logger.debug('row_label=%s col_label=%s value=%s: preferred col label="%s"', row_label, col_label, value, pref_label  )
        else:
            logger.debug('row_label=%s col_label=%s value=%s: no preferred col label found', row_label, col_label, value )
    if pref_label in row:
        desc = col_label
        if pref_label != col_label:
            col_desc += '(preferred="{}"'.format(pref_label)
        logger.error('Collision on row=%s col=%s, old_value=%s, new_value=%s ?  (Will use new value.)', row_label, col_desc, row[pref_label], value )
    row[pref_label] = value

def write_table( title, table ):
    print('\n--- {} ---'.format(title) )
    row_labels = sorted( table.keys() )
    col_labels = set( )
    preferred_col_headers = table.get( '*col_pref*', dict( ) )
    for row_label in row_labels:
        # merge col-labels for this row with overall col_labels.
        row = table[row_label]
        col_labels |= set( row.keys() )
    col_labels = sorted( col_labels )
    # Start with headers...
    print('{}{}'.format( DELIM, title ), end='' )
    for col_label in col_labels:
        print('{}{}'.format( DELIM, col_label ), end='' )
    print('') # end the header line.
    for row_label in row_labels:
        if row_label.startswith('*'):
            continue # skip keys starting with '*' (like '*col_pref*')
        print('{}{}'.format( DELIM, row_label), end='' )
        row = table[ row_label ]
        for col_label in col_labels:
            print('{}{}'.format( DELIM, row.get(col_label, '?') ), end='' )
        print('') # end the detail line.
    print('----------------')

line_cnt = 0
prog_name = sys.argv[0]
in_filename = sys.argv[1]
# key='*' is a hack for column name rewrites.
# add_table_cell will check to see if it should use the
# more sort-friendly values, otherwise will col-label used as-is.
# Typically you need to run it once and see what your col lables
# turn out to be then come back and put these it.
avg_col_prefs = { 'Average_R:' : 'a.ROUGE', 
                  'Average_P:' : 'b.PREC', 
                  'Average_F:' : 'c.F-SCORE', 
}


#----------------------------------------------------------

avg_table = dict( )
detail_tables = collections.defaultdict( dict ) # dictionary of table dicts, one for each rouge number.
timestamp = time.strftime("%Y-%m-%d %0H:%0M:%0S", time.localtime())
u.eprint('Hello from {}'.format(prog_name))
print('Generating tablized rouge results from')
logger.info('\n\n----- begin $s -----', prog_name )
print('input file: "{}"'.format(in_filename) )
print('local time: {} '.format(timestamp) )
print()
print( "note: printing 'average' lines for table validation")
print()
with open( in_filename, 'r' ) as in_file:
    for line in in_file:
        line_cnt += 1
        line = line.strip()
        fields = line.split()
        if len(fields) <= 1:
            logger.error('%04d: skipping line w/no fields = "%s"', line_cnt, line)
            continue # skip empty lines
        logger.debug('%04d: "%s"', line_cnt, line)
        if re.search( r' ROUGE-\d Average_', line ):
            # example: "9 ROUGE-1 Average_R: 0.21842 (95%-conf.int. 0.19702 - 0.23755)"
            print('{:04d}: avg_line: "{}"'.format(line_cnt, line))
            group_id, rouge_n, label, value, _, low, _, high = fields
            add_table_cell( table=avg_table,  row_label=rouge_n, col_label=label, value=value, pref_cols=avg_col_prefs )
            continue
        logger.debug('fields=%s', str(fields) )
        group_id, rouge_n, label, docset, rval, pval, fval = fields
        logger.debug('   group_id=%s rouge_n=%s label=%s docset=%s (r,p,f)=( %s, %s, %s )' \
            .format( group_id, rouge_n, label, docset, rval, pval, fval ) )
        rval = verify_prefix_value( 'R:', rval )
        pval = verify_prefix_value( 'P:', pval )
        fval = verify_prefix_value( 'F:', fval )
        add_table_cell( table=detail_tables[rouge_n], row_label=docset, col_label='a.ROUGE', value=rval )
        add_table_cell( table=detail_tables[rouge_n], row_label=docset, col_label='b.PREC', value=pval )
        add_table_cell( table=detail_tables[rouge_n], row_label=docset, col_label='c.F-SCORE', value=fval )

u.eprint('{}: Loaded {} lines from file="{}"'.format( prog_name, line_cnt, in_filename ) )

write_table( 'Averages', avg_table )
logger.debug('avg_table=%s', avg_table )
for key in sorted( detail_tables.keys() ):
    write_table( key, detail_tables[key] )
u.eprint('{}: Done.'.format( prog_name ))
