import React, { Component } from "react";
import ContentBlock from "./ContentBlock";

class Document extends Component {
  state = {
    error: null,
    document: {
      title: null,
      author: null,
      lastModified: null,
      id: null,
      contents: []
    }
  };

  render() {
    return (
      <div className="Document">
        {this.state.document.contents.map(content => (
          <ContentBlock
            key={content.id}
            content={content}
            onSelectIdea={this.props.onSelectIdea}
          />
        ))}
      </div>
    );
  }

  componentDidMount() {
    fetch(process.env.REACT_APP_SEARCH_DOCUMENT.concat("/" + this.props.docId))
      .then(res => res.json())
      .then(
        results => {
          this.setState({
            document: results
          });
        },
        error => {
          this.setState({
            error
          });
        }
      );
  }
}

export default Document;
