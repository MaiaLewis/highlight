import React, { Component } from "react";
import Header from "./components/Header";
import SearchResults from "./components/SearchResults";
import DocumentView from "./components/DocumentView";
import "./App.css";

class App extends Component {
  state = {
    error: null,
    saveStatus: "",
    currentDocs: 0,
    totalDocs: 0,
    status: "not_connected",
    document: null
  };

  render() {
    const { error, saveStatus, currentDocs, totalDocs, document } = this.state;
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (saveStatus === "not_connected") {
      return (
        <div className="button" onClick={this.onConnectToDrive}>
          Connect to Drive
        </div>
      );
    } else if (saveStatus === "saving") {
      return (
        <React.Fragment>
          <Header onDisconnectDrive={this.handleDisconnectDrive} />
          <p>
            Loading {currentDocs}/{totalDocs}
          </p>
        </React.Fragment>
      );
    } else if (document !== null) {
      return (
        <React.Fragment>
          <Header onDisconnectDrive={this.handleDisconnectDrive} />
          <DocumentView
            docId={document}
            onCloseDocument={this.handleCloseDocument}
          />
        </React.Fragment>
      );
    } else {
      return (
        <React.Fragment>
          <Header onDisconnectDrive={this.handleDisconnectDrive} />
          <SearchResults onViewDocument={this.handleViewDocument} />
        </React.Fragment>
      );
    }
  }

  componentDidMount() {
    fetch(process.env.REACT_APP_AUTH_ACCOUNT)
      .then(res => res.json())
      .then(
        results => {
          console.log(this.state);
          if (results.saveStatus === "not_connected") {
            this.setState({
              saveStatus: "not_connected"
            });
          } else if (results.saveStatus === "connected") {
            this.saveDocuments();
          } else if (results.saveStatus === "saving") {
            this.updateProgress(results.progressURL);
          } else if (results.saveStatus === "up_to_date") {
            this.setState({
              saveStatus: "up_to_date"
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

  onConnectToDrive = () => {
    fetch(process.env.REACT_APP_AUTH_OAUTH2CALLBACK)
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

  handleViewDocument = docId => {
    this.setState({
      document: docId
    });
  };

  handleCloseDocument = () => {
    this.setState({
      document: null
    });
  };

  handleDisconnectDrive = () => {
    fetch(process.env.REACT_APP_AUTH_DISCONNECT)
      .then(res => res.json())
      .then(
        results => {
          console.log(results);
          this.setState({
            saveStatus: "not_connected"
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
    fetch(process.env.REACT_APP_WRITE_GRAPH)
      .then(res => res.json())
      .then(
        results => {
          this.setState({
            saveStatus: "saving"
          });
          this.updateProgress(results.progressURL);
        },
        error => {
          this.setState({
            error
          });
        }
      );
  };

  updateProgress = progressURL => {
    var self = this;
    fetch(progressURL)
      .then(res => res.json())
      .then(
        results => {
          this.setState({
            currentDocs: results.currentDocs,
            totalDocs: results.totalDocs,
            status: results.status
          });
          if (results.state === "SUCCESS") {
            this.setState({
              saveStatus: "up_to_date"
            }); //need an FE error case if celery job returns error
          } else {
            this.setState({
              saveStatus: "saving"
            });
            setTimeout(function() {
              self.updateProgress(progressURL);
            }, 2000);
          }
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
