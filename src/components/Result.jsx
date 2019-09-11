import React, { Component } from "react";

class Result extends Component {
  render() {
    const result = this.props.result;
    return (
      <div className="Result">
        <div
          className="button"
          onClick={() => this.props.onViewDocument(result.docId)}
        >
          {result.title}
        </div>
        <p>{result.author}</p>
        <p>{result.lastModified}</p>
        <ul>
          {result.topics.map(topic => (
            <li key={topic}>{topic}</li>
          ))}
        </ul>
      </div>
    );
  }
}

export default Result;
