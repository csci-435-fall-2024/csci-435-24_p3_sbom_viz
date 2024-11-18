import unittest
from security import *
from parse_files import *

class Security_Tester(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        file_path="../../Artifacts/Examples/Erroneous SBOMs/sampleSPDX.json"
        with open(file_path, 'r') as file:
            sbom_data=file.read()
            write_sbom(sbom_data, 'sbom_test.json')

        scan_output=run_security_scan("sbom_test.json")
        self.__trivy_sec_out=scan_output
        self.sbom_parser=SPDXParser()
        self.sbom_parser.parse_file(file_path)
        self.trivy_output=reformat_trivy_output(self.__trivy_sec_out, self.sbom_parser)
        
    def test_find_corresponding_sbom_component(self):
        purl="pkg:npm/debug@4.1.1"
        expected="SPDXRef-npm-debug-4.1.1"
        actual=find_corresponding_sbom_component(purl, self.sbom_parser)
        self.assertEqual(expected, actual)

    def test_make_vuln_dict(self):
        vuln_info_1=self.__trivy_sec_out["Results"][0]["Vulnerabilities"][0]
        expected_1={"CVE_ID": "CVE-2017-16137",
                "SeveritySource":"ghsa",
                "Status":"fixed",
                "Title":"nodejs-debug: Regular expression Denial of Service",
                "Description": "The debug module is vulnerable to regular expression denial of service when untrusted user input is passed into the o formatter. It takes around 50k characters to block for 2 seconds making this a low severity issue.",
                "Severity": "LOW",
                "CWE_IDs":["CWE-400"],
                "CVSS": {"ghsa": {
                            "V3Vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L",
                            "V3Score": 3.7
                          },
                        "nvd": {
                            "V2Vector": "AV:N/AC:L/Au:N/C:N/I:N/A:P",
                            "V3Vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L",
                            "V2Score": 5,
                            "V3Score": 5.3
                          },
                        "redhat": {
                            "V3Vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L",
                            "V3Score": 5.3
                          }
                        },
                "Displayed_CVSS":3.7,
                "References": [],
                "PublishedDate":"2018-06-07T02:29:03.817Z",
                "LastModifiedDate":"2023-11-07T02:40:28.13Z"}
        actual_1=make_vuln_dict(vuln_info_1)
        for key in expected_1.keys():
            self.assertEqual(expected_1[key], actual_1[key])

        vuln_info_2=self.__trivy_sec_out["Results"][0]["Vulnerabilities"][10]
        expected_2={"CVE_ID": "CVE-2022-33987",
                "SeveritySource":"ghsa",
                "Status":"fixed",
                "Title":"nodejs-got: missing verification of requested URLs allows redirects to UNIX sockets",
                "Description": "The got package before 12.1.0 (also fixed in 11.8.5) for Node.js allows a redirect to a UNIX socket.",
                "Severity": "MEDIUM",
                "CWE_IDs":[],
                "CVSS": {
                        "ghsa": {
                            "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N",
                            "V3Score": 5.3
                        },
                        "nvd": {
                            "V2Vector": "AV:N/AC:L/Au:N/C:N/I:P/A:N",
                            "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N",
                            "V2Score": 5,
                            "V3Score": 5.3
                        },
                        "redhat": {
                            "V3Vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N",
                            "V3Score": 5.3
                        }
                        },
                "Displayed_CVSS":5.3,
                "References": [],
                "PublishedDate":"2022-06-18T21:15:07.933Z",
                "LastModifiedDate":"2022-06-28T16:15:31.27Z"}
        actual_2=make_vuln_dict(vuln_info_2)
        for key in expected_2.keys():
            self.assertEqual(expected_2[key], actual_2[key])
        
    def test_reformat_trivy_output(self):
        expected_severity_distr=[{"name":"Critical", "count": 1},
                                 {"name":"High", "count":2},
                                 {"name":"Medium", "count": 8},
                                 {"name":"Low", "count": 3},
                                 {"name":"None", "count": 0}]
        actual_severity_distr=self.trivy_output["Summary"]["SeverityDistr"]
        self.assertEqual(expected_severity_distr, actual_severity_distr)
        #write test for top 10

    @classmethod
    def tearDownClass(self):
        # Code to clean up after all tests (only once)
        print("Starting tearing down process")
        filename='sbom_test.json'
        os.remove(filename)

# Run the tests
if __name__ == "__main__":
    unittest.main()