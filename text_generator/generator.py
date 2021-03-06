import random

import nltk
from nltk import word_tokenize
#from nltk.collocations import TrigramAssocMeasures
from nltk.util import ngrams

def generate_model(list_ngrams, word, CFD, num=90):
    """
    generate model based on ngrams
    """
    list_random = list(set(list_ngrams))
    message = ''
    while len(message.split(' ')) < num:
        random.shuffle(list_random)
        word_2 = 'test'
        for item in list_random:
            if item[0] == word.lower() and item[0] != word_2:
                message += "{0} {1} {2} ".format(word, item[1], item[2])
                word = CFD[item[2]].max()
                word_2 = word
                list_random.remove(item)
                break
            else:
                continue
    return message

def generate_model_2(cfdist, word, num=15):
    """
    generate model based on CFD for single words
    http://www.nltk.org/book/ch02.html
    """
    message = word.capitalize()
    while len(message.split(' ')) < num:
        print(word, end=' ')
        word = cfdist[word].max()


def read_file(filename):
    with open(filename, "r", encoding='utf-8') as file:
        contents = file.read().replace('\n\n', ' ')
        contents = contents.replace("wrote:", ' ')
        contents = contents.replace('  ', ' ')
        contents = contents.strip("..
    return contents


def generate_using_nltk(input_text):
    words = word_tokenize(input_text.lower())
    generated_ngrams = list(ngrams(words, 3))
    bigrams = nltk.bigrams(words)
    cfd = nltk.ConditionalFreqDist(bigrams)
    #FD = nltk.FreqDist(generated_ngrams)
    print(generate_model(generated_ngrams, 'run', cfd))


def generate_using_markov(filename):
    """
    http://www.cyber-omelette.com/2017/01/markov.html
    """
    raw = read_file(filename)
    raw = word_tokenize(raw.lower())
    markov = build_chain(raw)
    generated_text = generate_message(markov)
    print(generated_text)


def build_chain(input_text):
    index = 1
    words = input_text
    chain = {}
    for word in words[index:]:
        key = words[index - 1]
        if key in chain:
            chain[key].append(word)
        else:
            chain[key] = [word]
        index += 1
    return chain


def generate_message(chain, count=100):
    word1 = random.choice(list(chain.keys()))
    message = word1.capitalize()
    while len(message.split(' ')) < count:
        word2 = random.choice(chain[word1])
        word1 = word2
        message += ' ' + word2
    return message


generate_using_markov('letsrun_1.txt')
