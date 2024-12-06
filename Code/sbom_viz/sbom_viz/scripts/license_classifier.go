package main

import (
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/google/licenseclassifier"
)
// Input is one string, i.e., "MIT, GPL-3.0, Apache-2.0"
// Run this file on the command line with:

// go run license_classifier.go -licenses "MIT, GPL-3.0, Apache-2.0"
// or to build the executable (so that go doesn't have to be installed),
// 		BUILD: go build -o license_classifier license_classifier.go
//		RUN:   ./license_classifier -licenses "MIT, GPL-3.0, Apache-2.0"
func main() {
	// Define the command-line flags
	licensesFlag := flag.String("licenses", "", "Comma-separated list of license names to classify")

	// Parse the command-line flags
	flag.Parse()

	// If no licenses are provided, print usage and exit
	if *licensesFlag == "" {
		fmt.Println("Please provide a list of licenses using the '-licenses' flag.")
		flag.Usage()
		os.Exit(1)
	}

	// Split the licenses into a slice
	licenses := strings.Split(*licensesFlag, ",")

	// Iterate over the licenses and classify each one
	for _, license := range licenses {
		license = strings.TrimSpace(license) // Trim spaces from the input
		licenseType := licenseclassifier.LicenseType(license)

		// Print the license and its type
		if licenseType == "" {
			fmt.Printf("License '%s' is not recognized.\n", license)
		} else {
			fmt.Printf("License: %s, Type: %s\n", license, licenseType)
		}
	}
}
