import json
from Neo4j import NEO4J
from typing import List, Dict
from Vertex import VERTEX
from Edge import EDGE
from Graph import GRAPH


def json_parser(file_path, neo4j, no_h_atoms):
    """
    Takes a string and checks if its and existing file path.
    Then parses .json file into a GRAPH object and returns it.
    This is thought to be used for molecules, therefore resulting graphs will always be undirected
    with two Edges of different IDs per chemical bond that carry the same information.
    IDs start with '1' not with '0'!
    EDGE.label carries the bonding order and VERTEX.label carries the atomic number in the periodic table.
    Return type: GRAPH
    """

    open_file = open(file_path, 'r')
    raw_parsed = json.load(open_file)
    chem_dict = raw_parsed["PC_Compounds"][0]

    # Set some variables for a better overview
    molecule_name = chem_dict["props"][10]["value"]["sval"]
    atoms: Dict = chem_dict["atoms"]
    atoms_id: List[str] = atoms["aid"]
    atoms_element_number: List[str] = atoms["element"]
    bonds: Dict = chem_dict["bonds"]
    bonds_partner1_id: List[str] = bonds["aid1"]
    bonds_partner2_id: List[str] = bonds["aid2"]
    order: List[str] = bonds["order"]

    # Instantiate Vertices
    list_of_vertices = []
    for atom in atoms_id:
        atom_id = int(atom)
        atom_label = str(atoms_element_number[atom_id - 1])
        if no_h_atoms:
            if atom_label == "1":
                pass
            else:
                list_of_vertices.append(VERTEX(atom_id, atom_label))
        else:
            list_of_vertices.append(VERTEX(atom_id, atom_label))

    # Instantiate Edges
    list_of_edges = []
    for i in range(len(bonds_partner1_id)):
        atom_1_id = int(bonds_partner1_id[i])
        atom_2_id = int(bonds_partner2_id[i])
        start_and_end1: List[VERTEX] = [j for j in list_of_vertices if j.get_id() == atom_1_id] + \
                                       [j for j in list_of_vertices if j.get_id() == atom_2_id]
        if len(start_and_end1) == 2:
            start_and_end2 = [start_and_end1[1], start_and_end1[0]]
            list_of_edges.append(EDGE(i + 1, start_and_end1, str(order[i])))
            list_of_edges.append(EDGE(i + len(bonds_partner1_id) + 1, start_and_end2, str(order[i])))
        else:
            if no_h_atoms:
                pass
            else:
                raise Exception("Error occured reading json file!")

    # Set VERTEX.neighbours
    for edge in list_of_edges:
        for vertex in list_of_vertices:
            if edge.get_start_and_end()[0].get_id() == vertex.get_id():
                vertex.append_out_neighbour(edge.get_start_and_end()[1])

    # Instantiate GRAPH object
    graph = GRAPH(molecule_name, list_of_vertices, list_of_edges, len(list_of_vertices), int(len(list_of_edges)/2),
                  False, is_labeled_nodes=True, is_labeled_edges=True)

    # for input graphs, each vertex needs to contain a mapping of itself
    for v in graph.get_list_of_vertices():
        v.add_vertex_to_mapping(v, graph.get_name())

    # create Neo4J View
    if neo4j:
        neo4jProjekt = NEO4J(neo4j[0], neo4j[1], neo4j[2], list_of_vertices, list_of_edges, molecule_name, False)
    return graph
