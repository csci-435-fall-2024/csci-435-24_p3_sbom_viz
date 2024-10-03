/**
 * Represents the web application, its render ability, and its ability to switch between pages.
 */
class App {
    // Set up the web application
    constructor() {
        this.page = new FileInputPage(this);  // current "page" of the application (the state of what part of the application is rendered to the screen)
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
    }
    // Render a form asking the user to input a file.
    render() {
        this.app.appElement.innerHTML = `
            <h1>Hello, OOP!</h1>
        `; 
    }
}

new App();