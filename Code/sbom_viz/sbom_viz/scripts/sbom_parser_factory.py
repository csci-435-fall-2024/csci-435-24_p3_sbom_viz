"""
This file defines the SbomParserFactory class. It is used to determine the correct form of parser to instantiate
based on an uploaded sbom file.
"""
from sbom_viz.scripts.spdx_json_parser import SpdxJsonParser
from sbom_viz.scripts.spdx_xml_parser import SpdxXmlParser
from sbom_viz.scripts.cyclonedx_json_parser import CycloneDxJsonParser
from sbom_viz.scripts.cyclonedx_xml_parser import CycloneDxXmlParser

class SbomParserFactory():
    """Used in views.py to acquire an sbom parser when a file is uploaded."""
    def __init__(self):
        """Empty init since no attributes are needed."""
        pass

    def get_parser(self, sbom_string):
        """
        Determine the data transfer type and sbom version of the inputted sbom file string. Return an sbom parser
        object accordingly.
        """
        pass
