"""
2019-05-16, AJ

A Vertex class designed to be used for modular product calculation.
Clique finding can be invoked on the modular product and these clique can
be used to create a graph with standard vertices of class 'VERTEX', so that
the result is printable.
Graphs containing vertices of 'class MP_VERTEX' can not be saved for now!

The modular product function is modified concering the 'MP_VERTEX' class type.
It returns a modular product graph containing vertices of this type.
"""

from Graph import GRAPH
from Edge import EDGE


class MP_VERTEX:
    def __init__(self, vertex_graph1, vertex_graph2, label):
        self.__vertex_graph1 = vertex_graph1
        self.__vertex_graph2 = vertex_graph2
        self.__label = label
        self.__neighbours = []

    def __str__(self):
        '''
        builds a string representation of a vertex
        '''
        res = "[" + str(self.__vertex_graph1) + ";" + str(self.__vertex_graph2) + ";" + str(self.__label) + "]"
        return res

    def get_vertex_graph1(self):
        return self.__vertex_graph1

    def get_vertex_graph2(self):
        return self.__vertex_graph2

    def get_neighbours(self):
        return self.__neighbours

    def get_label(self):
        return self.__label

    def get_cardinality(self):
        return len(self.__neighbours)

    def set_neighbours(self, neighbours):
        self.__neighbours = neighbours

    def append_neighbour(self, new_neighbour):
        if not isinstance(new_neighbour, type(self)):
            raise TypeError("\n Dude... passed parameter has to be of type 'VERTEX'! \n")
        else:
            self.__neighbours.append(new_neighbour)


def modular_product_MP_VERTEX(g1, g2):
    # Number of vertices is the product of the number of vertices of both graphs
    new_number_of_vertices = g1.get_number_of_vertices() * g2.get_number_of_vertices()
    # Initialize all vertices of the modular product in MP_vertices and collect them in a list.
    # For now, a default label is passed.
    new_list_of_vertices = []
    for v1 in g1.get_list_of_vertices():
        for v2 in g2.get_list_of_vertices():
            new_list_of_vertices.append(MP_VERTEX(v1, v2, "Default_Label"))
    # Initialize an empty list of edges and an edge counter.
    # Iterate over all pairs of vertices (twice --> both directions).
    new_list_of_edges = []
    new_number_of_edges = 0
    for v1 in new_list_of_vertices:
        # Avoid cases where vertices are identical.
        list_cut = new_list_of_vertices.copy()
        list_cut.remove(v1)
        for v2 in list_cut:
            if not v1.get_vertex_graph1() == v2.get_vertex_graph1() and \
                    not v1.get_vertex_graph2() == v2.get_vertex_graph2():
                if [v1.get_vertex_graph1() in v2.get_vertex_graph1().get_neighbours(),
                    v2.get_vertex_graph1() in v1.get_vertex_graph1().get_neighbours()] == \
                    [v1.get_vertex_graph2() in v2.get_vertex_graph2().get_neighbours(),
                     v2.get_vertex_graph2() in v1.get_vertex_graph2().get_neighbours()]:
                    """ INSERT CODE THAT SHOULD INCLUDE MORE CONDITIONALS e.g. SAME LABEL, DIRECTION etc. """
                    # Like this, two vertices in the modular product graph always have two or no edges connecting
                    # them. Once with each vertex being the start vertex.
                    # The information about type of connection is not conserved in this modular product!
                    # Possibly, this can be done by edge systematic edge labelling (not yet implemented).
                    new_list_of_edges.append(EDGE("Default_id", [v1, v2], "Default_Label"))
                    new_number_of_edges += 1
                    # Appending the neighbours attribute of the vertices
                    v1.append_neighbour(v2)
    # The modular product as undirected graph is returned with a default name.
    # Vertex and Edge labels are enabled, yet set to a default value for the moment, same as the edge id.
    return GRAPH("Modular Product of " + g1.get_name() + " and " + g2.get_name(),
                 new_list_of_vertices, new_list_of_edges, new_number_of_vertices, int(new_number_of_edges/2),
                 False, is_labeled_edges=True, is_labeled_nodes=True)
