import subprocess
import json

def run_security_scan(path_to_sbom: str, bind_mount_path:str=None):
    filename="sampleSPDX.json"
    #To Do: sanitize input, error checks, bomber scan for backup
    result=subprocess.run(args=["docker", "run", "--rm", "-v", bind_mount_path+":/root/.cache", "aquasec/trivy:latest", "sbom", "--format=json", "/root/.cache/"+filename], text=True, capture_output=True)
    #bomber_output=subprocess.run(args=["../security_scanning_tools/bomber_0.5.1_windows_amd64/bomber.exe", "scan", path_to_sbom, "--output", "json"], text=True)
    trivy_output=result.stdout.strip()
    #print(bomber_output)
    return json.loads(trivy_output)

def update_summary(sec_info:dict, vuln_dict:dict, sbom_id, update_top_10:bool, cve_to_remove=None):
    #To do: double check None
    top_10_vuln= {"SBOM_ID": "",
                "SeveritySource":"",
                "Title":"",
                "Description": "",
                "Severity": "",
                "CWE_IDs":[],
                "Displayed_CVSS": 0}
    
    severity=vuln_dict["Severity"]
    sec_info["Summary"]["SeverityDistr"][severity]+=1

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
            

def find_corresponding_sbom_component(purl:str, sbom_file):
    with open(sbom_file, 'r') as file:
        data = json.load(file)

        # Iterating through the json list #SPDX 2.3
        for package in data['packages']:
            if "externalRefs" not in package.keys():
                continue
            external_refs=package["externalRefs"]
            if len(external_refs)!=0:
                for ind, ref in enumerate(external_refs):
                    if external_refs[ind]["referenceType"]=="purl" and external_refs[ind]["referenceLocator"]==purl:
                        return package["SPDXID"]

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

    

def reformat_trivy_output(scan_output, sbom_file_path, stop_ind=-1):
    sec_info={"Summary":{"SeverityDistr":{"CRITICAL": 0,
                                            "HIGH": 0,
                                            "MEDIUM": 0,
                                            "LOW": 0,
                                            "NONE": 0
                                        },
                        "Top_10":{}}, 
                "Effected_Components":{}}
    top_10_cvss={} #tied scores?
    
    for pkg_type in scan_output["Results"]:
        for count, vuln in enumerate(pkg_type["Vulnerabilities"]):
            #print(count)
            purl=vuln["PkgIdentifier"]["PURL"]
            sbom_id=find_corresponding_sbom_component(purl, sbom_file_path)
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
            cvss=vuln_dict["Displayed_CVSS"]
            if len(top_10_cvss)<10:
                top_10_cvss[vuln_dict["CVE_ID"]]=cvss
                top_10_cvss={key: value for key, value in sorted(top_10_cvss.items(), key=lambda item: item[1], reverse=True)} #descending? copy or changes directly?
                update_summary(sec_info, vuln_dict, sbom_id, True)
            elif cvss>list(top_10_cvss.items())[-1][1]: #tie?
                lowest_cve, lowest_cvss = top_10_cvss.popitem()
                cve_to_remove=lowest_cve
                top_10_cvss[vuln_dict["CVE_ID"]]=cvss
                top_10_cvss={key: value for key, value in sorted(top_10_cvss.items(), key=lambda item: item[1], reverse=True)} 
                update_summary(sec_info, vuln_dict, sbom_id, True, cve_to_remove)
            else:
                update_summary(sec_info, vuln_dict, sbom_id, False)
            if count==stop_ind:
                return sec_info 
    
    sec_info["Summary"]["Top_10"] = dict(sorted(sec_info["Summary"]["Top_10"].items(), key=lambda item: item[1]["Displayed_CVSS"], reverse=True))
    return sec_info

def get_sec_config():
    config = {}

    with open("./sbom_viz/scripts/sec_config.txt", 'r') as file:
        for line in file:
            key, value = line.strip().split('=', 1)  # Split at the first '='
            config[key] = value
    return config

if __name__ == "__main__":
    scan_output=run_security_scan("../../Artifacts/Examples/Erroneous SBOMs/sampleSPDX.json", get_sec_config()["trivy_path"])
    x=reformat_trivy_output(scan_output, "../../Artifacts/Examples/Erroneous SBOMs/sampleSPDX.json")
    print(json.dumps(x))