import os
import requests
import operator
import re
import nltk
import json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from collections import Counter
from bs4 import BeautifulSoup
from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
q = Queue(connection=conn)

from models import *

def count_and_save_words(url):

    errors = []

    try:
        r = requests.get(url)
    except:
        errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
        return {"error": errors}

    # text processing
    raw = BeautifulSoup(r.text, features="html.parser").get_text()
    nltk.data.path.append('./nltk_data/')  # set the path
    tokens = nltk.word_tokenize(raw)
    text = nltk.Text(tokens)

    # remove punctuation, count raw words
    nonPunct = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in text if nonPunct.match(w)]
    raw_word_count = Counter(raw_words)
    # save the results
    try:
        result = Result(
            url=url,
            result_all=raw_word_count,
        )
        db.session.add(result)
        db.session.commit()
        return result.id
    except:
        errors.append("Unable to add item to database.")
        return {"error": errors}


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def get_counts():
    # get url that the person has entered
    data = json.loads(request.data.decode())
    url = data['url']
    print(url)
    if 'http://' not in url[:7]:
        url = 'http://' + url
    job = q.enqueue_call(
        func=count_and_save_words, args=(url,), result_ttl=5000
    )
    return(job.get_id())

@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        if not type(job.result) is dict:
            result = Result.query.filter_by(id=job.result).first()
            results = sorted(
                result.result_all.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:20]
            db.session.delete(result)
            db.session.commit()
            return jsonify(results)
        else:
            return jsonify(job.result), 400
    else:
        return "Nay!", 202


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
