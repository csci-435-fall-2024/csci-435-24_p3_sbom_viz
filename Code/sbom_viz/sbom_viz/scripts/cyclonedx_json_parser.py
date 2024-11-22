import json

class CycloneDxJsonParser():
    """
    This class is used to parse an uploaded sbom file and provides accessor methods
    for information needed by other parts of the application.
    """
    def __init__(self):
        """Initialize parser attributes to store important information"""
        self.sbom_dict = {}
        self.version = ""
        self.components_list = []
        self.relationship_list = []
        self.id_data_map = {}
        self.license_frequency_map = {}
        self.id_license_map = {}
        self.purl_id_map = {}

    def add_to_licenses_frequency_map(self, license_string):
        """
        This function is to be called from parse_licensing_information. It handles the logic for either adding a new license to the 
        frequency map or increment the license's corresponding value if it is already present.
        """
        if (license_string not in self.license_frequency_map):
            self.license_frequency_map[license_string] = 1
        else:
            self.license_frequency_map[license_string] += 1

    def add_to_id_license_map(self, id, license): 
        """
        This function is a helper function to be called from parse_license_information(). It can be modified to change how the application
        processes components with multiple license definitions. As of now, duplicates are ignored.
        """
        ignore_count = 0
        if (id in self.id_license_map and license != self.id_license_map[id]): # True when an id already has a license stored that is different from the passed in license
            ignore_count += 1 
        elif (id not in self.id_license_map): 
            self.id_license_map[id] = license
        return ignore_count

    def parse_licensing_information(self):
        """
        This function fills self.license_frequency_map and self.id_data_map with sbom component data.
        It is only intended to be called by self.parse_file().
        """
        pass

    def find_version(self):
        """
        Determine the version of SPDX and store it as a string in self.version.
        It is only intended to be called by self.parse_file().
        """
        pass

    def parse_document_information(self):
        """
        This function adds a dictionary representing the metadata describing the sbom document itself to 
        self.components_list.
        It is only intended to be called by self.parse_file().
        """
        pass

    def parse_components(self):
        """
        This function adds the remainder of the components to self.components_list. 
        It is only intended to be called by self.parse_file(), and after self.parse_document_information().
        """
        pass

    def parse_relationship_information(self):
        """
        This function fills self.relationship_list
        """
        relationship_list = []
        self.relationship_list = relationship_list


    def parse_id_to_data_map(self):
        """
        This function defines the logic for building the id-to-data dictionary which allows the Front-End code to acquire a component's 
        data from the id it is provided by the tree JSON object. 
        This function is only intended to be called from parse_file(). 
        get_id_data_map() should be used to acquire the dictionary object after a file is parsed. 
        """
        pass
    
    def parse_purl_to_id_map(self):
        """
        This function generates the purl-to-id mapping which is used to determine which component a security vulnerability is associated
        with.
        This function is only intended to be called from parse_file(). It needs to be called after parse_components().
        """
        pass

    def parse_file(self, file_string):
        self.sbom_dict = json.loads(file_string)
        self.get_version()
        self.parse_licensing_information()
        self.parse_document_information()
        self.parse_file_information()
        self.parse_package_information()
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
        license_info = {}
        license_info['distribution'] = self.license_frequency_map
        license_info['mapping'] = self.id_license_map
        return license_info
    
    def get_purl_id_map(self):
        return self.purl_id_map