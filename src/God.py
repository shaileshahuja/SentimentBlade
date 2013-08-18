__author__ = 'Shailesh'

import copy
from collections import defaultdict
from nltk.tokenize import wordpunct_tokenize
from termcolor import colored
from nltk.corpus import stopwords,names
import math
from Sentiment import Sentiment


class God:
    stopWords = set(stopwords.words())
    engNames = set(names.words())
    GlobalAdjList = {"disappointing", "disappointed", "disappointment", "fresh", "freshly", "tasty", "delicious",
                     "poor", "badly", "sadly", "sucks", "sucked", "crispy", "yelled", "love", "loved", "loving",
                     "poorly", "underwhelming"}

    def __init__(self, lexicon, debug=False):
        self.lexicon = lexicon
        self.debug = debug

    def SetDebugParameters(self, positiveThreshold=1, negativeThreshold=-1):
        self.positiveThreshold = positiveThreshold
        self.negativeThreshold = negativeThreshold

    def PredictBase(self, adjectives):
        """
        Predict the base of the multiplier using the number of polar adjectives.
        The values have been determined experimentally to maximize results.
        """
        # Get the list of Adjectives which have sentiment polarity greater than 0.1
        PolarAdjList = [l for l in adjectives if l in self.lexicon and math.fabs(float(self.lexicon[l])) > 0.1]
        if len(PolarAdjList) > 0:
            return 12.0/len(PolarAdjList)
        #    elif len(list2) < 8:
        #        return 2.0
        else:
            return 1.0
    #    return 1.0

    def PredictMultiplier(self, word, dependencies, words, i):
        """
        Given a word, calculate how other words affect the polarity of this word.
        E.g: "not good" will change the polarity of "good" to negative.
        Returns a multiplier for the word.
        """
        # multiplier = 1.0 # start with the default multiplier of one, which means no change in polarity
        # NegativeModifiers = {"not","n't", "no", "nothing","at"}
        # PositiveModifiers = {"very","so","really", "super", "extremely"}
        # NeutralModifiers = {"neither","nor"}
        # TooExceptionList = {"good", "awesome","brilliant","kind","great","tempting","big",
        #                     "overpowering","full","filled","stuffed","perfect","rare"}
        # DilutionList = {"little", "bit"}
        # modifierSet = set()
        # for rel in dependencies:
        #     modifierSet |= dependencies[rel]
        # if i > 0 and words[i - 1].lower() == "too" and word not in TooExceptionList:
        #     if word in ["much", "many"]:
        #         multiplier = -100.0
        #     elif float(self.lexicon[word]) < 0:
        #         multiplier *= 2.0
        #     else:
        #         multiplier *= -0.5
        # elif modifierSet & NegativeModifiers:
        #     multiplier *= -1.0
        # elif modifierSet & PositiveModifiers:
        #     multiplier *= 2.0
        # elif modifierSet & NeutralModifiers:
        #     multiplier *= 0.0
        # elif i > 0:
        #     if words[i - 1].lower() == "not":
        #         multiplier *= -1.0
        #
        # if (i > 0 and words[i - 1].lower() in DilutionList) or (i > 1 and words[i - 2].lower() in DilutionList):
        #     multiplier *= 0.5
        # return multiplier
        multiplier = 1.0
        NegativeModifiers = ["not", "n't", "no", "nothing"]
        PositiveModifiers = ["very", "so", "really"]
        NeutralModifiers = ["neither", "nor"]
        TooExceptionList = ["good", "awesome", "brilliant", "kind", "great", "tempting", "big", "overpowering",
                            "full", "filled", "stuffed", "perfect", "rare"]
        if i > 0:
            if words[i-1].lower() == "not" and words[i].lower() in self.lexicon:
                multiplier *= -0.5
            elif (words[i-1].lower() in NegativeModifiers or (len(words[i-1]) > 2 and words[i-1].lower().endswith("nt") and words[i-1].lower()[-3] not in ['a','e','i','o','u']) or words[i-1].lower().endswith("n't")) \
                or (i > 1 and (words[i-2].lower() in NegativeModifiers or (len(words[i-2]) > 2 and words[i-2].lower().endswith("nt") and words[i-2].lower()[-3] not in ['a','e','i','o','u']) or
                                   words[i-2].lower().endswith("n't") or (words[i-1].lower() == "t" and words[i-2].lower() == "'")))or (i > 2 and words[i-2].lower() == "t" and words[i-3].lower() == "'"):
                multiplier *= -1.0
            elif words[i-1].lower() in PositiveModifiers:
                multiplier *= 2.0
            elif words[i-1].lower() in NeutralModifiers or (i > 1 and words[i-2].lower() in NeutralModifiers):
                multiplier *= 0.0
            elif words[i-1].lower() == "too" and words[i].lower() not in TooExceptionList and words[i].lower() in self.lexicon:
                if words[i].lower() in ["much","many"]:
                    multiplier = -100.0
                elif float(self.lexicon[words[i].lower()]) < 0:
                    multiplier *= 2.0
                else:
                    multiplier *= -0.5
        return multiplier

    def CalculateNotScore(self, notCount):
        """
        Method to calculate the reduction in overall score based on the negativity in the review.
        The values have been determined experimentally.
        Ideally, this method should not be used, as it is against the objective of this program.
        Usage will be removed later.
        """
        if notCount >= 10:
            notScore = 4
        elif notCount >= 7:
            notScore = 2
        elif notCount >= 4:
            notScore = 1
        else:
            notScore = 0
        return notScore

    def ExtractSentDetails(self, sentence):
        """
        Method to extract properties form a sentence object.
        :param sentence: The dictionary of sentence properties extracted from the JSON/XML sentence element
        """
        if "Adjectives" in sentence:
            adjList = [w.lower() for w in sentence["Adjectives"] if w.lower() not in God.stopWords and w.lower() not in God.engNames]
            adjectives = set(adjList)
        else:
            adjectives = set()
        dependencies = defaultdict(dict)
        if "Dependencies" in sentence:
            if not isinstance(sentence["Dependencies"],list):
                sentence["Dependencies"] = [sentence["Dependencies"]]
            for dep in sentence["Dependencies"]:
                line = dep.split(',')
                if len(line) != 3:
                    continue
                relation, adj, other = line
                adj, other = adj.lower(), other.lower()
                if relation in {'amod', 'acomp', 'ccomp', 'pobj', 'dep'}:
                    adj, other = other, adj
                if relation not in dependencies[adj]:
                    dependencies[adj][relation] = set()
                dependencies[adj][relation].add(other)
                if relation == 'conj':
                    adjectives.add(other)
        dictconj, other = defaultdict(dict), None
        for adj in dependencies:
            if 'conj' in dependencies[adj]:
                for other in dependencies[adj]['conj']:
                    dictconj[other] = copy.deepcopy(dependencies[adj])
        for adj in dictconj:
            for relation in dictconj[adj]:
                if relation not in dependencies[adj]:
                    dependencies[adj][relation] = set()
                dependencies[adj][relation] |= dictconj[adj][relation]
        return adjectives, dependencies

    def DumpDetails(self, sentences, notCount, label):
        """
        This method uses the same logic as predict sentiment to rate reviews.
        However, all the small details on how the calculation is done are printed for a review
        """
        AdjR = 0.0
        adjAll = []
        for sentence in sentences:
            # if sentence["Text"].startswith("Joanie is not helpful"):
            #     x = 1
            adjectives, dependencies = self.ExtractSentDetails(sentence)
            adjAll.extend(adjectives)
            allAdjectives = adjectives | God.GlobalAdjList
            AdjS = 0.0
            words = wordpunct_tokenize(sentence["Text"])
            if len(words) <= 3:
                allAdjectives |= set([x.lower() for x in words])
            for i in range(len(words)):
                word = words[i].lower()
                if word in {"but", "if"}:
                    AdjS = 0.0
                    print words[i],
                elif word in allAdjectives and word in self.lexicon:
                    multiplier = self.PredictMultiplier(word, dependencies[word], words, i)
                    score = float(self.lexicon[word]) * multiplier
                    if multiplier < 1:
                        colortext = colored(words[i] + " (" + '{:.3}'.format(score) + ")", 'red',None,['underline'])
                    elif multiplier > 1:
                        colortext = colored(words[i] + " (" + '{:.3}'.format(score) + ")", 'red',None,['bold'])
                    else:
                        colortext = colored(words[i] + " (" + '{:.3}'.format(score) + ")", 'red')
                    AdjS += score
                    print colortext,
                else:
                    print words[i],
            print
            colortext = colored("Adjectives: " + '{:.3}'.format(AdjS),'red')
            print colortext
            AdjR += AdjS
        print
        notScore = self.CalculateNotScore(notCount)
        print "Label:", label, "Not Count:", notCount
        base = self.PredictBase(adjAll)
        colortext = colored("Adjectives: " + str(AdjR) + "*" + str(base) + " - " + str(notScore) + " = " + str(AdjR*base),'red')
        print colortext

    def PredictReviewScore(self, sentences, notCount, label=0):
        """
        This method gives a score to a review.
        """
        AdjR = 0.0
        # if text.startswith("For more photos and reviews do check out fourleggedfoodies"):
        #     x = 1
        adjAll = []
        for sentence in sentences:
            adjectives, dependencies = self.ExtractSentDetails(sentence)
            adjAll.extend(adjectives)
            allAdjectives = adjectives | God.GlobalAdjList
            AdjS = 0.0
            words = wordpunct_tokenize(sentence["Text"])
            if len(words) <= 3:
                allAdjectives |= set([x.lower() for x in words])
            for i in range(len(words)):
                word = words[i].lower()
                if word in {"but", "if"}:
                    AdjS = 0.0
                elif word in allAdjectives and word in self.lexicon:
                    AdjS += float(self.lexicon[word]) * self.PredictMultiplier(word, dependencies[word], words, i)
            AdjR += AdjS
        AdjR *= self.PredictBase(adjAll)
        notScore = self.CalculateNotScore(notCount)
        finalScore = AdjR
        if self.DebugRequested(finalScore, label):
            self.DumpDetails(sentences, notCount, label)
        return finalScore

    def DebugRequested(self, score, label):
        if not self.debug:
            return False
        if label == Sentiment.NEGATIVE and score > self.positiveThreshold:
            return True
        elif label == Sentiment.POSITIVE and score < self.negativeThreshold:
            return True
        return False