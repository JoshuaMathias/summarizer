import bs4
import argparse

import local_util as u
# "local_util" mainly for u.eprint() which is like print but goes to stderr.


class ArticleContent():
    def __init__(self, id='', type = 'story', headline='', dateline='', date='', body=list()):
        self.id = id
        self.type = type
        self.headline = headline
        self.dateline = dateline
        self.date = date
        self.setBody(body)

    def __str__(self):
        return 'ArticleContent(): headline="{}"'.format(self.headline)

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

    def __str__(self):
        return 'DocumentSet(): topic_id="{}" #docs={}'.format( self.topic_id, len(self.docs) )

    def addDoc(self, doc):
        self.docs.append(doc)

class ContentReader():
    def __init__(self,
                 aquaint='/opt/dropbox/17-18/573/AQUAINT',
                 aquaint2 = '/opt/dropbox/17-18/573/AQUAINT-2'):
        self.AQUAINT_DIR = aquaint
        self.AQUAINT2_DIR = aquaint2

    def __str__(self):
        return 'ContentReader()'

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
        tag = body.find(tagid)
        if tag:
            return tag.contents[0].strip()
        else:
            return ''

    def __extract_tag_or_attr(self, body, tagid, attrid):
        if body.has_attr(attrid):
            return body[attrid].strip()
        else:
            return self.__extract_tag__(body, tagid)

    def read_sgml_repo(self, filename):
        articles = list()
        doctree = bs4.BeautifulSoup(open(filename).read(), 'html.parser')
        for doc in doctree.find_all('doc'):
            art = ArticleContent(id = self.__extract_tag_or_attr(doc, 'docno', 'id'),
                                 type = self.__extract_tag_or_attr(doc, 'doctype', 'type').lower(),
                                 headline = self.__extract_tag__(doc, 'headline'),
                                 date = self.__extract_tag__(doc, 'datetime'),
                                 dateline = self.__extract_tag__(doc, 'dateline'),
                                 body=list())

            for text_block in doc.find_all('text'):
                for para in text_block.find_all('p'):
                    art.addParagraph(para.contents[0])
            articles.append(art)

        return articles

    def __aquaint_file__(self, doc_id):
        u.eprint('> ContentReader.__aquaint_file__() doc_id="{}"'.format(doc_id) )
        reason = "None"
        if doc_id[3:8] == '_ENG_':  # True for AQUAINT-2 files
            reason = "doc_id[3:8] == '_ENG_':  # True for AQUAINT-2 files"
            filename = '%s/data/%s/%s.xml' % (self.AQUAINT2_DIR,
                                              doc_id[0:7].lower(),
                                              doc_id[0:doc_id.find('.')-2].lower())
        else:
            reason="Not doc_id[3:8] == '_ENG_'"
            file_extension = doc_id[0:3].upper()
            if file_extension != 'NYT':
                reason += " (also file_extension='{}' != 'NYT')".format(file_extension)
                file_extension += '_ENG'
            filename = '%s/%s/%s/%s_%s' % (self.AQUAINT_DIR,
                                         doc_id[0:3].lower(),
                                         doc_id[3:7],
                                         doc_id[3:doc_id.find('.')],
                                         file_extension)

        u.eprint('|   filename="{}" w/reason={}'.format(filename, reason))

        art = None

        doctree = bs4.BeautifulSoup(open(filename).read(), 'html.parser')
        for doc in doctree.find_all('doc'):
            id = self.__extract_tag_or_attr(doc, 'docno', 'id')
            if id == doc_id:
                art = ArticleContent(id = id,
                                     type=self.__extract_tag_or_attr(doc, 'doctype', 'type').lower(),
                                     headline=self.__extract_tag__(doc, 'headline'),
                                     date=self.__extract_tag__(doc, 'datetime'),
                                     dateline=self.__extract_tag__(doc, 'dateline'),
                                     body=list())

                text_block = doc.find('text')
                for para in text_block.find_all('p'):
                    art.addParagraph(para.contents[0])
                break

        return art

    def __read_aquaint_doc__(self, doc_id):
        u.eprint('> ContentReader.__read_aquaint_doc__(): doc_id={}, calling self.__aquaint_file__(doc_id)'.format(doc_id) )
        x = self.__aquaint_file__(doc_id)
        u.eprint('< ContentReader.__read_aquaint_doc__(): returning {}'.format(x))
        return x

    def read_topic_index(self, filename):


        u.eprint('ContentReader.read_topic_index(): filename={}'.format(filename))
        topicIndex = bs4.BeautifulSoup(open(filename).read(), 'html.parser')
        for topic in topicIndex.find_all('topic'):
            topic_id = topic['id']
            u.eprint('ContentReader.read_topic_index(): topic_id={}'.format(topic_id))
            topic_cat = topic['category']
            u.eprint('ContentReader.read_topic_index(): topic_cat={}'.format(topic_cat))
            topic_title = topic.find('title').contents[0]
            u.eprint('ContentReader.read_topic_index(): topic_title={}'.format(topic_title))
            docset_cnt = 0
            for docset_tag in topic.find_all('docseta'):
                docset_cnt += 1
                u.eprint('ContentReader.read_topic_index():     docset_cnt={}, docset_tag={}'.format( docset_cnt, docset_tag ) )
                docset_id = docset_tag['id']
                docset = DocumentSet(docset_id, topic_id, topic_cat, topic_title)
                doc_cnt = 0
                for doc in docset_tag.find_all('doc'):
                    doc_cnt += 1
                    # original:     docset.addDoc( self.__read_aquaint_doc__( doc['id'].strip() ) )
                    u.eprint('\t\tdoc_cnt={}, doc={}'.format(doc_cnt, doc))
                    thing = doc['id'].strip()
                    u.eprint('\t\tdoc_cnt={}, calling __read_aquaint_doc__() on thing="{}"'.format( doc_cnt, thing ) )
                    docset.addDoc(self.__read_aquaint_doc__( thing ) )
                u.eprint('ContentReader.read_topic_index(): before yield: yielding docset={}'.format(docset))

                yield docset


if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    argparser = argparse.ArgumentParser(description = 'Document reader #e2jkplusplus')
    argparser.add_argument('topic_file', metavar='TOPICFILE', help='Topic Index File')
    args = argparser.parse_args()

    content_reader = ContentReader('aquaint_test1', 'aquaint_test2')

    print('reading file: "%s"' % args.topic_file)

    for docset in content_reader.read_topic_index(args.topic_file):
        print('DOCSET: %s' % docset.id)
        for doc in docset.docs:
            if doc is not None:
                print('doc %s -- %d paragraphs' % (doc.id, len(doc.body)))
            else:
                print('DOC ERROR')
        print()
