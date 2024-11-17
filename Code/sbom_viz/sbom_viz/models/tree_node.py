'''
TreeNodes make up our tree for visualization
'''
class TreeNode:
    '''
    Constructor for TreeNode

    Each node has an sbom_id (shared between ghosts) and node_id (unique)
    '''
    def __init__(self, sbom_id: int, node_id: int, ghost=False):
        self.sbom_id = sbom_id
        self.node_id = node_id
        self.ghost = ghost
        self.relationships = {}
        self.children = []

    '''
    Recursively returns itself and all children as a dictionary
    '''
    def to_dict(self):
        return {
            "name" : self.sbom_id,
            "id": self.sbom_id,
            "node_id": self.node_id,
            "ghost": self.ghost,
            "relationships": self.relationships,
            "children": [child.to_dict() for child in self.children]
        }