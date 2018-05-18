# Based on Brian Dusell's Python Rouge implementation
#
# see https://github.com/bdusell/rougescore
#
# I have initially copied the original code, only modifying to
# add a few features to support LING573 work and providing
# additional comments to help me understand the process
#

import collections
import six
import argparse
import string

class RougeCounter():
    def __init__(self, alpha):
        self.alpha = alpha

    # Create a generator of n-gram collections based on
    # the tokenized values in the word list
    def __ngram_generator__(self, words, n):
        queue = collections.deque(maxlen=n)
        for w in words:
            queue.append(w)
            if len(queue) == n:
                yield(tuple(queue))

    # Provide a rapid tally of values in the n-gram
    # collection generated from the word list
    def __ngram_counts__(self, words, n):
        return collections.Counter(self.__ngram_generator__(words, n))

    # Get the maximum size of the n-gram collection for
    # the word list
    def __ngram_count__(self, words, n):
        return max(len(words) - n + 1, 0)

    def __counter_overlap__(self, counter1, counter2):
        result = 0

        # For each tuple (k) and count (v) in the related n-gram
        # collection, add the minimum number of times the tuple
        # appears in either of the collections
        for k, v in six.iteritems(counter1):
            result += min(v, counter2[k])

        return result

    # In our case, numerator and denominator will always be non-negative
    # so we need to weed out zero-valued denominators
    def __safe_divide__(self, numerator, denominator):
        if denominator > 0.0:
            return numerator / denominator
        else:
            return 0.0

    # Recall value = number_of_overlapping_words / total_words_in_reference_summary
    def __recall__(self, matches, recall_total):
        return self.__safe_divide__(matches, recall_total)

    # Precision value = number_of_overlapping_words / total_words_in_system_summary
    def __precision__(self, matches, precision_total):
        return self.__safe_divide__(matches, precision_total)

    def __safe_f1__(self, matches, recall_total, precision_total):
        recall_score = self.__recall__(matches, recall_total)
        precision_score = self.__precision__(matches, precision_total)

        denom = (1.0 - self.alpha) * precision_score + self.alpha * recall_score
        if denom > 0.0:
            return (precision_score * recall_score) / denom
        else:
            return 0.0

    def __get_rouge_statistics__(self, peer, models, n):
        matches = 0
        recall_total = 0

        peer_counter = self.__ngram_counts__(peer, n)

        for model in models:
            model_counter = self.__ngram_counts__(model, n)
            matches += self.__counter_overlap__(peer_counter, model_counter)
            recall_total += self.__ngram_count__(model, n)

        precision_total = len(models) * self.__ngram_count__(peer, n)

        return matches, recall_total, precision_total

    # This is an adaptation of the standard LCS dynamic programming algorithm
    # tweaked for lower memory consumption.
    # Sequence a is laid out along the rows, b along the columns.
    # Minimize number of columns to minimize required memory
    def __lcs__(self, a, b):
        if len(a) < len(b):
            a, b = b, a

        # Sequence b now has the minimum length
        # Quit early if one sequence is empty
        if len(b) == 0:
            return 0

        # Use a single buffer to store the counts for the current row, and
        # overwrite it on each pass
        row = [0] * len(b)
        left = 0
        for ai in a:
            left = 0
            diag = 0
            for j, bj in enumerate(b):
                up = row[j]
                if ai == bj:
                    value = diag + 1
                else:
                    value = max(left, up)
                row[j] = value
                left = value
                diag = up

        # Return the last cell of the last row
        return left

    def rouge_n(self, peer, models, n):
        matches, recall_total, precision_total = self.__get_rouge_statistics__(peer, models, n)
        return self.__safe_f1__(matches, recall_total, precision_total)

    def recall_n(self, peer, models, n):
        matches, recall_total, precision_total = self.__get_rouge_statistics__(peer, models, n)
        return self.__recall__(matches, recall_total)

    def precision_n(self, peer, models, n):
        matches, recall_total, precision_total = self.__get_rouge_statistics__(peer, models, n)
        return self.__precision__(matches, precision_total)

    def rouge_l(self, peer, models):find
        matches = 0
        recall_total = 0
        for model in models:
            matches += self.__lcs__(model, peer)
            recall_total += len(model)
        precision_total = len(models) * len(peer)
        return self.__safe_f1__(matches, recall_total, precision_total)

if __name__ == "__main__":
    # Command Line Argument Parsing. Provides argument interpretation and help text.
    argparser = argparse.ArgumentParser(description = 'rougescore by team #e2jkplusplus, based on original from Brian Dusell')
    argparser.add_argument('-p', metavar='peer', help='Peer (optimal) summary')
    argparser.add_argument('-n', metavar='ngram', type=int, default=-1, help='ngram size')
    argparser.add_argument('-a', metavar='alpha', type=float, default=0.5, help='alpha weighting for rouge output')
    argparser.add_argument('models', metavar='MODEL', nargs='+', help='Proposed summary(ies)')
    args = argparser.parse_args()

    rouge_scorer = RougeCounter(args.a)
    peer = ''.join(ch for ch in args.p.lower() if ch not in set(string.punctuation)).split()
    model_list = list()
    for model in args.models:
        model_list.append(''.join(ch for ch in model.lower() if ch not in set(string.punctuation)).split())

    if args.n == -1:
        for n in range(1, 4):
            print('ROUGE %d :\t%s\tRecall %s\tPrecision %s' % (n,
                                                               rouge_scorer.rouge_n(peer, model_list, n),
                                                               rouge_scorer.recall_n(peer, model_list, n),
                                                               rouge_scorer.precision_n(peer, model_list, n)))
    else:
        print('ROUGE %d :\t%s\tRecall %s\tPrecision %s' % (args.n,
                                                           rouge_scorer.rouge_n(peer, model_list, args.n),
                                                           rouge_scorer.recall_n(peer, model_list, args.n),
                                                           rouge_scorer.precision_n(peer, model_list, args.n)))


    print('ROUGE L :\t%s' % rouge_scorer.rouge_l(peer, model_list))