class TreeNode:
    def __init__(self, sbom_id: int, node_id: int, ghost=False):
        self.sbom_id = sbom_id
        self.node_id = node_id
        self.ghost = ghost
        self.relationships = {}
        self.children = []

    def to_dict(self):
        return {
            "name" : self.sbom_id,
            "id": self.sbom_id,
            "node_id": self.node_id,
            "ghost": self.ghost,
            "relationships": self.relationships,
            "children": [child.to_dict() for child in self.children]
        }