/*
 * Script for the file display page
 * 1) Enable header navigation links if a file has been uploaded,
 * 2) Show the [uploaded file name], if the server knows what file to use
 * 3) Wait for a new file to be uploaded, and update the [updated file name] when needed
 */

// Enable the navigation links ONLY if a file has already been uploaded.
async function setUpNavLinks() {
    const response = await fetch("http://127.0.0.1:8000/uploaded");
    const json = await response.json();
    const uploaded = json["uploaded"];
    if (uploaded) {
        // Set destinations
        document.getElementById("diagram-link").setAttribute("href", "diagram/");
        document.getElementById("licenses-link").setAttribute("href", "licenses/");
        document.getElementById("vulnerabilities-link").setAttribute("href", "vulnerabilities/");
        document.getElementById("pdf-preview-link").setAttribute("href", "pdf-preview/");
    } else {
        // Set styling
        document.getElementById("diagram-link").classList.add("disabled-nav-link");
        document.getElementById("licenses-link").classList.add("disabled-nav-link");
        document.getElementById("vulnerabilities-link").classList.add("disabled-nav-link");
        document.getElementById("pdf-preview-link").classList.add("disabled-nav-link");
    }
}

// On page initialization, display the name of the file if it has already been uploaded on a previous visit to the page.
async function setUpFileName() {
    const response_uploaded = await fetch("http://127.0.0.1:8000/uploaded");
    const json_uploaded = await response_uploaded.json();
    const uploaded = json_uploaded["uploaded"];
    if (uploaded) {
        const response_filename = await fetch("http://127.0.0.1:8000/filename");
        const json_filename = await response_filename.json();
        const filename = json_filename["filename"];
        document.getElementById("filename-display").innerHTML = `<div class="bold centered">Selected File:</div>${filename}`;
    }
}

setUpNavLinks();
setUpFileName();

// When a new file has been uploaded, change the text of the filename field to display the new file to be uploaded
document.getElementById("file-select-input").addEventListener("change", (e) => {
    if (e.target.files.length == 0) { // If the file selection was removed,
        setUpFileName();              // reset the current SBOM file to the one currently uploaded, or no file if none has been uploaded.
    } else {
        document.getElementById("filename-display").innerHTML = `<div class="bold centered">Selected File:</div>${e.target.files[0].name}`;   // If a file was selected, display the name of the selected file to the user
    }
})