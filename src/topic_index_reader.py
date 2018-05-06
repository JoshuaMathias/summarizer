import xml.sax
import argparse

import article_content
import article_reader

class E2JKTopicContentHandler(xml.sax.ContentHandler):
    def __init__(self, topic_index):
        xml.sax.ContentHandler.__init__(self)
        self.topic_index = topic_index
        self.state = 'START'

    def startElement(self, name, attrs):
        if name == 'TACtaskdata':
            self.topic_index.year = attrs.getValue('year')
            self.topic_index.track = attrs.getValue('track')
            self.topic_index.task = attrs.getValue('task')
            self.topic_index.dataset = attrs.getValue('dataset')
            self.state = 'INDEX'
        elif name == 'topic':
            self.topic = article_content.Topic(attrs.getValue('id'), attrs.getValue('category'))
            self.topic_index.addTopic(self.topic)
            self.state = 'TOPIC'
        elif name == 'title':
            self.state = 'TITLE'
        elif name == 'docsetA' or name == 'docsetB':
            self.docset = article_content.DocSet(attrs.getValue('id'), name)
            self.docset.topic_title = self.topic.title
            self.docset.topic_id = self.topic.id
            self.topic.addDocSet(self.docset)
            self.state = 'DOCSET'
        elif name == 'doc':
            self.docset.addDocument(attrs.getValue('id'))


    def endElement(self, name):
        if name == 'title':
            self.state = 'TOPIC'
        elif name == 'topic':
            self.state = 'INDEX'
        elif name == 'docsetA' or name == 'docsetB':
            self.state = 'DOCSET'
        elif name == 'TACtaskdata':
            self.state = 'END'

    def characters(self, content):
        if self.state == 'TITLE':
            self.topic.title = content.strip()

class TopicIndexReader():
    def __init__(self, filename,
                 aquaint1 = '/opt/dropbox/17-18/573/AQUAINT',
                 aquaint2 = '/opt/dropbox/17-18/573/AQUAINT-2',
                 dbname = 'shelve_db'):
        self.topic_file = open(filename, 'r')
        self.content_handler = E2JKTopicContentHandler(article_content.TopicIndex())
        self.aquaint1 = aquaint1
        self.aquaint2 = aquaint2
        self.dbname = dbname

    def read_topic_index_file(self, docset_type = 'all'):
        xml.sax.parse(self.topic_file, self.content_handler)

        if self.content_handler.state != 'END':
            print('WARNING: XML file not structured as expected')

        topic_index = self.content_handler.topic_index

        art_reader = article_reader.ArticleReader(self.dbname, self.aquaint1, self.aquaint2)
        art_reader.load_database(topic_index.allDocuments(docset_type))
        for topic in topic_index.topics:
            for docset in topic.docsets:
                docset.articles = art_reader.get_articles(docset.documents)

        return topic_index

if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    argparser = argparse.ArgumentParser(description = 'Topic Index Reader #e2jkplusplus')
    argparser.add_argument('topic_file', metavar='TOPICFILE', help='Topic Index File')
    args = argparser.parse_args()

    print('reading file: "%s"' % args.topic_file)
    topic_index = TopicIndexReader(args.topic_file,
                                   aquaint1 = 'aquaint_test1',
                                   aquaint2 = 'aquaint_test2',
                                   dbname = 'shelve_db').read_topic_index_file(docset_type = 'docseta')

    for topic in topic_index.topics:
        print('TOPIC: %s/%s' % (topic.id, topic.category))
        for docset in topic.docsets:
            print('    DOCSET: %s' % docset.id)
            for article in docset.articles:
                print('        %s:%s' % (article.id, article.headline))
