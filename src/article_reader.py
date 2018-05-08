import shelve
import argparse
import sys
import bs4

import article_content

class ArticleReader():
    def __init__(self, dbname, aquaint, aquaint2):
        self.dbname = dbname
        self.AQUAINT_DIR = aquaint
        self.AQUAINT2_DIR = aquaint2

    def __aquaint_filename__(self, doc_id):
        if doc_id[3:8] == '_ENG_':  # True for AQUAINT-2 files
            filename = '%s/data/%s/%s.xml' % (self.AQUAINT2_DIR,
                                              doc_id[0:7].lower(),
                                              doc_id[0:doc_id.find('.')-2].lower())
        else:
            #--------------------------
            # Wow, this is ugly.
            # If this is an AQUAINT1 directory, use "XIN" as the code for "XIE" ids
            # and add "_ENG" to the end of all files EXCEPT for "NYT"
            # jgreve: don't see a cleaner way to do it. :-(
            #--------------------------
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

    def __extract_byline__(self, text):
        NYTStyle = text.find('_')
        APStyle = text.find('--')

        if NYTStyle > 0 and NYTStyle < 32:
            byline = text[0:NYTStyle].strip()
            return text[NYTStyle+1:].strip(), byline

        if APStyle > 0 and APStyle < 32:
            byline = text[0:APStyle].strip()
            return text[APStyle+2:].strip(), byline

        return text, ''

    def __add_paragraph__(self, article, paraText):
        if len(article.paragraphs) == 0:
            paraText, byline = self.__extract_byline__(paraText)
            if not article.dateline and len(byline) > 0:
                article.dateline = byline

        article.paragraphs.append(paraText)

    def __extract_tag__(self, body, tagid):
        tag = body.find(tagid)
        if tag:
            return tag.contents[0].strip()
        else:
            return ''

    def __extract_tag_or_attr(self, body, tag_id, attr_id):
        if body.has_attr(attr_id):
            return body[attr_id].strip()
        else:
            return self.__extract_tag__(body, tag_id)

    def __load_doc_ids_from_doc_tree__(self, doctree, doc_ids):
        return_articles = set()
        for doc in doctree.find_all('doc'):
            doc_id = self.__extract_tag_or_attr(doc, 'docno', 'id')
            if doc_id in doc_ids:
                art = article_content.Article(doc_id)
                art.headline = self.__extract_tag__(doc, 'headline')
                art.datetime = self.__extract_tag__(doc, 'datetime')
                art.dateline = self.__extract_tag__(doc, 'dateline')

                text_block = doc.find('text')
                for para in text_block.find_all('p'):
                    self.__add_paragraph__(art, str(para.contents[0].encode('utf-8')))

                return_articles.add(art)

        return return_articles

    def __load_doc_ids__(self, doc_id, doc_ids, db):
        article_filename = self.__aquaint_filename__(doc_id)
        try:
            article_file = open(article_filename, 'r')
            doctree = bs4.BeautifulSoup(article_file.read(), 'html.parser')
            articles = self.__load_doc_ids_from_doc_tree__(doctree, doc_ids)
            return articles
        except FileNotFoundError:
            sys.stderr.write('ERROR: Could not find Article File "%s"\n' % article_filename)
            return []

    def load_database(self, doc_ids):
        db = shelve.open(self.dbname, writeback=True)
        for doc_id in doc_ids:
            if doc_id not in db:
                articles = self.__load_doc_ids__(doc_id, doc_ids, db)
                for article in articles:
                    db[article.id] = article.toDict()
        db.close()

    def get_articles(self, doc_ids):
        articles = list()
        with shelve.open(self.dbname) as db:
            for doc_id in doc_ids:
                if doc_id in db:
                    dict_struct = db[doc_id]
                    articles.append(article_content.articleFromDict(dict_struct))

        return articles

if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    argparser = argparse.ArgumentParser(description = 'Article Reader #e2jkplusplus')
    argparser.add_argument('article_id', metavar='ARTICLE_ID', help='Article (AQUAINT Document) ID')
    args = argparser.parse_args()

    reader = ArticleReader('shelve_db', 'aquaint_test1', 'aquaint_test2')
    print('looking up id: "%s"' % args.article_id)

    reader.load_database([args.article_id])

    for article in reader.get_articles([args.article_id]):
        print (article.toDict()) 
