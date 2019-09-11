import React, { Component } from "react";
import Idea from "./Idea";

class ContentBlock extends Component {
  render() {
    const content = this.props.content;
    return (
      <p className={"Content" + content.level}>
        {content.ideas.map(idea => (
          <Idea
            key={idea.id}
            idea={idea}
            onSelectIdea={this.props.onSelectIdea}
          />
        ))}
      </p>
    );
  }
}

export default ContentBlock;
