# STARTER CODE FOR HMM FEATURE VECTORS
# ----------------------------------------------------------------
# This code creates the hmm feature vectors for the devtest
# sentences. To run, use `python3 src/hmm_vec.py -c config_un.yml`
# from the root dir. The code will print only the first vector of
# each doc set, which consists of the sentence, followed by the
# four HMM features.
# ----------------------------------------------------------------
# DESCRIPTION OF FEATURES IN FEATURE VECTORS
# paragraph position = 1(first), 2(not first or last), 3 last
# number of terms = log(number of words + 1)
# baseline term prob = log(probability(term|baseline))
# Document term prob = log(probability(term|doc))

import os
import re
import math
import argparse
import content_provider
import sum_config
import local_util as u
from nltk.tokenize import sent_tokenize, word_tokenize # for tokenizing sentences and words

def get_vecs(docset, train_wcounts, train_tally):
    doc_wcounts = {}
    doc_tally = 0

    for idx, article in enumerate(docset.docs):


        article_word_count = 0
        if len(article.body) == 0:
            u.eprint('WARNING: empty article {} (#{} docset={})'.format(article, idx, docset))
            continue

        sentence_position = 0
        for paragraph in article.body:
            raw_words = word_tokenize(paragraph)

            words = []

            for w in raw_words:
                if re.search("[a-zA-Z]", w) != None:
                    words.append(w.lower())

            for word in words:
                if word not in doc_wcounts:
                    doc_tally += 1
                    doc_wcounts[word] = 1
                else:
                    doc_wcounts[word] += 1
    print(doc_tally)

    sentence_vecs = []

    for idx, article in enumerate(docset.docs):
        sentence_position = 0
        for paragraph in article.body:
            sentences = sent_tokenize(paragraph)
            sentence_count = 0
            for sentence in sentences:
                myvec = []

                raw_words = word_tokenize(sentence)

                words = []

                for w in raw_words:
                    if re.search("[a-zA-Z]", w) != None:
                        words.append(w.lower())

                myvec.append(sentence)

                sentence_count += 1
                if sentence_count == 1:
                    myvec.append(1)
                elif sentence_count == len(sentences):
                    myvec.append(3)
                else:
                    myvec.append(2)

                base_prob = 0
                doc_prob = 0

                for word in words:
                    if word not in doc_wcounts:
                        print("MISSING", word)

                    if word in train_wcounts:
                        base_prob += math.log(train_wcounts[word]/train_tally)

                    doc_prob += math.log(doc_wcounts[word]/train_tally)

                myvec.append(math.log(len(sentence) + 1))
                myvec.append(base_prob)
                myvec.append(doc_prob)

                sentence_vecs.append(myvec)





    return sentence_vecs

if __name__ == "__main__":
    # --------------
    # TRAINING DATA
    # --------------

    train_dir = "/dropbox/17-18/573/Data/models/training/2009/"
    train_docs = os.listdir(train_dir)

    train_wcounts = {}
    train_tally = 0

    for doc in train_docs:
        text = open(train_dir + doc).read()
        raw_words = word_tokenize(text)

        words = []

        for w in raw_words:
            if re.search("[a-zA-Z]", w) != None:
                words.append(w.lower())

        for word in words:
            if word not in train_wcounts:
                train_tally += 1
                train_wcounts[word] = 1
            else:
                train_wcounts[word] += 1

    # --------------
    # /END TRAINING DATA
    # --------------

    version = "1.0"
    dir_path = os.path.dirname(os.path.realpath(__file__))
    argparser = argparse.ArgumentParser(description='summarizer.py v. '+version+' by team #e2jkplusplus')
    argparser.add_argument('-c', '--config', metavar='CONFIG', default=os.path.join(dir_path, 'config.yml'), help='Config File(s)')
    args = argparser.parse_args()

    config = sum_config.SummaryConfig(args.config)

    if config.AQUAINT:
        reader = content_provider.ContentReader(aquaint=config.AQUAINT1_DIRECTORY,
                                                aquaint2=config.AQUAINT2_DIRECTORY)

        for docset in reader.read_topic_index(config.aquaint_topic_file_path()):
            u.eprint('%s : %s' % (docset.id, docset.topic_title))
            vecs = get_vecs(docset, train_wcounts, train_tally)
            print(vecs[0])
