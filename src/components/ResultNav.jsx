import React, { Component } from "react";

class ResultNav extends Component {
  render() {
    return (
      <div className="ResultNav">
        <div className="button" onClick={() => this.props.onChangeTab("basic")}>
          All Documents
        </div>
        <div className="button" onClick={() => this.props.onChangeTab("topic")}>
          Topics
        </div>
      </div>
    );
  }
}

export default ResultNav;
