__author__ = 'shailesh'
import numpy as np
import csv

class UtilMethods(object):
    @staticmethod
    def LoadWordsSetFromFile(filePath):
        words = set()
        file = open(filePath,'r')
        for word in file:
            words.add(word.strip())
        return words

    @staticmethod
    def LoadWordsListFromFile(filePath):
        words = []
        file = open(filePath,'r')
        for word in file:
            words.append(word.strip())
        return words

    @staticmethod
    def LoadMatrix(filePath, dimensions):
        matrix = np.empty((dimensions,dimensions),dtype=float)
        with open(filePath,'r') as file:
            for i in range(dimensions):
                print float(i)/dimensions*100, "% complete"
                data = file.readline()
                array = data.split()
                for j in range(dimensions):
                    matrix[i,j] = float(array[j])
        return matrix

    @staticmethod
    def CompareFloat(a,b):
        if abs(a-b)<0.000001:
            return True
        else:
            return False

    @staticmethod
    def LoadDictionary(filePath, length):
        with open(filePath,'r') as file:
            synDict = dict()
            antDict = dict()
            for i in range(length):
                word = file.readline().strip()
                synonyms = file.readline().split()
                antoynms = file.readline().split()
                synSet = set(synonym for synonym in synonyms)
                antSet = set(antonym for antonym in antoynms)
                synDict[word] = synSet
                antDict[word] = antSet
        return synDict, antDict

    @staticmethod
    def LoadLexiconFromCSV(filepath,isConcise = True):
        lexicon = dict()
        file = open(filepath,'rb')
        fr = csv.reader(file, delimiter = ";")
        for row in fr:
            if len(row) >= 1 and type(row[0]) == str:
                row2 = row[0].split(",")
            if isConcise:
                lexicon[row2[0]] = row2[1]
            else:
                lexicon[(row2[0],row2[1])] = row2[2]
        return lexicon

    @staticmethod
    def number_samples_with_class(predicted, label):
        count = 0
        for next in predicted:
            if next == label:
                count+=1
        return count

    @staticmethod
    def number_accurate_with_class(predicted, real, label):
        i = 0
        accurate = 0
        while i < len(predicted):
            if predicted[i] == label:
                if predicted[i] == real[i]:
                    accurate+=1
            i+=1
        return accurate

    @staticmethod
    def precision_with_class(predicted, real, label):
        predicted_count = UtilMethods.number_samples_with_class(predicted, label)
        accurate = UtilMethods.number_accurate_with_class(predicted, real, label)
        if predicted_count == 0:
            predicted_count = 0.001
        return float(accurate) / predicted_count

    @staticmethod
    def recall_with_class(predicted, real, label):
        real_count = UtilMethods.number_samples_with_class(real, label)
        accurate = UtilMethods.number_accurate_with_class(predicted, real, label)
        if real_count == 0:
            return 0
        return float(accurate) / real_count

    @staticmethod
    def f1_with_class(predicted, real, label):
        precision = UtilMethods.precision_with_class(predicted, real, label)
        recall = UtilMethods.recall_with_class(predicted, real, label)
        if precision + recall == 0:
            precision = 0.001
            recall = 0.001
        return 2* (precision * recall) / (precision + recall)

    @staticmethod
    def accuracy(predicted, real):
        i = 0
        accurate = 0
        while i < len(predicted):
            if predicted[i] == real[i]:
                accurate+=1
            i+=1
        return float(accurate)/len(real)
