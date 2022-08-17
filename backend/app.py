from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import pipeline


# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

model = pipeline("ner", grouped_entities=True,
                 model="tokeron/alephbert-finetuned-metaphor-detection")


@app.route('/detect', methods=['GET'])
def detect():
    # get the text param
    text = request.args.get('text')
    response_object = {}

    res = model(text)

    # remove from res its elements with key "score" (float cannot be jsonified)
    res = [{k: v for k, v in r.items() if k != "score"} for r in res]
    res = add_word_index(res, text)
    # add res to response_object
    response_object["result"] = res
    return jsonify(response_object)


def add_word_index(res, text):
    word_indices = get_word_indices(text)
    for r in res:
        r["word_index"] = get_word_at_index(word_indices, r["start"])
    return res


# given a list of word indices and a number, return the word at that index
def get_word_at_index(indices, index):
    for position, (start, end) in enumerate(indices):
        if start <= index <= end:
            return position
    return None


# given a text, get start and end indices of all words
def get_word_indices(text):
    words = text.split()
    indices = []
    offset = 0
    for i, word in enumerate(words):
        indices.append((offset, offset + len(word)))
        offset += len(word) + 1
    return indices


if __name__ == '__main__':
    app.run()
