import React, { Component } from "react";

class Result extends Component {
  render() {
    const result = this.props.result;
    return (
      <div className="Result">
        <p>{result.title}</p>
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
