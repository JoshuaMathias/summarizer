import re
from pynlp import StanfordCoreNLP

def res(body_text):
    annotators = 'tokenize, ssplit, lemma, ner, entitymentions, coref, sentiment, openie'

    options = {'openie.resolve_coref': True}

    nlp = StanfordCoreNLP(annotators=annotators, options=options)

    document = nlp(body_text)

    sentences = []
    referents = []
    for chain in document.coref_chains:

        # SENTENCS
        sent = chain.__str__()
        list_of_sentences = sent.split("\n")

        list_of_approved = []
        for item in list_of_sentences:
            if re.search('[a-zA-Z]', item):
                item = re.sub(" \'", "\'", item)
                item = re.sub(" \"", "\"", item)
                item = re.sub(" \.", "\.", item)
                list_of_approved.append(item)

        # /SENTENCES

        # REFERENTS
        tokens = []
        phrases = []
        for v in chain.__iter__():
            tt = v.__str__()
            tt = re.sub(" \'", "\'", tt)
            tt = re.sub(" \"", "\"", tt)
            tt = re.sub(" \.", "\.", tt)

            tokens.append(tt)

        referent = chain.referent.__str__()
        referent = re.sub(" \'", "\'", referent)
        referent = re.sub(" \"", "\"", referent)
        referent = re.sub(" \.", "\.", referent)

        referents.append(referent)

        # /REFERENTS

        # RESOLVE REFERENCES
        for s in list_of_approved:
            old = s[:]
            for t in tokens:
                old = re.sub("\(+" + t + "\)+-\[id=\d+\]", t, old)
                s = re.sub("\(+" + t + "\)+-\[id=\d+\]", referent, s)
            new = re.sub("\(+" + referent + "\)+-\[id=\d+\]", referent, s)
        # /RESOLVE REFERENCES

            sentences.append([old, s])

    return [sentences, referents]
