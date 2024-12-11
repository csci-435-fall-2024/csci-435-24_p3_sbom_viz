import subprocess
import json
import os
import logging
try:
    # for testing
    from trivy_output_parser import TrivyOutputParser
    from bomber_output_parser import BomberOutputParser
except:
    # for running from views
    from sbom_viz.scripts.trivy_output_parser import TrivyOutputParser
    from sbom_viz.scripts.bomber_output_parser import BomberOutputParser


def run_bomber_scan(path_to_sbom: str):
    result=subprocess.run(args=["bomber", "scan", path_to_sbom, "--output", "json"], text=True, encoding="utf-8", capture_output=True)
    try:
        # convert output from subprocess into a dictionary
        bomber_output=json.loads(result.stdout.strip())
        logger.info("[bomber] Bomber scan was successful")
        return bomber_output
    except json.decoder.JSONDecodeError as e:
        if "No packages were detected. Nothing has been scanned." in result.stdout:
            logger.info("[bomber] No packages were detected. Nothing has been scanned.")
            return None
        # shouldn't reach this case since file not found should have been handled by trivy scan (it's here just in case)
        elif "The system cannot find the file specified" in result.stdout:
            logger.error("[bomber] "+result.stdout.strip())
            logger.info("The program has exited due to file not found error")
            remove_sbom(path_to_sbom)
            exit()
    
def run_trivy_scan(path_to_sbom:str):
    try:
        result=subprocess.run(args=["trivy", "sbom", "--format=json", path_to_sbom], text=True, encoding="utf-8", capture_output=True)

        # convert output from subprocess into a dictionary
        trivy_output=json.loads(result.stdout.strip())

        # if trivy found no packages to scan
        if "Results" not in trivy_output.keys():
            logger.info("[trivy] Found no packages to scan")
            return None
        logger.info("[trivy] Trivy scan was successful")
        return trivy_output
    except json.decoder.JSONDecodeError as e:
        # if there is no stdout, it's likely that trivy wasn't able to scan the sbom due to errors like "file not found" or unsupported type
        if result.stdout=='':
            logger.info("[trivy] Trivy scan failed")
            for log_message in result.stderr.split('\n'):
                if log_message=='':
                    continue
                message_parts=log_message.split('\t')
                if message_parts[2]=="[vuln] Vulnerability scanning is enabled":
                    logger.debug("[trivy] Vulnerability scanning is enabled")
                if message_parts[2]=="Detected SBOM format":
                    logger.debug("[trivy] Detected SBOM format; "+ message_parts[3])
                if message_parts[1]=="FATAL":
                    # if the system cannot find the file exit the program; there is no point to try with bomber since it'll likely encounter the same issue
                    if "failed to open sbom file error" in message_parts[3]:
                        logger.error("[trivy] "+message_parts[3])
                        logger.info("The program has exited due to file not found error")
                        remove_sbom(path_to_sbom)
                        exit()
                    else:
                        logger.info("[trivy] "+message_parts[3])
            return False
        else:
            print(result.stderr)
            logger.error("[trivy] An unexpected error occured during the Trivy scan")
            return False
            #raise e
    
def run_security_scan(path_to_sbom: str):
    # To Do: sanitize input, file type check for scanning tools
    scan_type="trivy"
    # run trivy first
    result=run_trivy_scan(path_to_sbom)

    # if the trivy scan doesn't work, use bomber
    if result==False or result==None:
        if result==False:
            logger.info("Trivy failed to scan. Now attempting Bomber scan.")
        else:
            logger.info("Trivy found nothing to scan. Now attempting Bomber scan.")
        scan_type="bomber"
        result=run_bomber_scan(path_to_sbom)
    
    if result==None:
        return None
    
    # if neither security tool worked, log warning message
    if result==False:
        logger.warning("Unable to scan for security vulnerabilites")
        return False
    
    logger.info("Finished security scan")
    return (scan_type, result)

def write_sbom(sbom_data, file_path):
    # Write data to JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(sbom_data)

    logger.debug(f"SBOM file '{file_path}' has been created successfully.")

def remove_sbom(filename):
    if os.path.exists(filename):
        os.remove(filename)
        logger.debug(f"File '{filename}' has been deleted successfully.")
    else:
        logger.debug(f"File '{filename}' does not exist.")

def get_security_output(sbom_parser): 
    #might have to change path for writing sbom
    sbom_data=sbom_parser.get_sbom_data()
    file_ext=sbom_data[0]
    filename="sbom."+file_ext
    write_sbom(sbom_data[1], filename)
    try:   
        scan_output=run_security_scan(filename)
        if (scan_output==False) or (scan_output==None):
            print(scan_output)
            remove_sbom(filename)
            return scan_output
        scan_type=scan_output[0]
        if scan_type=="trivy":
            parser=TrivyOutputParser(sbom_parser, scan_output[1])
            final_security_output=parser.reformat_trivy_output()
        elif scan_type=="bomber":
            parser=BomberOutputParser(sbom_parser, scan_output[1])
            final_security_output=parser.reformat_bomber_output()
    except Exception as e:
        remove_sbom(filename)
        raise e
    remove_sbom(filename) # should I remove? #are we storing already loaded sboms
    return final_security_output

logger = logging.getLogger('security')

#run_trivy_scan("../../Artifacts/sbom_examples/cyclonedx/1.2/laravel.bom.1.2.xml") #xml on trivy
#print(run_trivy_scan("../../Artifacts/sbom_examples/cyclonedx/1.3/cargo-valid-bom-1.3.json")) # scanning occured but found nothing
#run_trivy_scan("../../Artifacts/sbom_examples/cyclonedx/1.4/railsgoat.cyclonedx.json")
#print(run_trivy_scan("../../Artifacts/sbom_examples/cyclonedx/1.5/small.cyclonedx.json"))
#run_trivy_scan("../../Artifacts/sbom_examples/spdx/2.2/example1.spdx")
#run_trivy_scan("../../Artifacts/sbom_examples/spdx/3.0/example1.json") #trivy unable to determine sbom format
#run_trivy_scan("../../Artifacts/sbom_examples/spdx/2.2/examle1.spdx") #file not found
#print(run_trivy_scan("../../Artifacts/Examples/Erroneous SBOMs/bom.json"))

#run_bomber_scan("../../Artifacts/sbom_examples/cyclonedx/1.2/laravel.bom.1.2.xml") # No packages were detected. Nothing has been scanned
#print(run_bomber_scan("../../Artifacts/sbom_examples/cyclonedx/1.3/cargo-valid-bom-1.3.json")) # scanning occured but found nothing
#print(run_bomber_scan("../../Artifacts/sbom_examples/cyclonedx/1.4/expression-license.json"))
#print(run_bomber_scan("../../Artifacts/sbom_examples/cyclonedx/1.4/railsgoat.cyclonedx.json"))
#run_bomber_scan("../../Artifacts/sbom_examples/cyclonedx/1.5/small.cyclonedx.json")
#run_bomber_scan("../../Artifacts/sbom_examples/spdx/2.2/example1.spdx")
#run_bomber_scan("../../Artifacts/sbom_examples/spdx/3.0/example1.json") #trivy unable to determine sbom format
#run_bomber_scan("../../Artifacts/sbom_examples/spdx/2.2/examle1.spdx") #file not found
#print(run_bomber_scan("../../Artifacts/sbom_examples/spdx/2.3/sampleSPDX.json"))

#scan=run_security_scan("../../Artifacts/sbom_examples/cyclonedx/1.2/laravel.bom.1.2.xml")
#scan=run_security_scan("../../Artifacts/sbom_examples/cyclonedx/1.4/railsgoat.cyclonedx.json")
#scan=run_security_scan("../../Artifacts/sbom_examples/cyclonedx/1.3/cargo-valid-bom-1.3.json")
#scan=run_security_scan("../../Artifacts/sbom_examples/cyclonedx/1.5/small.cyclonedx.json")
#scan=run_security_scan("../../Artifacts/sbom_examples/spdx/2.2/example1.spdx") # both no packages to scan
#scan=run_security_scan("../../Artifacts/sbom_examples/spdx/3.0/example1.json") 
#scan=run_security_scan("../../Artifacts/sbom_examples/spdx/2.2/examle1.spdx") #file not found
#scan=run_security_scan("../../Artifacts/sbom_examples/spdx/2.3/sampleSPDX.json")
#scan=run__scan("../../Artifacts/sbom_examples/cyclonedx/1.3/cargo-valid-bom-1.3.json")
#scan=run_security_scan("../../Artifacts/sbom_examples/spdx/2.2/example7-bin.spdx.json")
#print(scan)

