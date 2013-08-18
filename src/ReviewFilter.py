"""
This file is to used for filtering the crawled reviews, if it is needed.
TODO: Convert this code into a class with useful functions
"""
__author__ = 'shailesh'

from XMLHandler import LoadCrawledXMLFile,DumpSortedReviews
from YelpReview import Review
import random

# load the reviews that have been crawled
filePath = "../files/CrawlerOutput.xml"
reviews = LoadCrawledXMLFile(filePath)

# sorting uses a lot of measures to have more balance in the distribution of ratings in the top 1000 reviews
reviews.sort(cmp=Review.CompareReviews)
reviews.reverse()
top1000 = reviews[:1000]

#shuffle the reviews, as they were in a predictable order, which is not good for training a classifier
random.shuffle(top1000)
SplitByRating = dict()

for review in top1000:
    if review.stars not in SplitByRating:
        SplitByRating[review.stars] = []
    SplitByRating[review.stars].append(review)

# after analysis, the frequency of reviews for different number of stars are (in the top 1000):
# 1.0 - 25
# 2.0 - 63
# 3.0 - 167
# 4.0 - 228
# 5.0 - 517

# now take a total of 200 reviews from each category for human classification
TrainingDataSet = []
TrainingDataSet.extend(SplitByRating["1.0"][:10])
TrainingDataSet.extend(SplitByRating["2.0"][:30])
TrainingDataSet.extend(SplitByRating["3.0"][:30])
TrainingDataSet.extend(SplitByRating["4.0"][:50])
TrainingDataSet.extend(SplitByRating["5.0"][:80])

# put remaining reviews in another list for machine classification
rest800 = []
rest800.extend(SplitByRating["1.0"][10:])
rest800.extend(SplitByRating["2.0"][30:])
rest800.extend(SplitByRating["3.0"][30:])
rest800.extend(SplitByRating["4.0"][50:])
rest800.extend(SplitByRating["5.0"][80:])

# doing this for no reason
random.shuffle(rest800)

# now combine both lists
finalreviewslist = []
finalreviewslist.extend(TrainingDataSet)
finalreviewslist.extend(rest800)

# now dump the output to xml file
filePath = "../files/FinalReviewsList.xml"
DumpSortedReviews(finalreviewslist,filePath)