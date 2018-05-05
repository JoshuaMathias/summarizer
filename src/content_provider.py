import bs4
import argparse
import shelve

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

    def __extract_byline__(self, text):
        NYTStyle = text.find('_')
        APStyle = text.find('--')

        if NYTStyle > 0 and NYTStyle < 32:
            self.byline = text[0:NYTStyle].strip()
            return text[NYTStyle+1:].strip()

        if APStyle > 0 and APStyle < 32:
            self.byline = text[0:APStyle].strip()
            return text[APStyle+2:].strip()

        return text

    def setBody(self, bodyText):
        self.body = bodyText

    def setHeadline(self, headline):
        self.headline = headline

    def addParagraph(self, paraText):
        if self.body is None:
            self.body = list()

        if len(self.body) == 0:
            paraText = self.__extract_byline__(paraText)

        self.body.append(paraText)

class DocumentSet():
    def __init__(self, id='', topic_id='', topic_cat='', topic_title='', docs = list()):
        self.id = id
        self.topic_id = topic_id
        self.topic_cat = topic_cat
        self.topic_title = topic_title
        self.docs = docs

    def __str__(self):
        return 'DocumentSet(): topic_id="{}" #docs={}'.format( self.topic_id, len(self.docs) )

    def addDoc(self, doc):
        self.docs.append(doc)

class Topic():
    def __init__(self, id, category, title):
        self.id = id
        self.category = category
        self.title = title
        self.doc_set = dict()

    def addDocumentSet(self, docset_id, articles):
        self.doc_set[docset_id] = DocumentSet(docset_id, self.id, self.category, self.title, articles)

    def getDocumentSet(self, docset_id):
        if docset_id in self.doc_set:
            return self.doc_set[docset_id]
        else:
            return None

class ContentReader():
    def __init__(self,
                 aquaint='/opt/dropbox/17-18/573/AQUAINT',
                 aquaint2 = '/opt/dropbox/17-18/573/AQUAINT-2',
                 dbname='shelfdb'):
        self.AQUAINT_DIR = aquaint
        self.AQUAINT2_DIR = aquaint2
        self.dbname = dbname

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

    def __aquaint_filename__(self, doc_id):
        if doc_id[3:8] == '_ENG_':  # True for AQUAINT-2 files
            filename = '%s/data/%s/%s.xml' % (self.AQUAINT2_DIR,
                                              doc_id[0:7].lower(),
                                              doc_id[0:doc_id.find('.')-2].lower())
        else:
            file_extension = doc_id[0:3].upper()
            if file_extension == 'XIE':
                file_extension = 'XIN'
            if file_extension != 'NYT':
                file_extension += '_ENG'
            filename = '%s/%s/%s/%s_%s' % (self.AQUAINT_DIR,
                                         doc_id[0:3].lower(),
                                         doc_id[3:7],
                                         doc_id[3:doc_id.find('.')],
                                         file_extension)

        return filename

    def __get_doc_list__(self, doc_ids):
        result_articles = list()

        with shelve.open(self.dbname) as db:
            for doc_id in doc_ids:
                if doc_id not in db:
                    filename = self.__aquaint_filename__(doc_id)
                    try:
                        articles_file = open(filename, 'r')
                        doctree = bs4.BeautifulSoup(articles_file.read(), 'html.parser')
                        for doc in doctree.find_all('doc'):
                            id = self.__extract_tag_or_attr(doc, 'docno', 'id')
                            if id not in db:
                                art = ArticleContent(id=id,
                                                     type=self.__extract_tag_or_attr(doc, 'doctype', 'type').lower(),
                                                     headline=self.__extract_tag__(doc, 'headline'),
                                                     date=self.__extract_tag__(doc, 'datetime'),
                                                     dateline=self.__extract_tag__(doc, 'dateline'),
                                                     body=list())

                                text_block = doc.find('text')
                                for para in text_block.find_all('p'):
                                    art.addParagraph(para.contents[0])

                        articles_file.close()
                    except FileNotFoundError:
                        print('ERROR: File Not Found "%s"' % filename)
                    
                result_articles.append(db[doc_id])
        return result_articles

    def __aquaint_file__(self, doc_id_list):
        article_list = list()
        document_sources = dict()
        for doc_id in doc_id_list:
            filename = self.__aquaint_filename__(doc_id)
            if filename not in document_sources:
                document_sources[filename] = list()
            document_sources[filename].append(doc_id)

        for filename in document_sources:
            doc_ids = document_sources[filename]
            try:
                doc_count = 0
                articles_file = open(filename,'r')
                doctree = bs4.BeautifulSoup(articles_file.read(), 'html.parser')
                for doc in doctree.find_all('doc'):
                    id = self.__extract_tag_or_attr(doc, 'docno', 'id')
                    if id in doc_ids:
                        art = ArticleContent(id=id,
                                             type=self.__extract_tag_or_attr(doc, 'doctype', 'type').lower(),
                                             headline=self.__extract_tag__(doc, 'headline'),
                                             date=self.__extract_tag__(doc, 'datetime'),
                                             dateline=self.__extract_tag__(doc, 'dateline'),
                                             body=list())

                        text_block = doc.find('text')
                        for para in text_block.find_all('p'):
                            art.addParagraph(para.contents[0])

                        doc_count += 1
                        article_list.append(art)

                        if doc_count == len(doc_ids):
                            articles_file.close()
                            break

                    articles_file.close()
            except FileNotFoundError:
                print('ERROR: File Not Found "%s"' % filename)

        return article_list

    def read_topic_index(self, filename):
        topicIndex = bs4.BeautifulSoup(open(filename).read(), 'html.parser')
        for topic_node in topicIndex.find_all('topic'):
            topic = Topic(topic_node['id'], topic_node['category'], topic_node.find('title').contents[0])

            for docset_tag in topic_node.find_all('docseta'):
                docset_id = docset_tag['id']
                docs = list()
                for doc in docset_tag.find_all('doc'):
                    docid = doc['id'].strip()
                    if docid == None or len(docid) == 0:
                        print('ERROR: Unknown Document ID for doc %s' % doc)
                    docs.append(docid)
                articles = self.__aquaint_file__(docs)

                topic.addDocumentSet(docset_id, articles)

                yield topic.getDocumentSet(docset_id)


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
