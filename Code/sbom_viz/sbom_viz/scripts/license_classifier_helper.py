import subprocess
import json

def process_with_go_script(cleaned_licenses):
    try:
        cleaned_json = json.dumps(cleaned_licenses)
        # Run the Go script using subprocess
        result = subprocess.run(
            ['./sbom_viz/scripts/license_classifier'],  # Command to run Go script
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