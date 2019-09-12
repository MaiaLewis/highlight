import React, { Component } from "react";

class Idea extends Component {
  render() {
    const idea = this.props.idea;
    return (
      <span
        className="Idea"
        id={idea.id}
        onClick={() => this.props.onSelectIdea(idea.id)}
      >
        {idea.text + " "}
      </span>
    );
  }
}

export default Idea;
