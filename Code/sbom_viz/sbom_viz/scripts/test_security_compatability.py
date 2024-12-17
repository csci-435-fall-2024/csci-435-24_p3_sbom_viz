from security import *
from parse_files import *
import unittest

class Security_SBOM_Version_Tester(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.file_path="../../Artifacts/sbom_examples/cyclonedx/1.2/juiceshop.cyclonedx.json"

        with open(self.file_path, 'r', encoding="utf-8") as file:
            sbom_data=file.read()
            write_sbom(sbom_data, 'sbom_test.json')

        scan_output=run_security_scan("sbom_test.json")
        self.__trivy_sec_out=scan_output
        self.sbom_parser=SPDXParser()
        self.sbom_parser.parse_file(self.file_path)
        self.trivy_output=reformat_trivy_output(self.__trivy_sec_out, self.sbom_parser)
        
    def test_run_trivy_scan(self):
        file_path="trivy_sec_output"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(self.trivy_output)

    

# Run the tests
if __name__ == "__main__":
    unittest.main()