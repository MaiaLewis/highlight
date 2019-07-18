import React, { Component } from "react";
import Result from "./Result";

class SearchResults extends Component {
  render() {
    const results = this.props.results;
    return (
      <div>
        {results.map(result => (
          <Result key={result.id} result={result} />
        ))}
      </div>
    );
  }
}

export default SearchResults;
