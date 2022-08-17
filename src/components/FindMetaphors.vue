<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="8">
        <v-textarea
          v-model="text"
          clearable
          filled
          shaped
          label="טקסט לזיהוי"
          clear-icon="mdi-close-circle"
          no-resize
          rows="8"
        >
        </v-textarea>
        <v-btn class="primary" @click="sendText()"> זהה מטאפורות </v-btn>        
        <div class="mt-5" v-html="annotatedText"></div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  name: "FindMetaphors",

  data() {
    return {
      text: "",
      result: [],
    };
  },
  computed: {
    annotatedText() {
      // return empty string if result is empty
      if (this.result.length === 0) {
        return "";
      }
      // split text based on spaces and new lines
      // iterate each word in text. if word index is in result, add <span> tag with class "highlight", else return span tag with word as text
      return this.text.split(/\s+|\n/).map((word, index) => {
        if (this.isWordAnnotated(index)) {
          return `<span class="yellow">${word}</span>`;
        }
        return `<span>${word}</span>`;
      }).join(" ");
    },
  },
  watch: {
    text(newText) {
      // clear result if text is empty or null
      if (!newText) {
        this.text = "";
        this.result = [];
      }
    },
  },
  methods: {
    // use axios to send the text to the server
    // and get the result back
    // then update the textarea with the result
    //
    sendText() {
      axios
        .get("http://127.0.0.1:5000/detect", {
          params: {
            text: this.text,
          },
        })
        .then((response) => {
          this.result = response.data.result;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    isWordAnnotated(index) {
      // return true if index is in one of result objects, in field word_index
      return this.result.some((obj) => {
        return obj.word_index === index;
      });
    },
  },
};
</script>
