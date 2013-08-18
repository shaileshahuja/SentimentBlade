# coding=utf-8
__author__ = 'shailesh'


class Review(object):
    """ Review data structure to represent one review from Yelp
    """
    def __init__(self, stars, url, date, user, review, useful, funny, cool):
        self.stars = stars
        self.url = url
        self.date = date
        self.user = user
        self.review = review
        self.useful = useful
        self.funny = funny
        self.cool = cool

    @staticmethod
    def CreateFromRawData(stars, url, date, user, review, useful, funny, cool):
        url = "http://www.yelp.com.sg" + url
        review = review.encode("ascii", "ignore")
        if useful == u' ':  # NOTE: comparison with unicode character &nbsp;, not ascii space
            useful = str(0)
        else:
            useful = str(useful[1])
        if funny == u' ':
            funny = str(0)
        else:
            funny = str(funny[1])
        if cool == u' ':
            cool = str(0)
        else:
            cool = str(cool[1])
        return Review(stars, url, date, user, review, useful, funny, cool)

    @staticmethod
    def CompareReviews(r1, r2):
        if len(r1.review) < 80 <= len(r2.review):  # if one review is very small, then that review should be ranked lower
            return -1
        if len(r2.review) < 80 <= len(r1.review):
            return 1
        if float(r1.stars) <= 3.0 < float(r2.stars):
        # if a review has less than 4 stars, then it should be ranked higher to balance the sentiment distribution
        # it was observed reviews with 4 and 5 stars form the majority of the reviews
            return 1
        if float(r2.stars) <= 3.0 < float(r1.stars):
            return -1
        if int(r1.useful)!= int(r2.useful):
            return int(r1.useful) - int(r2.useful)
        if int(r1.cool)!= int(r2.cool):
            return int(r1.cool) - int(r2.cool)
        if int(r1.funny)!= int(r2.funny):
            return int(r1.funny) - int(r2.funny)
        return len(r1.review) - len(r2.review)
