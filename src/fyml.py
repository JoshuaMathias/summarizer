#!/bin/python3
#--------------------------------------------------------
# fyml: Flatten  YML files to something suitable for
#--------------------------------------------------------
# sourcing in a bash script.
# Too error-prone to chase down hardwired references to D2 vs D3 everywhere.
# jgreve Sun May 13 14:19:25 PDT 2018
#--------------------------------------------------------


# To run successfully, use the command below from the home directory of this project:
# $ python3 src/summarizer.py -c config_un.yml

import local_util as u
logger = u.get_logger( __name__ ) # will call setup_logging() if necessary

import argparse
import topic_index_reader
import sum_config
import os

def flatten_yaml( d, prefix='E2JK_' ):
    for key in sorted( d.keys() ):
        ukey = key.upper()
        thing = d[key]
        #print('# prefix={}, key={}, thing={}'.format(prefix, key, thing) )
        if isinstance( thing, dict ):
            flatten_yaml( d[key], '{}{}_'.format( prefix, ukey ) )
        else:
            value = "" if thing is None else str(thing)
            print('export {}{}="{}"'.format(prefix, ukey, value) )
        

# Command Line Argument Parsing. Provides argument interpretation and help text.
version = "1.0"
prog_name ="fyml.py"
dir_path = os.path.dirname(os.path.realpath(__file__))
argparser = argparse.ArgumentParser(description='{} v. {} by team #e2jkplusplus'.format( prog_name, version ) )
argparser.add_argument('-c', '--config', metavar='CONFIG', default=os.path.join(dir_path, 'config.yml'), help='Config File(s)')
args = argparser.parse_args()

u.eprint('Hello from "{}" version {} (by team "#e2jkplusplus").'.format( prog_name, version ) )
logger.info('parsed args=%s', args)

config = sum_config.SummaryConfig(args.config)
u.eprint('config={}'.format(config))
u.eprint('config.cfg={}'.format(config.cfg))
flatten_yaml( config.cfg )
u.eprint('Done.')
