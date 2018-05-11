import os
import re
from nltk import sent_tokenize, word_tokenize

import argparse
import topic_index_reader
import sum_config
import local_util as u

summaries_dir = "/dropbox/17-18/573/Data/models/training/2009"
docsets_file = "/dropbox/17-18/573/Data/Documents/training/2009/UpdateSumm09_test_topics.xml"

sum_files = os.listdir(summaries_dir)
sum_files = sorted(sum_files)

gold_sum_names = {}

for file in sum_files:

    text = open(summaries_dir + "/" + file, "r").read()
    sents = sent_tokenize(text)

    # for sent in sents:
    #     print(sent)
    # print("\n======================\n")

    # Get all files names to match source docs

    first_split = file.split(".")
    call = first_split[0].split("-")
    first_letter = first_split[3]
    new_name = call[0] + first_letter + "-" + call[1]
    # D0944H-A
    # D0944-A.M.100.H.H

    print(new_name)

    new_sent_vec = []

    count = 1
    for s in sents:
        new_sent_vec = [s, count, 0]

    if new_name not in gold_sum_names:
        seq_sents = []

        for x in new_sent_vec:
            seq_sents.append(x)

        gold_sum_names[new_name] = [new_sent_vec]
    else:
        temp_list = []
        # print(new_name)
        # print(gold_sum_names[new_name])
        for l in gold_sum_names[new_name]:
            # print(l)
            temp_list.append(l)
        temp_list.append(new_sent_vec)
        # print(temp_list)
        gold_sum_names[new_name] = temp_list




version = "1.0"
dir_path = os.path.dirname(os.path.realpath(__file__))
argparser = argparse.ArgumentParser(description='summarizer.py v. '+version+' by team #e2jkplusplus')
argparser.add_argument('-c', '--config', metavar='CONFIG', default=os.path.join(dir_path, 'config.yml'), help='Config File(s)')
args = argparser.parse_args()

config = sum_config.SummaryConfig(args.config)

wout = open("stupid.txt", "w+")


if config.AQUAINT:
    index_reader = topic_index_reader.TopicIndexReader(docsets_file,
                                                       aquaint1 = config.AQUAINT1_DIRECTORY,
                                                       aquaint2 = config.AQUAINT2_DIRECTORY,
                                                       dbname = 'shelve_train_db')

    u.eprint('config.topic_file_path()="{}"'.format(config.aquaint_topic_file_path()))
    topic_index = index_reader.read_topic_index_file(docset_type = 'docseta')

    for docset in topic_index.documentSets(docset_type='docseta'):
        u.eprint('\n============\n%s : %s' % (docset.id, docset.topic_title))
        print(docset.id)
        if docset.id in gold_sum_names:
            print("success")
            article_sentences = []
            print(len(docset.articles))
            for idx, article in enumerate(docset.articles):

                article_word_count = 0
                # TODO: GET ARTICLE ID INFORMATION AND STORE IT FOR LATER USE

                # jgreve: who knew articles can be empty?
                if len(article.paragraphs) == 0:
                    u.eprint('WARNING: empty article {} (#{} docset={})'.format(article, idx, docset))
                    continue

                sentence_position = 0

                # print(article.paragraphs[0])

                for paragraph in article.paragraphs:

                    paragraph = paragraph.replace('\\n', " ")
                    paragraph = paragraph.replace('\\t', " ")
                    paragraph = paragraph.replace('\\\'', " ")
                    paragraph = paragraph.replace('\\\"', " ")

                    paragraph = re.sub("^b[\"|\']", "", paragraph)
                    paragraph = re.sub("  +", " ", paragraph)
                    paragraph = re.sub(" \'$", "\'", paragraph)
                    paragraph = re.sub(" \"$", "\"", paragraph)
                    paragraph = re.sub("^ ", "", paragraph)
                    # print(paragraph)

                    sents = sent_tokenize(paragraph)
                    for sent in sents:
                        article_sentences.append(sent)

            gold_sents = gold_sum_names[docset.id]

            # print("GOLD:", gold_sents)
            print("second Succ")

            if docset.id == "D0944H-A":
                count = 0
                print("LAST SUCC")
                print("SENTS", article_sentences[0])
                for line in article_sentences:
                    count += 1

                    print("\n=======\n" +line + "\n\n" + gold_sents[2][0])
                    wout.write(line + "\n")

                    # for g in gold_sents:
                    #     print("\n=======\n" +line + "\n\n" + g[0])
                    #     if line == g:
                    #         g[2] = count


            # for r in gold_sents:
            #     # print("R:", r)
            #     if r[2] == 0:
            #         print(docset.id, r)






        else:
            print("\n=================\nDID NOT GO\n=================\n")



# JOHN CODE BELOW
# N = 3 # number of Summary-states in HMM
#  # HMM transition counts are better
#  # as a 2D array, e.g. #STATES x #STATES.  Dict keys for now to make the
#  # connection between G1->G2 and the corresponding HMM state clear.
#  SUCCESSFUL_OBSERVATIONS = {
#     # only count if we observe G1->G2 or G2->G3 etc.
#     "STATE_2_Yes --> STATE_4_Yes" : 0, # G1->G2, j=1: 2j->2(j+1) to use the gaper's terms
#     "STATE_4_Yes --> STATE_6_Yes" : 0, # G2->G3, for j=2: 2j->2(j+1)
#     "STATE_6_Yes --> STATE_8_Yes" : 0  # Is there a G3->G4 ?
#  }
#  TOTAL_OBSERVATIONS = {
#     # count total trials, like a coin toss: H=G1->G2, T=not G1->G2.  Above just counts "heads", here we count total trials.
#     "STATE_2_Yes --> STATE_4_Yes" : 0, # G1->G2 ?
#     "STATE_4_Yes --> STATE_6_Yes" : 0, # G2->G3
#     "STATE_6_Yes --> STATE_8_Yes" : 0  # Hmm... is there a G3->G4 ?
#  }
#  for RAW in all DOC_SETS:
#      GOLD_SUMMARIES = load_summaries_for_docset( RAW )
#      for g in range( 0, N ):
#          j = g+1 # Paper uses one-based indices, keep zero vs one-based clear.
#          key = 'STATE_{}_Yes --> STATE_{}_Yes'.format( 2*j, 2*(j+1) )
#          # e.g. for j=1 : "STATE_2_Yes --> STATE_4_Yes"
#          for GOLD in GOLD_SUMMARIES: # really just 4 summaries for each docset...
#              TOTAL_OBSERVATIONS[ key ] += 1
#              r = find_index_of_sentence( RAW, GOLD[g] )
#              if r < 0:
#                  raise ValueError( 'GOLD sentence not in RAW={}? GOLD[{}]="{}"'.format(RAW,g,GOLD[g] ) ).
#              assert GOLD[g] == RAW[r] # safety check.
#                  SUCCESSFUL_OBSERVATIONS[ key ] += 1
#  # Now that we've checked all G1->G2 observations across all GOLD docs
#  # (the human-generated training summaries):
#  HMM_PROBS = dict( )
#  for key in TOTAL_OBSERVATIONS :
#      HMM_PROBS[key] = SUCCESSFUL_OBSERVATIONS[key] / TOTAL_OBSERVATIONS[key]
