import subprocess
import json
import os

def run_security_scan(path_to_sbom: str):
    #To Do: sanitize input, error checks, bomber scan for backup
    # runs from current directory
    result=subprocess.run(args=["./sbom_viz/security_scanning_tools/executables/trivy_0.57.0_windows-64bit/trivy.exe", "sbom", "--format=json", path_to_sbom], text=True, capture_output=True)
    #bomber_output=subprocess.run(args=["../security_scanning_tools/executables/bomber_0.5.1_windows_amd64/bomber.exe", "scan", path_to_sbom, "--output", "json"], text=True)
    trivy_output=result.stdout.strip()
    #print(bomber_output)
    return json.loads(trivy_output)

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
    #unknown, none?/

def update_top_10(sec_info:dict, vuln_dict:dict, sbom_id, cve_to_remove=None):
    top_10_vuln= {"SBOM_ID": "",
                "SeveritySource":"",
                "Title":"",
                "Description": "",
                "Severity": "",
                "Displayed_CVSS": 0}
    
    # update top 10
    if update_top_10:
        if cve_to_remove is not None:
            del sec_info["Summary"]["Top_10"][cve_to_remove]
        for key in top_10_vuln.keys():
            if key == "SBOM_ID":
                top_10_vuln[key]=sbom_id
            else:
                top_10_vuln[key]=vuln_dict[key]
        sec_info["Summary"]["Top_10"][vuln_dict["CVE_ID"]]=top_10_vuln
            
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
    vuln_dict={"CVE_ID": "",
                "SeveritySource":"",
                "Status":"",
                "Title":"",
                "Description": "",
                "Severity": "",
                "CWE_IDs":[],
                "CVSS": {},
                "Displayed_CVSS":0,
                "References": [],
                "PublishedDate":"",
                "LastModifiedDate":""}
    try:
        for key in vuln_dict.keys():
            if key in ["SeveritySource", "Status", "Title", "Description", "Severity", "CVSS", "PublishedDate", "LastModifiedDate"]:
                vuln_dict[key]=vuln_info[key]
            elif key == "CVE_ID":
                vuln_dict[key]=vuln_info["VulnerabilityID"]
            elif key == "CWE_IDs" and "CweIDs" in vuln_info.keys():
                vuln_dict[key]=vuln_info["CweIDs"]
            elif key ==  "Displayed_CVSS":
                vuln_dict[key]=vuln_info["CVSS"][vuln_dict["SeveritySource"]]["V3Score"]
            elif key == "References":
                pass
    except KeyError as e:
        print(vuln_dict)
        raise e
    
    return vuln_dict

def reformat_trivy_output(scan_output, sbom_parser, stop_ind=-1):
    sec_info={"Summary":{"SeverityDistr":[{"name":"Critical", "count":0}, 
                                          {"name":"High", "count":0}, 
                                          {"name":"Medium", "count":0}, 
                                          {"name":"Low", "count":0},
                                          {"name":"None", "count":0}],
                        "Top_10":{}}, 
                "Effected_Components":{}}

    top_10_cvss={} #tied scores?
    
    for pkg_type in scan_output["Results"]:
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
            if len(top_10_cvss)<10:
                top_10_cvss[vuln_dict["CVE_ID"]]=cvss
                top_10_cvss={key: value for key, value in sorted(top_10_cvss.items(), key=lambda item: item[1], reverse=True)}
                update_top_10(sec_info, vuln_dict, sbom_id)
            elif cvss>list(top_10_cvss.items())[-1][1]: #tie?
                lowest_cve, lowest_cvss = top_10_cvss.popitem()
                cve_to_remove=lowest_cve
                top_10_cvss[vuln_dict["CVE_ID"]]=cvss
                top_10_cvss={key: value for key, value in sorted(top_10_cvss.items(), key=lambda item: item[1], reverse=True)} 
                update_top_10(sec_info, vuln_dict, sbom_id, cve_to_remove)
            
            if count==stop_ind:
                return sec_info 
    
    sec_info["Summary"]["Top_10"] = dict(sorted(sec_info["Summary"]["Top_10"].items(), key=lambda item: item[1]["Displayed_CVSS"], reverse=True))
    return sec_info

# currently only for json
def write_sbom(sbom_data, file_path):
    # Write data to JSON file
    with open(file_path, 'w') as file:
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
    final_security_output=reformat_trivy_output(scan_output, sbom_parser)
    remove_sbom("sbom.json") # should I remove? #are we storing already loaded sboms
    return final_security_output