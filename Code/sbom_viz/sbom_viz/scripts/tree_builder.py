from sbom_viz.models.tree_node import TreeNode
from typing import Optional, List

'''
TreeBuilder is responsible for building a tree from SBOM relationships and components
'''
class TreeBuilder:
    '''
    Constructor for TreeBuilder
    
    Sets the root nodes of the tree
    '''
    def __init__(self, sbom_relationships: list, sbom_components: list) -> None:
        self.sbom_relationships = sbom_relationships
        self.sbom_components = sbom_components
        self.root = TreeNode("SBOM Root", 0)
        self.built_sbom_ids = set()
        self.next_node_id = 1
        self.root_nodes = self.set_root_nodes()
    
    '''
    Builds the rest of the tree recursively building off of the root nodes
    '''
    def build_tree(self) -> None:
        for root_node in self.root_nodes:
            self.recursively_add_children(root_node)

    '''
    Used to add children of a node and then its children recursively until all leaf nodes are met
    '''
    def recursively_add_children(self, parent_node: TreeNode) -> None:
        child_relationships = [relationship for relationship in self.sbom_relationships if relationship["source_id"] == parent_node.sbom_id]

        for relationship in child_relationships:
            new_node = self.add_node(parent_node, relationship["target_id"], relationship["type"])

            if new_node and not new_node.ghost:
                self.recursively_add_children(new_node)

    '''
    Adds a single node and its relationship to its parent
    '''
    def add_node(self, parent_node: TreeNode, child_sbom_id: int, relationship_type: str) -> Optional[TreeNode]:
        if parent_node.ghost:
            return
        
        if relationship_type in parent_node.relationships:
            if child_sbom_id not in parent_node.relationships[relationship_type]:
                parent_node.relationships[relationship_type].append(child_sbom_id)
        else:
            parent_node.relationships[relationship_type] = [child_sbom_id]

        ghost = False
        if child_sbom_id in self.built_sbom_ids:
            ghost = True

        current_children_ids = [n.sbom_id for n in parent_node.children]
        
        if child_sbom_id not in current_children_ids:
            new_node = TreeNode(child_sbom_id, self.get_next_node_id(), ghost)

            parent_node.children.append(new_node)

            self.built_sbom_ids.add(child_sbom_id)

            return new_node

    '''
    Sets the root nodes of the tree (nodes without parents)
    '''
    def set_root_nodes(self) -> List[TreeNode]:
        all_components = set(component["id"] for component in self.sbom_components)
        children = set(relationship["target_id"] for relationship in self.sbom_relationships)

        root_nodes_ids = all_components - children

        root_nodes = []
        for root_node_id in root_nodes_ids:
            root_nodes.append(self.add_node(self.root, root_node_id, "RELATED_TO"))
        
        return root_nodes

    '''
    Returns the tree as a Dictionary
    '''
    def get_tree_as_dict(self) -> dict:
        return self.root.to_dict()
    
    '''
    Returns the root node
    '''
    def get_root_node(self) -> TreeNode:
        return self.root
    
    '''
    Generator for producing the next node_id (each is unique)
    '''
    def get_next_node_id(self) -> int:
        current_id = self.next_node_id
        self.next_node_id += 1
        return current_id