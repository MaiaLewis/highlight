import React, { Component } from "react";
import Disconnect from "./Disconnect";

class Header extends Component {
  render() {
    return (
      <React.Fragment>
        <Disconnect onDisconnectDrive={this.props.onDisconnectDrive} />
        <h1>Documents</h1>
      </React.Fragment>
    );
  }
}

export default Header;
