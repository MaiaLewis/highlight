import React, { Component } from "react";
import Results from "./Results";

class ResultsBasic extends Component {
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
      <Results results={results} onViewDocument={this.props.onViewDocument} />
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

export default ResultsBasic;
