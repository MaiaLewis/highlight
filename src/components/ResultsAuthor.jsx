import React, { Component } from "react";
import Result from "./Result";

class SearchResults extends Component {
  state = {
    error: null,
    isLoaded: false,
    results: {
      documents: [],
      authorFilters: [],
      topicFilters: [],
      documentFilters: []
    }
  };

  render() {
    const results = this.state.results;
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

  componentDidMount() {
    fetch(process.env.REACT_APP_READ_GRAPH)
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
}

export default SearchResults;
