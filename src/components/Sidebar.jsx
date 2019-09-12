import React, { Component } from "react";

class Sidebar extends Component {
  render() {
    if (this.props.relatedIdeas.length > 0) {
      console.log(this.props.relatedIdeas[0].text);
      return (
        <div className="Sidebar">
          <div>
            <b>Related Info</b>
            {this.props.relatedIdeas.map(foo => (
              <p key={foo.id}>{foo.text}</p>
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
