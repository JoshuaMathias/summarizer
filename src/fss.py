# This function taks a list of documents (from class) and writes a single file to summary
import os
from nltk.tokenize import sent_tokenize

def first_sent_sum(docset):

    # docsetID = docset[0].docID
    docsetID = "docset_5678"
    selected_content = ""
    word_count = 0

    for article in docset:
        # paragraphs = article.body
        paragraphs = article

        if word_count < 100:
            for paragraph in paragraphs:
                sentences = sent_tokenize(paragraph)

                first_sentence = sentences[0]
                words = first_sentence.split(" ")

                if len(words) + word_count < 100:
                    selected_content += first_sentence + "\n"
                    word_count += len(words)

    directory = "output/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    wout = open(directory + docsetID, "w+")
    wout.write(selected_content)

# path = 'test_data/test1.txt'
# path2 = 'test_data/test2.txt'
#
# text1 = open(path).read().split("\n\n")
# text2 = open(path).read().split("\n\n")
#
# text_set = [text1, text2]
#
# first_sent_sum(text_set)
