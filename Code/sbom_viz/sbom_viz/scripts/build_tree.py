from lib4sbom.parser import SBOMParser

#Build a dictionary mapping component-ids of parent nodes to a list of their children represented as tuples of (id, type-of-relationship)
def get_relationship_graph(parser):
    relationship_edges = {}
    relationships = parser.get_relationships()
    for i in relationships:
        if (i["target_id"] not in relationship_edges):
            relationship_edges[i["target_id"]] = [(i["source_id"], i["type"])]
        else:
            relationship_edges[i["target_id"]].append((i["source_id"], i["type"]))
    return relationship_edges

def get_relationship_tree(parser):
    relationship_graph = get_relationship_graph(parser)
    
