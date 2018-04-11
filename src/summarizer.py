#!/bin/python3
import sys
import argparse
import content_provider


class Summarizer():
    def __init__(self, nchars):
        self.nchars = nchars

    def summarize(self, article):
        summary = '--- begin summary: "{}" ---\n'.format(article.id)
        length = 0
        for para in article.body:
            line = para.strip()
            remaining = self.nchars - length
            if remaining < 1:
                break
            summary += line[0:remaining] + '\n'
            length += len(line)

        summary += '--- end summary: "{}" ---\n'.format(article.id)
        return summary

if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    argparser = argparse.ArgumentParser(description = 'summarizer.py v. 0.0 by team #e2jkplusplus')
    argparser.add_argument('filename', metavar='FILE', nargs='+', help='Story File(s)')
    args = argparser.parse_args()

    print('Hello from "summarizer.py" version 0.0 (by team "#e2jkplusplus").')

    nchars = 140 # tweet-size
    smry = Summarizer(nchars)

    articles = content_provider.ContentReader().read_raw_files(args.filename)

    for article in articles:
        print(smry.summarize(article))
    print('Done.')