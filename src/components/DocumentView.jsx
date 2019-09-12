import React, { Component } from "react";
import Document from "./Document";
import Sidebar from "./Sidebar";

class DocumentView extends Component {
  state = {
    error: null,
    docId: null,
    relatedIdeas: []
  };

  render() {
    return (
      <React.Fragment>
        <div className="button" onClick={this.props.onCloseDocument}>
          Close
        </div>
        <Document
          docId={this.props.docId}
          onSelectIdea={this.handleSelectIdea}
        />
        <Sidebar relatedIdeas={this.state.relatedIdeas} />
      </React.Fragment>
    );
  }

  handleSelectIdea = ideaId => {
    fetch("http://localhost:5000/search/info".concat("/" + ideaId))
      .then(res => res.json())
      .then(
        results => {
          this.setState({
            relatedIdeas: results
          });
        },
        error => {
          this.setState({
            error
          });
        }
      );
  };
}

export default DocumentView;
