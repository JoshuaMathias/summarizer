# qrmatrix.py.d3b, attempt to recreate qrmatrix.py.d3err
# qrmatrix.py.d3_orig, ROUGE-1, 0.22264, 0.25731, 0.23795  
# this is the official D3 version.
# This function taks a list of documents (from class) and writes a single file to summary
import local_util as u
logger = u.get_logger( __name__ ) #  https://docs.python.org/3/howto/logging.html

import os
import sum_config
import re # for removing multiple \s characters and source formatting
import math # for exp for weighting function
from operator import itemgetter
import sys

import preprocess
from nltk.tokenize import sent_tokenize, word_tokenize # for tokenizing sentences and words

from scipy import spatial

# tally: # times word appears in document
# ac: number of articles (total article count)
# dc: number of documents the word appears in
def get_tfidf(tally, ac, dc):
    return tally * (math.log(ac / (1 + dc)))

# tf * document frequency
# Muliply by -1 so that it's a positive number (dc is always less than ac+1)
def get_tfdf(tally, ac, dc, lowest_df):
    return tally * (1+(math.log(dc / (1 + ac)) - lowest_df)) # Subtract lowest df to normalize and get a positive number (higher is better). Add 1 so we never get 0.

# Document frequency from FastSum paper
def get_doc_freq(ac, dc):
    return dc / ac



#----------------------------------------------
# Stop Word variations, Rouge-1 recall:
#        | Tokenize.Yes | Tokenize.No |
#--------+--------------+-------------+
# QR.Yes | 0.24838      |  0.22264    |
# QR.No  | -na-         |  0.24428    |
#----------------------------------------------
# QR.Yes/No indicates, respectively, whether the QRMatrix blocked or included stopwords.
# Tokenize.Yes/No indicates, repsectively, whether the stop wrods were tokenized with NLTK.
# Note that the sentences are always processd with NLTK tokenization.
# In D3 the effect was QR.No and Tokenize.No




def qr_sum(docset, config, trained_word_counts, num_trained_docsets):
    global STOP_TOKENIZE        # jgreve: these flags are additions to the original D3 logic, note that
    global STOP_QRFLAG          # the local stop_words variable (used below) is left as-is.
    global STOP_DEBUG_CUTOFF
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
    # 6 int for chronological ordering yyyymmddppp

    words_dict = {} # {word, index}
    words_vec = [] # [word]
    words_tally = {}
    words_docs = {} # key=word value=list of article names in which word appears

    article_length = [] # num_words

    # TODO: Define method of refusing fragment sentences
    short = 100 # temporary solution to fragment sentences making it into summary

    preprocessor = preprocess.preprocess()
    STOP_TOKENIZE = preprocessor.STOP_TOKENIZE       # jgreve: these flags are additions to the original D3 logic, note that
    STOP_QRFLAG = preprocessor.STOP_QRFLAG          # the local stop_words variable (used below) is left as-is.
    STOP_DEBUG_CUTOFF = preprocessor.STOP_DEBUG_CUTOFF

    article_count = 0
    logger.info('%s: docset=%s', fname, docset )
    for idx, article in enumerate(docset.articles):
        article_count += 1

        article_word_count = 0
        # TODO: GET ARTICLE ID INFORMATION AND STORE IT FOR LATER USE

        # ORDERING
        # -----------------------------------------
        # Extract date from article id
        title = article.id
        date = "x"
        # print(title)
        if len(title) < 17:
            date = title[3:11]
        else:
            date = title[8:16]
        # -----------------------------------------

        # print(date)

        # jgreve: who knew articles can be empty?
        if len(article.paragraphs) == 0:
            logger.warning('empty %s in docset#%s=%s)', article, idx, docset)
            continue

        sentence_position = 0
        for paragraph in article.paragraphs:
            sentences = preprocessor.preprocess_sents(paragraph)

            for sentence in sentences:
                words, norm_words = preprocessor.preprocess_words(sentence)

                article_word_count += len(words)

                # ORDERING
                # -----------------------------------------
                sentence_position += 1
                # print(sentence_position)
                position = str(sentence_position)
                # Make sentence position a 3-digit number
                if len(position) == 1:
                    position = "0" + position
                if len(position) == 2:
                    position = "0" + position
                # Combine date and position for super int yyyymmddppp
                priority_str = date + position
                priority = int(priority_str)
                # -----------------------------------------

                # Checks for first char cap and last char .
                first_char = False
                last_char = False

                if sentence[0].lower() != sentence[0]:
                    first_char = True

                if sentence[-1] == "." or sentence[-1] == "?" or sentence[-1] == "!":
                    last_char = True

                if len(words) > 6 and first_char == True and last_char == True: #arbitrary length of fragments
                    all_sentences.append([sentence, norm_words, [None], sentence_position, len(article_length), 0, priority])
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

    if len(words_docs) > 0:
        lowest_word_docs = float("inf")
        for word_docs in words_docs:
            if len(word_docs) < lowest_word_docs:
                lowest_word_docs = len(word_docs)

# CREATE FEATURE VECTORS
    # highest_word_count = 0
    # for _, trained_word_stats in trained_word_counts.items():
    #     if highest_word_count < trained_word_stats[0]:
    #         highest_word_count = trained_word_stats[0]
    # lowest_df = math.log(lowest_word_docs) / (1 + (article_count / num_trained_docsets)) # Used to normalize (and make positive) the value of tfdf for each word
    lowest_df = math.log(lowest_word_docs) / (1 + (article_count)) # Used to normalize (and make positive) the value of tfdf for each word
    for sentence in all_sentences:
        # print("\n\n", sentence[0], "\n", sentence[3], sentence[4])

        feat_vec = [0 for i in range(len(words_vec)) ]

        for word in sentence[1]:
            if word in words_dict:
                # word_val = words_tally[word]
                # trained_word_count = 1
                # trained_docset_count = 1
                # if num_trained_docsets > 0:
                #     if word in trained_word_counts:
                #         word_stats = trained_word_counts[word]
                #         trained_word_count = word_stats[0]
                #         trained_docset_count = word_stats[1]
                word_val = get_tfdf(words_tally[word], article_count, len(words_docs[word]), lowest_df)
                # word_val = get_tfidf(words_tally[word], num_trained_docsets, trained_docset_count)
                # word_val = get_doc_freq(article_count, len(words_docs[word]))
                # word_val *= words_tally[word]
                feat_vec[words_dict[word]] = word_val

        # print(sum(feat_vec))

        sentence[2] = feat_vec

# QR MATRIX
    selected_content = [] # list of sentences selected for

    # while 100 words not used up and shortest sentence isn't too long
    while word_count <= 100 and word_count + short <= 100:
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
                #if len(x[1]) + word_count < 150:
                #if len(x[1]) + word_count < 100:
                #---------------------------
                # jgreve: Seems word count limit should be based on
                # number of non-tokenized words in derived our output sentence.
                # For example, 2nd best-ranked sentence from
                # DocSet( id:D1001A-A "Columbine Massacre" 20):
                #    x[0]="...suspects in Tuesday's massacre.",
                #    x[1]=[..., 'suspects', 'tuesday', 'massacre']
                # Tokenized x[0] will have more words.
                # Seems like an x[0].split() would get us back on track.
                x_word_count = len( x[0].split() ) # word count for x, metric will likely change.
                if x_word_count + word_count < 100:
                    logger.debug( ':KEEP: x_word_cnt=%d, len(x[1])=%d, word_cnt=%s, x[0]=%s, x[1]=%s', x_word_count, len(x[1]), word_count, x[0], x[1])
                    selected_content.append(x)
                    #word_count += len(x[1])
                    word_count += x_word_count
                    added = True
                    remove_words = x[1]
                    break
                else:
                    logger.debug( ':skip: x_word_cnt=%d, len(x[1])=%d, word_cnt=%s, x[0]=%s, x[1]=%s', x_word_count, len(x[1]), word_count, x[0], x[1])
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

    ordered_sum = sorted(selected_content, key= itemgetter(6)) # Sorts selected sentences by date/position

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
