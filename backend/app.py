from flask import Flask, jsonify, request
from flask_cors import CORS
from transformers import pipeline
import pandas as pd
from dotenv import load_dotenv
import os

# Get the absolute path to the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path=os.path.join(parent_dir, '.env'))

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

model = pipeline("ner", grouped_entities=True,
                 model="tokeron/BEREL_Piyyut")


# READ GROUND TRUTH DATA (PIYYUT CORPUS). WE ALLOW THE USER TO SELECT FROM THE PIYYUT CORPUS
# read ground_truth/piyyut_text.csv into a dataframe, utf-8 encoding
piyyut_texts = pd.read_csv("ground_truth/piyyut_texts.csv", encoding="utf-8")
# strip all leading and trailing whitespaces from the "name" column
piyyut_texts["name"] = piyyut_texts["name"].str.strip()
# read ground_truth/piyyut_annotations.csv into a dataframe, utf-8 encoding
piyyut_annotations = pd.read_csv("ground_truth/piyyut_annotations.csv", encoding="utf-8")



@app.route('/detect', methods=['GET'])
def detect():
    # get the text param
    text = request.args.get('text')
    response_object = {}

    annotations = model(text)

    # for each key "score" in res, cast its value to string (float cannot be jsonified)
    for annot in annotations:
        annot["score"] = str(annot["score"])

    annotations = add_word_index(annotations, text)
    # add res to response_object
    response_object["result"] = annotations
    return jsonify(response_object)


# create a route "piyyutim" that returns all the name of the piyyutim as a json
@app.route('/piyyutim', methods=['GET'])
def piyyutim():
    # a paramater called "names" is optional, and may contain a list of piyyutim names for which to return the texts
    names = request.args.get('names')
    response_object = {}

    # if names is None, return all piyyutim names:
    if names is None:
        response_object["result"] = piyyut_texts["name"].tolist()
        return jsonify(response_object)

    # else, return the texts of the piyyutim in names
    names = names.split(",")

    # for each piyyut in names, get its text and annotations
    response_object["result"] = []
    for name in names:
        text = piyyut_texts[piyyut_texts["name"] == name].iloc[0].to_dict()
        text_id = text["id"]
        annotations = piyyut_annotations[piyyut_annotations["text_id"] == text_id].to_dict("records")
        annotations = split_multiword_annotations(annotations)
        # add to each annotation a "score" key with value 1.0, rename some keys, and add word_index
        for annotation in annotations:
            annotation["score"] = "1" # it is string because float cannot be jsonified
            # rename key "start_offset" to "start"
            annotation["start"] = annotation.pop("start_offset")
            # rename key "end_offset" to "end"
            annotation["end"] = annotation.pop("end_offset")
            # add word_index
            annotation = add_word_index([annotation], text["fulltext"])[0]
        response_object["result"].append({"text": text, "annotations": annotations})
    
    return jsonify(response_object)

    # response_object["result"] = piyyut_texts[piyyut_texts["name"].isin(names)].to_dict("records")
    # return jsonify(response_object)


def split_multiword_annotations(annotations : list):
    # split multiword annotations into single word annotations
    # if the "phrase" key contains multiple words, split it into multiple annotations
    # maintain the "start_offset" and "end_offset" keys according to the split
    new_annotations = []
    for annot in annotations:
        phrase = annot["phrase"].strip()
        start = annot["start_offset"]
        if " " in phrase:
            words = phrase.split()
            for word in words:
                new_annot = annot.copy()
                new_annot["phrase"] = word
                new_annot["start_offset"] = start
                new_annot["end_offset"] = start + len(word)
                new_annotations.append(new_annot)
                start += len(word) + 1
        else:
            new_annotations.append(annot)

    return new_annotations


def add_word_index(annotations : list, text):
    word_indices = get_word_indices(text)
    for annot in annotations:
        annot["word_index"] = get_word_at_index(word_indices, annot["start"])
    return annotations


# given a list of word indices and a number, return the word at that index
def get_word_at_index(word_indices, index):
    for position, (start, end) in enumerate(word_indices):
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
    port = int(os.getenv('VUE_APP_FLASK_SERVER_PORT', 5000))  # Use 5000 as default if FLASK_SERVER_PORT is not set
    print("VUE_APP_FLASK_SERVER_PORT from .env: " + str(os.getenv('VUE_APP_FLASK_SERVER_PORT')))
    print("Starting server on port " + str(port))
    app.run(host='0.0.0.0', port=port)
