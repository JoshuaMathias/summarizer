# This function taks a list of documents (from class) and writes a single file to summary
import os
import sum_config

from nltk.tokenize import sent_tokenize

def first_sent_sum(docset, config):

    docsetID = docset.id
    docsetTopic = docset.topic_title
    selected_content = ""
    word_count = 0

    for article in docset.docs:
        paragraph = article.body[0]

        sentences = sent_tokenize(paragraph)

        first_sentence = sentences[0]
        words = first_sentence.split(" ")

        if len(words) + word_count < 100:
            selected_content += first_sentence
            word_count += len(words)

    directory = config.DEFAULT_SUMMARY_DIR

    id_part = docsetID.split("-")

    full_file_name = id_part[0] + "-A.M.100." + id_part[1] + ".9"
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    wout = open(directory + "/" + full_file_name, "w+")
    wout.write(selected_content)

    return selected_content
