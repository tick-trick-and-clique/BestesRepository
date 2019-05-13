'''
Created on 12.05.2019

@author: AJ
'''


from Graph import GRAPH
from Vertex import VERTEX
from Edge import EDGE


def modular_product(g1, g2):
    # Number of vertices is the product of the number of vertices of both graphs
    new_number_of_vertices = g1.get_number_of_vertices() * g2.get_number_of_vertices()
    # Initialize all vertices of the modular product by concatenating the IDs (cartesian product)
    # and collect them in a list.
    # For now, a default label is passed.
    new_list_of_vertices = []
    for v1 in g1.get_list_of_vertices():
        for v2 in g2.get_list_of_vertices():
            new_list_of_vertices.append(VERTEX(v1.get_id() + v2.get_id(), "Default_Label"))
    # Initialize an empty list of edges and an edge counter.
    # Iterate over all pairs of vertices (twice --> both directions) for both graphs.
    # Skip cases where vertices are identical.
    new_list_of_edges = []
    new_number_of_edges = 0
    for v1 in g1.get_list_of_vertices():
        g1_cut = g1.get_list_of_vertices()
        g1_cut.remove(v1)
        for v2 in g1_cut:
            for v3 in g2.get_list_of_vertices():
                g2_cut = g2.get_list_of_vertices()
                g2_cut.remove(v3)
                for v4 in g2_cut:
                    # If, for both graphs, a two-element list is identical, add an edge. The elements in this list
                    # correspond to booleans that are evaluated from ID check of vertex 1 in the neighbours attribute of
                    # vertex 2 and vice versa.
                    if ([v1.get_id() in v2.get_neighbours(), v2.get_id() in v1.get_neighbours()] ==
                            [v3.get_id() in v4.get_neighbours(), v4.get_id() in v3.get_neighbours()]):
                        """ INSERT CODE THAT SHOULD INCLUDE MORE CONDITIONALS e.g. SAME LABEL, DIRECTION etc. """
                        # Like this, two vertices in the modular product graph always have two or no edges connecting
                        # them. Once with each vertex being the start vertex.
                        # The information about type of connection is not conserved in this modular product!
                        # Possibly, this can be done by edge systematic edge labelling (not yet implemented).
                        start_vertex1 = None
                        end_vertex1 = None
                        start_vertex2 = None
                        end_vertex2 = None
                        for new_v in new_list_of_vertices:
                            if new_v.get_id() == v1.get_id() + v3.get_id():
                                start_vertex1 = new_v
                                end_vertex2 = new_v
                            elif new_v.get_id() == v2.get_id() + v4.get_id():
                                end_vertex1 = new_v
                                start_vertex2 = new_v
                        new_list_of_edges.append(EDGE("Default_id", [start_vertex1, end_vertex1], "Default_Label"))
                        new_list_of_edges.append(EDGE("Default_id", [start_vertex2, end_vertex2], "Default_Label"))
                        new_number_of_edges += 1
    # The modular product as undirected graph is returned with a default name.
    return GRAPH("Modular Product of " + g1.get_name() + " and " + g2.get_name(),
                 new_list_of_vertices, new_list_of_edges, new_number_of_vertices, new_number_of_edges,
                 False)
