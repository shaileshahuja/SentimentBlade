__author__ = 'shailesh'

from sklearn.svm import LinearSVC
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from time import time
from sklearn import metrics
import numpy as np
from sklearn.utils.extmath import density

categories = [
    'alt.atheism',
    'talk.religion.misc',
    'comp.graphics',
    'sci.space',
    ]

print "Loading 20 newsgroups dataset for categories:"
print categories if categories else "all"

data_train = fetch_20newsgroups(subset='train', categories=categories)

data_test = fetch_20newsgroups(subset='test', categories=categories)
print 'data loaded'

categories = data_train.target_names    # for case categories == None


def size_mb(docs):
    return sum(len(s.encode('utf-8')) for s in docs) / 1e6

data_train_size_mb = size_mb(data_train.data)
data_test_size_mb = size_mb(data_test.data)

print("%d documents - %0.3fMB (training set)" % (
    len(data_train.data), data_train_size_mb))
print("%d documents - %0.3fMB (training set)" % (
    len(data_test.data), data_test_size_mb))
print "%d categories" % len(categories)
print

# split a training set and a test set
y_train, y_test = data_train.target, data_test.target

print "Extracting features from the training dataset using a sparse vectorizer"
vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                             stop_words='english', token_pattern=ur"(?u)\b\w\w+\b")
X_train = vectorizer.fit_transform(data_train.data)
print "n_samples: %d, n_features: %d" % X_train.shape
print

print "Extracting features from the test dataset using the same vectorizer"
X_test = vectorizer.transform(data_test.data)
print "n_samples: %d, n_features: %d" % X_test.shape
print
feature_names = np.asarray(vectorizer.get_feature_names())


def trim(s):
    """Trim string to fit on terminal (assuming 80-column display)"""
    return s if len(s) <= 80 else s[:77] + "..."



###############################################################################
# Benchmark classifiers
def benchmark(clf):
    print 80 * '_'
    print "Training: "
    print clf
    t0 = time()
    clf.fit(X_train, y_train)
    train_time = time() - t0
    print "train time: %0.3fs" % train_time

    t0 = time()
    pred = clf.predict(X_test)
    test_time = time() - t0
    print "test time:  %0.3fs" % test_time

    score = metrics.f1_score(y_test, pred)
    print "f1-score:   %0.3f" % score

    if hasattr(clf, 'coef_'):
        print "dimensionality: %d" % clf.coef_.shape[1]
        print "density: %f" % density(clf.coef_)
        print "top 10 keywords per class:"
        for i, category in enumerate(categories):
            top10 = np.argsort(clf.coef_[i])[-10:]
            print trim("%s: %s" % (
                category, " ".join(feature_names[top10])))
        print

    print "classification report:"
    print metrics.classification_report(y_test, pred,
                                        target_names=categories)
    print "confusion matrix:"
    print metrics.confusion_matrix(y_test, pred)

    print
    clf_descr = str(clf).split('(')[0]
    return clf_descr, score, train_time, test_time

results = []
for penalty in ["l2", "l1"]:
    print 80 * '='
    print "%s penalty" % penalty.upper()
    # Train Liblinear model
    results.append(benchmark(LinearSVC(loss='l2', penalty=penalty,
                                       dual=False, tol=1e-3)))

class L1LinearSVC(LinearSVC):

    def fit(self, X, y):
        # The smaller C, the stronger the regularization.
        # The more regularization, the more sparsity.
        self.transformer_ = LinearSVC(penalty="l1",
                                      dual=False, tol=1e-3)
        X = self.transformer_.fit_transform(X, y)
        return LinearSVC.fit(self, X, y)

    def predict(self, X):
        X = self.transformer_.transform(X)
        return LinearSVC.predict(self, X)

print 80 * '='
print "LinearSVC with L1-based feature selection"
results.append(benchmark(L1LinearSVC()))

for result in results:
    print result