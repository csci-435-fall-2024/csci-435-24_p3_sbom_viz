from sbom_viz.models.tree_node import TreeNode

'''
RelationshipMap is responsible for holding the mapping of child node_ids to parent relationships to itself:

{ "child_node_id" : {"parent_relationship_to_child1", "parent_relationship_to_child_2"}, ... }
'''
class RelationshipMap:
    '''
    Constructor for RelationshipMap
    '''
    def __init__(self) -> None:
        self.map = dict()

    '''
    Adds a relationship to a potentially already existing key
    or if it doesn't exist, a new key
    '''
    def add_relationship(self, child_node_id: int, relationship: str) -> None:
        if child_node_id in self.map:
            self.map[child_node_id].add(relationship)
        else:
            self.map[child_node_id] = {relationship}
            
    '''
    Returns the dictionary representation of the mapping
    '''
    def get_dict(self) -> dict:
        return {str(node_id): list(relationships_list) for node_id, relationships_list in self.map.items()}