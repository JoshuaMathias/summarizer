import bs4

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

class ContentReader():
    def __init__(self, aquaint='/opt/dropbox/17-18/573/AQUAINT', aquaint2 = '/opt/dropbox/17-18/573/AQUAINT-2'):
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