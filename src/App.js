import React, { Component } from "react";
import Header from "./components/Header";
import SearchResults from "./components/SearchResults";
import "./App.css";

class App extends Component {
  state = {
    error: null,
    isLoaded: false,
    results: []
  };

  componentDidMount() {
    fetch("https://highlight-search.herokuapp.com/save/save")
      .then(res => res.json())
      .then(
        results => {
          if ("url" in results) {
            window.location.href = results.url;
          } else {
            this.setState({
              isLoaded: true,
              results: results
            });
          }
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
    const { error, isLoaded, results } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div>Loading...</div>;
    } else {
      return (
        <React.Fragment>
          <Header />
          <SearchResults results={results} />
        </React.Fragment>
      );
    }
  }
}

export default App;
