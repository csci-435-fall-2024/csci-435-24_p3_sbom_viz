/**
 * Represents the web application, its render ability, and its ability to switch between pages.
 */
class App {
    // Set up the web application
    constructor() {
        this.page = new FileInputPage(this);  // current "page" of the application (the state of what part of the application is rendered to the screen)
        this.fileText = ""; // temporary, will later be stored in a database
        this.appElement = document.getElementById("app"); // corresponding HTML element to modify view
        this.render(); // Set up the view
    }

    // Update the view by rendering the current page
    render() {
        this.page.render();
    }

}

/**
 * Represents the file input page on the web application and its ability to upload and accept
 * file data from the user.
 */
class FileInputPage {
    // Set up the page
    constructor(app) {
        this.app = app;
        this.file = null;
        this.selectFile = this.selectFile.bind(this);
        this.uploadFileText = this.uploadFileText.bind(this);
    }

    // Render a form asking the user to input a file.
    render() {
        this.app.appElement.innerHTML = `
            <form>
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
        document.getElementById("file-select-input").addEventListener("change", this.selectFile);
        document.getElementById("upload-button").addEventListener("click", this.uploadFileText);
    }

    // Store the file name
    selectFile(event) {
        this.file = event.target.files[0];
        document.getElementById("upload-button").disabled = (this.file ? false : true);
    }

    // Read a file when uploaded
    uploadFileText() {
        let fileReader = new FileReader();
        fileReader.onload = () => {
            //console.log(fileReader.result);
            this.app.page = new FileDisplayPage(this.app, fileReader.result);
            this.app.render();
        };
        fileReader.readAsText(this.file);
    }
}

class FileDisplayPage {
    // Set up the page
    constructor(app, text) {
        this.app = app;
        this.text = text;
    }

    // Render the page to display the file
    render() {
        this.app.appElement.innerHTML = `
            <h1>Display File</h1>
            <p id="text-p"></p>
        `;
        document.getElementById("text-p").textContent = this.text;
    }
}

new App();