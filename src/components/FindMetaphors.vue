<template>
  <div id="main" class="ma-5">
    <v-row>
      <v-col cols="7">
        <v-textarea
          v-model="input"
          clearable
          filled
          shaped
          label="טקסט/ים לזיהוי"
          clear-icon="mdi-close-circle"
          no-resize
          rows="8"
          hide-details
        >
        </v-textarea>
      </v-col>
      <v-col cols="4">
        <div class="mt-4">
          <v-slider
            v-model="score"
            :min="0"
            :max="1"
            :step="0.1"
            thumb-label="always"
            :thumb-size="25"
            label="רמת דיוק"
            hide-details
          ></v-slider>
          <!-- <div class="text-caption">מציג 100% מהתיוגים.</div> -->
          <!-- Add a button to download JSON file from the data -->
          <v-row dense>
            <v-col cols="7">
              <v-btn
                class="mt-3 primary"
                @click="downloadJSON()"
                :disabled="modelAnnotations.length == 0"
              >
                הורדת תיוגים כקובץ JSON
              </v-btn>
            </v-col>
            <!-- Add a textfield for corpus name -->
            <v-col cols="5">
              <v-text-field
                v-model="corpus_name"
                filled
                dense
                shaped
                label="שם הקורפוס"
                hide-details
                :disabled="modelAnnotations.length == 0"
              ></v-text-field>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>
    <v-row dense class="mt-2" align="center">
      <v-col cols="1">
        <v-btn class="primary" @click="sendTexts()"> תיוג </v-btn>
      </v-col>
      <v-col cols="2"> ({{ texts.length }} טקסטים זוהו) </v-col>
    </v-row>
    <!-- Present each text next to its annotated result. -->
    <v-row v-for="(orig, index) in modelAnnotations" :key="index">
      <v-col cols="5">
        <v-card outlined color="#F5F5F5">
          <v-card-title> תיוג מודל #{{ index + 1 }} </v-card-title>
          <v-card-text class="black--text">
            <span
              v-html="annotateText(texts[index], orig, index, false)"
            ></span>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="5">
        <v-card outlined color="#F5F5F5">
          <v-card-title> תיוג משתמש #{{ index + 1 }} </v-card-title>
          <v-card-text :id="cardId(index)" class="black--text">
            <span
              v-html="annotateText(texts[index], userAnnotations[index], index)"
            ></span>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="2">
        <div
          class="text-body-2 ml-10"
          style="text-align: left; line-height: 17px"
        >
          Model Recall: {{ getRecall(index) * 100 }}
          <br />
          Precision: {{ getPrecision(index) * 100 }}
          <br />
          TP: {{ getTruePositives(index) }}
          <br />
          FN: {{ getFalseNegatives(index) }}
          <br />
          FP: {{ getFalsePositives(index) }}
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import axios from "axios";
import { flaskAddr } from "@/flask_addr";

export default {
  name: "FindMetaphors",
  data() {
    return {
      input: "", // user input is turned into separate texts (see computed.texts)
      modelAnnotations: [],
      userAnnotations: [], // ground truth, model annotationes are evaluated against them.
      score: 0.3, // threshold for annotations' score
      corpus_name: "no_name",
    };
  },
  computed: {
    texts() {
      // split user input into separate texts
      // a line break separates between texts (actually, two line breaks)
      if (this.input == "") {
        return [];
      }
      return this.input.trim().split(/\n{2,}/);
    },
  },
  watch: {
    input(newInput) {
      // when user input changes, clear previous annotations
      // clear annotations if input is empty or null
      if (!newInput) {
        this.input = "";
        this.modelAnnotations = [];
        this.userAnnotations = [];
        this.corpus_name = "no_name";
      }
    },
  },
  methods: {
    downloadJSON() {
      // download the texts and annotations as a JSON file
      var data = {
        corpus: {
          name: this.corpus_name,
          data: {
            texts: [],
          },
        },
      };

      // iterate each text in texts, and add it to the JSON
      this.texts.forEach((text, index) => {
        data.corpus.data.texts.push({
          name: `text${index + 1}`,
          full_text: text,
        });
      });

      // add a "tags" array with a single object {name: "metaphor"}
      data.corpus.data.tags = [{ name: "metaphor" }];

      // add an "annotations" array with all the annotations.
      // each object in the array has the following keys:
      // - "text_name" with the text name (e.g., "text1")
      // - "tag" : "metaphor"
      // - "start" : start index of the annotation
      // - "end" : end index of the annotation
      // - "user": "user" | "model"
      // start generating the JSON
      data.corpus.data.annotations = [];
      this.modelAnnotations.forEach((annotations, i) => {
        // iterate each annotation in annotations, and add it to the JSON
        annotations.forEach((annotation, j) => {
          // add the annotation to the JSON
          data.corpus.data.annotations.push({
            text_name: `text${i + 1}`,
            tag: "metaphor",
            start: annotation.start,
            end: annotation.end,
            user: "Model",
          });
        });
      });
      this.userAnnotations.forEach((annotations, i) => {
        // iterate each annotation in annotations, and add it to the JSON
        annotations.forEach((annotation, j) => {
          // add the annotation to the JSON
          data.corpus.data.annotations.push({
            text_name: `text${i + 1}`,
            tag: "metaphor",
            start: annotation.start,
            end: annotation.end,
            user: "User",
          });
        });
      });

      // stringify and indent the JSON
      var jsonStr = JSON.stringify(data, null, 2);

      // download the JSON file with the name corpus_name.json
      this.download(`${this.corpus_name}.json`, jsonStr);
    },
    // from https://stackoverflow.com/questions/3665115/how-to-create-a-file-in-memory-for-user-to-download-but-not-through-server
    download(filename, text) {
      var element = document.createElement("a");
      element.setAttribute(
        "href",
        "data:text/plain;charset=utf-8," + encodeURIComponent(text)
      );
      element.setAttribute("download", filename);

      element.style.display = "none";
      document.body.appendChild(element);

      element.click();

      document.body.removeChild(element);
    },
    getRecall(textIndex) {
      if (this.userAnnotations[textIndex].length == 0) return 1; // empty case

      // calculates the recall of the model annotations compared to the user annotations (ground truth).
      var tp = this.getTruePositives(textIndex);
      var fn = this.getFalseNegatives(textIndex);

      // recall = tp / (tp + fn)
      if (tp + fn == 0) return 0;

      return (tp / (tp + fn)).toFixed(2);
    },
    getTruePositives(textIndex) {
      var tp = 0; // true positives: a word that is annotated by the model and also by the user.
      // calc true positives
      var annotations = this.modelAnnotations[textIndex];
      for (var i = 0; i < annotations.length; i++) {
        if (
          this.userAnnotations[textIndex].some(
            (e) => e.word_index === annotations[i].word_index
          )
        ) {
          tp++;
        }
      }
      return tp;
    },
    getFalseNegatives(textIndex) {
      var fn = 0; // false negatives: not annotated by the model but annotated by the user.
      // calc false negatives
      var annotations = this.userAnnotations[textIndex];
      for (var i = 0; i < annotations.length; i++) {
        if (
          !this.modelAnnotations[textIndex].some(
            (e) => e.word_index === annotations[i].word_index
          )
        ) {
          fn++;
        }
      }
      return fn;
    },
    getFalsePositives(textIndex) {
      var fp = 0; // false positives: annotated by the model but not annotated by the user.
      // calc false positives
      var annotations = this.modelAnnotations[textIndex];
      for (var i = 0; i < annotations.length; i++) {
        if (
          !this.userAnnotations[textIndex].some(
            (e) => e.word_index === annotations[i].word_index
          )
        ) {
          fp++;
        }
      }
      return fp;
    },
    getPrecision(textIndex) {
      // calculates the precision of the model annotations compared to the user annotations (ground truth).
      var tp = this.getTruePositives(textIndex);
      var fp = this.getFalsePositives(textIndex);

      // precision = tp / (tp + fp)
      if (fp == 0) return 1;

      return (tp / (tp + fp)).toFixed(2);
    },
    cardId(index) {
      return `card_${index}`;
    },
    // use axios to send the texts to the server for annotation
    // and get the result back
    sendTexts() {
      this.modelAnnotations = [];
      this.userAnnotations = [];
      var tmpResult = new Array(this.texts.length);

      // iterate each text in texts, and send it to the server,
      // put each result in tmpResult in the same index as the text
      this.texts.forEach((text, index) => {
        axios
          .get(flaskAddr + "detect", {
            params: {
              text: text,
            },
          })
          .then((response) => {
            tmpResult[index] = response.data.result;
          })
          .catch((error) => {
            console.log(error);
          });
      });

      // wait until tmpResult is full

      // TODO: remove the timeouts and set a more stable solution.
      // wait for all requests to be done, then update this.modelAnnotations
      setTimeout(() => {
        this.modelAnnotations = tmpResult;
        // set userAnnotations with a clone of modelAnnotations
        this.userAnnotations = JSON.parse(
          JSON.stringify(this.modelAnnotations)
        );
      }, 1000);

      // should wait for rebuild
      setTimeout(() => {
        // see https://stackoverflow.com/questions/56574059/how-to-find-index-of-selected-text-in-getselection-using-javascript
        for (var i = 0; i < this.texts.length; i++) {
          document
            .getElementById(this.cardId(i))
            .addEventListener("mouseup", function (e) {
              // see https://stackoverflow.com/questions/36845515/mouseevent-path-equivalent-in-firefox-safari
              // (why we use composedPath() instead of path. path didn't work in chrome as well)
              var wordIndex = parseInt(e.composedPath()[0].id); // word index == span id
              var textIndex = parseInt(e.composedPath()[1].id.split("_")[1]); // see cardId, we extract the number after the underscore
              // console.log(wordIndex);
              // console.log(textIndex);
              var selection = window.getSelection();
              var start = selection.anchorOffset;
              var end = selection.focusOffset;
              if (end != start) {
                // i.e., not an empty selection (click a word)
                addAnnotation(selection, wordIndex, start, end, textIndex);
              }
            });
        }
      }, 2000);
    },
    annotateText(content, annotations, annotationIndex, correct = true) {
      // replace each \n in current text with \n and space
      let text = content.replace(/\n/g, "\n ");

      // split text based on spaces
      // iterate each word in text. if word index is in result,
      // add <span> tag with a highlight, else return span tag with word as text
      text = text
        .split(" ")
        .map((word, wordIndex) => {
          var newline = word.endsWith("\n") ? "<br>" : "";
          if (this.isWordAnnotated(annotations, wordIndex)) {
            //return `<span class="yellow">${word}</span>`;
            // https://www.w3schools.com/howto/howto_css_dropdown.asp
            if (correct) {
              // see created hook for explanation
              // why return false? see https://stackoverflow.com/questions/2084750/javascript-anchor-avoid-scroll-to-top-on-click
              // (that was a big headache)
              var mySpan = `<div class="dropdown"><span id="${wordIndex}" class="dropbtn yellow">${word}</span><div class="dropdown-content"><a href="#" onclick="removeAnnotation(${wordIndex}, ${annotationIndex}); return false;">הסרה</a></div></div>${newline}`;
              return mySpan;
            } else {
              return `<span id="${wordIndex}" class="yellow">${word}</span>${newline}`;
            }
          }
          return `<span id="${wordIndex}">${word}</span>${newline}`;
        })
        .join(" ");

      return text;
    },
    isWordAnnotated(annotations, index) {
      // return true if index is in one of result objects, in field word_index
      return annotations.some((obj) => {
        return obj.word_index === index && obj.score >= this.score;
      });
    },
    removeAnnotation(wordIndex, annotationIndex) {
      // remove annotation at wordIndex from userAnnotations[annotationIndex]
      this.userAnnotations[annotationIndex] = this.userAnnotations[
        annotationIndex
      ].filter((obj) => {
        return obj.word_index !== wordIndex;
      });

      // clone userAnnotations from its original state
      // if we do not do this, state is not updated
      this.userAnnotations = JSON.parse(JSON.stringify(this.userAnnotations));
    },
    addAnnotation(word, wordIndex, start, end, annotationIndex) {
      this.userAnnotations[annotationIndex].push({
        entity_group: "metaphor",
        start: start,
        end: end,
        word: word,
        word_index: wordIndex,
      });

      // here rebuild happens, no need to clone...
    },
  },
  created() {
    // see https://codehunter.cc/a/vue.js/how-to-access-a-vue-function-from-onclick-in-javascript
    // struglled with this one, but it now works :(
    window.removeAnnotation = this.removeAnnotation;
    window.addAnnotation = this.addAnnotation;
  },
};
</script>
<style>
.my-span-class:hover {
  outline: 1px solid black;
}
.annotated {
  font-weight: bold;
}
/* .dropbtn {
  background-color: #04aa6d;
  color: white;
  padding: 16px;
  font-size: 16px;
  border: none;
} */

/* The container <div> - needed to position the dropdown content */
.dropdown {
  position: relative;
  display: inline-block;
}

/* Dropdown Content (Hidden by Default) */
.dropdown-content {
  display: none;
  position: absolute;
  background-color: white;
  /* min-width: 160px; */
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  z-index: 1;
}

/* Links inside the dropdown */
.dropdown-content a {
  color: black;
  padding: 3px 10px;
  text-decoration: none;
  display: block;
}

/* Change color of dropdown links on hover */
.dropdown-content a:hover {
  background-color: #f8f8f8;
}

/* Show the dropdown menu on hover */
.dropdown:hover .dropdown-content {
  display: block;
}

/* Change the background color of the dropdown button when the dropdown content is shown */
.dropdown:hover .dropbtn {
  background-color: #3e8e41;
}
</style>