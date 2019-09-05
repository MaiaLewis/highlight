import React, { Component } from "react";

class Header extends Component {
  render() {
    return (
      <React.Fragment>
        <div className="button" onClick={this.props.onDisconnectDrive}>
          Disconnect Drive
        </div>
        <h1>Documents</h1>
      </React.Fragment>
    );
  }
}

export default Header;
