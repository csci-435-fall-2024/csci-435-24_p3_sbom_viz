/**
 * Represents the page that displays the contents of the file after it has been
 * loaded.
 */
export class FileDisplayPage {
    // Set up the page
    constructor(app, text) {
        this.app = app;
        this.text = text; // text contents of the file
    }

    // Render the page to display the file
    render() {
        this.app.appElement.innerHTML = `
            <h1>Display File</h1>
            <p id="text-p"></p>
        `;
        /* Set the text of the paragraph to display the text of the file.
         * NOTE: Do NOT use innerHTML here, because it will interpret the elements of an XML document
         * as HTML elements rather than plaintext, and an XML document may not be correctly displayed! */
        document.getElementById("text-p").textContent = this.text;
    }
}