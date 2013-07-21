__author__ = 'shailesh'

import os
import sys
import math
from nltk.tokenize import wordpunct_tokenize
from nltk.corpus import stopwords,names
import json
from Utils import UtilMethods as util
def classify(predicted, lower, upper):
    if predicted > lower:
        return 1
    elif predicted < upper:
        return -1
    else:
        return 0

def PredictBase(adjectives, lexicon):
    list2 = [l for l in adjectives if l in lexicon and math.fabs(float(lexicon[l])) > 0.1]
    if 0 < len(list2):
        return 12.0/len(list2)
    #    elif len(list2) < 8:
    #        return 2.0
    else:
        return 1.0
#    return 1.0

def PredictMultiplier(i, words, lexicon):
    multiplier = 1.0
    NegativeModifiers = ["not","n't", "no", "nothing"]
    PositiveModifiers = ["very","so","really"]
    NeutralModifiers = ["neither","nor"]
    TooExceptionList = ["good", "awesome","brilliant","kind","great","tempting","big","overpowering","full","filled","stuffed","perfect","rare"]
    if i > 0:
        if words[i-1].lower() == "not" and words[i].lower() in lexicon:
            multiplier*=-0.5
        elif (words[i-1].lower() in NegativeModifiers or (len(words[i-1]) > 2 and words[i-1].lower().endswith("nt") and words[i-1].lower()[-3] not in ['a','e','i','o','u']) or words[i-1].lower().endswith("n't")) \
            or (i > 1 and (words[i-2].lower() in NegativeModifiers or (len(words[i-2]) > 2 and words[i-2].lower().endswith("nt") and words[i-2].lower()[-3] not in ['a','e','i','o','u']) or
                               words[i-2].lower().endswith("n't") or (words[i-1].lower() == "t" and words[i-2].lower() == "'")))or (i > 2 and words[i-2].lower() == "t" and words[i-3].lower() == "'"):
            multiplier *=-1.0
        elif words[i-1].lower() in PositiveModifiers:
            multiplier *= 2.0
        elif words[i-1].lower() in NeutralModifiers or (i > 1 and words[i-2].lower() in NeutralModifiers):
            multiplier *= 0.0
        elif words[i-1].lower() == "too" and words[i].lower() not in TooExceptionList and words[i].lower() in lexicon:
            if words[i].lower() in ["much","many"]:
                multiplier = -100.0
            elif float(lexicon[words[i].lower()]) < 0:
                multiplier *= 2.0
            else:
                multiplier *= -0.5
    return multiplier

def CalculateNotScore(notCount):
    if notCount >=10:
        notScore = 4
    elif notCount >=7:
        notScore = 2
    elif notCount >=4:
        notScore = 1
    else:
        notScore = 0
    return notScore

def PredictSentiment(sentences, lexicon, notCount):
    AdjR = 0.0
    # if text.startswith("For more photos and reviews do check out fourleggedfoodies"):
    #     x = 1
    adjAll = []
    for sentence in sentences:
        if "Adjectives" in sentence:
            if not isinstance(sentence["Adjectives"],list):
                sentence["Adjectives"] = [sentence["Adjectives"]]
            adjList = [w.lower() for w in sentence["Adjectives"] if w.lower() not in stopWords and w.lower() not in engnames]
            adjAll.extend(adjList)
            adjectives = set(adjList)
        else:
            adjectives = set()
        ExtraAdjectives = adjectives | GlobalAdjList
        AdjS = 0.0
        words = wordpunct_tokenize(sentence["Text"])
        if len(words) <=3:
            ExtraAdjectives|= set([x.lower() for x in words])
        for i in range(len(words)):
            if words[i].lower() in ExtraAdjectives and words[i].lower() in lexicon:
                AdjS += float(lexicon[words[i].lower()])*PredictMultiplier(i,words, lexicon)
        sentence["Label"] = classify(AdjS,0,0)
        AdjR+=AdjS
    AdjR *= PredictBase(adjAll, lexicon)
    notScore = CalculateNotScore(notCount)
    return AdjR - notScore

def PredictAndAppendLabel(classificationData):
    for k in range(len(classificationData["ClassificationModel"])):
        current = classificationData["ClassificationModel"][str(k + 1)]
        notCount = current["NotCount"]
        if "Sentences" in current:
            if not isinstance(current["Sentences"],list):
                current["Sentences"] = [current["Sentences"]]
            sentences = current["Sentences"]
        else:
            continue
        current["Label"] = classify(PredictSentiment(sentences, lexicon, notCount),1,1)
    return classificationData

filePath = "/home/shailesh/webservice/src/classifier_v3.0/samples.txt"
os.system("java -jar stanfordparser.jar txt " + filePath)
GlobalAdjList = {"disappointing","disappointed","fresh","freshly","tasty","delicious","poor","disappointment","badly","sadly","sucks","sucked","crispy","yelled","love","loved","loving","amazing"}
stopWords = set(stopwords.words("english"))
engnames = set(names.words())
filename = os.path.join(os.path.dirname(filePath),"ParsedList.json")
with open(filename,'r') as file:
    TrainingFile = file.read()
lexicon = util.LoadLexiconFromCSV(os.path.join(os.path.dirname(sys.argv[0]),"SentiWordNet_Lexicon_concise.csv"))
classificationData = json.loads(TrainingFile)
classifiedData = json.dumps(PredictAndAppendLabel(classificationData), indent = 4)
filename = os.path.join(os.path.dirname(filePath), 'PredictedList.json')
with open(filename,'w') as file:
    file.write(classifiedData)

print "Classification complete. Final output stored at:," + filename