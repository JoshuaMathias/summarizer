import unittest
import summarizer
import content_provider
import rougescore
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
                       'This is a story about summarization. It is important to have enough ' \
                       'characters here to fill out the text. Also, it is important to summarize\n' \
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

    # Not a great test, but mostly a template for mocking file reading in Python
    # (Seems readline iteration is broken in unittest mock, hence the weird StringIO invocation)
    def test_SummaryReturnsMinSizeWhenStoryIsLarger(self):
        smrzr = summarizer.Summarizer(140)
        article = content_provider.ArticleContent(id='test.dat', body=[self.storyBody])
        summary = smrzr.summarize(article)
        self.assertEqual(summary, self.summary)

    def test_ContentReaderDefaultsAquaintAndAquaint2(self):
        cr = content_provider.ContentReader()
        self.assertEqual(cr.AQUAINT_DIR, '/opt/dropbox/17-18/573/AQUAINT')
        self.assertEqual(cr.AQUAINT2_DIR, '/opt/dropbox/17-18/573/AQUAINT-2')

    def test_ContentReaderReassignsAquaintAndAquaint2(self):
        cr = content_provider.ContentReader(aquaint2 = 'MyAquaint2Path', aquaint = 'MyAquaintPath')
        self.assertEqual(cr.AQUAINT_DIR, 'MyAquaintPath')
        self.assertEqual(cr.AQUAINT2_DIR, 'MyAquaint2Path')

    def test_ContentReadRawFile(self):
        cr = content_provider.ContentReader()
        mock_file = io.StringIO(''.join(self.storyText))
        with patch('content_provider.open', return_value=mock_file, create=True):
            articles = cr.read_raw_files('test.dat')
            self.assertEqual(articles[0].body[0], self.storyBody)
            self.assertEquals(len(articles[0].body), 1)
            self.assertEquals(len(articles), 1)

    def test_ContentReadSGML(self):
        cr = content_provider.ContentReader()
        mock_file = io.StringIO(''.join(self.storySGML))
        with patch('content_provider.open', reeturn_value=mock_file, create=True):
            articles = cr.read_raw_files('test.dat')
            self.assertEqual(len(articles[0].body), 1)

    def test_RougeScore(self):
        rouge1 = rougescore.rouge_n(self.peer1, [self.model], 1, 0.5)
        rouge2 = rougescore.rouge_n(self.peer1, [self.model], 2, 0.5)

        print("ROUGE1 = %s  ROUGE2 = %s\n" % (rouge1, rouge2))

        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()