from collections import defaultdict

import numpy as np


class NaiveBayesClassifier:
    def __init__(self):
        self.classes = None
        self.probability_list_word = None
        self.aprior_numbers_list = None

    def fit(self, X, y):  # y - метки для новостей, X - сами новости
        """Fit Naive Bayes classifier according to X, y."""
        link_with_class = defaultdict(dict)
        total_word_count = defaultdict(int)

        counter = defaultdict(dict)
        for i, estimation in enumerate(y):
            if estimation not in counter:
                counter[estimation] = 1
            else:
                counter[estimation] += 1
            words = X[i].split()
            for word in words:
                if word in link_with_class[estimation]:
                    link_with_class[estimation][word] += 1
                    total_word_count[word] += 1
                else:
                    link_with_class[estimation][word] = 1
                    total_word_count[word] += 1

        self.classes = list(link_with_class.keys())

        probability_list_word = defaultdict(dict)
        for m, dict_word_prob in enumerate(link_with_class):
            for word_prob in link_with_class[dict_word_prob]:
                number_in_class = int(link_with_class[dict_word_prob][word_prob]) + 1
                number_in_all_class = total_word_count[word_prob]
                probability = number_in_class / number_in_all_class
                probability_list_word[dict_word_prob][word_prob] = probability
        self.probability_list_word = probability_list_word

        aprior_numbers_list = {}
        for tag in np.unique(y):
            number = int(counter[tag]) / len(X)
            aprior_numbers_list[tag] = number
        self.aprior_numbers_list = aprior_numbers_list

    def predict(self, X):  # классификация слова (интересно, возможно, неинтересно)
        """Perform classification on an array of test vectors X."""
        predictions = []

        for text in X:
            class_probs = defaultdict(float)

            for cls in self.classes:
                class_probs[cls] += np.log(self.aprior_numbers_list[cls])

                for word in text.split():
                    if word in self.probability_list_word[cls]:
                        class_probs[cls] += np.log(self.probability_list_word[cls][word])
                    else:
                        class_probs[cls] += np.log(1 / (len(self.probability_list_word[cls]) + 1))

            max_prob_cls = max(class_probs, key=class_probs.get)
            predictions.append(max_prob_cls)
        return predictions

    def score(self, X_test, y_test):
        """Returns the mean accuracy on the given test data and labels."""
        y_pred = self.predict(X_test)

        num_correct = sum(y_pred[i] == y_test[i] for i in range(len(y_pred)))
        accuracy = num_correct / len(y_pred)

        return accuracy
