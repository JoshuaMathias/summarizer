#!/bin/python3
import sys
import argparse


class Summarizer():
    def __init__(self, nchars):
        self.nchars = nchars

    def summarize(self, filename):
        summary = '--- begin summary: "{}" ---\n'.format(filename)
        with open(filename, 'r') as f:
            length = 0
            for line in f:
                line = line.strip()
                remaining = self.nchars - length
                if remaining < 1:
                    break
                summary += line[0:remaining] + '\n'
                length += len(line)

        summary += '--- end summary: "{}" ---\nDone.\n'.format(filename)
        return summary

if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    argparser = argparse.ArgumentParser(description = 'summarizer.py v. 0.0 by team #e2jkplusplus')
    argparser.add_argument('filename', metavar='FILE', nargs='+', help='Story File(s)')
    args = argparser.parse_args()

    print('Hello from "summarizer.py" version 0.0 (by team "#e2jkplusplus").')

    nchars = 140 # tweet-size
    smry = Summarizer(nchars)

    for file_name in args.filename:
        print(smry.summarize(file_name))

