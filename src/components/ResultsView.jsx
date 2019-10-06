import React, { Component } from "react";
import ResultsBasic from "./ResultsBasic";
import ResultsTopic from "./ResultsTopic";
import ResultNav from "./ResultNav";

class ResultsView extends Component {
  state = {
    searchTopics: [],
    searchAuthors: [],
    tab: "basic"
  };

  render() {
    if (this.state.tab === "basic") {
      return (
        <React.Fragment>
          <ResultNav onChangeTab={this.handleChangeTab} />
          <ResultsBasic onViewDocument={this.props.onViewDocument} />
        </React.Fragment>
      );
    } else if (this.state.tab === "topic") {
      return (
        <React.Fragment>
          <ResultNav onChangeTab={this.handleChangeTab} />
          <ResultsTopic onViewDocument={this.props.onViewDocument} />
        </React.Fragment>
      );
    }
  }

  handleChangeTab = newTab => {
    this.setState({
      tab: newTab
    });
  };
}

export default ResultsView;
