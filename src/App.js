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
    fetch(process.env.AUTH_ACCOUNT)
      .then(res => res.json())
      .then(
        results => {
          if (!results.includes("credentials")) {
          } else if (!results.includes("docsSaved")) {
            this.setState({
              isConnected: true
            });
          } else {
            this.setState({
              isConnected: true,
              areDocuments: true
            });
          }
          console.log(this.state);
        },
        error => {
          this.setState({
            error
          });
        }
      );
  }

  handleConnectToDrive = () => {
    fetch(process.env.AUTH_OAUTH2CALLBACK)
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
    fetch(process.env.AUTH_DISCONNECT)
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
    fetch(process.env.SAVE_SAVE)
      .then(res => res.json())
      .then(
        results => {
          this.setState({
            areDocuments: true
          });
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
