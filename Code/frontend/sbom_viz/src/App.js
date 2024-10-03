import logo from './logo.svg';
import './App.css';
import React from 'react';


class ImportDataPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      callback: this.props.callback
    };
  }

  render() {
    return (
      <form id="uploadForm">
        {/* SBOM Type Input Selector */}
        <label for="sbom-type-selector">Select SBOM Standard:</label>
        <div name="sbom-type-selector">
          {/* SPDX option */}
          <label for="sbom-type-spdx">SPDX</label>
          <input type="radio" name="sbom-type-option" id="sbom-type-spdx" checked />
          {/* CycloneDX option */}
          <label for="sbom-type-spdx">CycloneDX</label>
          <input type="radio" name="sbom-type-option" id="sbom-type-cyclone-dx" />
        </div>
        {/* Upload File Button */}
        <label for="upload">Upload File:</label>
        <input type="file" name="upload" onChange={this.state.callback} />
      </form>
    );
  }

}

class DisplayDataPage extends React.Component {
  constructor(props) {
    super(props);
  }
  
  render() {
    console.log(this.props.text)
    return (<p>{this.props.text}</p>);
  }
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      uploaded: false,
      fileText: ''
    };
    this.upload = this.upload.bind(this);
  }

  render() {
    if (!this.state.uploaded) {
      return (
        <div className="App">
          <ImportDataPage callback={this.upload}/>
        </div>
      );
    } else {
      console.log(this.state.fileText);
      return (
        <div className="App">
          <DisplayDataPage text={this.state.fileText}/>
        </div>
      );
    }
  }

  upload(event) {
    let fileReader = new FileReader();
    fileReader.onload = function() {
      this.setState({uploaded: true, fileText: fileReader.result});
      return fileReader.result;
    };
    fileReader.onload = fileReader.onload.bind(this);
    fileReader.readAsText(event.target.files[0]);
  }
}

export default App;
