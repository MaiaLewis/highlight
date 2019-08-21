import React, { Component } from "react";
import Result from "./Result";

class SearchResults extends Component {
  state = {
    error: null,
    isLoaded: false,
    results: []
  };

  componentDidMount() {
    fetch(process.env.SEARCH_SEARCH)
      .then(res => res.json())
      .then(
        results => {
          this.setState({
            isLoaded: true,
            results: results
          });
        },
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  render() {
    const results = this.state.results;
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
