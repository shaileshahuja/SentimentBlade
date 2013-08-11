__author__ = 'shailesh'

from xml.etree import ElementTree as ET
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from time import time
__author__ = 'shailesh'

from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics, grid_search, cross_validation
import numpy as np
from sklearn.utils.extmath import density
import random

class LinearSVMClassfier(object):

    def __init__(self, categories):
        self.categories = categories

    def Lemmatize(self, lemmatizer, token, tag):
        if tag[0].lower() in {'a', 'n', 'v', 'r'}:
            return lemmatizer.lemmatize(token.lower(), tag[0].lower())
        return lemmatizer.lemmatize(token.lower())

    def LoadTestData(self, filePath):
        print "Loading dataset..."
        lemmatizer = WordNetLemmatizer()
        root = ET.parse(filePath).getroot()
        positive, negative, neutral = [], [], []
        for doc in root:
            docTokens = []
            review = doc.find('review').text
            label = doc.find('polarity').text
            confidence = doc.find('confidence').text
            if confidence != '1':
                break
            sentences = sent_tokenize(review)
            sentences = [sentences[0]] * 2 + sentences[1:]  # giving first sentence more weight by injecting words
            # commented out since the F1 score reduced by 1.5% and time consumed increased by 3 times
            # for sentence in sentences:
            #     tokens = word_tokenize(sentence)
            #     tagged_tokens = nltk.pos_tag(tokens)
            #     # filtered_tokens = filter(lambda (word, tag): word not in '.,-', tagged_tokens)
            #     lemmatized_tokens = [self.Lemmatize(lemmatizer, token, tag) + "/" + tag[0] for token, tag in tagged_tokens]
            #     docTokens.extend(lemmatized_tokens)
            # fReview = ' '.join(docTokens)  # use this when tokenization is done to lemmatize and pos tag the sentences
            fReview = ' '.join(sentences)  # use this when sentences are split
            # fReview = review  # use this if raw document needs to be used
            if label == '-1':
                negative.append(fReview)
            elif label == '1':
                positive.append(fReview)
            else:
                neutral.append(fReview)
            # documents.append((review, label))
        print 'Data loaded'
        return positive, negative, neutral

    def Trim(self, s):
        """Trim string to fit on terminal (assuming 80-column display)"""
        return s if len(s) <= 80 else s[:77] + "..."

    def Benchmark(self, clf, X_train, y_train, X_test, y_test, feature_names):
        '''
        Method to benchmark the classfier using various evaluation metrics
        '''
        print 80 * '_'
        print "Training: "
        print clf
        t0 = time()
        clf.fit(X_train, y_train)
        train_time = time() - t0
        print "train time: %0.3fs" % train_time
        # use this with GridSearchCV
        # print "Best Score:", clf.best_score_
        # print "Best parameters:", clf.best_params_
        # print "Best parameters:", clf.best_estimator_
        t0 = time()
        pred = clf.predict(X_test)
        print pred
        test_time = time() - t0
        print "test time:  %0.3fs" % test_time
        labels = np.asarray(self.categories, dtype=np.int)
        F1, precision, recall, _ = metrics.precision_recall_fscore_support(y_test, pred, labels=labels, average='weighted')
        print "f1-score:   %0.3f" % F1
        confidence = clf.decision_function(X_test)
        print "Confidence Score:", confidence
        if hasattr(clf, 'coef_'):
            print "dimensionality: %d" % clf.coef_.shape[1]
            print "density: %f" % density(clf.coef_)
            print "top 10 keywords per class:"
            for i, category in enumerate(self.categories):
                top10 = np.argsort(clf.coef_[i])[-10:]
                print self.Trim("%s: %s" % (
                    category, " ".join(feature_names[top10])))
            print
        try:
            print "classification report:"
            print metrics.classification_report(y_test, pred, target_names=self.categories)
        except ZeroDivisionError:
            width = 3
            headers = ["precision", "recall", "f1-score", "support"]
            fmt = '%% %ds' % width  # first column: class name
            fmt += '  '
            fmt += ' '.join(['% 9s' for _ in headers])
            fmt += '\n'

            headers = [""] + headers
            report = fmt % tuple(headers)
            report += '\n'

            p, r, f1, s = metrics.precision_recall_fscore_support(y_test, pred,
                                                                  labels=labels,
                                                                  average=None)

            for i, label in enumerate(labels):
                values = [categories[i]]
                for v in (p[i], r[i], f1[i]):
                    values += ["%0.2f" % float(v)]
                values += ["%d" % int(s[i])]
                report += fmt % tuple(values)

            report += '\n'
            print report

        print "confusion matrix:"
        print metrics.confusion_matrix(y_test, pred)

        print
        clf_descr = str(clf).split('(')[0]
        return clf_descr, F1, precision, recall

    def ClassifierTest(self, trainData, trainLabels, testData, testLabels):
        # split a training set and a test set
        y_train, y_test = np.asarray(trainLabels), np.asarray(testLabels)

        print "Extracting features from the training dataset using a sparse vectorizer"
        vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                                     stop_words='english', token_pattern=ur"(?u)\b\w\w+\b")  # add \/\w to include pos tags
        X_train = vectorizer.fit_transform(trainData)
        print "n_samples: %d, n_features: %d" % X_train.shape
        print

        print "Extracting features from the test dataset using the same vectorizer"
        X_test = vectorizer.transform(testData)
        print "n_samples: %d, n_features: %d" % X_test.shape
        print
        feature_names = np.asarray(vectorizer.get_feature_names())

        print 80 * '='
        print "L2 penalty, dual"
        # Train Liblinear model, features were carefully chosen after extensive experimentation
        clr = LinearSVC(loss='l2', penalty='l2', dual=True, tol=1e-3, C=0.1, class_weight= {-1: 50, 0: 30, 1: 1})
        # perform a grid search on the classifier to get the best value of C
        # clr = grid_search.GridSearchCV(svr, {'C': [0.001,0.01,0.02,0.03,0.05,0.1,0.13,0.14,0.20,0.40,0.80,1,1.13,1.35,1.75]})

        #benchmark the results of the classifier
        result = self.Benchmark(clr, X_train, y_train, X_test, y_test, feature_names)

        # classifier with keyword reduction
        # print 80 * '='
        # print "LinearSVC with L1-based feature selection"
        # result = self.Benchmark(L1LinearSVC())

        print result
        return result

    def CrossValidation(self, folds,  positive, negative, neutral):
        labels = [1] * len(positive) + [-1] * len(negative) + [0] * len(neutral)
        labels = np.asarray(labels)
        Kfolds = cross_validation.StratifiedKFold(labels, n_folds=folds)
        documents = positive + negative + neutral
        documents = np.asarray(documents)
        F1List, precList, recList = [], [], []
        for train, test in Kfolds:
            _, F1, precision, recall = self.ClassifierTest(documents[train], labels[train], documents[test], labels[test])
            F1List.append(F1)
            precList.append(precision)
            recList.append(recall)
        print "Macro Averaged Metrics:\n"
        print "F1:", np.mean(F1List)
        print "Precision:", np.mean(precList)
        print "Recall:", np.mean(recList)

    def RandomIterationAverage(self, iterations, positive, negative, neutral):
        F1List, precList, recList = [], [], []
        for i in range(iterations):
            random.shuffle(positive)
            random.shuffle(negative)
            random.shuffle(neutral)
            size = lambda x: int(len(x) / 10.0 * 9)  # function to compute training data size
            remaining = lambda x: len(x) - size(x)  # function to compute test data size
            sizePos, sizeNeg, sizeNeut = size(positive), size(negative), size(neutral)
            trainData = positive[:sizePos] + negative[:sizeNeg] + neutral[:sizeNeut]
            trainLabels = [1] * sizePos + [-1] * sizeNeg + [0] * sizeNeut
            testData = positive[sizePos:] + negative[sizeNeg:] + neutral[sizeNeut:]
            testLabels = [1] * remaining(positive) + [-1] * remaining(negative) + [0] * remaining(neutral)
            _, F1, precision, recall = self.ClassifierTest(trainData, trainLabels, testData, testLabels)
            F1List.append(F1)
            precList.append(precision)
            recList.append(recall)
        print "Macro Averaged Metrics:\n"
        print "F1:", np.mean(F1List)
        print "Precision:", np.mean(precList)
        print "Recall:", np.mean(recList)


class L1LinearSVC(LinearSVC):
    """
    class to transforn the documents to consider only important keywords
    based on the results, this classifier was rejected due to comparatively poor results
    """
    def fit(self, X, y):
        # The smaller C, the stronger the regularization.
        # The more regularization, the more sparsity.
        self.transformer_ = LinearSVC(penalty="l1",
                                      dual=True, tol=1e-3)
        X = self.transformer_.fit_transform(X, y)
        return LinearSVC.fit(self, X, y)

    def predict(self, X):
        X = self.transformer_.transform(X)
        return LinearSVC.predict(self, X)


if __name__ == "__main__":
    filePath = "/home/shailesh/SentimentRazor/files/ParsedReviewList.xml"
    categories = ['-1', '0', '1']
    svm = LinearSVMClassfier(categories)
    positive, negative, neutral = svm.LoadTestData(filePath)
    F1scores = svm.CrossValidation(10, positive, negative, neutral)