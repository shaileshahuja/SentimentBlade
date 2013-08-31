__author__ = 'Shailesh'

from Sentiment import Sentiment


class God:

    @staticmethod
    def CompareAngels(angel1, angel2, sentences):
        if angel1 is None or angel2 is None:
            return
        label1 = Sentiment.GetSentimentClass(angel1.PredictReviewScore(sentences))
        label2 = Sentiment.GetSentimentClass(angel2.PredictReviewScore(sentences))
        if label1 != label2:
            angel1.DumpDetails(sentences)
            angel2.DumpDetails(sentences)
