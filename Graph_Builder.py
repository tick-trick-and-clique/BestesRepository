#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 10.05.2019
@author: tilman
'''
import random
import string
import math
from collections import defaultdict
from typing import List
from Graph import GRAPH
from Vertex import VERTEX
from Edge import EDGE
from itertools import combinations

def buildRndGraph(nr_nodes, p_connected, labeled_nodes=False, labeled_edges=False, directed=False,
                  name_graph=None):
    """
    Creates random Graphs concerning given parameters and saves the graph to "<name_graph>.graph" format
    p_connected:= probability, that there is a connection (directed or undirected)
    between two arbitrarily chosen vertices
    """
    list_vertices: List[VERTEX] = []
    list_edges: List[EDGE] = []

    # 1 Create Vertices
    for vertex_id in range(1, nr_nodes + 1):
        append_VERTEX_to_list(list_vertices, vertex_id, labeled_nodes)

    # 2 Create Edges if arbitrarily number [0.0, 1.0] <= p_connected
    list_combinations = combinations(list_vertices, 2)
    # list of all possible combinations of length 2 --> lookup list for vertex combinations
    edge_id = 1  # Initialise first edge id
    #print(list_combinations)
    for combination in list_combinations:  # Example: Combination:= [1,3]
        #print(combination)
        if directed:
            directed_edge_normal = (random.random() <= math.sqrt(p_connected))
            # if TRUE: draw edge in "natural" direction of combination
            directed_edge_reverse = (random.random() <= math.sqrt(p_connected))
            # if TRUE: draw edge in "reverse" direction of combination
            if directed_edge_normal:  # draw edge in "normal" direction of combination: 0->1
                # print("1-direct, normal")
                tmp_dir_edge = combination
                edge_id = append_EDGE_to_List(list_edges, edge_id, tmp_dir_edge, directed, labeled_edges)[1]
            elif directed_edge_reverse:  # draw edge in "reversed" direction of combination: 1->0
                # print("1-direct, reverse")
                tmp_dir_edge = [combination[1], combination[0]]
                edge_id = append_EDGE_to_List(list_edges, edge_id, tmp_dir_edge, directed, labeled_edges)[1]
        elif (directed is False) and (random.random() <= p_connected):
            # print("2-NON-direct")
            tmp_edge = combination
            edge_id = append_EDGE_to_List(list_edges, edge_id, tmp_edge, directed, labeled_edges)[1]

    # 3 Create Graph
    if not directed:
        # For undirected graphs, the number of edges is half the number of edges entries in the GRAPH object
        if name_graph:
            graph = GRAPH(name_graph, list_vertices, list_edges, len(list_vertices),
                          int(len(list_edges) / 2), directed, labeled_nodes, labeled_edges)
        else:
            default_name = "random_graph(%s, %s, %s)" % (nr_nodes, p_connected, directed)
            graph = GRAPH(default_name, list_vertices, list_edges, len(list_vertices),
                          int(len(list_edges) / 2), directed, labeled_nodes, labeled_edges)
    else:
        if name_graph:
            graph = GRAPH(name_graph, list_vertices, list_edges, len(list_vertices),
                          len(list_edges), directed, labeled_nodes, labeled_edges)
        else:
            default_name = "random_graph(%s, %s, %s)" % (nr_nodes, p_connected, directed)
            graph = GRAPH(default_name, list_vertices, list_edges, len(list_vertices),
                          int(len(list_edges) / 2), directed, labeled_nodes, labeled_edges)

    # 4 Set out-neighbours setting
    graph.fill_neighbourhood()

    return graph


def buildRndCluster(n, d, del_vert=0, del_edges=0, labeled_nodes=False, labeled_edges=False, directed=False, seed=None):
    '''
    Parameters
    ----------
    :param d: The degree of each node.
    :param n: Number of nodes. The value of ``n * d`` must be even.
    :param del_vert: Number of vertices, which will be deleted in a second step
    :param del_edges: Number of edges, which will be deleted in a second step
    :param seed: The seed for random number generator.
    :param labeled_nodes:
    :param labeled_edges:
    :param directed:
    :return: Returns a random ``d``-regular graph on ``n`` with predefined deletions (default: NO DELETIONS)
    The resulting graph has no self-loops or parallel edges.

    Notes
    -----
    The nodes are numbered from ``1`` to ``n``.

    Raises
    ------
    IOError
    If ``n * d`` is odd or ``d`` is greater than or equal to ``n``.
    '''
    """
    References
    ----------
    MODIFIKATION FROM THE NetworkX Package:
    "
    Copyright (C) 2004-2012, NetworkX Developers
    Aric Hagberg <hagberg@lanl.gov>
    Dan Schult <dschult@colgate.edu>
    Pieter Swart <swart@lanl.gov>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

      * Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.

      * Redistributions in binary form must reproduce the above
        copyright notice, this list of conditions and the following
        disclaimer in the documentation and/or other materials provided
        with the distribution.

      * Neither the name of the NetworkX Developers nor the names of its
        contributors may be used to endorse or promote products derived
        from this software without specific prior written permission.


    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """
    if (n * d) % 2 != 0:
        raise IOError("n * d must be even")

    if not 0 <= d < n:
        raise IOError("the 0 <= d < n inequality must be satisfied")

    if d == 0:
        return GRAPH('empty_graph', [], [], 0, 0, False)

    if seed is not None:
        random.seed(seed)

    def suitable(edges, potential_edges):
    # Helper subroutine to check if there are suitable edges remaining
    # If False, the generation of the graph has failed
        if not potential_edges:
            return True
        for s1 in potential_edges:
            for s2 in potential_edges:
                # Two iterators on the same dictionary are guaranteed
                # to visit it in the same order if there are no
                # intervening modifications.
                if s1 == s2:
                    # Only need to consider s1-s2 pair one time
                    break
                if s1 > s2:
                    s1, s2 = s2, s1
                if (s1, s2) not in edges:
                    return True
        return False

    def try_creation():
        # Attempt to create an edge set

        edges = set()
        edges_combinations = set()
        stubs = list(range(1, n+1)) * d
        # print("stubs", type(stubs), stubs, sep="\t")
        while stubs:
            potential_edges = defaultdict(lambda: 0)
            random.shuffle(stubs)
            stubiter = iter(stubs)
            #zippo = zip(stubiter, stubiter)
            #zip_set =set(zippo)
            #print("zip_set:\t%s" % zip_set)
            for s1, s2 in zip(stubiter, stubiter):
                # print("TYPE (s1, s2), edges, potential_edges: %s\t%s\t%s" %(type(s1), type(edges), type(potential_edges)))
                # print("s1, s2: %s, %s" % (s1, s2))
                if s1 > s2:
                    s1, s2 = s2, s1
                    # print("s1, s2: %s, %s (SWITCHED)" % (s1, s2))
                    # Bedeutet, dass nur edges in eine Richtung (quasi ungerichtet) entstehen, oder?!
                if s1 != s2 and ((s1, s2) not in edges): #  FIXME: tritt nie ein, da type(s1, s2) nie in edges sein kann!!
                    edges.add((s1, s2))
                else:
                    potential_edges[s1] += 1
                    # print("s1, potential_edges[s1]: %s:{%s}" % (s1, potential_edges[s1]))
                    potential_edges[s2] += 1
                    # print("s2, potential_edges[s2]: %s:{%s}" % (s1, potential_edges[s2]))

            if not suitable(edges, potential_edges):
                return None  # failed to find suitable edge set

            stubs = [node for node, potential in potential_edges.items()
                     for _ in range(potential)]
            # print("stubs after WEIRDO: %s" % stubs)
        return list(edges)

    # Even though a suitable edge set exists, the generation of such a set is not guaranteed.
    # Try repeatedly to find one.
    edges = try_creation()
    while edges is None:
        edges = try_creation()
    #for edge in edges:
    #    print("edge: %s" % str(edge))
    # print("len(edges): %s" % len(edges))

    # Create VERTEX-Objects:
    vertices_objects: List[VERTEX] = []
    list_vert_ids: List[string] = []
    for edge in edges:
        list_vert_ids.extend(edge)
    list_unique_vert_ids = list(set(list_vert_ids))
    for vertex_id in list_unique_vert_ids:
        append_VERTEX_to_list(vertices_objects, vertex_id, labeled_nodes)

    # Create EDGE-Objects
    edges_objects: List[EDGE] = []
    edge_id = 1
    list_vert_ids: List[string] = []



    for edge in edges:
        # print(edge)
        edge_with_objects = [get_VERTEX_with_ID(vertices_objects, edge[0]), get_VERTEX_with_ID(vertices_objects, edge[1])]
        inverted_edge_with_objects = [edge_with_objects[1], edge_with_objects[0]]

        if labeled_edges:
            # Edges have to be appended in both directions for undirected graphs
            edges_objects.append(EDGE(edge_id, edge_with_objects, random_string()))
            edges_objects.append(EDGE(edge_id, inverted_edge_with_objects, random_string()))
            edge_id += 1
        else:
            edges_objects.append(EDGE(edge_id, edge_with_objects, ""))
            edges_objects.append(EDGE(edge_id, inverted_edge_with_objects, ""))
            edge_id += 1
    #  Create GRAPH-Object
    graph = GRAPH("random_cluster_graph(%s, %s, %s, %s)" % (n, d, del_vert, del_edges),
                  [], edges_objects, 0, 0, labeled_nodes, labeled_edges, directed)

    # Set neighbours setting
    graph.fill_neighbourhood()

    # Delete vertices according to input
    while del_vert > 0:
        rand_index = random.randint(0, len(graph.get_list_of_vertices())-1)
        vertex_tbd = graph.get_list_of_vertices()[rand_index]
        graph.del_vertex(vertex_tbd)
        del_vert -= 1

    # Delete edges according to input
    while del_edges > 0:
        rand_index = random.randint(0, len(graph.get_list_of_edges())-1)
        edge_tbd = graph.get_list_of_edges()[rand_index]
        graph.del_edge(edge_tbd)
        del_edges -= 1
        # graph.del_vertex(rand_index)

    return graph


def random_string(stringLength=3):
    """ Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def printListEdges(list):
    """just for monitoring purpose of algorithm"""
    output = ""
    for edge in list:
        output += str(edge.get_id()) + ";" + str(edge.get_start_and_end()[0].get_id()) \
                  + ";" + str(edge.get_start_and_end()[1].get_id()) + ";" + str(edge.get_label()) + "\t"
    print(output)


def append_VERTEX_to_list(vertices, vertex_id: int, labeled=False):
    """Appends VERTEX with a given VERTEX-ID to a given list of VERTEX"""
    if labeled:
        vertices.append(VERTEX(vertex_id, random_string()))
    else:
        vertices.append(VERTEX(vertex_id, ""))
    return vertices


def append_EDGE_to_List(edges, edge_id, start_and_end: List[VERTEX], directed=False, labeled=False):
    """Appends a new EDGE with a given EDGE-ID start-and-end-Vertex-ID to a given list of EDGE"""
    if directed:
        if labeled:
            edges.append(EDGE(edge_id, start_and_end, random_string()))
            edge_id += 1
        else:
            edges.append(EDGE(edge_id, start_and_end, ""))
            edge_id += 1
    else:
        # Edges have to be appended in both directions for undirected graphs
        if labeled:
            edges.append(EDGE(edge_id, start_and_end, random_string()))
            edges.append(EDGE(edge_id, [start_and_end[1], start_and_end[0]], random_string()))
            edge_id += 1
        else:
            edges.append(EDGE(edge_id, start_and_end, ""))
            edges.append(EDGE(edge_id, [start_and_end[1], start_and_end[0]], ""))
            edge_id += 1
    return edges, edge_id


def add_EDGE_to_set(edges: List[EDGE], edge_id, start_and_end, directed=False, labeled=False):
    """Appends a new EDGE with a given EDGE-ID start-and-end-Vertex-ID to a given set of EDGE"""
    if directed:
        if labeled:
            edges.add(EDGE(edge_id, start_and_end, random_string()))
        else:
            edges.add(EDGE(edge_id, start_and_end, ""))
    else:
        if labeled:
            # Edges have to be appended in both directions for undirected graphs
            edges.add(EDGE(edge_id, start_and_end, random_string()))
            edges.add(EDGE(edge_id, [start_and_end[1], start_and_end[0]], random_string()))
        else:
            # print("____SET APPEND___")
            tmp_edge = EDGE(edge_id, start_and_end, "")
            inv_edge = EDGE(edge_id, [start_and_end[1], start_and_end[0]], "")
            # print("tmp_edge, id, (start, end): %s\t(%s,%s)" %
            #       (tmp_edge.get_id(), tmp_edge.get_start_and_end()[0], tmp_edge.get_start_and_end()[1] ))
            # print("inv_edge, id, (start, end): %s\t(%s,%s)" %
            #       (inv_edge.get_id(), inv_edge.get_start_and_end()[0], inv_edge.get_start_and_end()[1]))
            edges.add(tmp_edge)
            edges.add(inv_edge)
    return edges

def get_VERTEX_with_ID(list_vertices: List[VERTEX], vertex_id):
    for vertex_obj in list_vertices:
        if vertex_obj.get_id() == vertex_id:
            return vertex_obj
