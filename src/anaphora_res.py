from pynlp import StanfordCoreNLP

def anaph_res(body_text):
    annotators = 'tokenize, ssplit, pos, lemma, ner, entitymentions, coref, sentiment, openie'

    options = {'openie.resolve_coref': True}

    nlp = StanfordCoreNLP(annotators=annotators, options=options)

    document = nlp(text)

    return document.coref_chains
