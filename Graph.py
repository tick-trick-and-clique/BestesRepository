#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import random
import os
import string
import itertools
from queue import Queue
from Edge import EDGE
from Vertex import VERTEX
from typing import List
from copy import copy

class GRAPH(object):
    # TODO: number_of_vertices and number_of_edges is kind of obsolete, remove and reconstruct from given lists?!
    def __init__(self, name, list_of_vertices, list_of_edges, number_of_vertices, number_of_edges, is_directed,
                 has_labeled_nodes=False, has_labeled_edges=False):
        self.__name = name
        self.__list_of_vertices: List[VERTEX] = list_of_vertices
        self.__list_of_edges: List[EDGE] = list_of_edges
        # TODO: In or out?! Reconstructs list_of_nodes from list_of_edges, IFF just the latter is not empty
        if not self.__list_of_vertices and self.__list_of_edges:
            list_vertices: List[VERTEX] = []
            for edge in self.__list_of_edges:
                list_vertices.append(edge.get_start_and_end()[0])
                list_vertices.append(edge.get_start_and_end()[1])
            unique_vertices = set(list_vertices)
            self.__list_of_vertices = list(unique_vertices)
        self.__number_of_vertices = len(self.__list_of_vertices)
        if is_directed:
            self.__number_of_edges = len(self.__list_of_edges)
        else:
            self.__number_of_edges = int(len(self.__list_of_edges)/2)
        self.__is_directed = is_directed
        self.__has_labeled_nodes = has_labeled_nodes  # has to be transferred while initialising the graph
        self.__has_labeled_edges = has_labeled_edges  # has to be transferred while initialising the graph

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
        return copy(self.__list_of_vertices)

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

    def get_has_labeled_nodes(self):
        return self.__has_labeled_nodes

    def get_has_labeled_edges(self):
        return self.__has_labeled_edges

    def get_cardinality_of_vertex(self, vertex):
        cardinality = len(vertex.get_out_neighbours())
        for v in self.get_list_of_vertices():
            if vertex in v.get_out_neighbours():
                cardinality += 1
        return cardinality

    def del_vertex(self, vertex_tbd: VERTEX):
        '''
        Deletes a given vertex from self.__list_of_vertices and self.__list_of_edges
        :param vertex_tbd: vertex to be deleted; Either of Datatype object(VERTEX) or vertex-ID as int or string
        :return: None
        '''
        if isinstance(vertex_tbd, VERTEX):
            #  Update out-neighbours
            for vertex in self.reversed_edges(self.__list_of_vertices, vertex_tbd):
                new_neighbours = [vert for vert in vertex.get_out_neighbours() if not vert == vertex_tbd]
                vertex.set_out_neighbours(new_neighbours)
            #  Delete vertex from list and corresponding edges
            self.__list_of_vertices[:] = [vertex for vertex in self.__list_of_vertices if not vertex_tbd == vertex]
            self.__list_of_edges[:] = [edge for edge in self.__list_of_edges
                                       if not (vertex_tbd in edge.get_start_and_end())]
        else:
            raise IOError("Wrong input format: Parameter <vertex_tbd> has to be an VERTEX -object")

        #  Update number of vertices and edges
        self.__number_of_vertices = len(self.__list_of_vertices)
        self.__number_of_edges = len(self.__list_of_edges)
        # print("AFTER:\n" + "number_of_vertices, number_of_edges: (%s, %s) " %
        #       (len(self.__list_of_vertices), len(self.__list_of_edges)) + "\n")

    def del_edge(self, edge_tbd: EDGE):
        '''
        Deletes a given edge from self.__list_of_edges
        :param edge_tbd: vertex to be deleted; Either of Datatype object(EDGE) or edge-ID as int or string
        :return: None
        '''
        #  For directed graphs:
        if self.__is_directed:
            if isinstance(edge_tbd, EDGE):
                #  Update Out-neighbours
                concerned_vertex = self.get_vertex_by_id(edge_tbd.get_start_and_end()[0])
                end_id = edge_tbd.get_start_and_end()[1]
                new_neighbours = [v_id for v_id in concerned_vertex.get_out_neighbours() if not v_id == end_id]
                concerned_vertex.set_out_neighbours(new_neighbours)
                #  Delete edge_tbd
                self.__list_of_edges[:] = [edge for edge in self.__list_of_edges if not edge_tbd == edge]
            else:
                raise IOError("Wrong input format: Parameter <edge_tbd> be an EDGE -object")

        #  For undirected graphs (inverted edges have to be deleted too)
        else:
            if isinstance(edge_tbd, EDGE):
                #  Update Out-neighbours
                vertex1 = edge_tbd.get_start_and_end()[0]
                vertex2 = edge_tbd.get_start_and_end()[1]
                neighbours1 = vertex1.get_out_neighbours()
                #concerned_vertex1 = self.get_vertex_by_id(vertex1)
                new_neighbours1 = [v_id for v_id in vertex1.get_out_neighbours() if not v_id == vertex2]
                vertex1.set_out_neighbours(new_neighbours1)
                new_neighbours2 = [v_id for v_id in vertex2.get_out_neighbours() if not v_id == vertex1]
                vertex2.set_out_neighbours(new_neighbours2)
                #  Delete edge_tbd and inverted correspondent
                edge_inverted_tbd = self.inverted_edge(edge_tbd)
                self.__list_of_edges[:] = \
                    [edge for edge in self.__list_of_edges if not (edge == edge_tbd or edge == edge_inverted_tbd)]
            else:
                raise IOError("Wrong input format: Parameter <edge_tbd> has to be an EDGE -object")

        #  Update number of vertices and edges
        self.__number_of_vertices = len(self.__list_of_vertices)
        self.__number_of_edges = len(self.__list_of_edges)

    def __str__(self):
        '''
        builds a string representation of of vertices and edges the graph
        '''
        res = "number of vertices:\n"
        res += str(len(self.__list_of_vertices)) + "\n"

        res += "vertices:\n"
        for vertex in self.__list_of_vertices:
            res += str(vertex) + ",\n"

        res += "number of edges:\n"
        if self.__is_directed:
            res += str(len(self.__list_of_edges)) + "\n"
        else:
            res += str(int(len(self.__list_of_edges)/2)) + "\n"

        res += "edges:\n"
        for edge in self.__list_of_edges:
            res += str(edge) + ",\n"
        return res

    def reversed_edges(self, list_of_vertices, current_vertex):
        """
        returns list of vertices (in-neighbours of <current_vertex>, which have <current_vertex> as an out-neighbours
        """
        vertices_with_reverse_edges = []
        for elem in list_of_vertices:
            if current_vertex in elem.get_out_neighbours():
                vertices_with_reverse_edges.append(elem)
        return vertices_with_reverse_edges

    def inverted_edge(self, edge: EDGE):
        start_id = edge.get_start_and_end()[0]
        end_id = edge.get_start_and_end()[1]
        for edge_obj in self.__list_of_edges:
            if edge_obj.get_start_and_end()[0] == end_id and \
                    edge_obj.get_start_and_end()[1] == start_id:
                return edge_obj


    def bron_kerbosch(self, R, P, X, pivot=None):
        """
        bron kerbosch algo to find maximal cliques in graph
        with pivot. Function returns a list of cliques, which are lists of vertices.
        """
        result = []
        if not P and not X:
            return [R]
        if pivot == "max":
            pivot_vertex = self.select_max_pivot(P, X)
        elif pivot == "random":
            pivot_vertex = self.select_random_pivot(P, X)
        elif pivot is None:
            for vertex in P.copy():
                new_R = R.copy()
                new_R.add(vertex)
                neighbours = vertex.get_out_neighbours()
                new_P = set([val for val in P if val in neighbours])  # P intersects w/ neighbours of vertex
                new_X = set([val for val in X if val in neighbours])  # X intersects w/ neighbours of vertex
                result += self.bron_kerbosch(new_R, new_P, new_X)
                P.remove(vertex)
                X.add(vertex)
            return result
        else:
            raise ValueError("Given optional pivot argument is illegal!")
        for vertex in [elem for elem in P if elem not in pivot_vertex.get_out_neighbours()]:
            new_R = R
            new_R.add(vertex)
            new_P = set([val for val in P if val in vertex.get_out_neighbours()])
            new_X = set([val for val in X if val in vertex.get_out_neighbours()])
            result += self.bron_kerbosch(new_R, new_P, new_X, pivot=pivot)
            P.remove(vertex)
            X.add(vertex)
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
            elif self.get_cardinality_of_vertex(vertex) > self.get_cardinality_of_vertex(pivot):
                pivot = vertex
        return pivot

    def check_clique_properties(self):
        """
        checks if all vertices in R(list) are adjacent to every other vertex in R
        """
        v_set = set(self.get_list_of_vertices())
        for vertex in v_set:
            n_set = vertex.get_out_neighbours()
            if n_set.difference(v_set) != vertex:
                return False

    def save_to_txt(self, output_file=1, sequential_number=None):
        """
        saves representation of the GRAPH object to textfile: ["self.__name.graph"]
        """
        if output_file == 1:
            output_file = self.get_name() + ".graph"
        if not os.path.isdir(os.path.dirname(output_file)) \
                and not os.path.isdir(os.path.dirname(os.path.abspath(output_file))):
            raise NotADirectoryError("Given path is not a directory!")
        if output_file[-6:] != ".graph":
            raise RuntimeError("Given path of filename must end with '.graph'")

        # If multiple graphs should be saved to the same location, addition of a sequential number is necessary to
        # impede overwriting
        if sequential_number is not None:
            output_file = output_file[:-6] + "_" + str(sequential_number) + output_file[-6:]
        if os.path.isdir(os.path.dirname(output_file)):
            filename = output_file
        else:
            filename = os.path.abspath(output_file)
        with open(filename, "w") as f:
            f.write("#nodes;" + str(self.__number_of_vertices) + "\n")
            if self.__is_directed:
                f.write("#edges;" + str(int(len(self.__list_of_edges))) + "\n")
            else:
                f.write("#edges;" + str(int(len(self.__list_of_edges)/2)) + "\n")
            f.write("nodes labelled;" + str(self.__has_labeled_nodes) + "\n")
            f.write("edges labelled;" + str(self.__has_labeled_edges) + "\n")
            f.write("directed graph;" + str(self.__is_directed))
            if len(self.__list_of_vertices) > 0:
                f.write("\n")
                for vertex in self.get_list_of_vertices():
                    f.write("\n" + str(vertex.get_id()) + ";" + str(vertex.get_label()))
            if len(self.__list_of_edges) > 0:
                f.write("\n")
                if self.__is_directed == False:
                    i = 0
                    print("undirected")
                    for edge in self.__list_of_edges:
                        if i%2 == 0:
                            f.write("\n" + str(edge.get_start_and_end()[0].get_id()) + ";"
                                    + str(edge.get_start_and_end()[1].get_id()) + ";" + str(edge.get_label()))
                            i+=1
                        else:
                            i+=1
                else:
                    for edge in self.__list_of_edges:
                        f.write("\n" + str(edge.get_start_and_end()[0].get_id()) + ";"
                                + str(edge.get_start_and_end()[1].get_id()) + ";" + str(edge.get_label()))
        f.close()

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
        if vertex2 in vertex1.get_out_neighbours():
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

    def get_vertex_by_id(self, vertex_id: string) -> VERTEX:
        for vertex in self.__list_of_vertices:
            if vertex.get_id() == vertex_id:
                return vertex

    def graph_from_vertex_combination(self, list_of_vertices):
        """
        Return Type: GRAPH
        """
        lov = []
        loe = []
        for v in self.get_list_of_vertices():
            if v in list_of_vertices:
                lov.append(v)
        for edge in self.get_list_of_edges():
            if edge.get_start_and_end()[0] in list_of_vertices and edge.get_start_and_end()[1] in list_of_vertices:
                loe.append(edge)
        return GRAPH(self.get_name(), lov, loe, len(lov), len(loe), self.get_is_directed(),
                     self.get_has_labeled_nodes(), self.get_has_labeled_edges())

    def is_connected(self):
        """
        Function to examine whether this graph is connected. Here, a breadth first search is applied.
        Return Type: Boolean
        """
        queue = Queue()
        v_list = self.get_list_of_vertices()
        start = v_list[0]
        queue.put(start)
        already_seen = set()
        while not queue.empty():
            vertex = queue.get()
            already_seen.add(vertex)
            candidates = set()
            candidates.union(vertex.get_out_neighbours())
            for v in v_list:
                if vertex in v.get_out_neighbours():
                    candidates.add(v)
            for v in candidates:
                if v not in already_seen:
                    queue.put(v)
                    already_seen.add(v)
        if already_seen.__len__() == self.get_number_of_vertices():
            return True
        else:
            return False

    def fill_neighbourhood(self):
        """fills neighbourhood of all vertices in this graph. Mandatory after creating of a graph!"""
        for edge_obj in self.__list_of_edges:
            edge_obj.get_start_and_end()[0].add_out_neighbour(edge_obj.get_start_and_end()[1])


def density(graph1, graph2):
    """ function to calculate the density of two graphs and return the difference between """
    vn1 = graph1.get_number_of_vertices()
    en1 = graph1.get_number_of_edges()
    vn2 = graph2.get_number_of_vertices()
    en2 = graph2.get_number_of_edges()
    if en1 == 0:
        dens1 = 0
    else:
        dens1 = 2.0 * en1 / (vn1 * (vn1 - 1))
    if en2 == 0:
        dens2 = 0
    else:
        dens2 = 2.0 * en2 / (vn2 * (vn2 - 1))
    return abs(dens1 - dens2)


def retrieve_graph_from_clique(clique, orig_graph):
    """
    Takes a clique, i.e. a list of vertices, and one of the original graphs as input and returns a subgraph of the
    original graph respective to the clique vertices. 'Original graph' is not to be confused with the graphs of the
    initial input. Here, 'original graph' refers to the graph from which the modular product was built. This can and
    will most probably a matching graph. The VERTEX.__id, VERTEX.__label, EDGE_id and EDGE.__label ,
    __is_directed attribute, __is_labelled_nodes attribute and __is_labelled_edges in the new subgraph originate from
    'orig_graph'. The vertices will carry the mapping to the vertices of the initial input graph(s) in their mapping
    attribute. The newly created subgraph carries a random 8-character name to make it's name a unique identifier.
    This function is analogous to 'mb_mapping_to_graph' for matching-based algorithm.
    Return Type: GRAPH
    """
    lov = []
    loe = []
    for vertex_mp in clique:
        orig_vertex = vertex_mp.get_mapping()[orig_graph.get_name()]
        copy_orig_vertex = VERTEX(orig_vertex.get_id(), orig_vertex.get_label())
        copy_orig_vertex.combine_mapping(vertex_mp)
        lov.append(copy_orig_vertex)
    for edge in orig_graph.get_list_of_edges():
        for copy_orig_vertex in lov:
            lov_cut = lov.copy()
            lov_cut.remove(copy_orig_vertex)
            for copy_orig_vertex2 in lov_cut:
                if edge.get_start_and_end()[0].get_id() == copy_orig_vertex.get_id() and \
                        edge.get_start_and_end()[1].get_id() == copy_orig_vertex2.get_id():
                    copy_orig_vertex.add_out_neighbour(copy_orig_vertex2)
                    loe.append(EDGE(edge.get_id(), [copy_orig_vertex, copy_orig_vertex2], edge.get_label()))
    graph_name = "".join([random.choice(string.ascii_letters) for i in range(8)])
    new_graph = GRAPH(graph_name, lov, loe, len(lov), len(loe), orig_graph.get_is_directed(),
                      has_labeled_nodes=orig_graph.get_has_labeled_nodes(),
                      has_labeled_edges=orig_graph.get_has_labeled_edges())
    return new_graph


def retrieve_original_subgraphs(matching_graph, input_graphs):
    """
    Takes a matching_graph, which is the product of a successful search for a subgraph isomorphism and whose vertices'
    mapping attribute carries the vertices in the input graphs that correspond to the identified isomorphism in the input
    graphs
    Return Type: [GRAPH, ...]
    """
    subgraphs = []
    for graph in input_graphs:
        if graph.get_name() in matching_graph.get_list_of_vertices()[0].get_mapping():
            lov = []
            loe = []
            for v1_mg in matching_graph.get_list_of_vertices():
                orig_v1 = v1_mg.get_mapping()[graph.get_name()]
                lov.append(orig_v1)
            for edge in graph.get_list_of_edges():
                for v1 in lov:
                    for v2 in lov:
                        if edge.get_start_and_end()[0] == v1 and edge.get_start_and_end()[1] == v2:
                            loe.append(edge)
            subgraphs.append(GRAPH(graph.get_name(), lov, loe, len(lov), len(loe), graph.get_is_directed(),
                                   graph.get_has_labeled_nodes(), graph.get_has_labeled_edges()))
    return subgraphs


def randomString(stringLength=3):
    """ Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def anchor_from_anchor_vertex_list(anchor_graph_list, p):
    """
    Function takes two lists of type [VERTEX, ...] as input. The vertices in 'p' corresponding to vertices in
    'anchor_graph_list' is then returned as list together with the remaining candidate subset of vertices of 'p' as
    tuple.
    Return Type: ([VERTEX, ...], [VERTEX, ...])
    """
    anchor_subset = []
    remaining_candidate_subset = []
    for vertex in p[:]:
        if vertex.get_id() in [v.get_id() for v in anchor_graph_list]:
            anchor_subset.append(vertex)
            p.remove(vertex)
    for vertex in p:
        true_list = []
        for v in anchor_subset:
            if vertex in v.get_out_neighbours() and v in vertex.get_out_neighbours():
                true_list.append(True)
        if len(true_list) == len(anchor_subset) and all(true_list):
            remaining_candidate_subset.append(vertex)
    return anchor_subset, remaining_candidate_subset


def remaining_candidates(r, p):
    """
    Function takes two lists of type [VERTEX, ...] as input and return the subset of 'p' where each vertex is a
    candidate for further clique expansion. Edges must be undirected.
    Return type: [VERTEX, ...]
    """
    result = []
    for v in p:
        truelist = []
        if v not in r:
            for vertex in r:
                if vertex in v.get_out_neighbours():
                    truelist.append(True)
                else:
                    truelist.append(False)
            if all(truelist):
                result.append(v)
    return result


def retrieve_fusion_graph(matching_graph, input_graphs):
    """
    Function takes a matching graph object and the input graphs as input and returns a fusion graph, i.e. a graph where
    each of the input graph are embedded and edges between embeddings representing vertex matchings. Each Vertex and
    Edge will carry a label, those that did not carry any in their input graph will receive the label '$None$'. The
    order of vertices in respect to their ID follows the order of the input graphs. Vertex and Edge IDs cant not be
    guaranteed to be identical in comparison of input graph and resulting alignment graph!
    Return type: GRAPH
    """
    lov = []
    loe = []
    for input_graph in input_graphs:
        lov += input_graph.get_list_of_vertices()
        loe += input_graph.get_list_of_edges()
    for i in range(len(lov)):
        lov[i].set_id(i + 1)
        if not lov[i].get_label():
            lov[i].set_label("$None$")
    name = ''
    is_directed = False
    for input_graph in input_graphs:
        name += input_graph.get_name() + "_AND_"
        is_directed = (is_directed or input_graph.get_is_directed())
    name = name[:-5]
    for vertex in matching_graph.get_list_of_vertices():
        map = vertex.get_mapping()
        combis = itertools.combinations(map.values(), 2)
        for combi in combis:
            combi[0].add_out_neighbour(combi[1])
            combi[1].add_out_neighbour(combi[0])
            edge1 = EDGE(0, [combi[0], combi[1]], "$matching$")
            loe.append(edge1)
            if not is_directed:
                edge2 = EDGE(0, [combi[1], combi[0]], "$matching$")
                loe.append(edge2)
    for i in range(len(loe)):
        loe[i].set_id(i + 1)
        if not loe[i].get_label():
            loe[i].set_label("$None$")
    graph = GRAPH(name, lov, loe, len(lov), len(loe), is_directed,
                  True, True)
    return graph


