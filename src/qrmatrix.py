# This function taks a list of documents (from class) and writes a single file to summary
import local_util as u
logger = u.get_logger( __name__ ) #  https://docs.python.org/3/howto/logging.html

import os
import sum_config
import re # for removing multiple \s characters and source formatting
import math # for exp for weighting function
from operator import itemgetter

from nltk.tokenize import sent_tokenize, word_tokenize # for tokenizing sentences and words

from scipy import spatial

def get_tfidf(tally, ac, dc):
    return tally * (math.log(ac / (1 + dc)))

def qr_sum(docset, config):

    word_count = 0
    fname='qr_sum' # for labeling log statments.

    all_sentences = [] # contains lists with
    # SENTENCE LIST
    # 0 sentenc
    # 1 sentence vec
    # 2 sentece matrix vect
    # 3 position in article
    # 4 article index in article_length
    # 5 sentence score
    # 6 cosine sim score

    words_dict = {} # {word, index}
    words_vec = [] # [word]
    words_tally = {}
    words_docs = {} # key=word value=list of article names in which word appears

    article_length = [] # num_words

    # TODO: Define method of refusing fragment sentences
    short = 100 # temporary solution to fragment sentences making it into summary

    # TODO: make dictionary of stop words
    stops = open("src/stop_words")
    stop_lines = stops.read().split("\n")

    stop_words = {}

    for line in stop_lines:
        line = line.lower()
        if line not in stop_words:
            stop_words[line] = 0

    article_count = 0
    logger.info('%s: docset=%s', fname, docset )
    for idx, article in enumerate(docset.articles):
        article_count += 1

        article_word_count = 0
        # TODO: GET ARTICLE ID INFORMATION AND STORE IT FOR LATER USE

        # jgreve: who knew articles can be empty?
        if len(article.paragraphs) == 0:
            logger.warning('empty %s in docset#%s=%s)', article, idx, docset)
            continue

        sentence_position = 0
        for paragraph in article.paragraphs:

            # jgreve: should this logic logic go into the article_content.Article(),
            # or whatever populates Articels ?
            paragraph = re.sub("(\n|\t)", " ", paragraph)
            paragraph = re.sub("  +", " ", paragraph)
            paragraph = re.sub("^ ", "", paragraph)

            sentences = sent_tokenize(paragraph)

            for sentence in sentences:
                raw_words = word_tokenize(sentence)
                norm_words = []
                words = []

                for w in raw_words:
                    if re.search("[a-zA-Z]", w) != None:
                        norm_words.append(w.lower())
                    # words.append(w)

                for w in norm_words:
                    if w not in stop_words:
                        words.append(w)

                article_word_count += len(words)

                sentence_position += 1
                # print(sentence_position)

                first_char = False
                last_char = False

                if sentence[0].lower() != sentence[0]:
                    first_char = True

                if sentence[-1] == ".":
                    last_char = True

                if len(words) > 6 and first_char == True and last_char == True: #arbitrary length of fragments
                    all_sentences.append([sentence, norm_words, [None], sentence_position, len(article_length), 0])
                    if len(words) < short:
                        short = len(words)

                for word in norm_words:
                    if word not in words_dict:
                        words_dict[word] = len(words_vec)
                        words_tally[word] = 1
                        words_vec.append(word)

                        words_docs[word] = [article.id]
                    else:
                        words_tally[word] += 1

                        temp_article_id = words_docs[word]

                        if article.id not in temp_article_id:
                            temp_article_id.append(article.id)

                        words_docs[word] = temp_article_id


        article_length.append(article_word_count)

# CREATE FEATURE VECTORS
    for sentence in all_sentences:
        # print("\n\n", sentence[0], "\n", sentence[3], sentence[4])

        feat_vec = [0 for i in range(len(words_vec)) ]

        for word in sentence[1]:
            if word in words_dict:
                # tfidf = get_tfidf(words_tally[word], article_count, len(words_docs[word]))
                # feat_vec[words_dict[word]] = tfidf
                feat_vec[words_dict[word]] = words_tally[word]

        # print(sum(feat_vec))

        sentence[2] = feat_vec

# QR MATRIX
    selected_content = [] # list of sentences selected for

    # while 100 words not used up and shortest sentence isn't too long
    while word_count < 100 and word_count + short < 100:
        for sentence in all_sentences:

            # TODO: implement computation for t and g values from CLASSY [2001]
            # t and g currently based on hardwired values from CLASSY [2001] article
            t = 3
            g = 10

            score = 0
            if article_length[sentence[4]] == 0:
                print("ZERO SCORE:", sentence[0])
            else:
                nonzeros = sum(sentence[2])
                score = nonzeros * (g * math.exp(-8*(sentence[3]/article_length[sentence[4]]) + t))
                # print(score)
                sentence[5] = score
                # print(sentence[0], sentence[5])

        ranked = sorted(all_sentences, key=itemgetter(5), reverse=True)

        remove_words = []
        added = False
        while added == False:
            for x in ranked:
                if len(x[1]) + word_count < 100:
                    logger.debug( 'len(x[1])=%d, word_cnt=%s, x[0]=%s, x[1]=%s', len(x[1]), word_count, x[0], x[1])
                    selected_content.append(x)
                    word_count += len(x[1])
                    added = True
                    remove_words = x[1]
                    break
            if added == False:
                word_count = 101
                break

        # u.eprint(ranked[0][0], word_count)
        logger.debug('ranked[0][0]=%s, word_count=%d', ranked[0][0], word_count )

        r_index = []
        for item in remove_words:
            r_index.append(words_dict[item])
            # print(item, words_dict[item])

        for sentence in all_sentences:
            for ind in r_index:
                sentence[2][ind] = 0

    ordered_sum = sorted(selected_content, key= itemgetter(3))

    summary = ""
    for s in ordered_sum:
        summary += s[0] + "\n"


# WRITE SUMMARY TO FILE
    #directory = config.DEFAULT_SUMMARY_DIR
    directory = config.OUTPUT_SUMMARY_DIRECTORY # jgreve: confg.yml files dont set the defaults. 

    # u.eprint('   docset.id      ="{}"'.format(docset.id)) # both appear to be the same
    # u.eprint('   docset.topic_id="{}"'.format(docset.topic_id))
    #docsetID = docset.topic_id # jgreve: apparently the id and the docset_id are different.
    # The D2 reqs say we need the docset_id.
    # (in case you're wondering I think the dash part is for -A and -B for test sets.)
    # (At any rate this is what we need to do to match the rouge logic.)

    # original logic: docsetID = docset.id # jgreve: turns out the 'id' is not actually the docset_id.
    # id_part = docsetID.split("-")
    #full_file_name = id_part[0] + "-A.M.100." + id_part[1] + ".9"
    if len( docset.topic_id ) != 6:
        logger.warning( 'expected 6 char topic_id instead of %d, docset=%s',  len(docset.topic_id), docset )
    part1 = docset.topic_id[0:-1] # up to but not including last char
    part2 = docset.topic_id[-1] # last char
    group_num = '9' # Because magic numbers are an anti-pattern.  jgreve
    # lets do some more sanity checks (because it would suck to try figuring out why this
    # doens't work two hours later at ROUGE eval  time (ask me how I know that)). jgreve
    if not re.search( r'[A-Z]\d\d\d\d$', part1 ):
        logger.warning('expected exactly a single letter A-Z and four digits for topic_id.part1 instead "%s" for docset=%',  part1, docset)
    if not re.search( r'^[A-Z]$', part2  ):
        logger.warning('expected exactly one uppercase letter A-Z for topic_id.part2 instead "%s" for docset=%s'.format( part2, docset))
    full_file_name = part1 + "-A.M.100." + part2 + "." + group_num

    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info('%s: making directory "%s"', fname, directory )
    filename = directory + "/" + full_file_name
    logger.info('%s: writing summary for %s to file="%s"', fname, docset, filename )
    with open(filename, "w+") as wout:
        wout.write(summary)

    return summary
