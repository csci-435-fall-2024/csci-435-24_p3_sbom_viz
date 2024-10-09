import { FileDisplayPage } from "./fileDisplayPage.js";

/**
 * Represents the file input page on the web application and its ability to upload and accept
 * file data from the user.
 */
export class FileInputPage {
    // Set up the page
    constructor(app) {
        this.app = app;
        this.file = null;
        // Methods must be bound to their owner object so they can access and modify the properties of their owner ("this")
        this.selectFile = this.selectFile.bind(this);
        this.uploadFileText = this.uploadFileText.bind(this);
    }

    // Render a form asking the user to input a file.
    render() {
        this.app.appElement.innerHTML = `
            <form>
                <h1>Upload File</h1>
                <!-- Radio Selector for SBOM Standard -->
                <label for="file-standard-selector">Select SBOM Standard:</label>
                <div id="file-standard-selector">
                    <!-- SPDX Radio Option -->
                    <label for="file-standard-spdx">SPDX</label>
                    <input type="radio" name="file-standard-selector-option" id="file-standard-spdx" value="spdx" checked />
                    <!-- CycloneDX Radio Option -->
                    <label for="file-standard-cyclone-dx">CycloneDX</label>
                    <input type="radio" name="file-standard-selector-option" id="file-standard-cyclone-dx" value="cyclone-dx" />
                </div>
                <div>
                    <!-- SBOM File Select Button -->
                    <label for="file-select-input">Select File:</label>
                    <input type="file" name="file-select-input" id="file-select-input"/>
                </div>
                <div>
                    <!-- SBOM Upload File Button -->
                    <button type="button" id="upload-button" disabled>Upload File</button>
                </div>
            </form>
        `; 
        document.getElementById("file-select-input").addEventListener("change", this.selectFile); // When the "Select File" button is clicked, store the filename and activate the upload file button if a file was selected
        document.getElementById("upload-button").addEventListener("click", this.uploadFileText); // When the "Upload File" button is clicked, upload the file text to the app and display it
    }

    // Store the file name and activate the upload button if the file exists
    selectFile(event) {
        this.file = event.target.files[0]; // Select the first file in a list returned from the file dialog
        document.getElementById("upload-button").disabled = (this.file ? false : true); // Enable the upload button if a file has been selected, otherwise disable it (a file cannot be read if it has not been selected)
    }

    // Read a file when uploaded, and switch from the "file input form" page to the "display file" page
    uploadFileText() {
        let fileReader = new FileReader();
        fileReader.onload = () => {
            // When the file is read, upload the file contents as plaintext and switch the page to display the file rather than ask the user to select a file. 
            this.app.page = new FileDisplayPage(this.app, fileReader.result);
            this.app.render(); // Re-render the app to display the new page.
        };
        fileReader.readAsText(this.file); // Read the file to execute fileReader.onload()
    }
}