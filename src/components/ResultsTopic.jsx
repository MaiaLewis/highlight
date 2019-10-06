import React, { Component } from "react";
import Results from "./Results";

class SearchResults extends Component {
  state = {
    error: null,
    isLoaded: false,
    results: []
  };

  render() {
    const results = this.state.results;
    return (
      <div>
        {results.map(result => (
          <div className="ResultContainer">
            <h4>{result.topicFilters[0].name}</h4>
            <Results
              key={result.topicFilters[0].name}
              results={result}
              onViewDocument={this.props.onViewDocument}
            />
          </div>
        ))}
      </div>
    );
  }

  componentDidMount() {
    fetch(process.env.REACT_APP_READ_GRAPH_TOPICS)
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
