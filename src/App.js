import React, { Component } from "react";
import Header from "./components/Header";
import SearchResults from "./components/SearchResults";
import "./App.css";

class App extends Component {
  state = {
    error: null,
    isLoaded: false,
    results: [
      {
        id: 1,
        title: "Didn't work",
        topics: ["Topic 1", "Topic 2", "Topic 3"],
        author: "Author Name",
        last_edit: "yyyy-mm-ddThh:mm:ss.ffffff"
      }
    ]
  };

  componentDidMount() {
    fetch("https://highlight-search.herokuapp.com/search")
      .then(res => res.json())
      .then(
        console.log("yay"),
        result => {
          window.location.href = result;
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
