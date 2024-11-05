# FigureOut - Detecting Metaphors in Hebrew Piyyut Poetry
The tool is available at [FigureOut](http://figureout.cs.technion.ac.il/). Use it to detect metaphors in Hebrew Piyyut poetry.

The metaphor detection is based on a machine learning model that was trained on a dataset of Hebrew Piyyut poetry. Details about the model and the dataset can be found in the paper [A Dataset for Metaphor Detection in Early Medieval Hebrew Poetry](https://aclanthology.org/2024.eacl-short.39.pdf).

# Key Features
- Metaphor detection based on textual input (Hebrew).
- Metaphor detection based on a pre-defined Hebrew Piyyut corpus.
- Side by side comparison of model annotations and user corrections.
  - Showing key statistics about the model's performance (precision, recall).
- Download annotations in JSON format.
- Dynamically adjust annotations based on a threshold.

# Developer Guide
## Installation (Linux)
- The backned is based on Flask.
- The frontend is based on Vue.js.
- Remember to create .env file in each environment (linux, windows).
- vue.js setup is explained in [this](https://github.com/TechnionTDK/project-guidelines/wiki/ExecuteVueAppOnLinux) tutorial.
- Execute the Flask server:
    - `authbind --deep python app.py`
 - Execute the Vue.js server:
    - `authbind --deep http-server -p 80 dist/`