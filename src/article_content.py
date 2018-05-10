import re

class Article():
    UNK_AGENCY = '<unk>' # constant (a class var)

    def __init__(self, id):
        self.id = id
        self.headline = ''
        self.datetime = ''
        self.dateline = ''
        self.paragraphs = list()
        self.agency = ''
        self._scrubbed = None # lazy init, dont bother unless somebody asks for it.

    def __str__(self):
        cutoff = self.headline if len(self.headline) <= 20 else self.headline[0:17]+'...'
        return 'Article( id:{} "{:.20s}" para={} )'.format(self.id, cutoff, len(self.paragraphs))

    def scrubbed_paragraphs(self):
        if self._scrubbed == None:
            self._scrubbed = [ ]
            for paragraph in self.paragraphs:
                #paragraph = re.sub("(\n|\t)", " ", paragraph)
                #paragraph = re.sub("  +", " ", paragraph)
                #paragraph = re.sub("^ ", "", paragraph)

                # should handle newlines (0x0a) tabs (0x09) linefeeds (0x0a) etc.
                paragraph = re.sub( r"\\[nt]", r" ", paragraph ) # flag escape seqs like
                paragraph = re.sub( r"\s+", r" ", paragraph ) # collapse all whitespace to single char.
                paragraph = paragraph.strip() # Also drop leading and trailing whitespace.
                self._scrubbed.append( paragraph )
        return self._scrubbed


    def toDict(self):
        return {'id' : self.id,
                'headline' : self.headline,
                'datetime' : self.datetime,
                'dateline' : self.dateline,
                'agency'   : self.agency, # XIN, NYT, etc. (actually file extension)
                'paragraphs' : self.paragraphs }

def articleFromDict(dict_value):
    doc_id = dict_value['id']
    article = Article(doc_id)
    article.headline = dict_value['headline']
    article.datetime = dict_value['datetime']
    article.dateline = dict_value['dateline']
    article.agency = dict_value.get('agency', 'unk') # XIN, NYT, etc. (actually file extension)
    article.paragraphs = dict_value['paragraphs']

    return article


class DocSet():
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.topic_title = ''
        self.topic_id = ''
        self.documents = list()
        self.articles = list()   # Initialize in case articles can't be found

    def __str__(self):
        size_info = '{}'.format( len(self.documents) )
        if len(self.articles) != len(self.documents):
            size_info += ' docs, but #articles={}?'.format( len(self.articles) )
        return 'DocSet( id:{} "{}" {})'.format(self.id, self.topic_title, size_info )


    def addDocument(self, doc):
        self.documents.append(doc)

class Topic():
    def __init__(self, id, category):
        self.id = id
        self.category = category
        self.title = ''
        self.docsets = list()

    def __str__(self):
        return 'Topic( id:{} category={} title={} #docsets={})'.format( self.id, self.category, self.title, len(self.docsets) )

    def addDocSet(self, docset):
        self.docsets.append(docset)


class TopicIndex():
    def __init__(self):
        self.topics = list()

    def __str__(self):
        return 'TopicIndex( #topics={} )'.format( len(self.topics) )

    def addTopic(self, topic):
        self.topics.append(topic)

    def allDocuments(self, docset_type = 'all'):
        doc_ids = set()
        for topic in self.topics:
            for docset in topic.docsets:
                if (docset_type == 'docseta' and docset.type.lower() == 'docseta') or \
                    (docset_type == 'docsetb' and docset.type.lower() == 'docsetb') or \
                    (docset_type != 'docseta' and docset_type != 'docsetb'):
                    for doc_id in docset.documents:
                        doc_ids.add(doc_id)
        return doc_ids

    def documentSets(self, docset_type='all'):
        for topic in self.topics:
            for docset in topic.docsets:
                if docset_type == 'docseta' or docset_type == 'docsetb':
                    if docset.type.lower() == docset_type:
                        yield docset
                else:
                    yield docset
