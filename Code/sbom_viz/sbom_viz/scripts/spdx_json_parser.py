import json
import re

class SpdxJsonParser():

    def __init__(self):
        self.data = ""
        self.format = ""
        self.version = ""
        self.document = {}
        self.file_list = []
        self.package_list = []
        self.relationship_list = []
        self.id_data_map = {} # component id to component data dictionary mapping
        self.license_frequency_map = {} 
        self.id_license_map = {}
        self.purl_id_map = {} # To be used to identify which component is associated with security vulnerabilities

    def add_to_licenses_frequency_map(self, license_string):
        if (license_string not in self.license_frequency_map):
            self.license_frequency_map[license_string] = 1
        else:
            self.license_frequency_map[license_string] += 1

    def add_to_id_license_map(self, id, license): 
        # This method will return an integer value for how many times licenses were ignored with a new value
        # This would happen if an id has a license added to it multiple times
        ignore_count = 0
        if (id in self.id_license_map and license != self.id_license_map[id]): # True when an id already has a license stored that is different from the passed in license
            ignore_count += 1 
        elif (id not in self.id_license_map): 
            self.id_license_map[id] = license
        return ignore_count

    def parse_licensing_information(self):
        if ((self.version == "SPDX-2.3" or self.version == "SPDX-2.2") and self.format == "json"): 
            data_object = json.loads(self.data)
            if ("dataLicense" in data_object): # This handles the top-level document metadata component
                self.add_to_licenses_frequency_map(data_object["dataLicense"])
                if ("SPDXID" in data_object):
                    self.add_to_id_license_map(data_object["SPDXID"], data_object["dataLicense"])
            if ('packages' in data_object):
                for package in data_object['packages']:
                    if ("licenseDeclared" in package and package["licenseDeclared"] == "NOASSERTION" and "licenseConcluded" in package): # SPDX documentation says to prefer licenseDeclared over licenseConcluded, so it is only used when licenseDeclared is NOASSERTION
                        self.add_to_licenses_frequency_map(package['licenseConcluded'])
                        if ("SPDXID" in package):
                            self.add_to_id_license_map(package["SPDXID"], package["licenseConcluded"])
                    elif ("licenseDeclared" in package):
                        self.add_to_licenses_frequency_map(package['licenseDeclared'])
                        if ("SPDXID" in package):
                            self.add_to_id_license_map(package["SPDXID"], package["licenseDeclared"])
            if ('files' in data_object):
                for file in data_object['files']:
                    if ("licenseConcluded" in file and file["licenseConcluded"] != "NOASSERTION"):
                        self.add_to_licenses_frequency_map(file["licenseConcluded"])
                        if ("SPDXID" in file):
                            self.add_to_id_license_map(file["SPDXID"], file["licenseConcluded"])
                    elif ("licenseInfoInFile" in file): # might be a list of licenses. This is an alternative storage of license info
                        licenseInfo = ""
                        count = 1
                        num_licenses = len(file["licenseInfoInFile"])
                        for license in file["licenseInfoInFile"]:
                            licenseInfo += license
                            if (count < num_licenses):
                                licenseInfo += " and "
                            count += 1
                        self.add_to_licenses_frequency_map(licenseInfo)
                        if ("SPDXID" in file):
                            self.add_to_id_license_map(file["SPDXID"], licenseInfo)
                    else: # if no licensing information is stored for a file, it is equivalent to NOASSERTION according to SPDX documentation https://spdx.github.io/spdx-spec/v2.3/file-information/
                        self.add_to_licenses_frequency_map("NOASSERTION")
                        if ("SPDXID" in file):
                            self.add_to_id_license_map(file["SPDXID"], "NOASSERTION")

        elif ((self.version == "SPDX-3.0") and self.format == "json"):
            data_object = json.loads(self.data)
            graph = data_object.get("@graph", [])
            
            for node in graph:
                if node.get("type") == "Relationship" and node.get("relationshipType") in ["hasConcludedLicense", "hasDeclaredLicense"]:
                    license_id = node.get("to", [])[0] if isinstance(node.get("to"), list) else node.get("to")
                    component_id = node.get("from")
                    
                    if component_id and license_id:
                        self.id_license_map[component_id] = license_id
                    
                    if license_id:
                        self.license_frequency_map[license_id] = self.license_frequency_map.get(license_id, 0) + 1

    def find_version(self):
        if (self.format == "json"):
            if "spdxVersion" in self.data:
                match = re.search("spdxVersion\"", self.data)
                seeker = match.end() 
                found_quote = False
                spdx_version = ""
                while True:
                    if (found_quote == False and self.data[seeker] == "\""):
                        found_quote = True
                    elif (self.data[seeker] == "\""):
                        break;
                    elif (found_quote):
                        spdx_version += self.data[seeker]
                    seeker += 1
                self.version = spdx_version
            elif "@context" in self.data:
                self.version = "SPDX-3.0"

    # returns a dictionary holding the sbom document component without the files, packages, or relationships attributes
    # since that information can be accessed through other functions
    def parse_document_information(self):
        document = {}
        if ((self.version == "SPDX-2.3" or self.version == "SPDX-2.2") and self.format == "json"): 
            data_object = json.loads(self.data)
            for attribute in data_object:
                if (attribute == "SPDXID"):
                    document['id'] = data_object[attribute]
                elif (attribute == 'files' or attribute == 'relationships' or attribute == 'packages'):
                    continue
                else:
                    document[attribute] = data_object[attribute]

        elif ((self.version == "SPDX-3.0") and self.format == "json"):
            data_object = json.loads(self.data)
            graph = data_object.get("@graph", [])
            for node in graph:
                if node.get("type") == "SpdxDocument":
                    for attribute in node:
                        if (attribute == "spdxId"):
                            document['id'] = node[attribute]
                        elif (attribute == 'files' or attribute == 'relationships' or attribute == 'packages'):
                            continue
                        else:
                            document[attribute] = node[attribute]
        self.document = document
    
    def parse_file_information(self):
        file_list = []
        if ((self.version == "SPDX-2.3" or self.version == "SPDX-2.2") and self.format == "json"): 
            data_object = json.loads(self.data)
            if ("files" in data_object):
                for file in data_object["files"]:
                    reformatted_file = {} # We need to replace the attribute name 'SPDXID' with 'id'
                    for attribute in file:
                        if (attribute == "SPDXID"):
                            reformatted_file['id'] = file[attribute]
                        else:
                            reformatted_file[attribute] = file[attribute]
                    file_list.append(reformatted_file)

        elif ((self.version == "SPDX-3.0") and self.format == "json"):
            data_object = json.loads(self.data)
            graph = data_object.get("@graph", [])
            for node in graph:
                if node.get("type") == "software_File":
                    reformatted_file = {}
                    for attribute in node:
                        if (attribute == "spdxId"):
                            reformatted_file['id'] = node[attribute]
                        elif (attribute == "software_copyrightText"):
                            reformatted_file['copyrightText'] = node[attribute]
                        elif (attribute == "software_downloadLocation"):
                            reformatted_file['downloadLocation'] = node[attribute]
                        else:
                            reformatted_file[attribute] = node[attribute]
                    file_list.append(reformatted_file)
        self.file_list = file_list

    def parse_package_information(self):
        package_list = []
        if ((self.version == "SPDX-2.3" or self.version == "SPDX-2.2") and self.format == "json"): 
            data_object = json.loads(self.data)
            if ('packages' in data_object):
                for package in data_object['packages']:
                    reformatted_package = {}
                    for attribute in package:
                        if (attribute == "SPDXID"):
                            reformatted_package['id'] = package[attribute]
                        else:
                            reformatted_package[attribute] = package[attribute]
                    package_list.append(reformatted_package)
        elif ((self.version == "SPDX-3.0") and self.format == "json"):
            data_object = json.loads(self.data)
            graph = data_object.get("@graph", [])
            for node in graph:
                if node.get("type") == "software_Package":
                    reformatted_file = {}
                    for attribute in node:
                        if (attribute == "spdxId"):
                            reformatted_file['id'] = node[attribute]
                        elif (attribute == "software_copyrightText"):
                            reformatted_file['copyrightText'] = node[attribute]
                        elif (attribute == "software_downloadLocation"):
                            reformatted_file['downloadLocation'] = node[attribute]
                        else:
                            reformatted_file[attribute] = node[attribute]
                    package_list.append(reformatted_file)
        
        self.package_list = package_list

    def parse_relationship_information(self):
        relationship_list = []
        if ((self.version == "SPDX-2.3" or self.version == "SPDX-2.2") and self.format == "json"): 
            data_object = json.loads(self.data)
            if ('relationships' in data_object):
                for relationship in data_object['relationships']:
                    reformatted_relationship = {}
                    for attribute in relationship:
                        if (attribute == 'spdxElementId'):
                            reformatted_relationship['source_id'] = relationship[attribute]
                        elif (attribute == 'relatedSpdxElement'):
                            reformatted_relationship['target_id'] = relationship[attribute]
                        elif (attribute == 'relationshipType'):
                            reformatted_relationship['type'] = relationship[attribute]
                    relationship_list.append(reformatted_relationship)
            if ('documentDescribes' in data_object): 
                # There may be relationships described from the top-level sbom component that weren't present in relationships
                for target_id in data_object['documentDescribes']:
                    relationship = {}
                    if ("SPDXID" in data_object):
                        relationship['source_id'] = data_object['SPDXID']
                    relationship['type'] = "DESCRIBES"
                    relationship['target_id'] = target_id
                    relationship_list.append(relationship)
        elif ((self.version == "SPDX-3.0") and self.format == "json"):
            data_object = json.loads(self.data)
            graph = data_object.get("@graph", [])
            for node in graph:
                if node.get("type") == "Relationship":
                    if node.get("relationshipType") in ["hasConcludedLicense", "hasDeclaredLicense"]:
                        continue
                    reformatted_relationship = {}
                    rel_type = node.get("relationshipType")
                    rel_type = node.get("relationshipType")
                    from_id = node.get("from")
                    to_list = node.get("to", [])

                    if isinstance(to_list, list):
                        for target in to_list:
                            reformatted_relationship = {
                                "type": rel_type,
                                "source_id": from_id,
                                "target_id": target,
                                "spdxId": node.get("spdxId"),
                                "creationInfo": node.get("creationInfo"),
                            }
                            relationship_list.append(reformatted_relationship)
                    else:
                        reformatted_relationship = {
                            "type": rel_type,
                            "from": from_id,
                            "target_id": to_list,
                            "spdxId": node.get("spdxId"),
                            "creationInfo": node.get("creationInfo"),
                        }
                        relationship_list.append(reformatted_relationship)
        self.relationship_list = relationship_list

    # Must be called after parsing document, file, and package information
    # Otherwise get_components() will be inacurate
    def parse_id_to_data_map(self):
        for component in self.get_components():
            if ('id' in component):
                self.id_data_map[component['id']] = component
    
    # Must be called after parsing document, file, and package information
    # Otherwise get_components() will be inacurate
    def parse_purl_to_id_map(self):
        
        for component in self.get_components():
            if ((self.version == "SPDX-2.3" or self.version == "SPDX-2.2") and self.format == "json" and 'id' in component and 'externalRefs' in component):
                for ref in component['externalRefs']:
                    if ('referenceType' in ref and ref['referenceType'] == "purl" and 'referenceLocator' in ref):
                        purl = ref['referenceLocator']
                        if (purl not in self.purl_id_map):
                            self.purl_id_map[purl] = component['id']
                        else:
                            print("\n\nDuplicate purl detected. This line comes from scripts/parse_files.py in the method parse_purl_to_id_map()\n\n")

    def parse_file(self, sbom_string):
        self.format = "json"
        self.data = sbom_string
        # determine and store version in self.version
        self.find_version()
        self.parse_licensing_information()
        self.parse_document_information()
        self.parse_file_information()
        self.parse_package_information()
        self.parse_relationship_information()
        self.parse_id_to_data_map()
        self.parse_purl_to_id_map()
        
    
    def get_document(self):
        return self.document
    
    def get_files(self):
        return self.file_list
    
    def get_relationships(self):
        return self.relationship_list
    
    def get_packages(self):
        return self.package_list

    def get_components(self):
        components = []
        components.append(self.document)
        components.extend(self.file_list)
        components.extend(self.package_list)
        return components
    
    def get_id_data_map(self):
        return self.id_data_map
    
    def get_license_information(self):
        license_info = {}
        license_info['distribution'] = self.license_frequency_map
        license_info['mapping'] = self.id_license_map
        return license_info

    def get_purl_id_map(self):
        return self.purl_id_map
    
    # for scanning vulnerabilities
    def get_sbom_data(self):
        return self.data
    

# '''Testing'''
# with open('example1.json', 'r') as f:
#     sbom_data = f.read()

# parser = SpdxJsonParser()
# parser.parse_file(sbom_data)

# print("Version:", parser.version)
# print("Document:", parser.document)
# print("Files:", parser.file_list)
# print("Packages:", parser.package_list)
# print("Relationships:", parser.relationship_list)



#example output: Version: SPDX-2.3
# Document: {'id': 'SPDXRef-DOCUMENT', 'name': 'SBOM-SPDX-2d85f548-12fa-46d5-87ce-5e78e5e111f4', 'spdxVersion': 'SPDX-2.3', 'creationInfo': {'created': '2022-11-03T07:10:10Z', 'creators': ['Tool: sigs.k8s.io/bom/pkg/spdx']}, 'dataLicense': 'CC0-1.0', 'documentNamespace': 'https://spdx.org/spdxdocs/k8s-releng-bom-7c6a33ab-bd76-4b06-b291-a850e0815b07', 'documentDescribes': ['SPDXRef-Package-hello-server-src', 'SPDXRef-File-hello-server']}
# Files: [{'id': 'SPDXRef-File-hello-server', 'name': 'hello-server', 'copyrightText': 'NOASSERTION', 'licenseConcluded': 'Apache-2.0', 'fileTypes': ['BINARY'], 'licenseInfoInFiles': ['NONE'], 'checksums': [{'algorithm': 'SHA1', 'checksumValue': '79b7bfed022c9c7c9957d8aec36cb6492a25b42a'}, {'algorithm': 'SHA256', 'checksumValue': 'bd2195f2551328fa3ad870726f5591fd82fdc5dd33a359be79d356dbecd5868b'}, {'algorithm': 'SHA512', 'checksumValue': 'c61eeb0b489bb219b898c6d3044fc431dec58ad999dae2cf0a8067dd1b3e4eef2b186d0f8af63b4d80732aa5146f7b13b1feb7a454227cf26d4525874231a281'}]}]        
# Packages: [{'id': 'SPDXRef-Package-hello-server-src', 'name': 'hello-server-src', 'versionInfo': '0.1.0', 'filesAnalyzed': False, 'licenseDeclared': 'Apache-2.0', 'licenseConcluded': 'Apache-2.0', 'downloadLocation': 'NONE', 'copyrightText': 'NOASSERTION', 'checksums': [], 'externalRefs': [{'referenceCategory': 'PACKAGE-MANAGER', 'referenceLocator': 'pkg:deb/debian/libselinux1-dev@3.1-3?arch=s390x', 'referenceType': 'purl'}]}, {'id': 'SPDXRef-Package-SPDXRef-Package-cargo-hyper-0.14', 'name': 'hyper', 'versionInfo': '0.14', 'filesAnalyzed': False, 'licenseDeclared': 'NOASSERTION', 'licenseConcluded': 'MIT', 'downloadLocation': 'https://github.com/rust-lang/crates.io-index', 'copyrightText': 'NOASSERTION', 'checksums': [{'algorithm': 'SHA256', 'checksumValue': '02c929dc5c39e335a03c405292728118860721b10190d98c2a0f0efd5baafbac'}], 'externalRefs': [{'referenceCategory': 'PACKAGE-MANAGER', 'referenceLocator': 'pkg:cargo/hyper@0.14', 'referenceType': 'purl'}]}, {'id': 'SPDXRef-Package-SPDXRef-Package-cargo-tokio-1', 'name': 'tokio', 'versionInfo': '1.19.2', 'filesAnalyzed': False, 'licenseDeclared': 'NOASSERTION', 'licenseConcluded': 'MIT', 'downloadLocation': 'https://github.com/rust-lang/crates.io-index', 'copyrightText': 'NOASSERTION', 'checksums': [{'algorithm': 'SHA256', 'checksumValue': 'c51a52ed6686dd62c320f9b89299e9dfb46f730c7a48e635c19f21d116cb1439498cebd51a4483d6e68c2fc62d27008252fa4f7b'}], 'externalRefs': [{'referenceCategory': 'PACKAGE-MANAGER', 'referenceLocator': 'pkg:cargo/tokio@1.19.2', 'referenceType': 'purl'}]}, {'id': 'SPDXRef-Package-SPDXRef-Package-cargo-pretty-env-logger-0.4.0', 'name': 'pretty_env_logger', 'versionInfo': '0.4.0', 'filesAnalyzed': False, 'licenseDeclared': 'NOASSERTION', 'licenseConcluded': 'MIT OR Apache-2.0', 'downloadLocation': 'NONE', 'copyrightText': 'NOASSERTION', 'checksums': [{'algorithm': 'SHA256', 'checksumValue': '926d36b9553851b8b0005f1275891b392ee4d2d833852c417ed025477350fb9d'}], 'externalRefs': [{'referenceCategory': 'PACKAGE-MANAGER', 'referenceLocator': 'pkg:cargo/pretty_env_logger@0.4.0', 'referenceType': 'purl'}]}]
# Relationships: [{'source_id': 'SPDXRef-Package-hello-server-src', 'type': 'DEPENDS_ON', 'target_id': 'SPDXRef-Package-SPDXRef-Package-cargo-pretty-env-logger-0.4.0'}, {'source_id': 'SPDXRef-Package-hello-server-src', 'type': 'DEPENDS_ON', 'target_id': 'SPDXRef-Package-SPDXRef-Package-cargo-tokio-1'}, {'source_id': 'SPDXRef-Package-hello-server-src', 'type': 'DEPENDS_ON', 'target_id': 'SPDXRef-Package-SPDXRef-Package-cargo-hyper-0.14'}, {'source_id': 'SPDXRef-File-hello-server', 'type': 'GENERATED_FROM', 'target_id': 'SPDXRef-Package-hello-server-src'}, {'source_id': 'SPDXRef-DOCUMENT', 'type': 'DESCRIBES', 'target_id': 'SPDXRef-Package-hello-server-src'}, {'source_id': 'SPDXRef-DOCUMENT', 'type': 'DESCRIBES', 'target_id': 'SPDXRef-File-hello-server'}]