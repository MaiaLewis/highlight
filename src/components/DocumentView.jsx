import React, { Component } from "react";
import Document from "./Document";
import Sidebar from "./Sidebar";

class DocumentView extends Component {
  state = {
    docId: null,
    entities: [],
    lemmas: []
  };

  render() {
    console.log(this.state);
    return (
      <React.Fragment>
        <div className="button" onClick={this.props.onCloseDocument}>
          Close
        </div>
        <Document
          docId={this.props.docId}
          onSelectIdea={this.handleSelectIdea}
        />
        <Sidebar entities={this.state.entities} lemmas={this.state.lemmas} />
      </React.Fragment>
    );
  }

  handleSelectIdea = (entities, lemmas) => {
    this.setState({
      entities: entities,
      lemmas: lemmas
    });
  };
}

export default DocumentView;
