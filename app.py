import os
import requests
import operator
import re
import nltk
from flask import Flask, render_template, request
from collections import Counter
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

@app.route('/', methods=['GET', 'POST'])

def index():
    errors = []
    results = {}
    if request.method == "POST":
        # get url that the person has entered
        try:
            url = request.form['url']
            r = requests.get(url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
            return render_template('index.html', errors=errors)
        if r:
            # text processing
            raw = BeautifulSoup(r.text, 'html.parser').get_text()
            nltk.data.path.append('./nltk_data/')  # set the path
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)
            # remove punctuation, count raw words
            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words)
            # save the results
            results = sorted(
                raw_word_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )
    return render_template('index.html', errors=errors, results=results)


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
