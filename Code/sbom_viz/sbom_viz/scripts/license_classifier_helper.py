import subprocess
import json
import os

def process_with_go_script(cleaned_licenses):

    # assume this is the first time running
    if not (os.path.isfile(os.path.join(os.getcwd(), "go.mod"))):

        print("go.mod not found - installing license classifier library and init module...")

        # init Go
        subprocess.run(
            ['go', 'mod', 'init', 'license-classifier'],
            shell=True
        )

        # install module
        subprocess.run(
            ['go', 'get', 'github.com/google/licenseclassifier'],
            shell=True
        )

        print("Finished!")

    try:
        cleaned_json = json.dumps(cleaned_licenses)
        # Run the Go script using subprocess
        rel_path = "sbom_viz\\scripts\\license_classifier.go"
        exec_dir = os.path.join(os.getcwd(), rel_path)
        result = subprocess.run(
            ['go', 'run', exec_dir],
            input=cleaned_json,  # Pass cleaned licenses as input
            text=True,  # Interpret input/output as text (not bytes)
            capture_output=True,  # Capture stdout and stderr
        )

        # Check if the Go script ran successfully
        if result.returncode == 0:
            # Parse the JSON response from the Go script
            response_data = json.loads(result.stdout)
            return response_data
        else:
            # If the Go script failed, return an error message
            return {'error': 'Go script failed', 'details': result.stderr}
    except Exception as e:
        return {'error': str(e)}