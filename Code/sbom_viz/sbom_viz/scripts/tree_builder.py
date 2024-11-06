from models.tree_node import TreeNode

class TreeBuilder:
    def __init__(self, sbom_relationships: dict, sbom_components: dict):
        self.sbom_relationships = sbom_relationships
        self.sbom_components = sbom_components
        self.root = TreeNode("SBOM Root", "ROOT")

        self.root_nodes = self.set_root_nodes()
        self.built_sbom_ids = []

        self.next_node_id = 0

    def build_tree(self):
        for root_node in self.root_nodes:
            self.recursively_add_children(root_node)

    def recursively_add_children(self, parent_node: TreeNode):
        child_relationships = [relationship for relationship in self.sbom_relationships if relationship["elementId"] == parent_node.sbom_id]

        for relationship in child_relationships:
            new_node = self.add_node(parent_node, relationship["relatedElement"], relationship["relationshipType"])

            if not new_node.ghost:
                self.recursively_add_children(new_node)

    def add_node(self, parent_node: TreeNode, child_sbom_id: int, relationship_type: str):
        if parent_node.ghost:
            return
        
        if relationship_type in parent_node.relationships:
            parent_node.relationships[relationship_type].append(child_sbom_id)
        else:
            parent_node.relationships[relationship_type] = [child_sbom_id]

        ghost = False
        if child_sbom_id in self.built_sbom_ids:
            ghost = True

        new_node = TreeNode(child_sbom_id, self.get_next_node_id(), ghost)

        parent_node.children.append(new_node)

        self.built_sbom_ids.append(child_sbom_id)

        return new_node

    def set_root_nodes(self):
        all_components = set(component["id"] for component in self.sbom_components)
        children = set(relationship["relatedElement"] for relationship in self.sbom_relationships)

        root_nodes_ids = all_components - children

        root_nodes = []
        for root_node_id in root_nodes_ids:
            root_nodes.append(self.add_node(self.root, root_node_id, "RELATED_TO"))
        
        return root_nodes

    def get_tree_as_dict(self):
        return self.root.to_dict()
    
    def get_next_node_id(self):
        current_id = self.next_node_id
        self.next_node_id += 1
        return current_id