import React, { Component } from "react";

class Result extends Component {
  render() {
    const result = this.props.result;
    var snippet;
    if (result.snippet.length > 0) {
      console.log(result.snippet);
      snippet = result.snippet[0].text;
    } else {
      snippet = null;
    }
    return (
      <div className="Result">
        <div
          className="button"
          onClick={() => this.props.onViewDocument(result.docId)}
        >
          {result.title}
        </div>
        <p>{result.author.name}</p>
        <p>{result.lastModified}</p>
        <p>
          <i>{snippet}</i>
        </p>
        <ul>
          {result.topics.map(topic => (
            <li key={topic.id}>
              {topic.name}, {topic.frequency}
            </li>
          ))}
        </ul>
      </div>
    );
  }
}

export default Result;
