from flask import Flask, render_template
from flask_cors import CORS
import os
import json

app = Flask(__name__, static_folder="build/static", template_folder="build")
CORS(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    results = [
    {
        "id": 1,
        "title": "Document Title",
        "topics": ["Topic 1", "Topic 2", "Topic 3"],
        "author": "Author Name",
        "last_edit": "yyyy-mm-ddThh:mm:ss.ffffff"
    },
    {
        "id": 2,
        "title": "Document Title",
        "topics": ["Topic 1", "Topic 2", "Topic 3"],
        "author": "Author Name",
        "last_edit": "yyyy-mm-ddThh:mm:ss.ffffff"
    },
    {
        "id": 3,
        "title": "Document Title",
        "topics": ["Topic 1", "Topic 2", "Topic 3"],
        "author": "Author Name",
        "last_edit": "yyyy-mm-ddThh:mm:ss.ffffff"
    }]
    results = json.dumps(results)
    return results

if __name__ == '__main__':
    app.run()