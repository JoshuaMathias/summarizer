# This function taks a list of documents (from class) and writes a single file to summary
import os
import sum_config
import local_util as u
import re

from nltk.tokenize import sent_tokenize

def first_sent_sum(docset, config):

    docsetTopic = docset.topic_title
    selected_content = ""
    word_count = 0

    u.eprint('docset={}'.format(docset) )
    for idx, article in enumerate(docset.docs):
        # jgreve: who knew articles can be empty?
        if len(article.body) == 0:
            u.eprint('WARNING: empty article {} (#{} docset={})'.format(article, idx, docset))
            continue

        paragraph = article.body[0]

        paragraph = re.sub("(\n|\t)", " ", paragraph)
        paragraph = re.sub("  +", " ", paragraph)
        paragraph = re.sub("^ ", "", paragraph)

        sentences = sent_tokenize(paragraph)

        first_sentence = sentences[0]
        words = first_sentence.split(" ")

        if len(words) + word_count < 100:
            selected_content += first_sentence + "\n"
            word_count += len(words)

    directory = config.DEFAULT_SUMMARY_DIR

    u.eprint('   docset.id      ="{}"'.format(docset.id)) # both appear to be the same
    u.eprint('   docset.topic_id="{}"'.format(docset.topic_id))
    #docsetID = docset.topic_id # jgreve: apparently the id and the docset_id are different.
    # The D2 reqs say we need the docset_id.
    # (in case you're wondering I think the dash part is for -A and -B for test sets.)
    # (At any rate this is what we need to do to match the rouge logic.)

    # original logic: docsetID = docset.id # jgreve: turns out the 'id' is not actually the docset_id.
    # id_part = docsetID.split("-")
    #full_file_name = id_part[0] + "-A.M.100." + id_part[1] + ".9"
    if len( docset.topic_id ) != 6:
        u.eprint('WARNING: expected 6 char topic_id instead of {} chars, topic_id="{}" for docset={})'.format( len(docset.topic_id), docset.topic_id, docset))
    part1 = docset.topic_id[0:-1] # up to but not including last char
    part2 = docset.topic_id[-1] # last char
    group_num = '9' # Because magic numbers are an anti-pattern.  jgreve
    # lets do some more sanity checks (because it would suck to try figuring out why this
    # doens't work two hours later at ROUGE eval  time (ask me how I know that)). jgreve
    if not re.search( r'[A-Z]\d\d\d\d$', part1 ):
        u.eprint('WARNING: expected exactly a single letter A-Z and four digits for topic_id.part1 instead "{}" for docset={})'.format( part1, docset))
    if not re.search( r'^[A-Z]$', part2  ):
        u.eprint('WARNING: expected exactly one uppercase letter A-Z for topic_id.part2 instead "{}" for docset={})'.format( part2, docset))
    full_file_name = part1 + "-A.M.100." + part2 + "." + group_num

    if not os.path.exists(directory):
        os.makedirs(directory)
    wout = open(directory + "/" + full_file_name, "w+")
    wout.write(selected_content)

    return selected_content
