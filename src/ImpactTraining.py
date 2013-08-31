__author__ = 'Shailesh'

from collections import defaultdict
import numpy
import csv
from Sentiment import Sentiment
from God import God
from Utils import UtilMethods as util
from PerformanceTest import PerformanceTest


def ImpactTraining(docPath, lexPath, lexiconID):
    """
    Final score of the review is calculated as follows:
    (Score1*Multiplier1 + Score2*Multiplier2 ... ScoreN*MultiplierN) * BaseMultiplier = ReviewScore
    Ignoring BaseMultiplier for this training, assuming it has minimal impact (TODO: test this impact)
    ScoreK*MultiplierK/ReviewScore * 100 = PercentImpact (impact %age of word K on the final score)
    TotalAdjustment = Expected Score - FinalScore
    AdjustmentK = PercentImpact of TotalAdjustment  (total adjustment needed for word K)
    Adjustment on word K for this review = AdjustmentK/MultiplierK
    Take the mean of all adjustments, and applying to the final lexicon, to get the new lexicon
    Repeat process until there is performance improvement.
    """
    oldAccuracy = 0
    se = PerformanceTest(lexPath, docPath)
    while True:
        adjustments = defaultdict(list)
        iterator = se.GetIter()
        god = God(se.lexicon)
        expectedSentiment, predictedOverall = [], []
        while True:
            try:
                sentences, label, notCount, docId = se.NextElement(iterator)
                expectedSentiment.append(label)
                predictedScore = god.PredictReviewScore(sentences, notCount, label)
                predictedOverall.append(Sentiment.GetSentimentClass(predictedScore, 1))
                if (label == Sentiment.POSITIVE and predictedScore >= label) or (label == Sentiment.NEGATIVE and predictedScore <= label):
                    continue
                totalImpact, impactTable = god.GetImpact(sentences)
                totalAdjustment = label - predictedScore
                for word, (wordScore, multiplier) in impactTable.iteritems():
                    wordAdjustment = ((wordScore/totalImpact) * totalAdjustment) / multiplier
                    if wordAdjustment != 0:
                        adjustments[word].append(wordAdjustment)
            except StopIteration:
                break
        newAccuracy = util.accuracy(predictedOverall, expectedSentiment)
        print "Accuracy:", oldAccuracy, "--->", newAccuracy
        if newAccuracy <= oldAccuracy:
            break
        for word in adjustments:
            se.lexicon[word] = str(float(se.lexicon[word]) + numpy.mean(adjustments[word]))
        oldAccuracy = newAccuracy

    filename = "../files/lexicons/" + lexiconID + ".csv"
    handle = open(filename, 'wb')
    wr = csv.writer(handle)
    for key, value in sorted(se.lexicon.items()):
        row = [key, value]
        wr.writerow(row)
    handle.close()

if __name__ == "__main__":
    jsonFile = "../files/1000NTLKMovieReviews.json"
    textFile = "../files/1000HungryGoWhereReviews.txt"
    textSFile = "../files/100HungryGoWhereReviews.txt"
    XMLFile = "../files/1000YelpKokariEstoriatoReviews.xml"
    lexPath = "../files/lexicons/SentiWordNet_Lexicon_concise.csv"
    ImpactTraining(jsonFile, lexPath, "NLTKMovies")