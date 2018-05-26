from nltk.tokenize import sent_tokenize, word_tokenize # for tokenizing sentences and words
import re # for removing multiple \s characters and source formatting
import local_util as u
logger = u.get_logger( __name__ ) #  https://docs.python.org/3/howto/logging.html

STOP_WORDS        = None
STOP_TOKENIZE     = True # +D3.err, original loop above: no change, still R1.R=0.22264.
STOP_QRFLAG       = True # Whether or not to apply stopwords to qrmatrix population.


def get_stop_words( ):
    global STOP_WORDS # be explicit about this being a global (module level variable).
    global STOP_TOKENIZE

    if STOP_WORDS:
        return STOP_WORDS # recycle what we already have.
    # If we reach this point, STOP_WORDS is None so we need to load it.
    STOP_WORDS = dict( ) # start a new dictionary,
    stop_words = STOP_WORDS # jgreve: aliasing original var name (lower case stop_wrods)
    # so I don't edit the actual logic.
   
    stop_file = "src/stop_words"
    logger.info('get_stop_words(): loading stop_words from %s', stop_file )
    stops = open(stop_file)
    stop_lines = stops.read().split("\n")

    #for line in stop_lines:
    #    line = line.lower()
    #    if line not in stop_words:
    #        stop_words[line] = 0

    logger.info('get_stop_words(): loading stop_words from %s', stop_file )
    stop_line_cnt = 0
    for line in stop_lines:
        stop_line_cnt += 1
        line = line.lower().strip()
        if STOP_TOKENIZE:
            words = word_tokenize( line )
            logger.debug('stop_words[{:03d}]: line="{}" --> words={}'.format(stop_line_cnt, line, words ))
            for word in words:
                stop_words[word] = 0
        else:
            # original D3 code.
            if line not in stop_words:
                stop_words[line] = 0
    msg = 'get_stop_words(): loaded #stop_words=%d, #lines=%d, STOP_TOKENIZE=%s STOP_QRFLAG=%s' % ( len(stop_words), stop_line_cnt, str(STOP_TOKENIZE), str(STOP_QRFLAG)  )
    logger.info( msg )
    u.eprint(msg)
    return STOP_WORDS # important: this *must* still point to the same thing stop_words does.

def write_statistics( label ):
    # place holder for other stats we might want to track.
    # the idea is summary.py will call this after the dust settles
    # so we can get some numbers on what happened.
    write_stop_word_stats(label)

def write_stop_word_stats(label):
    global STOP_TOKENIZE        # jgreve: these flags are additions to the original D3 logic, note that
    global STOP_QRFLAG          # the local stop_words variable (used below) is left as-is.
    logger.error('write_stop_word_stats(): writing stop_words frequency to STDOUT (search on "stop_wrods_FREQ")')
    if not STOP_QRFLAG:
        logger.error('   note: STOP_QRFLAG=False, so no stop-word activity to report')
        return # to do: actually count the stopword dict and bail if total(hits) = 0.
    stop_words = get_stop_words( )
    sys.stdout.write( '#stop_words=%d, STOP_TOKENIZE=%s STOP_QRFLAG=%s' % ( len(stop_words), str(STOP_TOKENIZE), str(STOP_QRFLAG)  ) )
    # note: requires the usage of our code increment
    # words in the STOP_WORDS dict whenever they actually
    # stop something.
    sys.stdout.write('\n--- stop_words_FREQ for {} ---'.format(label))
    u.write_values( sys.stdout, "stop_words", stop_words )
    u.write_values( sys.stdout, "stop_words_rev", stop_words, descending_freq=True)

# Return list of tokenized words from sentence
def preprocess_words(sentence):
    raw_words = word_tokenize(sentence)
    norm_words = []
    words = []
#-----------------------------------------------------------------------------

    # before D3.err (d3_orig) yields R1.R = 0.22264
    if not STOP_QRFLAG:
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
                if w not in stop_words:
                    norm_words.append(w) # keep it
                else:
                    stop_words[w] += 1 # track how often we "hit" this stop word.
                    if STOP_DEBUG_CUTOFF >= 1:
                        STOP_DEBUG_CUTOFF -= 1
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
        if w not in stop_words:
            words.append(w)
            # jgreve: this uses stopword logic but doesn't
            # make it into qrmatrix so leaving as-is.
    return words, norm_words


# Return sentences from paragraph
def preprocess_sents(paragraph):
    sentences = sent_tokenize(paragraph)
    return sentences

# Return a list of all the words (with frequency counts) in a docset
def words_from_docset(docset):
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