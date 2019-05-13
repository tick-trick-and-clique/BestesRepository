import math
import random


class GRAPH(object):
    def __init__(self, name, list_of_vertices, list_of_edges, number_of_vertices, number_of_edges, is_directed):
        self.__name = name
        self.__list_of_vertices = list_of_vertices
        self.__list_of_edges = list_of_edges
        self.__number_of_vertices = number_of_vertices
        self.__number_of_edges = number_of_edges
        self.__is_directed = is_directed

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
        res = "vertices: "
        for vertex in self.__list_of_vertices:
            res += str(vertex) + ", "

        res += "\nnumber of vertices: "
        res += str(self.__number_of_vertices)

        res += "\nedges: "
        for edge in self.__list_of_edges:
            res += str(edge) + ", "

        res += "\nnumber of edges: "
        res += str(self.__number_of_edges)
        return res

    def bron_kerbosch(self, R, P, X):
        '''
        bron-kerbosch-algorithm w/out pivoting
        '''

        if not P and not X:
            print("Found Clique")
            for elem in R:
                print(elem.get_id())
            return

        for vertex in P[:]:
            new_R = R + [vertex]
            new_P = [val for val in P if val in self.reverse_edges(vertex.get_neighbours(),vertex)]  # P intersects w/ neighbours of vertex
            new_X = [val for val in X if val in self.reverse_edges(vertex.get_neighbours(),vertex)]  # X intersects w/ neighbours of vertex

            self.bron_kerbosch(new_R, new_P, new_X)
            P.remove(vertex)
            X.append(vertex)
        return

    def reverse_edges(self,list_of_vertices, current_vertex):
        """
        Checks if neighbours of current vertex has reversed edge to currentvertex
        """
        vertices_with_reverse_edges = []
        for elem in list_of_vertices:
            if current_vertex in elem.get_neighbours():
                vertices_with_reverse_edges.append(elem)
        return vertices_with_reverse_edges
    
    def bron_kerbosch_pivot(self, R, P, X, pivot=None):
        """
        bron kerbosch algo to find maximal cliques in graph
        with pivot
        """
        if not P and not X:
            print("Found Clique:")
            for elem in R:
                print(elem)
            return
        if pivot == None:
            for vertex in P[:]:
                new_R = R + [vertex]
                new_P = [val for val in P if val in self.reverse_edges(vertex.get_neighbours(),vertex)]   # P intersects w/ neighbours of vertex
                new_X = [val for val in X if val in self.reverse_edges(vertex.get_neighbours(),vertex)]   # X intersects w/ neighbours of vertex

                self.bron_kerbosch_pivot(new_R, new_P, new_X)
                P.remove(vertex)
                X.append(vertex)
            return
        elif pivot == "max":
            pivot_vertex = self.select_max_pivot(P, X)
        elif pivot == "random":
            pivot_vertex = self.select_random_pivot(P, X)
        else:
            raise ValueError("Given optional pivot argument is illegal!")

        for vertex in [elem for elem in P if elem not in pivot_vertex.get_neighbours()]:
            new_R = R + [vertex]
            new_P = [val for val in P if val in self.reverse_edges(vertex.get_neighbours(),vertex)]  # p intersects/geschnitten N(vertex)
            new_X = [val for val in X if val in self.reverse_edges(vertex.get_neighbours(),vertex)]  # x intersects/geschnitten N(vertex)
            self.bron_kerbosch_pivot(new_R, new_P, new_X, pivot)
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
        seletcs a pivot element by maximal cardinality of possible vertices
        '''
        pivot = -math.inf
        for vertex in (set(P) | set(X)):
            if pivot == -math.inf:
                pivot = vertex
            elif len(vertex.get_neighbours()) > len(pivot.get_neighbours()):
                pivot = vertex

        return pivot

    def bron_kerbosch_anchor(self, R, P, X):  # noch falsch!
        """
        bron kerbosch algorithm to find maximal cliques in graph using an anchor in R
        """
        if self.check_clique_properties(R):
            # Für alle Knoten im Anker wird die Menge P auf den Schnitt mit den Nachbarn des jeweiligen Knotens
            # reduziert.
            for vertex in R:
                P = [v for v in P if v in vertex.get_neighbours()]
            # Start von Bron-Kerbosch mit modifizierter Menge P.
            self.bron_kerbosch_pivot(R, P, X)
            return
        else:
            raise Exception("Dang... anchor ain't no clique!")
            return

    def check_clique_properties(self, R):
        """
        checks if all vertices in R(list) are adjacent to every other vertex in R
        """
        check = True
        for vertex in R:
            if vertex.get_neighbours().sort() != (R - [vertex]).sort():
                check = False
        return check