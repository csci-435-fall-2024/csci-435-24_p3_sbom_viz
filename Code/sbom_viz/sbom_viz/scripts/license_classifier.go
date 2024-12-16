package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"sort"
	"strings"

	"github.com/google/licenseclassifier"
)

// IF MAKING CHANGES TO THIS SCRIPT - MUST REBUILD IT
// to build the executable (so that Go doesn't have to be installed),
// 		BUILD:   go build -o license_classifier license_classifier.go
//		RUN:     ./license_classifier {"licenses":["MIT License","GPL-3.0","Apache-2.0"]}
// 		OUTPUT:  [{'license': 'Apache-2.0', 'restrictiveness': 'notice'},
//       		 	{'license': 'MIT', 'restrictiveness': 'notice'},
//       		 	...]

// LicenseInput represents the structure of the input JSON
type LicenseInput struct {
	Licenses []string `json:"licenses"`
}

// Response represents the structure of the output JSON
type Response struct {
	LicenseName     string `json:"license"`
	Restrictiveness string `json:"restrictiveness"`
}

func main() {
	// Read input from stdin (JSON)
	var input LicenseInput
	decoder := json.NewDecoder(os.Stdin)
	err := decoder.Decode(&input)
	if err != nil {
		log.Fatal("Error reading input:", err)
		return
	}

	//log.Println("Input received:", input.Licenses)

	// Classify licenses and get their restrictiveness
	restrictivenessData, err := classifyLicenses(input.Licenses)
	if err != nil {
		log.Fatal("Error classifying licenses:", err)
		return
	}

	sortedRestrictivenessData := sortByRestrictiveness(restrictivenessData)

	// Output the restrictiveness data as JSON
	output, err := json.Marshal(sortedRestrictivenessData)
	if err != nil {
		log.Fatal("Error generating output:", err)
		return
	}

	// Write output to stdout so it can be caught by license_classifier_helper.py
	fmt.Println(string(output))
}

// classifyLicenses processes the licenses and classifies each one
func classifyLicenses(licenses []string) ([]Response, error) {
	var results []Response

	// Iterate over the licenses and classify each one
	for _, license := range licenses {
		license = strings.TrimSpace(license)
		licenseType := licenseclassifier.LicenseType(license)

		//log.Printf("License: '%s', Type Detected: '%s'\n", license, licenseType)

		// Add the result to the response list
		results = append(results, Response{
			LicenseName:     license,
			Restrictiveness: licenseType,
		})
	}

	return results, nil
}

func sortByRestrictiveness(results []Response) []Response {
	// Define restrictiveness ranking
	// https://opensource.google/documentation/reference/thirdparty/licenses

	restrictivenessOrder := map[string]int{
		"forbidden":    1,
		"restricted":   2,
		"reciprocal":   3,
		"notice":       4,
		"permissive":   5,
		"unencumbered": 6,
		"unknown":      7,
	}

	// Sort the results slice by restrictiveness
	//		license_type_i/j       = restricted, unencumbered, etc.
	//		rank_i/j               = 1,2,3... in the restrictivenessOrder above
	// 		known_license_type_i/j = bool whether or not license is known

	sort.SliceStable(results, func(i, j int) bool {
		// Normalize case for comparison
		license_type_i := strings.ToLower(results[i].Restrictiveness) // restricted, unencumbered, etc.
		license_type_j := strings.ToLower(results[j].Restrictiveness)

		// Default to "unknown" rank if the value is not in the map
		rank_i, known_license_type_i := restrictivenessOrder[license_type_i]
		if !known_license_type_i {
			rank_i = restrictivenessOrder["unknown"]
		}

		rank_j, known_license_type_j := restrictivenessOrder[license_type_j]
		if !known_license_type_j {
			rank_j = restrictivenessOrder["unknown"]
		}

		return rank_i < rank_j
	})

	return results
}
