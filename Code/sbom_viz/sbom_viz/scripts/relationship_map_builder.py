from sbom_viz.models.tree_node import TreeNode
from sbom_viz.models.relationship_map import RelationshipMap

'''
RelationshipMapBuilder is responsible for building
a RelationshipMap from the root TreeNode
'''
class RelationshipMapBuilder:
    '''
    Constructor for RelationshipMapBuilder
    '''
    def __init__(self, tree: TreeNode) -> None:
        self.tree = tree
        self.relationship_map = RelationshipMap()

    '''
    Calls the recursive traversal of the tree on the root node
    '''
    def build_map(self) -> None:
        self.dfs(self.tree)

    '''
    Traverses the tree using depth-first search and 
    builds the relationship map in the process   
    '''
    def dfs(self, node: TreeNode, visited = set()) -> None:
        visited.add(node)

        child_sbom_to_node_ids = dict()
        for child in node.children:
            child_sbom_to_node_ids[child.sbom_id] = child.node_id

        for relationship_type, targets in node.relationships.items():
            for target in targets:
                self.relationship_map.add_relationship(child_sbom_to_node_ids[target], relationship_type)

        for child in node.children:
            self.dfs(child, visited)

    '''
    Returns relationship map as a dictionary
    '''
    def get_map_as_dict(self) -> dict:
        return self.relationship_map.get_dict()