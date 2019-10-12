#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Edge import EDGE
from Vertex import VERTEX
"""
This class implements a so called 'state' like described for the
matching-based algorithm by Cordella et al.
"""


class MB_State:

    # DEV NOTE: core_1 and core_2 are supposed to be dictionaries with integers keys and VERTEX type values here
    # while the other four data structures hold integer type values.

    def __init__(self, g1, g2, sortVertices=False):
        self.graph1 = g1
        self.graph2 = g2
        self.core_1 = {}
        self.core_2 = {}
        self.in_1 = {}
        self.in_2 = {}
        self.out_1 = {}
        self.out_2 = {}
        self.vCount1 = g1.get_number_of_vertices()
        self.vCount2 = g2.get_number_of_vertices()
        gv1 = self.graph1.get_list_of_vertices()
        gv1 = sorted(gv1, key=lambda x: self.graph1.get_cardinality_of_vertex(x))
        for v in gv1:
            id = v.get_id()
            self.core_1[id] = None
            self.in_1[id] = 0
            self.out_1[id] = 0
        gv2 = self.graph2.get_list_of_vertices()
        gv2 = sorted(gv2, key=lambda x: self.graph2.get_cardinality_of_vertex(x))
        for v in gv2:
            id = v.get_id()
            self.core_2[id] = None
            self.in_2[id] = 0
            self.out_2[id] = 0
        self.core_len = 0
        self.both_1_len = 0
        self.both_2_len = 0
        self.in_1_len = 0
        self.in_2_len = 0
        self.out_1_len = 0
        self.out_2_len = 0

    def mb_algorithm(self, previously_added=None):
        result_as_mapping_dict = {}
        result_as_mapping_list = []
        if self.all_vertices_of_g2_covered():
            #print("Result:")
            #print("IDs of Vertices")
            #print("Graph 1  Graph2")
            for key, value in self.core_1.items():
                if value:
             #       print(key, value.get_id(), sep="\t")
                    result_as_mapping_dict[key] = value.get_id()
            #type(print("\n")
            self.restore_data_structures(previously_added)
            return [result_as_mapping_dict]
        else:
            p = self.compute_candidates()
            for candidate in p:
                if self.is_feasible(candidate):
                    self.add_pair(candidate)
                    result_as_mapping_list += self.mb_algorithm(previously_added=candidate)
            self.restore_data_structures(previously_added)
            return result_as_mapping_list

    def all_vertices_of_g2_covered(self):
        return self.vCount2 == self.core_len

    def compute_candidates(self):
        # Functions returns a set of index tuples corresponding to potential vertex matchings between the two graphs

        if self.out_1_len and self.out_2_len:
            v2 = min([key for key in self.out_2.keys() if not self.core_2[key]])
            p = {(key, v2) for key in self.out_1.keys() if not self.core_1[key]}
        elif self.in_1_len and self.in_2_len:
            v2 = min([key for key in self.in_2.keys() if not self.core_2[key]])
            p = {(key, v2) for key in self.in_1.keys() if not self.core_1[key]}
        elif not self.both_1_len and not self.both_2_len:
            g1_set = {key for key in self.core_1.keys() if not self.core_1[key]}
            v2 = min({key for key in self.core_2.keys() if not self.core_2[key]})
            p = {(v1, v2) for v1 in g1_set}
        else:
            p = {}
        return p

    def is_feasible(self, candidate):
        """Function returns whether the candidate pair of vertex indices (n, m) is feasible.
        Therefore, it is checked whether:
            - Vertices are compatible (evaluating the label)
            - Edges from and into the space of already matched vertices correspond and edge are compatible (evaluating
            the label)
            - The number of vertices from out and in edges, where vertices are not in the space of already matched
            vertices but have edges from or into the space, are equal
            - The number of vertices from out and in edges, where vertices are not in the space of already matched
            vertices and also do not have edges from or into the space, are equal
        CAUTION: Compatibility checks are ONLY performed from Graph 1 to Graph 2 for non-symmetric compatibility
        reasons!"""

        # DEV NOTE: EDGE label is interpreted as the edge compatibility attribute here

        g1_vertex_index, g2_vertex_index = candidate
        g1_vertex = [v for v in self.graph1.get_list_of_vertices() if g1_vertex_index == v.get_id()][0]
        g2_vertex = [v for v in self.graph2.get_list_of_vertices() if g2_vertex_index == v.get_id()][0]

        if not g1_vertex.is_compatible_vertex(g2_vertex):
            return False

        temp_out1 = 0
        temp_out2 = 0
        temp_in1 = 0
        temp_in2 = 0
        temp_new1 = 0
        temp_new2 = 0

        # Check 'out' edges of g1_vertex
        for edge in self.graph1.get_out_edge_list(g1_vertex):
            other_v_in_g1 = edge.get_start_and_end()[1]
            if self.core_1[other_v_in_g1.get_id()] is not None:
                other_v_in_g2 = self.core_1[other_v_in_g1.get_id()]
                if not self.graph2.has_edge(g2_vertex, other_v_in_g2) or \
                        not edge.is_compatible_edge(self.graph2.get_edge(g2_vertex, other_v_in_g2)):
                    return False
            else:
                if self.in_1[other_v_in_g1.get_id()] > 0:
                    temp_in1 += temp_in1
                if self.out_1[other_v_in_g1.get_id()] > 0:
                    temp_out1 += temp_out1
                if self.in_1[other_v_in_g1.get_id()] == 0 and \
                        self.out_1[other_v_in_g1.get_id()] == 0:
                    temp_new1 += temp_new1

        # Check 'in' edges of g1_vertex
        for edge in self.graph1.get_in_edge_list(g1_vertex):
            other_v_in_g1 = edge.get_start_and_end()[0]
            if self.core_1[other_v_in_g1.get_id()] is not None:
                other_v_in_g2 = self.core_1[other_v_in_g1.get_id()]
                if not self.graph2.has_edge(other_v_in_g2, g2_vertex) or \
                        not edge.is_compatible_edge(self.graph2.get_edge(other_v_in_g2, g2_vertex)):
                    return False
            else:
                if self.in_1[other_v_in_g1.get_id()] > 0:
                    temp_in1 += temp_in1
                if self.out_1[other_v_in_g1.get_id()] > 0:
                    temp_out1 += temp_out1
                if self.in_1[other_v_in_g1.get_id()] == 0 and \
                        self.out_1[other_v_in_g1.get_id()] == 0:
                    temp_new1 += temp_new1

        # Check 'out' edges of g2_vertex
        for edge in self.graph2.get_out_edge_list(g2_vertex):
            other_v_in_g2 = edge.get_start_and_end()[1]
            if self.core_2[other_v_in_g2.get_id()] is not None:
                other_v_in_g1 = self.core_2[other_v_in_g2.get_id()]
                if not self.graph1.has_edge(g1_vertex, other_v_in_g1) or \
                        not edge.is_compatible_edge(self.graph1.get_edge(g1_vertex, other_v_in_g1)):
                    return False
            else:
                if self.in_2[other_v_in_g2.get_id()] > 0:
                    temp_in2 += temp_in2
                if self.out_2[other_v_in_g2.get_id()] > 0:
                    temp_out2 += temp_out2
                if self.in_2[other_v_in_g2.get_id()] == 0 and \
                        self.out_2[other_v_in_g2.get_id()] == 0:
                    temp_new2 += temp_new2

        # Check 'in' edges of g2_vertex
        for edge in self.graph2.get_in_edge_list(g2_vertex):
            other_v_in_g2 = edge.get_start_and_end()[0]
            if self.core_2[other_v_in_g2.get_id()] is not None:
                other_v_in_g1 = self.core_2[other_v_in_g2.get_id()]
                if not self.graph1.has_edge(other_v_in_g1, g1_vertex) or \
                        not edge.is_compatible_edge(self.graph1.get_edge(other_v_in_g1, g1_vertex)):
                    return False
            else:
                if self.in_2[other_v_in_g2.get_id()] > 0:
                    temp_in2 += temp_in2
                if self.out_2[other_v_in_g2.get_id()] > 0:
                    temp_out2 += temp_out2
                if self.in_2[other_v_in_g2.get_id()] == 0 and \
                        self.out_2[other_v_in_g2.get_id()] == 0:
                    temp_new2 += temp_new2
        return temp_in1 <= temp_in2 and temp_out1 <= temp_out2 and temp_new1 <= temp_new2

    def add_pair(self, candidate):
        # Function updates data structures according to the new pair of vertices to be added to the matching
        self.core_len += 1
        g1_vertex_index, g2_vertex_index = candidate
        g1_vertex = [v for v in self.graph1.get_list_of_vertices() if g1_vertex_index == v.get_id()][0]
        g2_vertex = [v for v in self.graph2.get_list_of_vertices() if g2_vertex_index == v.get_id()][0]
        self.core_1[g1_vertex_index] = g2_vertex
        self.core_2[g2_vertex_index] = g1_vertex
        for edge in self.graph1.get_out_edge_list(g1_vertex):
            other_v = edge.get_start_and_end()[0]
            if not self.out_1[other_v.get_id()]:
                self.out_1[other_v.get_id()] = self.core_len
                self.out_1_len += 1
                self.both_1_len += 1
        for edge in self.graph1.get_in_edge_list(g1_vertex):
            other_v = edge.get_start_and_end()[0]
            if not self.in_1[other_v.get_id()]:
                self.in_1[other_v.get_id()] = self.core_len
                self.in_1_len += 1
                self.both_1_len += 1
        for edge in self.graph2.get_out_edge_list(g2_vertex):
            other_v = edge.get_start_and_end()[0]
            if not self.out_2[other_v.get_id()]:
                self.out_2[other_v.get_id()] = self.core_len
                self.out_2_len += 1
                self.both_2_len += 1
        for edge in self.graph1.get_in_edge_list(g2_vertex):
            other_v = edge.get_start_and_end()[0]
            if not self.in_2[other_v.get_id()]:
                self.in_2[other_v.get_id()] = self.core_len
                self.in_2_len += 1
                self.both_2_len += 1
        return

    def restore_data_structures(self, previously_added):
        # Function updates shared data structures according to the current core_len and the previously added vertex
        # matching pair
        if previously_added:
            for key, value in self.out_1.items():
                if value == self.core_len:
                    self.in_1[key] = 0
                    self.out_1_len -= 1
                    self.both_1_len -= 1
            for key, value in self.in_1.items():
                if value == self.core_len:
                    self.out_1[key] = 0
                    self.in_1_len -= 1
                    self.both_1_len -= 1
            for key, value in self.out_2.items():
                if value == self.core_len:
                    self.out_2[key] = 0
                    self.out_2_len -= 1
                    self.both_2_len -= 1
            for key, value in self.in_2.items():
                if value == self.core_len:
                    self.in_2[key] = 0
                    self.in_2_len -= 1
                    self.both_2_len -= 1
            self.core_len -= 1
            self.core_1[previously_added[0]] = None
            self.core_2[previously_added[1]] = None
        return

# TODO: Maps durch Listen ersetzen wo möglich, um bessere Performance zu erreichen
# TODO AJ: Der Output ist ziemlich groß, vor allem wenn man Unterkombinationen des kleineren Graphen dazu nimmt.
# Wahrscheinlich wäre es hilfreich, so viel Redundanz wie möglich loszuwerden