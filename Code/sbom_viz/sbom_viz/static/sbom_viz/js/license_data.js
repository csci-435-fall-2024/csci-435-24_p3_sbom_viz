// Extract JSON of license data from the license endpoint
export async function getLicenseData() {
    const response = await fetch("http://127.0.0.1:8000/license/");
    const freq_json = await response.json();
    const freq_result = processLicenseData(freq_json["distribution"]); // convert to a frequency list

    const restr_result = await getLicenseRestrictiveness(freq_result);

    return getCombinedJson({ frequency: freq_result, restrictiveness: restr_result });
} 

// Process the extracted license data to convert it to the proper format
function processLicenseData(inputData) {

    /* Step 1:
     * Extract the license types (TYPE) from the name of the license,
     * "(LicenseRef-TYPE1-##### AND/OR LicenseRef-TYPE2-##### AND/OR LicenseRef-TYPE3-##### ...)"
     * where LicenseRef and the sequence of digits ##### are optionally present. E.g., if a license
     * has name "(LicenseRef-MIT-2854389 AND LicenseRef-CC0-1.0-253809)", then it has license types
     * MIT and CC0-1.0.
     */
    let license_types = {}; // map to keep track of each license type and its count.
    // For each license name in the input data:
    for (let key in inputData) {
        // Handle multiple licenses for a single component
        let licenses = key.split(/ (OR|AND) /); // Separate "L1 AND/OR L2 AND/OR L3" ... into an array [L1, L2, L3, ...] and treat each license separately
        // If the license name was surrounded by parentheses, remove them ( "(L1 AND/OR L2 AND/OR L3)" -> "L1 AND/OR L2 AND/OR L3" )
        if (licenses[0].startsWith('(')) {
            licenses[0] = licenses[0].slice(1);
        }
        if (licenses[licenses.length-1].endsWith(')')) {
            licenses[licenses.length-1] = licenses[licenses.length-1].slice(0,-1);
        }
        //console.log("Key: ", key);
        //console.log("License list:", licenses);
        // For each license in the extracted list, we want to extract the type of the license as a string:
        for (let license of licenses) {
            /* Don't consider "AND" or "OR" if they are next, since these are just artifacts of using a
             * regular expression to split a string into an array in JavaScript (from above).
             */
            if ((license === "OR") || (license === "AND")) {
                continue;
            }
            let components = license.split('-');
            // If the license starts with "LicenseRef-", cut "LicenseRef-" out of the string.
            if ((components.length > 0) && (components[0] === "LicenseRef")) {
                components.splice(0,1);
            }
            // If the license ends with a sequence of digits "#######", cut them out of the string.
            if ((components.length > 0) && ([...components[components.length-1].matchAll(/^\d+$/g)].length > 0)) {
                components.pop();
            }
            // The remainder of the string is the type of license, since we have removed the "LicenseRef" prefix and digit sequence suffix.
            // However, if the remainder is empty or is NOASSERTION, that means the license name is unidentifiable or unknown, so classify it as "other." 
            let licenseName = components.join('-');
            if ((licenseName === "") || (licenseName === "NOASSERTION")) {
                licenseName = "other";
            }
            //console.log(licenseName);
            // Once we have determined the type of license, tally the number of times it was counted in the SBOM and add this to the current tally in the map.
            if (license_types.hasOwnProperty(licenseName)) {
                license_types[licenseName] += inputData[key]; // add to existing entry
            } else {
                license_types[licenseName] = inputData[key]; // create new entry if one does not exist, then add to it
            }
        }
    }
    //console.log(license_types);
    
    // Step 2: Put each license and its count in the resulting list as an object {license name, count}.
    let processedData = [];
    for (let key in license_types) {
        processedData.push({"license" : key, "version": "n/a", "count" : license_types[key]});
    }
    // Step 3: Sort descending, so most frequent licenses appear at the top.
    processedData.sort((a, b) => b["count"] - a["count"]);
    return processedData;
}

async function getLicenseRestrictiveness(data) {
    
    let cleaned_licenses = data.map(item => item["license"]); // get just the license name
    var restr_json;

    try {
        // store the cleaned license names at /licenses-clean/
        // POST body format:
        //      {"licenses":["MIT License","GPL-3.0","Apache-2.0"]}
        const response = await fetch("http://127.0.0.1:8000/licenses-clean/", {
            method: "POST",
            body: JSON.stringify({licenses: cleaned_licenses})
        });
        if (!response.ok){
            throw new Error("ERROR - licenses-clean");
        }
        // if no error, then the response is the classification in this format:
        //      [{'license': 'Apache-2.0', 'restrictiveness': 'notice'}, 
        //      {'license': 'MIT', 'restrictiveness': 'notice'}, 
        //       ...]
        restr_json = await response.json();
        restr_json = restr_json["restrictiveness"];
    } // try

    catch (error) {
        console.log(error);
    } 

    return restr_json;
}

function getCombinedJson({ frequency, restrictiveness }) {
    // Combine the frequency list and restrictiveness
    // into one JSON to be passed to the front end
    const combined = frequency.map(freq => {
        // Find the matching restrictiveness object
        const match = restrictiveness.find(res => res.license === freq["license"]);
        
        return {
          license: freq["license"],
          //version: freq.version,
          restrictiveness: match ? match.restrictiveness : "unknown", // Default to 'unknown' if no match
          count: freq.count
        };
      });

    return combined;
}