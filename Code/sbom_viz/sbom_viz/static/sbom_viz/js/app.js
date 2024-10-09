import { FileInputPage } from "./fileInputPage.js";
import { FileDisplayPage } from "./fileDisplayPage.js";

/**
 * Represents the web application, its render ability, and its ability to switch between pages.
 */
export class App {
    // Set up the web application
    constructor() {
        console.log("Hello!")
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