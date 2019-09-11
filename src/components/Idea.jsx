import React, { Component } from "react";

class Idea extends Component {
  render() {
    const idea = this.props.idea;
    return (
      <span
        className="Idea"
        entities={idea.entities}
        lemmas={idea.lemmas}
        id={idea.id}
        onClick={() => this.props.onSelectIdea(idea.entities, idea.lemmas)}
      >
        {idea.text + " "}
      </span>
    );
  }
}

export default Idea;
