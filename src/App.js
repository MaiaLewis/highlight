import React, { Component } from "react";
import Header from "./components/Header";
import SearchResults from "./components/SearchResults";
import "./App.css";

class App extends Component {
  state = {
    error: null,
    isConnected: false
  };

  componentDidMount() {
    //for local development use:
    //fetch("http://localhost:5000/save/save")
    fetch("https://highlight-search.herokuapp.com/save/save")
      .then(res => res.json())
      .then(
        results => {
          if ("url" in results) {
            window.location.href = results.url;
          } else {
            this.setState({
              isConnected: true
            });
          }
        },
        error => {
          this.setState({
            isConnected: false,
            error
          });
        }
      );
  }

  render() {
    const { error, isConnected } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isConnected) {
      return <div>Connecting...</div>;
    } else {
      return (
        <React.Fragment>
          <Header />
          <SearchResults />
        </React.Fragment>
      );
    }
  }
}

export default App;
