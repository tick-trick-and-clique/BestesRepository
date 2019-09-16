from Graph import GRAPH
from Vertex import VERTEX
from Edge import EDGE


def modular_product(g1, g2, anchor_graph_parameters=None):
    # Number of vertices is the product of the number of vertices of both graphs
    new_number_of_vertices = g1.get_number_of_vertices() * g2.get_number_of_vertices()
    # Initialize all vertices of the modular product. For now, a
    # default label is passed. A mapping for each vertex is updated, serving as reference to the input vertices
    # including the mapping of those input vertices.
    anchor = []
    new_list_of_vertices = []
    g1_list = g1.get_list_of_vertices()
    g2_list = g2.get_list_of_vertices()
    g1_vn = g1.get_number_of_vertices()
    g2_vn = g2.get_number_of_vertices()
    for i in range(g1_vn):
        for j in range(g2_vn):
            v = VERTEX(i + j*g1_vn, "Default_Label")
            v.combine_mapping(g1_list[i])
            v.combine_mapping(g2_list[j])
            if anchor_graph_parameters:
                anchor_vertices = anchor_graph_parameters[0].get_list_of_vertices()
                for anchor_vertex in anchor_vertices:
                    if g1_list[i].get_id() == anchor_vertex.get_id():
                        anchor.append(v)
            new_list_of_vertices.append(v)
    # Initialize an empty list of edges and an edge counter.
    # Iterate over all pairs of vertices (twice --> both directions) for both graphs.
    # Skip cases where vertices are identical.
    new_list_of_edges = []
    new_number_of_edges = 0
    edge_id = 1
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
                            if v1 in new_v.get_mapping().values() and v3 in new_v.get_mapping().values():
                                start_vertex = new_v
                            if v2 in new_v.get_mapping().values() and v4 in new_v.get_mapping().values():
                                end_vertex = new_v
                        new_list_of_edges.append(EDGE(edge_id, [start_vertex, end_vertex], "Default_Label"))
                        new_number_of_edges += 1
                        edge_id += 1
                        start_vertex.append_neighbour(end_vertex)
    # The modular product as undirected graph is returned with a default name.
    # Vertex and Edge labels are enabled, yet set to a default value for the moment, same as the edge id.
    return GRAPH("Modular Product of " + g1.get_name() + " and " + g2.get_name(),
                 new_list_of_vertices, new_list_of_edges, new_number_of_vertices, int(new_number_of_edges/2),
                 False, is_labeled_edges=True, is_labeled_nodes=True), anchor
