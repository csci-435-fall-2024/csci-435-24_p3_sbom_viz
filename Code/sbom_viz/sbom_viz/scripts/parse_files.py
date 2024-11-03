class SPDXParser():

    def __init__(self):
        self.data = ""
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

    def add_to_license_map(self, id, license): 
        # This method will return an integer value for how many times licenses were ignored with a new value
        # This would happen if an id has a license added to it multiple times
        ignore_count = 0
        if (id in self.id_license_map and license != self.id_license_map[id]):
            ignore_count += 1
        elif (id not in self.id_license_map):
            self.id_license_map[id] = license
        return ignore_count


    def parse_file(self, path):
        with open(path, 'r') as f:
            self.data = f.read()
        
    
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

    def get_id_purl_map(self):
        return self.purl_id_map