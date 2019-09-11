import math
import random
import os
from Edge import EDGE


class GRAPH(object):
    def __init__(self, name, list_of_vertices, list_of_edges, number_of_vertices, number_of_edges, is_directed,
                 is_labeled_nodes=False, is_labeled_edges=False, mapping=None):
        self.__name = name
        self.__list_of_vertices = list_of_vertices
        self.__list_of_edges = list_of_edges
        self.__number_of_vertices = number_of_vertices
        self.__number_of_edges = number_of_edges
        self.__is_directed = is_directed
        self.__is_labeled_nodes = is_labeled_nodes  # has to be transferred while initialising the graph
        self.__is_labeled_edges = is_labeled_edges  # has to be transferred while initialising the graph
        self.__mapping = mapping

    def get_name(self):
        '''
        returns name(String) of the graph
        '''
        return self.__name

    def set_name(self, name):
        '''
        sets name(string) of the graph
        '''
        self.__name = name

    def get_list_of_vertices(self):
        '''
        returns vertices(list) of the graph
        '''
        return self.__list_of_vertices

    def get_list_of_edges(self):
        '''
        returns edges(list) of the graph
        '''
        return self.__list_of_edges

    def get_number_of_vertices(self):
        '''
        returns number of vertices(int) of the graph
        '''
        return self.__number_of_vertices

    def get_number_of_edges(self):
        '''
        returns number of edges(int) of the graph
        '''
        return self.__number_of_edges

    def get_is_directed(self):
        return self.__is_directed

    def __str__(self):
        '''
        builds a string representation of of vertices and edges the graph
        '''
        res = "number of vertices:\n"
        res += str(self.__number_of_vertices) + "\n"

        res += "vertices:\n"
        for vertex in self.__list_of_vertices:
            res += str(vertex) + ",\n"

        res += "number of edges:\n"
        res += str(self.__number_of_edges) + "\n"

        res += "edges:\n"
        for edge in self.__list_of_edges:
            res += str(edge) + ",\n"
        return res

    def reverse_edges(self, list_of_vertices, current_vertex):
        """
        Checks if neighbours of current vertex has reversed edge to currentvertex
        """
        vertices_with_reverse_edges = []
        for elem in list_of_vertices:
            if current_vertex in elem.get_neighbours():
                vertices_with_reverse_edges.append(elem)
        return vertices_with_reverse_edges

    def bron_kerbosch(self, R, P, X, pivot=None):
        """
        bron kerbosch algo to find maximal cliques in graph
        with pivot. Function returns a list of cliques, which are lists of vertices.
        """
        result = []
        if not P and not X:
            # Dev Log Statement
            # print("Found Clique")
            for elem in R:
                # Dev Log Statement
                # print(elem)
                return [R]
        if pivot == "max":
            pivot_vertex = self.select_max_pivot(P, X)
        elif pivot == "random":
            pivot_vertex = self.select_random_pivot(P, X)
        elif pivot is None:
            for vertex in P[:]:
                new_R = R + [vertex]
                new_P = [val for val in P if val in self.reverse_edges(vertex.get_neighbours(),
                                                                       vertex)]  # P intersects w/ neighbours of vertex
                new_X = [val for val in X if val in self.reverse_edges(vertex.get_neighbours(),
                                                                       vertex)]  # X intersects w/ neighbours of vertex
                result += self.bron_kerbosch(new_R, new_P, new_X)
                P.remove(vertex)
                X.append(vertex)
            return result
        else:
            raise ValueError("Given optional pivot argument is illegal!")
        for vertex in [elem for elem in P if elem not in pivot_vertex.get_neighbours()]:
            new_R = R + [vertex]
            # p intersects/geschnitten N(vertex
            new_P = [val for val in P if val in self.reverse_edges(vertex.get_neighbours(), vertex)]
            # x intersects/geschnitten N(vertex)
            new_X = [val for val in X if val in self.reverse_edges(vertex.get_neighbours(), vertex)]
            result += self.bron_kerbosch(new_R, new_P, new_X, pivot=pivot)
            P.remove(vertex)
            X.append(vertex)
        return result

    def select_random_pivot(self, P, X):
        '''
        selects a pivot element randomly from union of P and X from bronkPivot(P,R,X)
        '''
        pivotList = list(set(P) | set(X))
        pivot = random.choice(pivotList)
        return pivot

    def select_max_pivot(self, P, X):
        '''
        selects a pivot element by maximal cardinality of possible vertices
        '''
        pivot = -math.inf
        for vertex in (set(P) | set(X)):
            if pivot == -math.inf:
                pivot = vertex
            elif len(vertex.get_neighbours()) > len(pivot.get_neighbours()):
                pivot = vertex

        return pivot


    def check_clique_properties(self):
        """
        checks if all vertices in R(list) are adjacent to every other vertex in R
        """
        check = True
        v_list = self.get_list_of_vertices()
        for vertex in v_list:
            n_list = vertex.get_neighbours()
            n_list.sort(key=lambda v: v.get_id())
            v_list_copy = v_list.copy()
            v_list_copy.remove(vertex)
            v_list_copy.sort(key=lambda v: v.get_id())
            if n_list != v_list_copy:
                check = False
        return check

    def save_to_txt(self, output_file=1):
        """
        saves representation of the GRAPH object to textfile: ["self.__name.graph"]
        """
        # Default value should be self.__name.graph
        if output_file == 1:
            output_file = self.get_name() + ".graph"        # Couldn't call self.get_name() in the method parameter list

        # If provided argument is not a valid directory and also is not a valid file name, raise NotADirectoryError
        if not os.path.isdir(os.path.dirname(output_file)) \
                and not os.path.isdir(os.path.dirname(os.path.abspath(output_file))):
            raise NotADirectoryError("Given path is not a directory!")

        # Provided argument is a directory, else it is a filename and the current working directory path is added
        if os.path.isdir(os.path.dirname(output_file)):
            filename = output_file
        else:
            filename = os.path.abspath(output_file)

        # If the provided argument does not end with '.graph', raise NameError
        if output_file[-6:] != ".graph":
            raise RuntimeError("Given path of filename must end with '.graph'")

        with open(filename, "w") as f:
            f.write("#nodes;" + str(self.__number_of_vertices) + "\n")
            f.write("#edges;" + str(self.__number_of_edges) + "\n") #streng genommen abhängig von davon, ob directed oder undirected, da bei undirected beide Richtungen als 1 zählen
            f.write("nodes labeled;" + str(self.__is_labeled_nodes) + "\n")  #HOW DO I FIGURE OUT THE BEST? PROBABLY WHEN ADDING NODES TO GRAPH?! PROBABLY WHEN ADDING NODES TO THE GRAPH
            f.write("edges labeled;" + str(self.__is_labeled_edges) + "\n")
            f.write("directed graph;" + str(self.__is_directed))
            if len(self.__list_of_vertices) > 0:
                f.write("\n")
                for vertex in self.__list_of_vertices:
                    f.write("\n" + str(vertex.get_id()) + ";" + str(vertex.get_label()))    #Wenn nodes ohne Label ";" weglassen?

            if len(self.__list_of_edges) > 0:
                f.write("\n")
                for edge in self.__list_of_edges:
                    f.write("\n" + str(edge.get_start_and_end()[0].get_id()) + ";"
                            + str(edge.get_start_and_end()[1].get_id()) + ";" + str(edge.get_label()))
        f.close()

    def is_compatible_vertex(self, own_vertex, vertex_other_graph):
        # Function returns whether two vertices of this and another graph are 'compatible'.
        # Here, this is performed by comparison of vertex labels.
        if own_vertex.get_label() == vertex_other_graph.get_label():
            return True
        else:
            return False

    def is_compatible_edge(self, own_edge, edge_other_graph):
        # Function returns whether two edges of this and another graph are 'compatible'.
        # Here, this is performed by comparison of edge labels.
        if own_edge.get_label() == edge_other_graph.get_label():
            return True
        else:
            return False

    def get_out_edge_list(self, vertex):
        # Function returns a list of directional edges leaving this vertex.
        edge_list = []
        for edge in self.get_list_of_edges():
            if vertex == edge.get_start_and_end()[0]:
                edge_list.append(edge)
        return edge_list

    def get_in_edge_list(self, vertex):
        # Function returns a list of directional edges going to this vertex.
        edge_list = []
        for edge in self.get_list_of_edges():
            if vertex == edge.get_start_and_end()[1]:
                edge_list.append(edge)
        return edge_list

    def has_edge(self, vertex1, vertex2):
        # Function should return whether there is a directional edge from vertex1 to vertex2
        if vertex2 in vertex1.get_neighbours():
            return True
        else:
            return False

    def get_edge(self, vertex1, vertex2):
        # Function returns EDGE type, this should only be invoked when self.has_edge has been performed
        edge_result = None
        for edge in self.get_list_of_edges():
            if edge.get_start_and_end()[0] == vertex1 and \
                    edge.get_start_and_end()[1] == vertex2:
                edge_result = edge
        if edge_result is None:
            print("Function GRAPH.get_edge: No edge could be found between given vertices!")
        return edge_result

    def get_mapping(self):
        return self.__mapping


def density(graph1, graph2):
    """ function to calculate the density of two graphs and return the difference between """
    vn1 = graph1.get_number_of_vertices()
    en1 = graph1.get_number_of_edges()
    vn2 = graph2.get_number_of_vertices()
    en2 = graph2.get_number_of_edges()
    dens1 = 2.0 * en1 / (vn1 * (vn1 - 1))
    dens2 = 2.0 * en2 / (vn2 * (vn2 - 1))
    return abs(dens1 - dens2)


def retrieve_graph_from_clique(clique, mapping, orig_graph):
    # The vertices in the clique will also be the vertices in the new graph so that the mapping does not have to be
    # updated. The connectivity though needs to be reduced. Therefore it is necessary for each pair of clique vertices
    # to identify the corresponding pair in one of the original graphs and see whether there is an edge.
    if mapping is None:
        loe = []
        for edge in orig_graph.get_list_of_edges():
            if edge.get_start_and_end()[0] in clique and edge.get_start_and_end()[1] in clique:
                loe.append(edge)
    else:
        loe = []
        for vertex_mp in clique:
            v_id = vertex_mp.get_id()
            orig_v_id = mapping[v_id][0]                                         # only consider first graph in mapping
            for vertex_orig in orig_graph.get_list_of_vertices():
                if orig_v_id == vertex_orig.get_id():
                    for neighbour in vertex_orig.get_neighbours():
                        n_id = neighbour.get_id()
                        for vertex_mp2 in clique:
                            if n_id == mapping[vertex_mp2.get_id()][0]:          # only consider first graph in mapping
                                new_edge = EDGE("Default_id", [vertex_mp, vertex_mp2], "Default_Label")
                                loe.append(new_edge)
        # Delete the neighbours attribute for all vertices in the clique.
        for vertex in clique:
            vertex.set_neighbours([])
        # Then, for each edge and vertex in the clique, append to the neighbours attribute of the vertex if it is the
        # start vertex in an edge.
        for edge in loe:
            for vertex in clique:
                if vertex == edge.get_start_and_end()[0]:
                    vertex.append_neighbour(edge.get_start_and_end()[1])
    # Now the new graph can be built
    new_graph = GRAPH("Default_name", clique, loe, len(clique), len(loe), orig_graph.get_is_directed(),
                      mapping=orig_graph.get_mapping())
    return new_graph
