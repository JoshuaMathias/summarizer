import unittest
import summarizer
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
                       'This is a story about summarization. It is important to have enough\n' \
                       'characters here to fill out the text. Also, it is important to summarize\n' \
                       't\n' \
                       '--- end summary: "test.dat" ---\n' \
                       'Done.\n' \

    # Not a great test, but mostly a template for mocking file reading in Python
    # (Seems readline iteration is broken in unittest mock, hence the weird StringIO invocation)
    def test_SummaryReturnsMinSizeWhenStoryIsLarger(self):
        smrzr = summarizer.Summarizer(140)
        mock_file = io.StringIO(''.join(self.storyText))
        with patch('summarizer.open', return_value=mock_file, create=True):
            summary = smrzr.summarize('test.dat')
            self.assertEqual(summary, self.summary)


if __name__ == '__main__':
    unittest.main()