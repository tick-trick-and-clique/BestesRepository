import math
import random
import os



class GRAPH(object):
    def __init__(self, name, list_of_vertices, list_of_edges, number_of_vertices, number_of_edges, is_directed, is_labeled_nodes=False, is_labeled_edges=False):
        self.__name = name
        self.__list_of_vertices = list_of_vertices
        self.__list_of_edges = list_of_edges
        self.__number_of_vertices = number_of_vertices
        self.__number_of_edges = number_of_edges
        self.__is_directed = is_directed
        self.__is_labeled_nodes = is_labeled_nodes  # has to be transferred while initialising the graph
        self.__is_labeled_edges = is_labeled_edges  # has to be transferred while initialising the graph

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
        with pivot
        """
        if not P and not X:
            print("Found Clique")
            for elem in R:
                print(elem)
            return
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

                self.bron_kerbosch(new_R, new_P, new_X)
                P.remove(vertex)
                X.append(vertex)
            return
        else:
            raise ValueError("Given optional pivot argument is illegal!")
        for vertex in [elem for elem in P if elem not in pivot_vertex.get_neighbours()]:
            new_R = R + [vertex]
            # p intersects/geschnitten N(vertex
            new_P = [val for val in P if val in self.reverse_edges(vertex.get_neighbours(), vertex)]
            # x intersects/geschnitten N(vertex)
            new_X = [val for val in X if val in self.reverse_edges(vertex.get_neighbours(), vertex)]
            self.bron_kerbosch(new_R, new_P, new_X, pivot=pivot)
            P.remove(vertex)
            X.append(vertex)
        return

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
            raise NameError("Given path of filename must end with '.graph'")

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

    def check_partial_graph_of(self, graph):
        """
        checks whether self is partial graph of graph
        """
        partial = True

        # check whether the ids of all vertices of self are also found in the list of vertices of graph
        for v1 in self.get_list_of_vertices():
            if v1.get_id() not in [v2.get_id() for v2 in graph.get_list_of_vertices()]:
                partial = False

        # check whether the ids of all edges of self are also found in the list of edges of graph
        for e1 in self.get_list_of_edges():
            if e1.get_id() not in [e2.get_id() for e2 in graph.get_list_of_edges()]:
                partial = False

        # check whether the __is_directed attribute ist the same
        if self.__is_directed != graph.__is_directed:
            partial = False

        return partial

    def is_compatible_vertex(self, own_vertex, vertex_other_graph):
        # TODO: Function should return whether two vertices of this and another graph are 'compatible'
        print("'is_compatible_vertex' not yet implemented!")
        return True

    def is_compatible_edge(self, own_edge, edge_other_graph):
        # TODO: Function should return whether two edges of this and another graph are 'compatible'
        print("'is_compatible_edge' not yet implemented!")
        return True

    def get_out_edge_list(self, vertex):
        # TODO: Function should return list of directional edges leaving this vertex
        print("'get_out_edge_count' is not yet implemented!")
        return []

    def get_in_edge_list(self, vertex):
        # TODO: Function should return list of directional edges going to this vertex
        print("'get_in_edge_count' is not yet implemented!")
        return []

    def has_edge(self, vertex1, vertex2):
        # TODO: Function should return whether there is a directional edge from vertex1 to vertex2
        some_boolean = True
        print("'has_edge' is not yet implemented!")
        return some_boolean

    def get_edge(self, vertex1, vertex2):
        # TODO: Function should return EDGE type, this should only be invoked when self.has_edge has been performed
        print("'get_edge' is not yet implemented!")
        return None
