import bs4
import argparse

AQUAINT2_PREFIX = ['AFP_ENG_', 'APW_ENG_', 'CNA_ENG_', 'LTW_ENG_', 'NYT_ENG_', 'XIN_ENG_']
AQUAINT_PREFIX = ['APW', 'NYT', 'XIE']

class ArticleContent():
    def __init__(self, id='', type = 'story', headline='', dateline='', date='', body=[]):
        self.id = id
        self.type = type
        self.headline = headline
        self.dateline = dateline
        self.date = date
        self.setBody(body)

    def setBody(self, bodyText):
        self.body = bodyText

    def setHeadline(self, headline):
        self.headline = headline

    def addParagraph(self, paraText):
        if self.body is None:
            self.body = list()

        self.body.append(paraText)

class DocumentSet():
    def __init__(self, id='', topic_id='', topic_cat='', topic_title=''):
        self.id = id
        self.topic_id = topic_id
        self.topic_cat = topic_cat
        self.topic_title = topic_title

        self.docs = list()

    def addDoc(self, doc):
        self.docs.append(doc)

class ContentReader():
    def __init__(self,
                 aquaint='/opt/dropbox/17-18/573/AQUAINT',
                 aquaint2 = '/opt/dropbox/17-18/573/AQUAINT-2'):
        self.AQUAINT_DIR = aquaint
        self.AQUAINT2_DIR = aquaint2

    def read_raw_files(self, *filenames):
        articles = list()
        for filename in filenames:
            art = ArticleContent(id=filename, type='story')
            with open(filename, 'r') as f:
                para = ''
                for line in f:
                    if len(line.strip()) == 0 and len(para) > 0:
                        art.addParagraph(para)
                        para = ''
                    elif len(line.strip()) > 0:
                        para += (line.strip() + ' ')

                if len(para) > 0:
                    art.addParagraph(para)

            articles.append(art)

        return articles

    def __extract_tag__(self, body, tagid):
        coll = body.find(tagid)
        if len(coll) > 0:
            return coll[0].content[0]
        else:
            return ''

    def __extract_tag_or_attr(self, body, tagid, attrid):
        if body.has_attr(attrid):
            return body[attrid]
        else:
            return body.find(tagid).contents[0]

    def read_sgml_repo(self, filename):
        articles = list()
        doctree = bs4.BeautifulSoup(open(filename).read(), 'html.parser')
        for doc in doctree.find_all('doc'):
            art = ArticleContent(id = self.__extract_tag_or_attr(doc, 'docno', 'id'),
                                 type = self.__extract_tag_or_attr(doc, 'doctype', 'type').lower(),
                                 headline = self.__extract_tag__(doc, 'headline'),
                                 date = self.__extract_tag__(doc, 'datetime'),
                                 dateline = self.__extract_tag__(doc, 'dateline'))

            for text_block in doc.find_all('text'):
                for para in text_block.find_all('p'):
                    art.addParagraph(para.contents[0])
            articles.append(art)

        return articles

    def __aquaint_file__(self, doc_id):
        if doc_id[3:8] == '_ENG_':  # True for AQUAINT-2 files
            filename = '%s/data/%s/%s.xml' % (self.AQUAINT2_DIR,
                                              doc_id[0:7].lower(),
                                              doc_id[0:doc_id.find('.')].lower())
        else:
            filename = '%s/%s/%s/%s_%s_ENG' % (self.AQUAINT_DIR,
                                         doc_id[0:3].lower(),
                                         doc_id[3:7],
                                         doc_id[3:doc_id.find('.')],
                                         doc_id[0:3].upper())

        doctree = bs4.BeautifulSoup(open(filename).read(), 'html.parser')
        for doc in doctree.find_all('doc'):
            id = self.__extract_tag_or_attr(doc, 'docno', 'id').strip()
            if id == doc_id:
                art = ArticleContent(id = id,
                                     type=self.__extract_tag_or_attr(doc, 'doctype', 'type').lower(),
                                     headline=self.__extract_tag__(doc, 'headline'),
                                     date=self.__extract_tag__(doc, 'datetime'),
                                     dateline=self.__extract_tag__(doc, 'dateline'))

            for text_block in doc.find_all('text'):
                for para in text_block.find_all('p'):
                    art.addParagraph(para.contents[0])

            return art

    def __read_aquaint_doc__(self, doc_id):
        return self.__aquaint_file__(doc_id)

    def read_topic_index(self, filename):
        topicIndex = bs4.BeautifulSoup(open(filename).read(), 'html.parser')
        for topic in topicIndex.find_all('topic'):
            topic_id = topic['id']
            topic_cat = topic['category']
            topic_title = topic.find('title').contents[0]
            for docset_tag in topic.find_all('docseta'):
                docset_id = docset_tag['id']
                docset = DocumentSet(docset_id, topic_id, topic_cat, topic_title)
                for doc in docset_tag.find_all('doc'):
                    docset.addDoc(self.__read_aquaint_doc__(doc['id'].strip()))

                yield docset


if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    argparser = argparse.ArgumentParser(description = 'Document reader #e2jkplusplus')
    argparser.add_argument('topic_file', metavar='TOPICFILE', help='Topic Index File')
    args = argparser.parse_args()

    content_reader = ContentReader()

    print('reading file: "%s"' % args.topic_file)

    for docset in content_reader.read_topic_index(args.topic_file):
        print('DOCSET: %s' % docset.id)
        for doc in docset.docs:
            print(doc.id)
        print()