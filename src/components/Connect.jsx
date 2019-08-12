import React, { Component } from "react";

class Connect extends Component {
  render() {
    return (
      <div className="button" onClick={this.props.onConnectToDrive}>
        Connect to Drive
      </div>
    );
  }
}

export default Connect;
