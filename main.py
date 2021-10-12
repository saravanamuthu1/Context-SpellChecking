from flask import Flask, render_template, request, redirect,abort,flash
from textblob import TextBlob
from spellchecker import SpellChecker
import re
import getpass
import os
import sys

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    dict_file = open("C:/Users/suhar/flask-projects/spell-check/static/dict.txt", 'r')
    corrections_file = open('suggestions.txt', 'w')

    correctwords = []
    misspelled = []
    list1 = []
    candidates = []
    possible = []
    txt = ""
    correct = ""

    dictionary = dict_file.read().split('\n')
    dictionary.pop()
    dict_file.close()

    if request.method == "POST":
        txt = request.form.get('val')
        misspellings = txt.split(' ')

        def sub_cost(source_char, target_char):
            if source_char == target_char:
                return 0
            elif (source_char == 'a' and target_char == 'e') or (source_char == 'e' and target_char == 'a'):
                return 1  # see (ii)
            elif (source_char == 's' and target_char == 'c') or (source_char == 'c' and target_char == 's'):
                return 1  # see (iii)
            else:
                return 2

        def ins_cost(first_or_last, char):
            return 1 if not first_or_last else 2  # see (i)

        def del_cost(first_or_last, char):
            if first_or_last:
                return 4  # see (i) and (vi)
            elif char == 'c':  # see (iv)
                return 4
            elif char == 'v':  # see (v)
                return 4
            else:
                return 1

        def min_distance(target, source):
            n = len(target)
            m = len(source)

            distance = [[0 for x in range(m + 1)] for x in range(n + 1)]

            # the weird boolean expressions in the cost functions tell if at the beginning/end of a word
            # see (i)
            for i in range(1, n + 1):
                distance[i][0] = distance[i - 1][0] + ins_cost(i == 1 or i == n + 1, target[i - 1])

            for j in range(1, m + 1):
                distance[0][j] = distance[0][j - 1] + del_cost(j == 1 or j == m + 1, source[j - 1])

            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    distance[i][j] = min(
                        distance[i - 1][j] + ins_cost(i == 1 or i == n + 1 or j == 1 or j == m + 1, target[i - 1]),
                        distance[i - 1][j - 1] + sub_cost(source[j - 1], target[i - 1]),
                        distance[i][j - 1] + del_cost(i == 1 or i == n + 1 or j == 1 or j == m + 1, source[j - 1]))

            return distance[n][m]

        for word in misspellings:
            possible=[]
            abs_min = min_distance(dictionary[0], word)
            correction = dictionary[0]
            it = 0
            for target in dictionary[1:len(dictionary)]:
                new_min = min_distance(target, word)
                if new_min <= abs_min:
                    abs_min = new_min
                    correction = target
                    if abs_min <= 3:
                        possible.append(correction)
                    if it == 0:
                        misspelled.append(word)
                else:
                    if it == 0:
                        correctwords.append(word)
                it += 1
            candidates.append(', '.join(possible))
            list1.append(correction)
            correct = ' '.join(list1)

            corrections_file.write(word + ' --> ' + correction + '\n')

        corrections_file.close()

    return render_template('index.html',a=txt , correct = correct, misspelled=misspelled,list1=list1,list2=candidates,len=len(misspelled) ,len1=len(list1))


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
