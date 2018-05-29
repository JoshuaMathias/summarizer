import preprocess

# Go through training set and write to file:
# 	One line for each word
#	Line: <word>	<word_count>	<docset_count>
# 	Where word_count is the total number of appearances in the training set
#	doc_count is the number of documents the word is found in
#	docset_count is the number of docsets the word is found in
def train_counts(docsets, out_file=None):
	word_counts = {}
	# doc_counts = {}
	num_docsets = 0
	preprocessor = preprocess.preprocess()
	for docset in docsets:
		num_docsets += 1
		docset_words = preprocessor.words_from_docset(docset)
		for word, count in docset_words.items():
			if word in word_counts:
				word_stats = word_counts[word]
				word_stats[0] += 1 # docset count
				word_stats[1] += count # word count

			else:
				word_stats = []
				word_stats.append(1)
				word_stats.append(count)
				word_counts[word] = word_stats

	if out_file is not None:
		with open(out_file, 'w') as counts_file:

			for word in word_counts:
				word_stats = word_counts[word]
				counts_file.write(str(word)+"\t"+str(word_stats[0])+"\t"+str(word_stats[1])+"\n")
			counts_file.write(str(num_docsets)+" total docsets"+"\n")
	return word_counts, num_docsets

# Read and return word_counts, docset_counts, num_docsets
def read_train_counts(word_counts_file):
	word_counts = {}
	num_docsets = 0
	with open(word_counts_file, 'r') as counts_file:
		for line in counts_file:
			line = line.strip()
			split_line = line.split()
			if len(split_line) > 2:
				if not split_line[-1] == "docsets":
					word_counts[split_line[0]] = (int(split_line[1]), int(split_line[2]))
				else:
					num_docsets = int(split_line[0])
	return word_counts, num_docsets
