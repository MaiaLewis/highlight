import React, { Component } from "react";

class Sidebar extends Component {
  render() {
    if (this.props.entities.length > 0 && this.props.lemmas.length > 0) {
      return (
        <div className="Sidebar">
          <div>
            <b>Entities</b>
            {this.props.entities.map(entity => (
              <p key={entity.id}>{entity.name}</p>
            ))}
          </div>
          <div>
            <b>Lemmas</b>
            {this.props.lemmas.map(lemma => (
              <p key={lemma.id}>{lemma.name}</p>
            ))}
          </div>
        </div>
      );
    } else if (this.props.entities.length > 0) {
      return (
        <div className="Sidebar">
          <div>
            <b>Entities</b>
            {this.props.entities.map(entity => (
              <p key={entity.id}>{entity.name}</p>
            ))}
          </div>
        </div>
      );
    } else if (this.props.lemmas.length > 0) {
      return (
        <div className="Sidebar">
          <div>
            <b>Lemmas</b>
            {this.props.lemmas.map(lemma => (
              <p key={lemma.id}>{lemma.name}</p>
            ))}
          </div>
        </div>
      );
    } else {
      return <div className="Sidebar" />;
    }
  }
}

export default Sidebar;
