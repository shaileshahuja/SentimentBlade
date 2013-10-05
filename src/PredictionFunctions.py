__author__ = 'Shailesh'


class PredictionFunctions:

    NegativeModifiers = {"not", "n't", "no", "nothing", "at"}
    PositiveModifiers = {"very", "so", "really", "super", "extremely"}
    NeutralModifiers = {"neither", "nor"}
    TooExceptionList = {"good", "awesome", "brilliant", "kind", "great", "tempting", "big",
                        "overpowering", "full", "filled", "stuffed", "perfect", "rare"}
    DilutionList = {"little", "bit"}
    # NegativeModifiers = ["not", "n't", "no", "nothing"]
    # PositiveModifiers = ["very", "so", "really"]


    @staticmethod
    def DependencyFunction(lexicon, word, dependencies, words, i):
        """
        Given a word, calculate how other words affect the polarity of this word.
        E.g: "not good" will change the polarity of "good" to negative.
        Returns a multiplier for the word.
        """
        multiplier = 1.0 # start with the default multiplier of one, which means no change in polarity

        modifierSet = set()
        for rel in dependencies:
            modifierSet |= dependencies[rel]
        if i > 0 and words[i - 1].lower() == "too" and word not in PredictionFunctions.TooExceptionList:
            if word in ["much", "many"]:
                multiplier = -100.0
            elif float(lexicon[word]) < 0:
                multiplier *= 2.0
            else:
                multiplier *= -0.5
        elif modifierSet & PredictionFunctions.NegativeModifiers:
            multiplier *= -1.0
        elif modifierSet & PredictionFunctions.PositiveModifiers:
            multiplier *= 2.0
        elif modifierSet & PredictionFunctions.NeutralModifiers:
            multiplier *= 0.0
        elif i > 0:
            if words[i - 1].lower() == "not":
                multiplier *= -1.0

        if (i > 0 and words[i - 1].lower() in PredictionFunctions.DilutionList) or (i > 1 and words[i - 2].lower() in PredictionFunctions.DilutionList):
            multiplier *= 0.5
        return multiplier


    @staticmethod
    def RelativeFunction(lexicon, word, dependencies, words, i):
        """
        Given a word, calculate how other words affect the polarity of this word.
        E.g: "not good" will change the polarity of "good" to negative.
        Returns a multiplier for the word.
        """
        multiplier = 1.0

        if i > 0:
            if words[i-1].lower() == "not" and words[i].lower() in lexicon:
                multiplier *= -0.5
            elif (words[i-1].lower() in PredictionFunctions.NegativeModifiers or (len(words[i-1]) > 2 and words[i-1].lower().endswith("nt") and words[i-1].lower()[-3] not in ['a','e','i','o','u']) or words[i-1].lower().endswith("n't")) \
                or (i > 1 and (words[i-2].lower() in PredictionFunctions.NegativeModifiers or (len(words[i-2]) > 2 and words[i-2].lower().endswith("nt") and words[i-2].lower()[-3] not in ['a','e','i','o','u']) or
                words[i-2].lower().endswith("n't") or (words[i-1].lower() == "t" and words[i-2].lower() == "'")))or (i > 2 and words[i-2].lower() == "t" and words[i-3].lower() == "'"):
                multiplier *= -1.0
            elif words[i-1].lower() in PredictionFunctions.PositiveModifiers:
                multiplier *= 2.0
            elif words[i-1].lower() in PredictionFunctions.NeutralModifiers or (i > 1 and words[i-2].lower() in PredictionFunctions.NeutralModifiers):
                multiplier *= 0.0
            elif words[i-1].lower() == "too" and words[i].lower() not in PredictionFunctions.TooExceptionList and words[i].lower() in lexicon:
                if words[i].lower() in ["much","many"]:
                    multiplier = -100.0
                elif float(lexicon[words[i].lower()]) < 0:
                    multiplier *= 2.0
                else:
                    multiplier *= -0.5
        return multiplier


    @staticmethod
    def CombinedFunction(lexicon, word, dependencies, words, i):
        """
        Given a word, calculate how other words affect the polarity of this word.
        E.g: "not good" will change the polarity of "good" to negative.
        Returns a multiplier for the word.
        """
        multiplier = PredictionFunctions.DependencyFunction(lexicon, word, dependencies, words, i)
        if multiplier == 1.0:
            multiplier = PredictionFunctions.RelativeFunction(lexicon, word, dependencies, words, i)
        return multiplier