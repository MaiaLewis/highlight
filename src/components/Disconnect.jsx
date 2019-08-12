import React, { Component } from "react";

class Connect extends Component {
  render() {
    return (
      <div className="button" onClick={this.props.onDisconnectDrive}>
        Disconnect
      </div>
    );
  }
}

export default Connect;
