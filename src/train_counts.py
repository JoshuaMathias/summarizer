import preprocess

# Go through training set and write to file:
# 	One line for each word
#	Line: <word>	<word_count>	<docset_count>
# 	Where word_count is the total number of appearances in the training set
#	doc_count is the number of documents the word is found in
#	docset_count is the number of docsets the word is found in
def train_counts(docsets, out_file):
	word_counts = {}
	# doc_counts = {}
	docset_counts = {}
	num_docsets = 0
	preprocessor = preprocess.preprocess()
	for docset in docsets:
		num_docsets += 1
		docset_words = preprocessor.words_from_docset(docset)
		for word, count in docset_words:
			if word in docset_counts:
				docset_counts[word] += 1
				word_counts[word] += count

			else:
				docset_counts[word] = 1
				word_counts[word] = count
		break # Test on only one docset
	with open(out_file, 'w') as counts_file:
		for word in docset_counts:
			counts_file.write(word+"\t"+docset_counts[word]+"\t"+word_counts[word]+"\n")
		counts_file.write(num_docsets+" total docsets"+"\n")

# Read and return word_counts, docset_counts, num_docsets
def read_train_counts(word_counts_file):
	word_counts = {}
	docset_counts = {}
	num_docsets = 0
	# with open(out_file, 'w') as counts_file:

	return word_counts, docset_counts, num_docsets
