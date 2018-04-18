# Using this script requires sumy package
# To install, use: pip install sumy
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.kl import KLSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

LANGUAGE = "english"
SENTENCES_COUNT = "5"


if __name__ == "__main__":
    directory = "~/dropbox/17-18/573/AQUAINT/nyt/2000/"

    # TODO: Get list of files and loop each file

    filename = "20000101_NYT"

    process_file = "doc.txt" # directory + filename

    url = "file://home/unclenacho/school/573/src/doc.txt"
    parser = HtmlParser.from_file(process_file, None, Tokenizer(LANGUAGE))

    # parser = PlaintextParser.from_file(process_file, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        print(sentence)
