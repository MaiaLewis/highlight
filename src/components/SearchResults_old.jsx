import React, { Component } from "react";
import Result from "./Result";

class SearchResults extends Component {
  render() {
    const results = this.props.results;
    return (
      <div>
        {results.map(result => (
          <Result key={result.title} result={result} />
        ))}
      </div>
    );
  }
}

export default SearchResults;
