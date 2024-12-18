import xmltodict

class SpdxXmlParser():
    """
    This class is used to parse an uploaded sbom file and provides accessor methods
    for information needed by other parts of the application.
    """
    def __init__(self):
        """Initialize parser attributes to store important information"""
        self.sbom_dict = {}
        self.data = ""
        self.version = ""
        self.root_key = ""  # Dynamically detected root key
        self.components_list = []
        self.relationship_list = []
        self.id_data_map = {}
        self.license_frequency_map = {}
        self.id_license_map = {}
        self.purl_id_map = {}

    def detect_root_key(self):
        """Find the root key dynamically from the parsed XML."""
        self.root_key = next(iter(self.sbom_dict))

    def add_to_licenses_frequency_map(self, license_string):
        """
        This function is to be called from parse_licensing_information. It handles the logic for either adding a new license to the 
        frequency map or increment the license's corresponding value if it is already present.
        """
        if license_string not in self.license_frequency_map:
            self.license_frequency_map[license_string] = 1
        else:
            self.license_frequency_map[license_string] += 1

    def add_to_id_license_map(self, id, license): 
        """
        This function is a helper function to be called from parse_license_information(). It can be modified to change how the application
        processes components with multiple license definitions. As of now, duplicates are ignored.
        """
        ignore_count = 0
        if id in self.id_license_map and license != self.id_license_map[id]:
            ignore_count += 1
        elif id not in self.id_license_map: 
            self.id_license_map[id] = license
        return ignore_count

    def parse_licensing_information(self):
        try:
            files = self.sbom_dict.get(self.root_key, {}).get('files', [])
            packages = self.sbom_dict.get(self.root_key, {}).get('packages', [])
            for component in files + packages:
                license_string = component.get('licenseDeclared', 'NOASSERTION')
                self.add_to_licenses_frequency_map(license_string)
                spdx_id = component.get('SPDXID', 'Unknown')
                self.add_to_id_license_map(spdx_id, license_string)
        except Exception as e:
            print(f"Error parsing licensing information: {e}")

    def find_version(self):
        """
        Determine the version of SPDX and store it as a string in self.version.
        It is only intended to be called by self.parse_file().
        """
        self.version = self.sbom_dict.get(self.root_key, {}).get('spdxVersion', 'Unknown')

    def parse_document_information(self):
        """
        This function adds a dictionary representing the metadata describing the sbom document itself to 
        self.components_list.
        It is only intended to be called by self.parse_file().
        """
        document = self.sbom_dict.get(self.root_key, {})
        metadata = {
            'id': document.get('SPDXID', 'Unknown'),
            'name': document.get('name', 'Unknown'),
            'dataLicense': document.get('dataLicense', 'Unknown'),
            'creationInfo': document.get('creationInfo', {})
        }
        self.components_list.append(metadata)

    def parse_component_information(self):
        """
        This function adds the remainder of the components to self.components_list. 
        It is only intended to be called by self.parse_file(), and after self.parse_document_information().
        """
        try:
            document = self.sbom_dict.get(self.root_key, {})
            files = document.get('files', [])
            if isinstance(files, dict):
                files = [files]
            elif not isinstance(files, list):
                files = []

            for file in files:
                if isinstance(file, dict):
                    self.components_list.append({
                        'id': file.get('SPDXID', "Unknown"),
                        'name': file.get('fileName', "Unknown"),
                        'licenseConcluded': file.get('licenseConcluded', "NOASSERTION")
                    })

            packages = document.get('packages', [])
            if isinstance(packages, dict):
                packages = [packages]
            elif not isinstance(packages, list):
                packages = []

            for package in packages:
                if isinstance(package, dict):
                    self.components_list.append({
                        'id': package.get('SPDXID', "Unknown"),
                        'name': package.get('name', "Unknown"),
                        'licenseDeclared': package.get('licenseDeclared', "NOASSERTION")
                    })

        except Exception as e:
            print(f"Error parsing components: {e}")

    def parse_relationship_information(self):
        """
        Extract relationships and populate self.relationship_list.
        """
        try:
            relationships = self.sbom_dict.get(self.root_key, {}).get('relationships', [])

            if isinstance(relationships, dict):
                relationships = [relationships]
            elif not isinstance(relationships, list):
                relationships = []

            for relationship in relationships:
                if isinstance(relationship, dict):
                    self.relationship_list.append({
                        'source_id': relationship.get('spdxElementId', "Unknown"),
                        'target_id': relationship.get('relatedSpdxElement', "Unknown"),
                        'type': relationship.get('relationshipType', "Unknown")
                    })
                else:
                    print(f"Skipping invalid relationship entry: {relationship}")
        except Exception as e:
            print(f"Error parsing relationships: {e}")

    def parse_id_to_data_map(self):
        """
        This function defines the logic for building the id-to-data dictionary which allows the Front-End code to acquire a component's 
        data from the id it is provided by the tree JSON object. 
        This function is only intended to be called from parse_file(). 
        get_id_data_map() should be used to acquire the dictionary object after a file is parsed. 
        """
        for component in self.components_list:
            self.id_data_map[component['id']] = component
    
    def parse_purl_to_id_map(self):
        """
        This function generates the purl-to-id mapping which is used to determine which component a security vulnerability is associated
        with.
        This function is only intended to be called from parse_file(). It needs to be called after parse_components().
        """
        for package in self.sbom_dict.get(self.root_key, {}).get('packages', []):
            spdx_id = package.get('SPDXID', 'Unknown')
            external_refs = package.get('externalRefs', [])
            if isinstance(external_refs, dict):
                external_refs = [external_refs]
            for ref in external_refs:
                if 'purl' in ref.get('referenceType', '').lower():
                    self.purl_id_map[ref.get('referenceLocator', '')] = spdx_id

    def parse_file(self, file_string):
        self.sbom_dict = xmltodict.parse(file_string)
        self.data = file_string
        self.detect_root_key()
        self.find_version()
        self.parse_licensing_information()
        self.parse_document_information()
        self.parse_component_information()
        self.parse_relationship_information()
        self.parse_id_to_data_map()
        self.parse_purl_to_id_map()

    def get_components(self):
        return self.components_list
    
    def get_relationships(self):
        return self.relationship_list
    
    def get_id_data_map(self):
        return self.id_data_map
    
    def get_license_information(self):
        """Return license information in a format requested by the front-end team."""
        return {
            'distribution': self.license_frequency_map,
            'mapping': self.id_license_map
        }
    
    def get_purl_id_map(self):
        return self.purl_id_map
    
    def get_sbom_data(self):
        return ("xml", self.data)
