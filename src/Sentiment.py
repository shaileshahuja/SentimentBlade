__author__ = 'Shailesh'


class Sentiment:
    POSITIVE = 1
    NEGATIVE = -1
    NEUTRAL = 0

    @staticmethod
    def GetSentimentClass(score, threshold=1):
        """
        This method returns the type of sentiment given the score of the review.
        :param score: The score of a review
        :param threshold: If score is higher than this threshold, review is considered positive
                          If score is lower than -threshold, review is considered negative
        """
        if score > threshold:
            return Sentiment.POSITIVE
        elif score < -threshold:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL