from Graph import GRAPH
from Vertex import VERTEX
from Edge import EDGE


def modular_product(g1, g2):
    # Number of vertices is the product of the number of vertices of both graphs
    new_number_of_vertices = g1.get_number_of_vertices() * g2.get_number_of_vertices()
    # Initialize all vertices of the modular product by concatenating the IDs and collect them in a list. For now, a
    # default label is passed. A mapping is generated, if one or both of the input graphs already carry a mapping to
    # other graphs, these mappings are combined for every new vertex.
    new_list_of_vertices = []
    g1_map = g1.get_mapping()
    g2_map = g2.get_mapping()
    mapping = {}
    mapping_helper_note = None
    if g1_map is not None and g2_map is not None:
        g1_graph_number = g1_map["number of graphs"]
        g2_graph_number = g2_map["number of graphs"]
        number_of_graphs_mapped = g1_graph_number + g2_graph_number
        for i in range(g1_graph_number):
            mapping["graph" + str(i)] = g1_map["graph" + str(i)]
        for j in range(g2_graph_number):
            mapping["graph" + str(g1_graph_number + j)] = g2_map["graph" + str(j)]
        mapping["number of graphs"] = number_of_graphs_mapped
        mapping_helper_note += "both"
    elif g1_map is not None:
        g1_graph_number = g1_map["number of graphs"]
        mapping["number of graphs"] = g1_graph_number + 1
        for i in range(g1_graph_number):
            mapping["graph" + str(i)] = g1_map["graph" + str(i)]
        mapping["graph" + str(g1_graph_number + 1)] = g2.get_name()
        mapping_helper_note += "graph1"
    elif g2_map is not None:
        g2_graph_number = g2_map["number of graphs"]
        mapping["number of graphs"] = g2_graph_number + 1
        for i in range(g2_graph_number):
            mapping["graph" + str(i)] = g2_map["graph" + str(i)]
        mapping["graph" + str(g2_graph_number + 1)] = g1.get_name()
        mapping_helper_note += "graph2"
    else:
        mapping = {"number of graphs": 2, "graph1": g1.get_name(), "graph2": g2.get_name()}
    g1_list = g1.get_list_of_vertices()
    g2_list = g2.get_list_of_vertices()
    g1_vn = g1.get_number_of_vertices()
    g2_vn = g2.get_number_of_vertices()
    for i in range(g1_vn):
        for j in range(g2_vn):
            new_list_of_vertices.append(VERTEX(i + j*g1_vn, "Default_Label"))
            if mapping_helper_note is None:
                mapping[i + j*g1_vn] = [g1_list[i].get_id(), g2_list[j].get_id()]
            elif mapping_helper_note == "both":
                mapping[i + j*g1_vn] = g1_map[g1_list[i].get_id()] + g2_map[g2_list[j].get_id()]
            elif mapping_helper_note == "graph1":
                mapping[i + j*g1_vn] = g1_map[g1_list[i].get_id()].append(g2_list[j].get_id())
            elif mapping_helper_note == "graph2":
                mapping[i + j*g1_vn] = g2_map[g2_list[j].get_id()].append(g1_list[i].get_id())
    # Initialize an empty list of edges and an edge counter.
    # Iterate over all pairs of vertices (twice --> both directions) for both graphs.
    # Skip cases where vertices are identical.
    new_list_of_edges = []
    new_number_of_edges = 0
    for v1 in g1_list:
        g1_cut = g1_list.copy()
        g1_cut.remove(v1)
        for v2 in g1_cut:
            for v3 in g2_list:
                g2_cut = g2_list.copy()
                g2_cut.remove(v3)
                for v4 in g2_cut:
                    # If, for both graphs, a two-element list is identical, add an edge. The elements in this list
                    # correspond to booleans that are evaluated from ID check of vertex 1 with the IDs of the neighbours
                    # attribute of vertex 2 and vice versa.
                    if ([v1.get_id() in [vertex.get_id() for vertex in v2.get_neighbours()],
                         v2.get_id() in [vertex.get_id() for vertex in v1.get_neighbours()]] ==
                            [v3.get_id() in [vertex.get_id() for vertex in v4.get_neighbours()],
                             v4.get_id() in [vertex.get_id() for vertex in v3.get_neighbours()]]):
                        """ INSERT CODE THAT SHOULD INCLUDE MORE CONDITIONALS e.g. SAME LABEL, DIRECTION etc. """
                        # Like this, two vertices in the modular product graph always have two or no edges connecting
                        # them. Once with each vertex being the start vertex.
                        # The information about type of connection is not conserved in this modular product!
                        # Possibly, this can be done by edge systematic edge labelling (not yet implemented).
                        start_vertex = None
                        end_vertex = None
                        for new_v in new_list_of_vertices:
                            if mapping_helper_note is None:
                                if mapping[new_v.get_id()] == [v1.get_id(), v3.get_id()]:
                                    start_vertex = new_v
                                elif mapping[new_v.get_id()] == [v2.get_id(), v4.get_id()]:
                                    end_vertex = new_v
                            elif mapping_helper_note == "both":
                                if mapping[new_v.get_id()] == g1_map[v1.get_id()] + g2_map[v3.get_id()]:
                                    start_vertex = new_v
                                elif mapping[new_v.get_id()] == g1_map[v2.get_id()] + g2_map[v4.get_id()]:
                                    end_vertex = new_v
                            elif mapping_helper_note == "graph1":
                                if mapping[new_v.get_id()] == g1_map[v1.get_id()].append(v3.get_id()):
                                    start_vertex = new_v
                                elif mapping[new_v.get_id()] == g1_map[v2.get_id()].append(v4.get_id()):
                                    end_vertex = new_v
                            elif mapping_helper_note == "graph2":
                                if mapping[new_v.get_id()] == g2_map[v3.get_id()].append(v1.get_id()):
                                    start_vertex = new_v
                                elif mapping[new_v.get_id()] == g2_map[v4.get_id()].append(v2.get_id()):
                                    end_vertex = new_v
                        new_list_of_edges.append(EDGE("Default_id", [start_vertex, end_vertex], "Default_Label"))
                        new_number_of_edges += 1
                        start_vertex.append_neighbour(end_vertex)
    # The modular product as undirected graph is returned with a default name.
    # Vertex and Edge labels are enabled, yet set to a default value for the moment, same as the edge id.
    return GRAPH("Modular Product of " + g1.get_name() + " and " + g2.get_name(),
                 new_list_of_vertices, new_list_of_edges, new_number_of_vertices, int(new_number_of_edges/2),
                 False, is_labeled_edges=True, is_labeled_nodes=True, mapping=mapping)
