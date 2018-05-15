import unittest
import summarizer
import article_reader
import topic_index_reader
import article_content
import rougescore
import sum_config
import bs4
from unittest.mock import patch
import io

class TestSummarizer(unittest.TestCase):
    def setUp(self):
        self.storyText = ['This is a story about summarization. It is important to have enough\n',
                         'characters here to fill out the text. Also, it is important to summarize\n',
                         'the main issues of summarization. Excuse me. Hi, Mom! Sorry, where was I?\n',
                         'Oh, yeah. It is important to give the summarizer irrelevant asides not\n',
                         'important to the main subject, whatever that is.\n']
        self.summary = '--- begin summary: "test.dat" ---\n' \
                       ' This is a story about summarization. It is important to have enough ' \
                       'characters here to fill out the text. Also, it is important to summarize\n\n' \
                       '--- end summary: "test.dat" ---\n'
        self.storyBody = 'This is a story about summarization. It is important to have enough ' \
                         'characters here to fill out the text. Also, it is important to summarize ' \
                         'the main issues of summarization. Excuse me. Hi, Mom! Sorry, where was I? ' \
                         'Oh, yeah. It is important to give the summarizer irrelevant asides not ' \
                         'important to the main subject, whatever that is. '
        self.storySGML = '<DOC>\n<DOCNO> TEST.0001 </DOCNO>\n<BODY>\n<TEXT>\n' \
                         '<P>\nThis is a story about summarization. It is important to have enough\n' \
                         'characterss here to fill out the text.\n</P>\n' \
                         '<P>\nAlso, it is important to summarize the main issues of summarization.\n' \
                         'Excuse me. Hi, Mom! Sorry, where was I? Oh, yeah.\n</P>\n' \
                         '<P>\nIt is important to give the summarizer irrelevant asides not important\n' \
                         'to the main subject, whatever that is.</P>'
        self.peer1 =     ['the', 'cat', 'was', 'found', 'under', 'the', 'bed']
        self.peer2 =     ['the', 'tiny', 'little', 'cat', 'was', 'found', 'under', 'the', 'big', 'funny', 'bed']
        self.model =     ['the', 'cat', 'was', 'under', 'the', 'bed']

        self.configText = 'project:\n    team_id: test\n    release_title: also test\n'

        self.sampleXML = '<DOC>\n<BODY>\n<TEXT>\n<P>\nThis is a test\nThis is still a test.\n</P>\n</TEXT>\n</BODY>\n</DOC>'

    # Not a great test, but mostly a template for mocking file reading in Python
    # (Seems readline iteration is broken in unittest mock, hence the weird StringIO invocation)
    def test_SummaryReturnsMinSizeWhenStoryIsLarger(self):
        smrzr = summarizer.Summarizer(25)
        article = article_content.Article('test.dat')
        article.paragraphs.append(self.storyBody)
        summary = smrzr.summarize(article)
        self.assertEqual(summary, self.summary)

    def test_IndexReaderDefaultsAquaintAndAquaint2(self):
        mock_file = io.StringIO('')
        with patch('topic_index_reader.open', return_value = mock_file, create=True):
            tir = topic_index_reader.TopicIndexReader('')
            self.assertEqual(tir.aquaint1, '/opt/dropbox/17-18/573/AQUAINT')
            self.assertEqual(tir.aquaint2, '/opt/dropbox/17-18/573/AQUAINT-2')

    # def test_ContentReaderReassignsAquaintAndAquaint2(self):
    #     cr = content_provider.ContentReader(aquaint2 = 'MyAquaint2Path', aquaint = 'MyAquaintPath')
    #     self.assertEqual(cr.AQUAINT_DIR, 'MyAquaintPath')
    #     self.assertEqual(cr.AQUAINT2_DIR, 'MyAquaint2Path')
    #
    # def test_ContentReadRawFile(self):
    #     cr = content_provider.ContentReader()
    #     mock_file = io.StringIO(''.join(self.storyText))
    #     with patch('content_provider.open', return_value=mock_file, create=True):
    #         articles = cr.read_raw_files('test.dat')
    #         self.assertEqual(articles[0].body[0], self.storyBody)
    #         self.assertEquals(len(articles[0].body), 1)
    #         self.assertEquals(len(articles), 1)
    #
    # def test_ContentReadSGML(self):
    #     cr = content_provider.ContentReader()
    #     mock_file = io.StringIO(''.join(self.storySGML))
    #     with patch('content_provider.open', reeturn_value=mock_file, create=True):
    #         articles = cr.read_raw_files('test.dat')
    #         self.assertEqual(len(articles[0].body), 1)

    def test_RougeScore(self):
        counter = rougescore.RougeCounter(0.5)
        rouge1 = counter.rouge_n(self.peer1, [self.model], 1)
        rouge2 = counter.rouge_n(self.peer1, [self.model], 2)

        self.assertAlmostEqual(rouge1, 0.923076923076923)
        self.assertAlmostEqual(rouge2, 0.7272727272727272)

    def test_Config(self):
        mock_file = io.StringIO(''.join(self.configText))
        with patch('sum_config.open', return_value=mock_file, create=True):
            config = sum_config.SummaryConfig('test.dat')
            self.assertEqual(config.TEAM_ID, 'test')
            self.assertEqual(config.RELEASE_TITLE, 'also test')
            self.assertFalse(config.AQUAINT)
            self.assertFalse(config.ONE_FILE)

    def test_ParagraphReader(self):
        doctree = bs4.BeautifulSoup(self.sampleXML, 'html.parser')
        textBlock = doctree.find('text')
        testArticleReader = article_reader.ArticleReader('','','')
        paraTag = textBlock.find('p')
        print('read from XML ||%s||' % paraTag.contents[0])
        modifiedText = testArticleReader.__convert_bs_string__(paraTag.contents[0])

        self.assertEqual(modifiedText, '\nThis is a test\nThis is still a test.\n')

if __name__ == '__main__':
    unittest.main()