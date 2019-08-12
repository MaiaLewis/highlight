import React, { Component } from "react";
import Header from "./components/Header";
import Connect from "./components/Connect";
import SearchResults from "./components/SearchResults";
import "./App.css";

class App extends Component {
  state = {
    error: null,
    isConnected: false,
    areDocuments: false
  };

  render() {
    const { error, isConnected, areDocuments } = this.state;
    if (isConnected && !areDocuments) {
      this.saveDocuments();
    }
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isConnected) {
      return <Connect onConnectToDrive={this.handleConnectToDrive} />;
    } else if (!areDocuments) {
      return (
        <React.Fragment>
          <Header onDisconnectDrive={this.handleDisconnectDrive} />
          <p>Loading documents...</p>
        </React.Fragment>
      );
    } else {
      return (
        <React.Fragment>
          <Header onDisconnectDrive={this.handleDisconnectDrive} />
          <SearchResults />
        </React.Fragment>
      );
    }
  }

  componentDidMount() {
    //for local development use:
    //fetch("http://localhost:5000/auth/account")
    fetch("https://highlight-search.herokuapp.com/auth/account")
      .then(res => res.json())
      .then(
        results => {
          if (results.includes("credentials") === false) {
            this.setState({
              isConnected: false,
              areDocuments: false
            });
          } else if (results.includes("docsSaved") === false) {
            this.setState({
              isConnected: true,
              areDocuments: false
            });
          } else {
            this.setState({
              isConnected: true,
              areDocuments: true
            });
          }
        },
        error => {
          this.setState({
            error
          });
        }
      );
  }

  handleConnectToDrive = () => {
    //for local development use:
    //fetch("http://localhost:5000/auth/oauth2callback")
    fetch("https://highlight-search.herokuapp.com/auth/oauth2callback")
      .then(res => res.json())
      .then(
        results => {
          window.location.href = results.url;
        },
        error => {
          this.setState({
            error
          });
        }
      );
  };

  handleDisconnectDrive = () => {
    //for local development use:
    //fetch("http://localhost:5000/auth/disconnect")
    fetch("https://highlight-search.herokuapp.com/auth/disconnect")
      .then(res => res.json())
      .then(
        results => {
          console.log(results);
          this.setState({
            isConnected: false
          });
        },
        error => {
          this.setState({
            error
          });
        }
      );
  };

  saveDocuments = () => {
    //for local development use:
    //fetch("http://localhost:5000/save/save")
    fetch("https://highlight-search.herokuapp.com/save/save")
      .then(res => res.json())
      .then(
        results => {
          console.log(results);
        },
        error => {
          this.setState({
            error
          });
        }
      );
  };
}

export default App;
