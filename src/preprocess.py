from nltk.tokenize import sent_tokenize, word_tokenize # for tokenizing sentences and words
import re # for removing multiple \s characters and source formatting
import local_util as u
logger = u.get_logger( __name__ ) #  https://docs.python.org/3/howto/logging.html


class preprocess:
	def __init__(self):
		self.STOP_WORDS        = None
		self.STOP_TOKENIZE     = True # +D3.err, original loop above: no change, still R1.R=0.22264.
		self.STOP_QRFLAG       = True # Whether or not to apply stopwords to qrmatrix population.
		self.STOP_DEBUG_CUTOFF = 50 # Only dump the first 50 stop_word hits.
		self.stop_words = self.get_stop_words()
		self.stop_file = "src/stop_words"

	def get_stop_words(self):

	    if self.STOP_WORDS:
	        return self.STOP_WORDS # recycle what we already have.
	    # If we reach this point, STOP_WORDS is None so we need to load it.
	    self.STOP_WORDS = dict( ) # start a new dictionary,
	    self.stop_words = self.STOP_WORDS # jgreve: aliasing original var name (lower case stop_wrods)
	    # so I don't edit the actual logic.
	   
	    self.stop_file = "src/stop_words"
	    logger.info('get_stop_words(): loading stop_words from %s', self.stop_file )
	    stops = open(self.stop_file)
	    stop_lines = stops.read().split("\n")

	    #for line in stop_lines:
	    #    line = line.lower()
	    #    if line not in stop_words:
	    #        stop_words[line] = 0

	    logger.info('get_stop_words(): loading stop_words from %s', self.stop_file )
	    stop_line_cnt = 0
	    for line in stop_lines:
	        stop_line_cnt += 1
	        line = line.lower().strip()
	        if self.STOP_TOKENIZE:
	            words = word_tokenize( line )
	            # logger.debug('stop_words[{:03d}]: line="{}" --> words={}'.format(stop_line_cnt, line, words ))
	            for word in words:
	                self.stop_words[word] = 0
	        else:
	            # original D3 code.
	            if line not in self.stop_words:
	                self.stop_words[line] = 0
	    msg = 'get_stop_words(): loaded #stop_words=%d, #lines=%d, STOP_TOKENIZE=%s STOP_QRFLAG=%s' % ( len(self.stop_words), stop_line_cnt, str(self.STOP_TOKENIZE), str(self.STOP_QRFLAG)  )
	    logger.info( msg )
	    u.eprint(msg)
	    return self.STOP_WORDS # important: this *must* still point to the same thing stop_words does.

	# Return list of tokenized words from sentence
	def preprocess_words(self, sentence):
	    raw_words = word_tokenize(sentence)
	    norm_words = []
	    words = []
	#-----------------------------------------------------------------------------

	    # before D3.err (d3_orig) yields R1.R = 0.22264
	    if not self.STOP_QRFLAG:
	        # Original D3 code, here for human traceability
	        for w in raw_words:
	            if re.search("[a-zA-Z]", w) != None:
	                norm_words.append(w.lower())
	            # words.append(w)
	    else:
	        # This started working in post-hoc anlaysis, then didn't
	        # with a minor refactoring, leading the 2nd stopword bug.
	        for w in raw_words:
	            if re.search("[a-zA-Z]", w) != None:
	                w = w.lower()
	                if w not in self.stop_words:
	                    norm_words.append(w) # keep it
	                else:
	                    self.stop_words[w] += 1 # track how often we "hit" this stop word.
	                    if self.STOP_DEBUG_CUTOFF >= 1:
	                        self.STOP_DEBUG_CUTOFF -= 1
	                        logger.debug('stop_words: hit w="%s", so not adding to norm_words', w )

	            # The following yields R1.R = 0.24428
	            #------------------------------------
	            #if w not in stop_words:
	            #    norm_words.append(w) # keep it
	            #------------------------------------

	            #------------------------------------
	            # The following yields R1.R = 0.24428
	            #------------------------------------
	            #if STOP_TOKENIZE:
	            #    # we'll check stopwords in the next loop
	            #    # (since the stop words are tokenized).
	            #    norm_words.append(w.lower())
	            #else:
	            #    # let's check stopwords now.
	            #    w = w.lower()
	            #    if w not in stop_words:
	            #        norm_words.append(w) # keep it
	            #    else:
	            #        stop_words[w] += 1 # track how much our stopwords actually stop.
	            #------------------------------------
	        # words.append(w)
	#-----------------------------------------------------------------------------

	    for w in norm_words:
	        if w not in self.stop_words:
	            words.append(w)
	            # jgreve: this uses stopword logic but doesn't
	            # make it into qrmatrix so leaving as-is.
	    return words, norm_words


	# Return sentences from paragraph
	def preprocess_sents(self, paragraph):
	    sentences = sent_tokenize(paragraph)
	    return sentences

	# Return a list of all the words (with frequency counts) in a docset
	def words_from_docset(self, docset):
		docset_words = {}
		for idx, article in enumerate(docset.articles):
				paragraphs = article.paragraphs
				if len(paragraphs):
					for paragraph in paragraphs:
						sentences = preprocess_sents(paragraph)
						for sentence in sentences:
							words = preprocess_words(sentence)
							for word in words:
								if word in docset_words:
									docset_words[word] += 1
								else:
									docset_words[word] = 1
		return docset_words