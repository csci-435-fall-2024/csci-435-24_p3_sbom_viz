package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/google/licenseclassifier"
)

// LicenseInput represents the structure of the input JSON
type LicenseInput struct {
	Licenses []string `json:"licenses"`
}

// Response represents the structure of the output JSON
type Response struct {
	LicenseName    string `json:"license"`
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

	// Output the restrictiveness data as JSON
	output, err := json.Marshal(restrictivenessData)
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
			LicenseName:    license,
			Restrictiveness: licenseType,
		})
	}

	return results, nil
}
