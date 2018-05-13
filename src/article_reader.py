import local_util as u
logger = u.get_logger( __name__ ) # will call setup_logging() if necessary

import shelve
import argparse
import sys
import bs4

import article_content
import collections

TAG_STATS = collections.Counter( )

class ArticleReader():
    def __init__(self, dbname, aquaint, aquaint2):
        self.dbname = dbname
        self.AQUAINT_DIR = aquaint
        self.AQUAINT2_DIR = aquaint2

    def __aquaint_filename__(self, doc_id):
        self.agency = article_content.Article.UNK_AGENCY # 'unk' or smth.
        if doc_id[3:8] == '_ENG_':  # True for AQUAINT-2 files
            self.agency = doc_id[0:8] # remember where we are getting articls From.
            #  prefix smth like...
            #  iafp_eng  apw_eng  cna_eng  ltw_eng  nyt_eng  xin_eng
            # not exactly an extension but close enough.

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
            self.agency = file_extension # Let's keep this around,
            filename = '%s/%s/%s/%s_%s' % (self.AQUAINT_DIR,
                                         doc_id[0:3].lower(),
                                         doc_id[3:7],
                                         doc_id[3:doc_id.find('.')],
                                         file_extension)
            # stash it in Article() objects eventually (may help with data analysis)
            # jgreve (2018-05-09)

        logger.debug('__aquaint_filename__(): self.agency="%s" type(self)=%s', self.agency, type(self) )

            
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
            # jgreve: worth printing a warning? fail silent is no fun...
            return ''

    def __extract_tag_or_attr(self, body, tag_id, attr_id):
        if body.has_attr(attr_id):
            return body[attr_id].strip()
        else:
            return self.__extract_tag__(body, tag_id)

    # jgreve: copied from master (2018-05-11)
    # Need to convert BeautifulSoup NavigableString object (returned as content text)
    # Unfortunately, the NavigableString class is not something that can be stored
    # by pickle/shelve due to recursion issues. Need to convert to string. Previous
    # attempt to utf-8 encode was creating bytestrings, despite the call to str()
    def __convert_bs_string__(self, thestring):
        return str(thestring)


    def __load_doc_ids_from_doc_tree__(self, doctree, doc_ids):
        global TAG_STATS
        return_articles = set()
        for doc in doctree.find_all('doc'):
            doc_id = self.__extract_tag_or_attr(doc, 'docno', 'id')
            if doc_id in doc_ids:
                logger.debug('type(doc)=%s', str(type(doc)) )
                #logger.debug('doc=%s', str(doc))
                tags = doc.find_all()
                TAG_STATS.update( tag.name for tag in tags )
                #logger.debug('tags=%s', str(tags))
                #for tag in TAG_STATS.most_common():
                #    logger.debug( 'tag_freq: "%s"', tag )
                art = article_content.Article(doc_id)
                art.headline = self.__extract_tag__(doc, 'headline')
                art.datetime = self.__extract_tag__(doc, 'datetime')
                
                art.agency = self.agency
                logger.debug('__load_doc_ids_from_doc_tree__(): art.agency="%s"', art.agency)
                # jgreve: sometimes also date_time ?  (see line 3 from 19990421_APW_ENG, below )
                # and... are tags case sensive in BeautSoup?
                #-----------------------------------------------------
                #    1 <DOC>
                #    2 <DOCNO> APW19990421.0001 </DOCNO>
                #    3 <DATE_TIME> 1999-04-21 15:11:08 </DATE_TIME>
                #    4 <BODY>
                #    5 <CATEGORY> financial </CATEGORY>
                #    6 <HEADLINE> Nabisco Earnings Drop 35 Percent </HEADLINE>
                #    7 <TEXT>
                #    8 <P>
                #    9     PARSIPPANY, 
                #-----------------------------------------------------
                art.dateline = self.__extract_tag__(doc, 'dateline')
                logger.debug('tag: doc_id=%s: dateline=%s', doc_id, art.dateline )
                logger.debug('tag: doc_id=%s: datetime=%s', doc_id, art.datetime )
                logger.debug('tag: doc_id=%s: date_time=%s', doc_id, doc.find('date_time') )

                text_block = doc.find('text')
                all_para_tags = text_block.find_all('p')

                if len(all_para_tags) > 0:
                    for para in all_para_tags:
                        #OLD: self.__add_paragraph__(art, str(para.contents[0].encode('utf-8')))
                        self.__add_paragraph__(art, self.__convert_bs_string__(para.contents[0]))
                else:
                    #OLD: blockText = str(text_block.contents[0].encode('utf-8'))
                    blockText = str(self.__convert_bs_string__(text_block.contents[0]))
                    if blockText:
                        paraBreaks = blockText.split('\n\t')
                        for para in paraBreaks:
                            self.__add_paragraph__(art, para.strip())
                    else:
                        logger.warning('__load_doc_ids_from_doc_tree__(): Article %s has no text', doc_id)

                return_articles.add(art)

        for tag in TAG_STATS.most_common():
            logger.debug( 'tag_freq: "%s"', tag )
        return return_articles

    def __load_doc_ids__(self, doc_id, doc_ids, db):
        article_filename = self.__aquaint_filename__(doc_id)
        try:
            article_file = open(article_filename, 'r')
            doctree = bs4.BeautifulSoup(article_file.read(), 'html.parser')
            articles = self.__load_doc_ids_from_doc_tree__(doctree, doc_ids)
            return articles
        except FileNotFoundError:
            logger.error('__load_doc_ids__(): Could not find Article File "%s"', article_filename)
            return []

    def load_database(self, doc_ids):
        logger.info('load_database(): #doc_ids=%d', len(doc_ids) )
        hit_cnt = 0
        miss_cnt = 0
        db = shelve.open(self.dbname, writeback=True)
        for doc_id in doc_ids:
            if doc_id not in db:
                miss_cnt += 1
                logger.debug('load_database(): adding to database: %s', doc_id)
                articles = self.__load_doc_ids__(doc_id, doc_ids, db)
                for article in articles:
                    db[article.id] = article.toDict()
            else:
                logger.debug('load_database(): already in database: %s', doc_id)
                hit_cnt += 1
        db.close()
        logger.info('load_database(): #doc_ids=%d, hit_cnt=%d miss_cnt=%d', len(doc_ids), hit_cnt, miss_cnt )

    def get_articles(self, doc_ids):
        articles = list()
        with shelve.open(self.dbname) as db:
            for doc_id in doc_ids:
                if doc_id in db:
                    dict_struct = db[doc_id]
                    articles.append(article_content.articleFromDict(dict_struct))
                else:
                    # jgreve: should this be a hard fail?
                    logger.warning('get_articles(): doc_id="%s" not in database!', doc_id )

        if len(doc_ids) != len(articles):
             logger.warning( 'get_articles(): expected %d doc_ids but only found %d', len(doc_ids), len(articles) )
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
