import logging

logger = logging.getLogger('security')

class BomberOutputParser():
    def __init__(self, sbom_parser, scan_output:dict):
        self.sbom_parser=sbom_parser
        self.scan_output=scan_output

    def __find_corresponding_sbom_component(self, purl:str):
        purl_id_map=self.sbom_parser.get_purl_id_map()
        return purl_id_map[purl]


    def __make_vuln_dict(self, vuln_info:dict):
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
            vuln_dict["VulnerabilityID"]=vuln_info["id"]
            vuln_dict["Title"]=vuln_info["title"]
            vuln_dict["Description"]=vuln_info["description"]
            vuln_dict["Severity"]=vuln_info["severity"]

            # if the vulnerability id is a CVE id, add NVD as a reference
            if "CVE" in vuln_dict["VulnerabilityID"]:
                nvd_ref="https://nvd.nist.gov/vuln/detail/"+vuln_dict["VulnerabilityID"]
                vuln_dict["References"].append(nvd_ref)

            # if the vulnerability id is a GHSA id, add ghsa as a reference
            elif "GHSA" in vuln_dict["VulnerabilityID"]:
                ghsa_ref="https://github.com/advisories/"+vuln_dict["VulnerabilityID"]
                vuln_dict["References"].append(ghsa_ref)

            # if the vulnerability id is a RUSTSEX id, add rustsec as a reference
            elif "RUSTSEC" in vuln_dict["VulnerabilityID"]:
                rustsec_ref="https://rustsec.org/advisories/"+vuln_dict["VulnerabilityID"]+".html"
                vuln_dict["References"].append(rustsec_ref)

        except KeyError as e:
            print(vuln_dict)
            raise e
        
        return vuln_dict

    def reformat_bomber_output(self):
        sec_info={"Summary":{"SeverityDistr":[{"name":"Critical", "count":0}, 
                                            {"name":"High", "count":0}, 
                                            {"name":"Medium", "count":0}, 
                                            {"name":"Low", "count":0},
                                            {"name":"None", "count":0},
                                            {"name":"Unknown", "count":0}],
                            "Top_10":{}}, 
                    "Effected_Components":{}}
        
        if "packages" not in self.scan_output.keys():
            logger.info("[bomber parser] No vulnerabilites were found by bomber scan using osv provider")
            return sec_info
        
        # update severity distributions
        sec_info["Summary"]["SeverityDistr"][5]["count"]=self.scan_output["summary"]["Unspecified"]
        sec_info["Summary"]["SeverityDistr"][3]["count"]=self.scan_output["summary"]["Low"]
        sec_info["Summary"]["SeverityDistr"][2]["count"]=self.scan_output["summary"]["Moderate"]
        sec_info["Summary"]["SeverityDistr"][1]["count"]=self.scan_output["summary"]["High"]
        sec_info["Summary"]["SeverityDistr"][0]["count"]=self.scan_output["summary"]["Critical"]

        for pkg in self.scan_output["packages"]:
            purl=pkg["coordinates"]
            sbom_id=self.__find_corresponding_sbom_component(purl)
            for vuln in pkg["vulnerabilities"]:                
                vuln_dict=self.__make_vuln_dict(vuln)
                # check if sbom_id is already in sec_info
                if sbom_id not in sec_info["Effected_Components"].keys():
                    component_dict={"PURL": "",
                        "Dependents":[],
                        "InstalledVersion": "",
                        "Vulnerabilities":[]}
                    component_dict["PURL"]=purl
                    sec_info["Effected_Components"][sbom_id]=component_dict

                sec_info["Effected_Components"][sbom_id]["Vulnerabilities"].append(vuln_dict) 
        
        return sec_info