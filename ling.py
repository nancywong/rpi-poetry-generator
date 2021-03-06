from os import listdir
from os import getcwd
import random, sys
import string

from textblob import TextBlob
from word import Word

import ultrasonic
import light


last_word = ""
NGRAM_SIZE = 4
all_words_dict = dict()


def main():
    setup()
    run()


def setup():
    reload(sys)
    sys.setdefaultencoding('ISO-8859-1')

    print "\nParsing texts..."
    parse_texts()


def run():
    print "\nGenerating lines..."
    print ""

    while True:
        loop()


def loop():
    lines = ''

    for _ in xrange(4): # while True
        line = get_next_line()

        f_line = string.center(line, 100)
        print f_line


def get_next_line():
    last_word = ""

    sentiment_val = get_sentiment_value()
    current_line, last_word = generate_line(sentiment_val, last_word)

    return current_line


### Parsing Functions
def parse_texts():
    texts_dir = getcwd() + "/texts"
    for dir_entry in listdir(texts_dir):
        print "..."
        text = open(texts_dir + "/" + dir_entry)
        contents = text.read()
        contents.encode('utf-8').strip()
        contents = contents.lower()
        text_to_ngrams(contents)
        text.close()


def text_to_ngrams(text):
    blob = TextBlob(text)
    ngrams = blob.ngrams(NGRAM_SIZE)
    parse_ngrams(ngrams)


def parse_ngrams(ngrams):

    global all_words_dict

    for ngram in ngrams:
        word = ngram[0]
        phrase = " ".join(ngram[1:])
        phrase_sentiment = TextBlob(phrase).sentiment.polarity

        if word in all_words_dict:
            # word is in dictionary, add phrase to word.sentiment_ngrams_dict
            all_words_dict[word].sentiment_ngrams_dict[phrase_sentiment] = phrase
        else:
            # create new word and add to all_words_dict
            new_word = Word(word, {phrase_sentiment: phrase})
            all_words_dict[word] = new_word


### Generating poetry
# Returns the next line of poetry
def generate_line(sentiment, start_word):
    line, last_word = "", start_word
    next_phrase = get_next_phrase(sentiment, start_word)
    for _ in range(get_num_lines()):
        line += " " + next_phrase
        last_word = next_phrase.split()[-1]
        next_phrase = get_next_phrase(sentiment, last_word)
    return str(line), last_word


def get_next_phrase(sentiment, word):
    global all_words_dict

    # error checking - keep trying until we get a key with values
    while word not in all_words_dict:
        # get random word
        word = random.choice(all_words_dict.keys())

    phrase = get_closest_sentiment_phrase(all_words_dict, sentiment, word)
    return phrase


def get_closest_sentiment_phrase(d, sentiment_val, word):
    # each key is a sentiment value between -1.0 and 1.0
    keys = d[word].sentiment_ngrams_dict.keys()
    closest_key = min(keys, key=lambda x:abs(x-sentiment_val))

    phrase = d[word].sentiment_ngrams_dict[closest_key]
    return phrase


### Helpers
def rand_num_lines():
    return random.randint(1, 3)


### Raspberry Pi Sensor inputs
def get_sentiment_value():
    # based on rpi light sensor
    val = light.get_light_intensity()

    val = clamp_light(val)
    return val


def get_num_lines():
    # based on rpi distance sensor
    dist = ultrasonic.get_distance()

    dist = clamp_distance(dist)

    return dist


# clamp values from 0 to 7000 to 1 to -1
def clamp_light(input):
    input = 7000.0 - input # invert
    output = (input - 3500)/3500.0

    if output < -1:
        output = -1

    if output > 1:
        output = 1

    return output 


# clamp values from 0 to 7000 to 1 to 5
def clamp_distance(input):
    output = (input / 25) + 1
	
    if output < 1:
        output = 1

    if output > 5:
        output = 5

    return int(output)


### Main
if __name__ == "__main__":
    main()
