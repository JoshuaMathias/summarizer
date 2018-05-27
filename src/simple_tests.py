import unittest
import summarizer
import article_reader
import topic_index_reader
import article_content
import rougescore
import sum_config
import sentence_distance
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

        self.samplePara = '  This starts with a tab\t and then cr\n   and then a thing happens like that.'
        self.fixedPara =  'This starts with a tab and then cr and then a thing happens like that.'

        self.para1Sample ="Ziggy played guitar, jamming good with Weird and Gilly and the spiders from Mars. He played it left hand but made it too far; became the special man. Then we were Ziggy's band"
        self.para2Sample ="Now Ziggy really sang, screwed up eyes and screwed down hairdo like some cat from Japan. He could lick 'em by smiling. He could leave 'em to hang. Came on so loaded man. Well hung and snow white tan."
        self.para3Sample ="So where were the spiders? While the fly tried to break our balls with just the beer light to guide us. So we bitched about the fans and should we crush his sweet hands?"

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

    def test_RougeScore(self):
        counter = rougescore.RougeCounter(0.5)
        rouge1 = counter.rouge_n(self.peer1, [self.model], 1)
        rouge2 = counter.rouge_n(self.peer1, [self.model], 2)

        self.assertAlmostEqual(rouge1, 0.923076923076923)
        self.assertAlmostEqual(rouge2, 0.7272727272727272)

    def test_Config(self):
        mock_file = io.StringIO(self.configText)
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
        modifiedText = testArticleReader.__convert_bs_string__(paraTag.contents[0])

        self.assertEqual(modifiedText, '\nThis is a test\nThis is still a test.\n')

    def test_ParagraphReaderFormatting(self):
        testArticleReader = article_reader.ArticleReader('','','')
        article = article_content.Article('test')
        testArticleReader.__add_paragraph__(article, self.samplePara)

        self.assertEqual(article.paragraphs[0], self.fixedPara)

    def test_TokenizeOnlyIfAlnumCharactersPresent(self):
        sample_sentence = 'If I told you 100 times, this is the 99th.'
        sample_tokens = sentence_distance.sentence_tokens_with_alpha_only(sample_sentence)
        self.assertEqual(len(sample_tokens), 9)
        self.assertEqual(sample_tokens[-1], '99th')

    def sampleArticle(self):
        sample_article = article_content.Article('test')
        sample_article.paragraphs.append(self.para1Sample)
        sample_article.paragraphs.append(self.para2Sample)
        sample_article.paragraphs.append(self.para3Sample)

        return sample_article

    def test_ArticleTokenize(self):
        sample_article = self.sampleArticle()

        tokenized_article = sentence_distance.TokenizedArticle(sample_article)

        self.assertEqual(3, len(tokenized_article.paragraphs))
        self.assertEqual(3, len(tokenized_article.paragraphs[0]))

    def test_ArticleStatisticsSetup(self):
        sample_article = self.sampleArticle()

        tokenized_article = sentence_distance.TokenizedArticle(sample_article)

        self.assertEqual(3, len(tokenized_article.statistics))
        self.assertEqual(tokenized_article.max_sentences, len(tokenized_article.statistics[0]))

    def test_PeerSummary(self):
        mock_file = io.StringIO('this thing.\nis acting as.\na simple.\ntest of summarization.\n')
        with patch('sentence_distance.open', return_value=mock_file, create=True):
            summary = sentence_distance.Summary('test.dat')
            self.assertEqual(4, len(summary.line_tokens))

    def test_JaccardDistance(self):
        tokens1 = sentence_distance.sentence_tokens_with_alpha_only(self.para1Sample)
        tokens2 = sentence_distance.sentence_tokens_with_alpha_only(self.para2Sample)

        self.assertAlmostEqual(1.0, sentence_distance.reverse_jaccard_distance_value(set(tokens1), set(tokens1)))
        self.assertGreater(0.09, sentence_distance.reverse_jaccard_distance_value(set(tokens1), set(tokens2)))

    def test_CosineDistance(self):
        tokens1 = sentence_distance.sentence_tokens_with_alpha_only(self.para1Sample)
        tokens2 = sentence_distance.sentence_tokens_with_alpha_only(self.para2Sample)

        self.assertAlmostEqual(1.0, sentence_distance.cosine_similarity_ngrams(set(tokens1), set(tokens1)))
        self.assertLess(0.15, sentence_distance.cosine_similarity_ngrams(set(tokens1), set(tokens2)))

    def test_StatisticsGatherer(self):
        docset = article_content.DocSet('test', 'test')
        docset.topic_id = 'Test'
        article = article_content.Article('test')
        article.paragraphs.append(self.para1Sample)
        article.paragraphs.append(self.para2Sample)
        docset.articles.append(article)
        tkn_docset = sentence_distance.TokenizedDocSet(docset)
        mock_file = io.StringIO('Ziggy played guitar jamming.\nNow Ziggy really sang.\nWhere were the spiders?\n')
        with patch('sentence_distance.open', return_value=mock_file, create=True):
            summary = sentence_distance.Summary('test.dat')
            for tkn_art in tkn_docset.articles:
                tkn_art.compare_summary(summary)
            self.assertLess(0.0, tkn_docset.articles[0].statistics[0, 0, 0])


if __name__ == '__main__':
    unittest.main()