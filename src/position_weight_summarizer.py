import numpy
import nltk

class WeightMatrix():
    def __init__(self, weight_file):
        weight_matrix = list()
        self.max_horizontal = 0
        for line in weight_file:
            weight_strings = line.strip().split(',')
            weights = list()
            for weight in weight_strings:
                weights.append(float(weight))
            weight_matrix.append(weights)
            self.max_horizontal = max(self.max_horizontal, len(weights))
        self.matrix = numpy.array([numpy.array(weight_value) for weight_value in weight_matrix])

    def weight_value(self, summary_line_index, horizontal_index):
        if summary_line_index >= len(self.matrix):
            summary_line_index = len(self.matrix) - 1

        if len(self.matrix[summary_line_index]) > horizontal_index:
            return self.matrix[summary_line_index][horizontal_index]
        else:
            return 0.0

class PositionWeights():
    def __init__(self, article_weight_file, sentence_weight_file):
        with open(article_weight_file, 'r') as awf:
            self.article_weights = WeightMatrix(awf)
        with open(sentence_weight_file, 'r') as swf:
            self.sentence_weights = WeightMatrix(swf)

        self.combined_weights = numpy.zeros((10, self.article_weights.max_horizontal, self.sentence_weights.max_horizontal))
        for summary_idx in range(10):
            for article_idx in range(self.article_weights.max_horizontal):
                for sentence_idx in range(self.sentence_weights.max_horizontal):
                    self.combined_weights[summary_idx, article_idx, sentence_idx] = self.combined_weight(summary_idx, article_idx, sentence_idx)

    def combined_weight(self, summary_index, article_index, sentence_index):
        return self.article_weights.weight_value(summary_index, article_index) * self.sentence_weights.weight_value(summary_index, sentence_index)

    def argmax(self, summary_index):
        idx = numpy.unravel_index(numpy.argmax(self.combined_weights[summary_index], axis=None), self.combined_weights[summary_index].shape)
        return idx

    def position_sum(self, docset):
        article_list = list()
        for article in docset.articles:
            text_list = list()
            for paragraph in article.paragraphs:
                text_list += nltk.tokenize.sent_tokenize(paragraph)
            article_list.append(text_list)

        print('ArticleIndex is of length %d' % len(article_list))
        print('Article One is of length %d' % len(article_list[0]))

        summary = list()
        summary_text = ''
        while len(summary_text.split()) < 100:
            cand_idx = self.argmax(len(summary))
            idx1 = cand_idx[0]
            idx2 = cand_idx[1]
            print('Hammering it home, index is %d %d' % (idx1, idx2))
            print('Sentence is "%s"' % article_list[idx1][idx2])
            candidate_sentence = article_list[idx1][idx2]
            if len(candidate_sentence.split()) + len(summary_text.split()) < 100:
                if len(summary_text) > 0:
                    summary_text += ' ' + candidate_sentence
                summary.append(candidate_sentence)
            else:
                break

        return summary_text



if __name__ == "__main__":
    testWeights = PositionWeights('../outputs/position_data/sample_article_data.csv', '../outputs/position_data/sample_sentence_data.csv')
    print('sample position 0, 0, 0 is %f' % testWeights.combined_weight(0, 0, 0))
    print('summary 0 article/sentence argmax is %d / %d' % testWeights.argmax(0))
