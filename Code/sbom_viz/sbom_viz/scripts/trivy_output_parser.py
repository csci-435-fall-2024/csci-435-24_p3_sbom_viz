import logging

logger = logging.getLogger('security')

class TrivyOutputParser():
    def __init__(self, sbom_parser, scan_output:dict):
        self.sbom_parser=sbom_parser
        self.scan_output=scan_output

    def __update_severity_distribution(self, sec_info:dict, vuln_dict:dict):
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

    def __update_top_10(self, sec_info:dict, vuln_dict:dict, sbom_id, cve_to_remove=None):
        top_10_vuln= {"SBOM_ID": "",
                    "SeveritySource":"",
                    "Title":"",
                    "Description": "",
                    "Severity": "",
                    "Displayed_CVSS": 0}
        
        # update top 10
        if cve_to_remove is not None:
            del sec_info["Summary"]["Top_10"][cve_to_remove]
        for key in top_10_vuln.keys():
            if key == "SBOM_ID":
                top_10_vuln[key]=sbom_id
            else:
                top_10_vuln[key]=vuln_dict[key]

        # add updated top 10 back into sec_info
        sec_info["Summary"]["Top_10"][vuln_dict["VulnerabilityID"]]=top_10_vuln

    def __find_corresponding_sbom_component(self, purl:str):
        purl_id_map=self.sbom_parser.get_purl_id_map()
        return purl_id_map[purl]

    def __make_vuln_dict(self, vuln_info):
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
                    logger.debug("[trivy parser] "+ key + " missing for "+vuln_info["VulnerabilityID"])
                elif key == "CWE_IDs" and "CweIDs" not in vuln_info.keys():
                    keys_missing.append(key)
                elif key ==  "Displayed_CVSS" and "CVSS" in keys_missing:
                    keys_missing.append("Displayed_CVSS")
                #elif key == "References" and ("PrimaryURL" not in vuln_info.keys() and "References" not in vuln_info.keys()):
                    #keys_missing.append("References")

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
                    if "PrimaryURL" in vuln_info.keys():
                        vuln_dict["References"].append(vuln_info["PrimaryURL"])
                    
                    # if the vulnerability has a CVE id, add NVD as a reference
                    if "CVE" in vuln_info["VulnerabilityID"]:
                        nvd_ref="https://nvd.nist.gov/vuln/detail/"+vuln_dict["VulnerabilityID"] 
                        if nvd_ref in vuln_info["References"] and nvd_ref not in vuln_dict["References"]:
                            vuln_dict["References"].append(nvd_ref)

                    # if ghsa is the severity source, add ghsa as a reference
                    if vuln_dict["SeveritySource"]=="ghsa" and ("GHSA" not in vuln_dict["VulnerabilityID"]):
                        ghsa_query="https://github.com/advisories?query="+vuln_dict["VulnerabilityID"]
                        vuln_dict["References"].append(ghsa_query)
        except KeyError as e:
            print(vuln_dict)
            raise e
        
        return vuln_dict

    def reformat_trivy_output(self):
        sec_info={"Summary":{"SeverityDistr":[{"name":"Critical", "count":0}, 
                                            {"name":"High", "count":0}, 
                                            {"name":"Medium", "count":0}, 
                                            {"name":"Low", "count":0},
                                            {"name":"None", "count":0},
                                            {"name":"Unknown", "count":0}],
                            "Top_10":{}}, 
                    "Effected_Components":{}}

        top_10_cvss={} #tied scores?
        for pkg_type in self.scan_output["Results"]:
            # no vulnerabilites found for packages of package type
            if "Vulnerabilities" not in pkg_type.keys():
                logger.info("[trivy parser] No vulnerabilites found for packages with package type "+pkg_type["Type"])
                continue
            for vuln in pkg_type["Vulnerabilities"]:
                purl=vuln["PkgIdentifier"]["PURL"]
                sbom_id=self.__find_corresponding_sbom_component(purl)
                vuln_dict=self.__make_vuln_dict(vuln)
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
                self.__update_severity_distribution(sec_info, vuln_dict)
                cvss=vuln_dict["Displayed_CVSS"]
                if cvss==None:
                    pass
                elif len(top_10_cvss)<10:
                    top_10_cvss[vuln_dict["VulnerabilityID"]]=cvss
                    top_10_cvss={key: value for key, value in sorted(top_10_cvss.items(), key=lambda item: item[1], reverse=True)}
                    self.__update_top_10(sec_info, vuln_dict, sbom_id)
                # if cvss is greater than the current #10, add it to the top 10 and drop current #10
                elif cvss>list(top_10_cvss.items())[-1][1]: #tie? 
                    lowest_cve, lowest_cvss = top_10_cvss.popitem()
                    cve_to_remove=lowest_cve
                    top_10_cvss[vuln_dict["VulnerabilityID"]]=cvss
                    # sort by CVSS score (highest to lowest)
                    top_10_cvss={key: value for key, value in sorted(top_10_cvss.items(), key=lambda item: item[1], reverse=True)} 
                    self.__update_top_10(sec_info, vuln_dict, sbom_id, cve_to_remove)

        # sort by CVSS score (highest to lowest)
        sec_info["Summary"]["Top_10"] = dict(sorted(sec_info["Summary"]["Top_10"].items(), key=lambda item: item[1]["Displayed_CVSS"], reverse=True))

        if not sec_info["Effected_Components"]:
            logger.info("[trivy parser] No vulnerabilites found overall.")
            
        return sec_info
    
