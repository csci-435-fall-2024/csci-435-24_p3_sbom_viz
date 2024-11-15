// Extract JSON of license data from the license endpoint
export async function getLicenseData() {
    const response = await fetch("http://127.0.0.1:8000/license/");
    const json = await response.json();
    const result = processLicenseData(json["distribution"]); // convert to a frequency list
    return result;
}
  
// Process the extracted license data to convert it to the proper format
function processLicenseData(inputData) {
    let processedData = [];
    // Put each license and its count in the list as an object {license name, count}.
    for (let key in inputData) {
        processedData.push({"license name" : key, "version": "n/a", "count" : inputData[key]});
    }
    // Sort descending, so most frequent licenses appear at the top.
    processedData.sort((a, b) => b["count"] - a["count"]);
    return processedData;
}