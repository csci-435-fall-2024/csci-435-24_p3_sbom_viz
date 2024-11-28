import subprocess
import json
import os
import logging
from sbom_viz.scripts.trivy_output_parser import TrivyOutputParser
from sbom_viz.scripts.bomber_output_parser import BomberOutputParser


def run_bomber_scan(path_to_sbom: str):
    result=subprocess.run(args=["bomber", "scan", path_to_sbom, "--output", "json"], text=True, encoding="utf-8", capture_output=True)
    #print(result)
    try:
        bomber_output=json.loads(result.stdout.strip())
        return bomber_output
    except json.decoder.JSONDecodeError as e:
        if "No packages were detected. Nothing has been scanned." in result.stdout:
            logging.info("[bomber] No packages were detected. Nothing has been scanned.")
            return False
        # shouldn't reach this case since file not found should have been handled by trivy scan (it's here just in case)
        elif "The system cannot find the file specified" in result.stdout:
            exit()
    
def run_trivy_scan(path_to_sbom:str):
    try:
        result=subprocess.run(args=["trivy", "sbom", "--format=json", path_to_sbom], text=True, encoding="utf-8", capture_output=True)

        # convert output from subprocess into a dictionary
        trivy_output=json.loads(result.stdout.strip())

        # if trivy found no packages to scan
        if "Results" not in trivy_output.keys():
            #print(result.stderr)
            #print(trivy_output)
            logging.info("[trivy] Found no packages to scan")
            return False
        
        return trivy_output
    except Exception as e:
        # if there is no stdout, it's likely that trivy wasn't able to scan the sbom due to errors like "file not found" or unsupported type
        if result.stdout=='':
            logging.info("[trivy] Trivy scan failed")
            for log_message in result.stderr.split('\n'):
                if log_message=='':
                    continue
                message_parts=log_message.split('\t')
                if message_parts[2]=="[vuln] Vulnerability scanning is enabled":
                    logging.debug("[trivy] Vulnerability scanning is enabled")
                if message_parts[2]=="Detected SBOM format":
                    logging.debug("[trivy] Detected SBOM format; "+ message_parts[3])
                if message_parts[1]=="FATAL":
                    # if the system cannot find the file exit the program; there is no point to try with bomber since it'll likely encounter the same issue
                    if "failed to open sbom file error" in message_parts[3]:
                        logging.error("[trivy] "+message_parts[3])
                        exit()
                    else:
                        logging.info("[trivy] "+message_parts[3])
            return False
        else:
            print(result)
            logging.error("[trivy] An unexpected error occured during the Trivy scan")
            raise e
    
def run_security_scan(path_to_sbom: str):
    # To Do: sanitize input, error checks, bomber scan for backup, file type check for scanning tools
    # Note: runs from current directory
    scan_type="trivy"
    # run trivy first
    result=run_trivy_scan(path_to_sbom)

    # if the trivy scan doesn't work, use bomber
    if result==False:
        logging.info("Trivy failed to scan. Now attempting Bomber scan.")
        scan_type="bomber"
        result=run_bomber_scan(path_to_sbom)
    
    # if neither work, exit and return error message
    if result==False:
        logging.warning("Unable to scan for security vulnerabilites or both tools determined there was nothing scan")
        exit()

    logging.info("Finished security scan")
    return (scan_type, result)

def update_severity_distribution(sec_info:dict, vuln_dict:dict):
    severity=vuln_dict["Severity"]
    if severity=="CRITICAL":
        sec_info["Summary"]["SeverityDistr"][0]["count"]+=1
    elif severity=="HIGH":
        sec_info["Summary"]["SeverityDistr"][1]["count"]+=1
    elif severity=="MEDIUM":
        sec_info["Summary"]["SeverityDistr"][2]["count"]+=1
    elif severity=="LOW":
        sec_info["Summary"]["SeverityDistr"][3]["count"]+=1
    elif severity=="NONE":
        sec_info["Summary"]["SeverityDistr"][4]["count"]+=1
    elif severity=="UNKNOWN":
        sec_info["Summary"]["SeverityDistr"][5]["count"]+=1

def update_top_10(sec_info:dict, vuln_dict:dict, sbom_id, cve_to_remove=None):
    top_10_vuln= {"SBOM_ID": "",
                "SeveritySource":"",
                "Title":"",
                "Description": "",
                "Severity": "",
                "Displayed_CVSS": 0}
    
    
    if cve_to_remove is not None:
        del sec_info["Summary"]["Top_10"][cve_to_remove]
    for key in top_10_vuln.keys():
        if key == "SBOM_ID":
            top_10_vuln[key]=sbom_id
        else:
            top_10_vuln[key]=vuln_dict[key]
    sec_info["Summary"]["Top_10"][vuln_dict["VulnerabilityID"]]=top_10_vuln
            
# directly parses sbom
def find_corresponding_sbom_component_old(purl:str, sbom_file):
    with open(sbom_file, 'r') as file:
        data = json.load(file)

        # Iterating through the json #SPDX 2.3
        for package in data['packages']:
            if "externalRefs" not in package.keys():
                continue
            external_refs=package["externalRefs"]
            if len(external_refs)!=0:
                for ind, ref in enumerate(external_refs):
                    if external_refs[ind]["referenceType"]=="purl" and external_refs[ind]["referenceLocator"]==purl:
                        return package["SPDXID"]

def find_corresponding_sbom_component(purl:str, sbom_parser):
    purl_id_map=sbom_parser.get_purl_id_map()
    return purl_id_map[purl]


def make_vuln_dict(vuln_info):
    keys_missing=[]
    vuln_dict={"VulnerabilityID": "",
                "SeveritySource":"",
                "Status":"",
                "Title":"",
                "Description": "",
                "Severity": "",
                "CWE_IDs":[],
                "CVSS": {},
                "Displayed_CVSS":None,
                "References": [],
                "PublishedDate":"",
                "LastModifiedDate":""}
    try:
        # find the missing keys to prevent key errors from crashing the code
        for key in vuln_dict.keys():
            if key in ["VulnerabilityID", "SeveritySource", "Status", "Title", "Description", "Severity", "CVSS", "PublishedDate", "LastModifiedDate"] and key not in vuln_info.keys():
                keys_missing.append(key)
                print(key, "missing")
            elif key == "CWE_IDs" and "CweIDs" not in vuln_info.keys():
                keys_missing.append(key)
            elif key ==  "Displayed_CVSS" and "CVSS" in keys_missing:
                keys_missing.append("Displayed_CVSS")
            elif key == "References":
                pass

        for key in vuln_dict.keys():
            if key in keys_missing:
                continue
            elif key in ["VulnerabilityID", "SeveritySource", "Status", "Title", "Description", "Severity", "CVSS", "PublishedDate", "LastModifiedDate"]:
                vuln_dict[key]=vuln_info[key]
            elif key == "CWE_IDs":
                vuln_dict[key]=vuln_info["CweIDs"]
            elif key ==  "Displayed_CVSS":
                vuln_dict[key]=vuln_info["CVSS"][vuln_dict["SeveritySource"]]["V3Score"]
            elif key == "References":
                pass
    except KeyError as e:
        print(vuln_dict)
        raise e
    
    return vuln_dict

def reformat_bomber_output(scan_output, sbom_parser):
    sec_info={"Summary":{"SeverityDistr":[{"name":"Critical", "count":0}, 
                                          {"name":"High", "count":0}, 
                                          {"name":"Medium", "count":0}, 
                                          {"name":"Low", "count":0},
                                          {"name":"None", "count":0},
                                          {"name":"Unknown", "count":0}],
                        "Top_10":{}}, 
                "Effected_Components":{}}
    
    # update severity distributions
    sec_info["Summary"]["SeverityDistr"][5]=scan_output["summary"]["Unspecified"]
    sec_info["Summary"]["SeverityDistr"][3]=scan_output["summary"]["Low"]
    sec_info["Summary"]["SeverityDistr"][2]=scan_output["summary"]["Moderate"]
    sec_info["Summary"]["SeverityDistr"][1]=scan_output["summary"]["High"]
    sec_info["Summary"]["SeverityDistr"][0]=scan_output["summary"]["Critical"]

    for pkg in scan_output["packages"]:
        purl=pkg["coordinates"]
        for count, vuln in enumerate(pkg["vulnerabilities"]):
            #print(count)
            sbom_id=find_corresponding_sbom_component(purl, sbom_parser)
            vuln_dict=make_vuln_dict(vuln)
            # check if sbom_id is already in sec_info
            if sbom_id not in sec_info["Effected_Components"].keys():
                component_dict={"PURL": "",
                    "Dependents":[],
                    "InstalledVersion": "",
                    "Vulnerabilities":[]}
                component_dict["PURL"]=purl
                component_dict["InstalledVersion"]=vuln["InstalledVersion"]
                sec_info["Effected_Components"][sbom_id]=component_dict

            sec_info["Effected_Components"][sbom_id]["Vulnerabilities"].append(vuln_dict) 
            
            if count==stop_ind:
                return sec_info 
    
    return sec_info

def reformat_trivy_output(scan_output, sbom_parser, stop_ind=-1):
    sec_info={"Summary":{"SeverityDistr":[{"name":"Critical", "count":0}, 
                                          {"name":"High", "count":0}, 
                                          {"name":"Medium", "count":0}, 
                                          {"name":"Low", "count":0},
                                          {"name":"None", "count":0},
                                          {"name":"Unknown", "count":0}],
                        "Top_10":{}}, 
                "Effected_Components":{}}

    top_10_cvss={} #tied scores?
    for pkg_type in scan_output["Results"]:
        # no vulnerabilites found for packages of package type
        if "Vulnerabilites" not in pkg_type["Vulnerabilities"]:
            print("No vulnerabilites found for packages with package type", pkg_type["Type"])
        for count, vuln in enumerate(pkg_type["Vulnerabilities"]):
            #print(count)
            purl=vuln["PkgIdentifier"]["PURL"]
            sbom_id=find_corresponding_sbom_component(purl, sbom_parser)
            vuln_dict=make_vuln_dict(vuln)
            # check if sbom_id is already in sec_info
            if sbom_id not in sec_info["Effected_Components"].keys():
                component_dict={"PURL": "",
                    "Dependents":[],
                    "InstalledVersion": "",
                    "Vulnerabilities":[]}
                component_dict["PURL"]=purl
                component_dict["InstalledVersion"]=vuln["InstalledVersion"]
                sec_info["Effected_Components"][sbom_id]=component_dict

            sec_info["Effected_Components"][sbom_id]["Vulnerabilities"].append(vuln_dict) 

            # update summary
            update_severity_distribution(sec_info, vuln_dict)
            cvss=vuln_dict["Displayed_CVSS"]
            if cvss==None:
                pass
            elif len(top_10_cvss)<10:
                top_10_cvss[vuln_dict["VulnerabilityID"]]=cvss
                top_10_cvss={key: value for key, value in sorted(top_10_cvss.items(), key=lambda item: item[1], reverse=True)}
                update_top_10(sec_info, vuln_dict, sbom_id)
            elif cvss>list(top_10_cvss.items())[-1][1]: #tie?
                lowest_cve, lowest_cvss = top_10_cvss.popitem()
                cve_to_remove=lowest_cve
                top_10_cvss[vuln_dict["VulnerabilityID"]]=cvss
                top_10_cvss={key: value for key, value in sorted(top_10_cvss.items(), key=lambda item: item[1], reverse=True)} 
                update_top_10(sec_info, vuln_dict, sbom_id, cve_to_remove)
            
            if count==stop_ind:
                return sec_info 
    
    sec_info["Summary"]["Top_10"] = dict(sorted(sec_info["Summary"]["Top_10"].items(), key=lambda item: item[1]["Displayed_CVSS"], reverse=True))
    return sec_info

# currently only for json
def write_sbom(sbom_data, file_path):
    # Write data to JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(sbom_data)

    print(f"JSON file '{file_path}' has been created successfully.")

def remove_sbom(filename):
    if os.path.exists(filename):
        os.remove(filename)
        print(f"File '{filename}' has been deleted successfully.")
    else:
        print(f"File '{filename}' does not exist.")

def get_security_output(sbom_parser): 
    #might have to change path for writing sbom
    write_sbom(sbom_parser.get_sbom_data(), 'sbom.json')   
    scan_output=run_security_scan("sbom.json")
    # need to consider if trivy fails
    scan_type=scan_output[0]
    if scan_type=="trivy":
        parser=TrivyOutputParser(sbom_parser, scan_output[1])
        final_security_output=parser.reformat_trivy_output()
    elif scan_type=="bomber":
        parser=BomberOutputParser()
    remove_sbom("sbom.json") # should I remove? #are we storing already loaded sboms
    return final_security_output

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)

#run_trivy_scan("../../Artifacts/sbom_examples/cyclonedx/1.2/laravel.bom.1.2.xml") #xml on trivy
#print(run_trivy_scan("../../Artifacts/sbom_examples/cyclonedx/1.3/cargo-valid-bom-1.3.json")) # scanning occured but found nothing
#run_trivy_scan("../../Artifacts/sbom_examples/cyclonedx/1.4/railsgoat.cyclonedx.json")
#print(run_trivy_scan("../../Artifacts/sbom_examples/cyclonedx/1.5/small.cyclonedx.json"))
#run_trivy_scan("../../Artifacts/sbom_examples/spdx/2.2/example1.spdx")
#run_trivy_scan("../../Artifacts/sbom_examples/spdx/3.0/example1.json") #trivy unable to determine sbom format
#run_trivy_scan("../../Artifacts/sbom_examples/spdx/2.2/examle1.spdx") #file not found

#run_bomber_scan("../../Artifacts/sbom_examples/cyclonedx/1.2/laravel.bom.1.2.xml") # No packages were detected. Nothing has been scanned
#print(run_bomber_scan("../../Artifacts/sbom_examples/cyclonedx/1.3/cargo-valid-bom-1.3.json")) # scanning occured but found nothing
#print(run_bomber_scan("../../Artifacts/sbom_examples/cyclonedx/1.4/railsgoat.cyclonedx.json"))
#run_bomber_scan("../../Artifacts/sbom_examples/cyclonedx/1.5/small.cyclonedx.json")
#run_bomber_scan("../../Artifacts/sbom_examples/spdx/2.2/example1.spdx")
#run_bomber_scan("../../Artifacts/sbom_examples/spdx/3.0/example1.json") #trivy unable to determine sbom format
#run_bomber_scan("../../Artifacts/sbom_examples/spdx/2.2/examle1.spdx") #file not found
#print(run_bomber_scan("../../Artifacts/sbom_examples/spdx/2.3/sampleSPDX.json"))

#run_security_scan("../../Artifacts/sbom_examples/cyclonedx/1.2/laravel.bom.1.2.xml")
#print(run_security_scan("../../Artifacts/sbom_examples/spdx/2.3/sampleSPDX.json")[1])

