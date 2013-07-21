__author__ = 'shailesh'

import os
import json


posRoot = "/home/shailesh/nltk_data/corpora/movie_reviews/pos"
negRoot = "/home/shailesh/nltk_data/corpora/movie_reviews/neg"
outputPath = "/home/shailesh/webservice/src/classifier_v3.0/movie_reviews.txt"


def PrepareTextFile():
    with open(outputPath, 'w') as outHandle:
        for filename in os.listdir(posRoot):
            fullPath = os.path.join(posRoot, filename)
            with open(fullPath, 'r') as inHandle:
                for line in inHandle.readlines():
                    outHandle.write(line.strip())
                outHandle.write('\n')
        for filename in os.listdir(negRoot):
            fullPath = os.path.join(negRoot, filename)
            with open(fullPath, 'r') as inHandle:
                for line in inHandle.readlines():
                    outHandle.write(line.strip())
                outHandle.write('\n')


def ParseAndAppendLabels(filePath):
    command = "java -jar " + os.path.dirname(os.path.abspath(__file__)) + "/stanfordparser.jar " + "txt" + " " + filePath
    error = os.system(command)
    outputPath = os.path.join(os.path.dirname(filePath), "ParsedList.json")
    with open(outputPath,'r') as file:
        TrainingFile = file.read()
    classificationData = json.loads(TrainingFile)
    for k in range(len(classificationData["ClassificationModel"])):
        current = classificationData["ClassificationModel"][str(k + 1)]
        if "Sentences" in current:
            if not isinstance(current["Sentences"],list):
                current["Sentences"] = [current["Sentences"]]
        else:
            continue
        if k <= 1000:
            current["Label"] = 1
        else:
            current["Label"] = -1
    labelledData = json.dumps(classificationData, indent=4)
    filename = os.path.join(os.path.dirname(filePath), 'MovieReviews.json')
    with open(filename, 'w') as file:
        file.write(labelledData)

if __name__ == '__main__':
    ParseAndAppendLabels(outputPath)