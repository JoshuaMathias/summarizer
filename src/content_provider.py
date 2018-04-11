class ArticleContent():
    def __init__(self, id='', type = 'story', headline='', dateline='', body=[]):
        self.id = id
        self.type = type
        self.headline = headline
        self.dateline = dateline
        self.setBody(body)

    def setBody(self, bodyText):
        self.body = bodyText

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