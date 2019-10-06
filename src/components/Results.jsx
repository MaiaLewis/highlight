import React, { Component } from "react";
import Result from "./Result";

class Results extends Component {
  render() {
    const results = this.props.results;
    return (
      <div>
        {results.documents.map(result => (
          <Result
            key={result.docId}
            result={result}
            onViewDocument={this.props.onViewDocument}
          />
        ))}
      </div>
    );
  }
}

export default Results;
