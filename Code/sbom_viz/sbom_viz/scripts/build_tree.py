from lib4sbom.parser import SBOMParser
from sbom_viz.scripts.parse_files import SPDXParser
relationship_graph = {}
id_data_map = {}
set_of_added_ids = set()

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

def recursive_build_children(current_id, relationship_to_parent):
    global id_data_map
    global set_of_added_ids
    global relationship_graph
    current_node = {
        "name": id_data_map[current_id]["name"],
        "id": current_id,
        "relationship_to_parent": relationship_to_parent,
    }
    if (current_id in set_of_added_ids):
        current_node["ghost"] = True
    else:
        set_of_added_ids.add(current_id)
        current_node["ghost"] = False
        if (current_id in relationship_graph):
            children = []
            for i in relationship_graph[current_id]:
                children.append(recursive_build_children(i[0], i[1]))
            current_node["children"] = children
    return current_node

def get_relationship_tree(parser, data_map):
    global id_data_map 
    global relationship_graph
    global set_of_added_ids
    id_data_map = data_map
    relationship_graph = get_relationship_graph(parser)
    set_of_added_ids = set()
    parent_nodes = {} 
    """
    parent_nodes is a dictionary that 
    1) Can be used to refer to all nodes that are the parent of some other node(s) through its keys
    2) Determine if the node is a top-level node or not based on its boolean value. If the value is True, this parent node has a parent itself.
    """
    for i in relationship_graph:
        parent_nodes[i] = False
    for i in parent_nodes:
        for j in relationship_graph[i]:
            if (j[0] in parent_nodes): #j[0] refers to the ID of the child we are examining
                parent_nodes[j[0]] = True  #If the child is a part of the parent node's set of children, set the associated flag to True

    """
    Now that we have access to top-level nodes, we can build the tree by recursively forming nodes with a lists of child nodes.
    A set of nodes present in the tree will be used to recognize if a node we are adding should be a ghost node. That is, a node that 
    will not have a subtree since its subtree is already displayed somewhere else.
    """    
    tree = {"name": "root", "children": []}
    top_level_children = []
    for i in parent_nodes:
        if (parent_nodes[i] == False): # This is a top leve parent node
            node = {
                "name": data_map[i]["name"],
                "id": i,
            }
            if (i in set_of_added_ids):
                node["ghost"] = True
            else:
                set_of_added_ids.add(i)
                node["ghost"] = False
                node["relationship"] = "root"
                children = []
                for o in relationship_graph[i]:
                    children.append(recursive_build_children(o[0], o[1])) #o[0] is the child's id, o[1] is the child's relationship to its parent
                if (len(children) > 0):
                    node["children"] = children
            top_level_children.append(node)
    """
    Now the top level nodes are added, but if a cycle of relationships begins at the top level, we are missing some branches of the tree. 
    We will next add the cycled top-level nodes in arbitrary order.
    """

    for i in parent_nodes:
        if (i not in set_of_added_ids):
            node = {
                "name": data_map[i]["name"],
                "id": i,
            }
            set_of_added_ids.add(i)
            node["ghost"] = False
            node["relationship"] = "root"
            children = []
            for o in relationship_graph[i]:
                children.append(recursive_build_children(o[0], o[1])) #o[0] is the child's id, o[1] is the child's relationship to its parent
            if (len(children) > 0):
                node["children"] = children
            top_level_children.append(node)

    tree["children"] = top_level_children
    return tree


