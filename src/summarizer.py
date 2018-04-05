#!/bin/python3
import sys


print('Hello from "summarizer.py" version 0.0 (by team "#e2jkplusplus").')

nchars = 140 # tweet-size
for file_name in sys.argv[1:]:
    with open( file_name, 'r') as f:
        length = 0
        print('--- begin summary: "{}" ---'.format(file_name) )
        for line in f:
            line = line.strip()
            remaining = nchars - length
            if remaining < 1:
                break
            print( line[0:remaining] )
            length += len(line)
            
        print('--- end summary: "{}" ---'.format(file_name) )
        print('Done.')
