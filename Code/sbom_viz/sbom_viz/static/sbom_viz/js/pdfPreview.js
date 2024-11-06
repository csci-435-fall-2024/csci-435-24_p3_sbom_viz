async function setFilenameText() {
    let response = await fetch("http://127.0.0.1:8000/filename");
    let json = await response.json();
    console.log(json);
    document.getElementById("filename-field").textContent = json["filename"];
}

setFilenameText();