import json
import re
class SPDXParser():

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
        if (self.version == "SPDX-2.3" and self.format == "json"): 
            data_object = json.loads(self.data)
            if ("dataLicense" in data_object): # This handles the top-level document metadata component
                self.add_to_licenses_frequency_map(data_object["dataLicense"])
                if ("SPDXID" in data_object):
                    self.add_to_id_license_map(data_object["SPDXID"], data_object["dataLicense"])
            for package in data_object['packages']:
                if ("licenseDeclared" in package and package["licenseDeclared"] == "NOASSERTION" and "licenseConcluded" in package): # SPDX documentation says to prefer licenseDeclared over licenseConcluded, so it is only used when licenseDeclared is NOASSERTION
                    self.add_to_licenses_frequency_map(package['licenseConcluded'])
                    if ("SPDXID" in package):
                        self.add_to_id_license_map(package["SPDXID"], package["licenseConcluded"])
                elif ("licenseDeclared" in package):
                    self.add_to_licenses_frequency_map(package['licenseDeclared'])
                    if ("SPDXID" in package):
                        self.add_to_id_license_map(package["SPDXID"], package["licenseDeclared"])
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


    def get_version(self):
        match = re.search("spdxVersion\":", self.data)
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

    # returns a dictionary holding the sbom document component without the files, packages, or relationships attributes
    # since that information can be accessed through other functions
    def parse_document_information(self):
        document = {}
        if (self.version == "SPDX-2.3" and self.format == "json"): 
            data_object = json.loads(self.data)
            for attribute in data_object:
                if (attribute == "SPDXID"):
                    document['id'] = data_object[attribute]
                elif (attribute == 'files' or attribute == 'relationships' or attribute == 'packages'):
                    continue
                else:
                    document[attribute] = data_object[attribute]
        self.document = document
    
    def parse_file_information(self):
        file_list = []
        if (self.version == "SPDX-2.3" and self.format == "json"): 
            data_object = json.loads(self.data)
            if ("files" in data_object):
                for file in data_object["files"]:
                    reformatted_file = {} # We need to replace the attribute name 'SPDXID' with 'id'
                    for attribute in file:
                        if (attribute == "SPDXID"):
                            reformatted_file['id'] = file[attribute]
                        elif (attribute == "fileName"):
                            reformatted_file['name'] = file[attribute]
                        else:
                            reformatted_file[attribute] = file[attribute]
                    file_list.append(reformatted_file)
        self.file_list = file_list

    def parse_package_information(self):
        package_list = []
        if (self.version == "SPDX-2.3" and self.format == "json"): 
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
        self.package_list = package_list

    def parse_relationship_information(self):
        relationship_list = []
        if (self.version == "SPDX-2.3" and self.format == "json"): 
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
            if (self.version == "SPDX-2.3" and self.format == "json" and 'id' in component and 'externalRefs' in component):
                for ref in component['externalRefs']:
                    if ('referenceType' in ref and ref['referenceType'] == "purl" and 'referenceLocator' in ref):
                        purl = ref['referenceLocator']
                        if (purl not in self.purl_id_map):
                            self.purl_id_map[purl] = component['id']
                        else:
                            print("\n\nDuplicate purl detected. This line comes from scripts/parse_files.py in the method parse_purl_to_id_map()\n\n")

    def parse_sbom(self, path):
        # store file contents as a string in self.data
        with open(path, 'r') as f: 
            self.data = f.read()
        # determine and store format in self.format 
        if (".json" in path): 
            self.format = "json"
        # determine and store version in self.version
        self.get_version()
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