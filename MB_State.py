#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This class implements a so called 'state' like described for the
matching-based algorithm by Cordella et al.
"""
import os
from runpy import run_path


def import_file(filename, function_name):
    if not os.path.isdir(os.path.dirname(filename)) and not os.path.exists(filename):
        raise Exception("No such file with given path or filename!")
    if not os.path.isdir(os.path.dirname(filename)):
        file_path = os.path.abspath(filename)
    else:
        file_path = filename
    settings = run_path(file_path)
    f = settings[function_name]
    return f


def is_identical_label(label, other_label):
    return label == other_label


class MB_State:

    # NOTE: core_1 and core_2 are supposed to be dictionaries with integers keys and VERTEX type values here
    # while the other four data structures hold integer type values.

    def __init__(self, g1, g2, vertex_comparison_import_para=None, edge_comparison_import_para=None, subsub=False):
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
        #self.gv1 = sorted(gv1, key=lambda x: self.graph1.get_cardinality_of_vertex(x))
        self.gv1 = gv1
        for i in range(len(gv1)):
            self.core_1[i] = None
            self.in_1[i] = 0
            self.out_1[i] = 0
        gv2 = self.graph2.get_list_of_vertices()
        #self.gv2 = sorted(gv2, key=lambda x: self.graph2.get_cardinality_of_vertex(x))
        self.gv2 = gv2
        for i in range(len(gv2)):
            self.core_2[i] = None
            self.in_2[i] = 0
            self.out_2[i] = 0
        self.core_len = 0
        self.both_1_len = 0
        self.both_2_len = 0
        self.in_1_len = 0
        self.in_2_len = 0
        self.out_1_len = 0
        self.out_2_len = 0
        self.max_matching_length = 0
        self.subsub = subsub
        self.vertex_comparison_function = None
        self.edge_comparison_function = None
        if isinstance(vertex_comparison_import_para, list):
            self.vertex_comparison_function = is_identical_label
        if isinstance(edge_comparison_import_para, list):
            self.edge_comparison_function = is_identical_label
        if vertex_comparison_import_para:
            self.vertex_comparison_function = import_file(vertex_comparison_import_para[0],
                                                          vertex_comparison_import_para[1])
        if edge_comparison_import_para:
            self.edge_comparison_function = import_file(edge_comparison_import_para[0],
                                                        edge_comparison_import_para[1])

    def mb_algorithm(self, previously_added=None):
        result_as_mapping_dict = {}
        result_as_mapping_list = []
        if self.all_vertices_of_g2_covered():
            for key, value in self.core_1.items():
                if value:
                    result_as_mapping_dict[self.gv1[key].get_id()] = value.get_id()
            self.restore_data_structures(previously_added)
            self.max_matching_length = len(result_as_mapping_dict.items())
            return [result_as_mapping_dict]
        else:
            p = self.compute_candidates()
            added = False
            for candidate in p:
                if self.is_feasible(candidate):
                    self.add_pair(candidate)
                    added = True
                    result_as_mapping_list += self.mb_algorithm(previously_added=candidate)
            if self.subsub:
                if not added:
                    for key, value in self.core_1.items():
                        if value:
                            result_as_mapping_dict[self.gv1[key].get_id()] = value.get_id()
                    self.restore_data_structures(previously_added)
                    if len(result_as_mapping_dict.items()) >= self.max_matching_length:
                        self.max_matching_length = len(result_as_mapping_dict.items())
                        return [result_as_mapping_dict]
                    else:
                        return []
                else:
                    self.restore_data_structures(previously_added)
                    result_as_mapping_list = [i for i in result_as_mapping_list if len(i) >= self.max_matching_length]
                    return result_as_mapping_list
            else:
                self.restore_data_structures(previously_added)
                result_as_mapping_list = [i for i in result_as_mapping_list if len(i) >= self.max_matching_length]
                return result_as_mapping_list

    def all_vertices_of_g2_covered(self):
        return self.vCount2 == self.core_len

    def compute_candidates(self):
        # Functions returns a set of index tuples corresponding to potential vertex matchings between the two graphs
        if self.out_1_len and self.out_2_len:
            if self.subsub:
                p = set()
                for key1 in self.out_1:
                    for key2 in self.out_2:
                        if self.out_1[key1] and self.out_2[key2] and not self.core_1[key1] and not self.core_2[key2]:
                            p.add((key1, key2))
            else:
                v2 = min([key for key in self.out_2.keys() if self.out_2[key] and not self.core_2[key]])
                p = {(key, v2) for key in self.out_1.keys() if not self.core_1[key]}
        elif self.in_1_len and self.in_2_len:
            if self.subsub:
                p = set()
                for key1 in self.in_1:
                    for key2 in self.in_2:
                        if self.in_1[key1] and self.in_2[key2] and not self.core_1[key1] and not self.core_2[key2]:
                            p.add((key1, key2))
            else:
                v2 = min([key for key in self.in_2.keys() if self.in_2[key] and not self.core_2[key]])
                p = {(key, v2) for key in self.in_1.keys() if not self.core_1[key]}
        elif not self.both_1_len and not self.both_2_len and not self.subsub:
            g1_set = {key for key in self.core_1.keys() if not self.core_1[key]}
            v2 = min({key for key in self.core_2.keys() if not self.core_2[key]})
            p = {(v1, v2) for v1 in g1_set}
        elif not self.both_1_len and not self.both_2_len and self.subsub:
            g1_set = {key for key in self.core_1.keys() if not self.core_1[key]}
            g2_set = {key for key in self.core_2.keys() if not self.core_2[key]}
            p = set()
            for v1 in g1_set:
                for v2 in g2_set:
                    p.add((v1, v2))
        else:
            p = {}
        return p

    def is_feasible(self, candidate):
        """Function returns whether the candidate pair of vertex indices (n, m) is feasible.
        Therefore, it is checked whether:
            - Vertices are compatible (evaluating the label)
            - Edges from and into the space of already matched vertices correspond and edge are compatible (evaluating
            the label, if wanted)
            - The number of vertices from out and in edges, where vertices are not in the space of already matched
            vertices but have edges from or into the space, are equal
            - The number of vertices from out and in edges, where vertices are not in the space of already matched
            vertices and also do not have edges from or into the space, are equal
        NOTE: Compatibility checks are symmetric, non-symmetric vertex/edge compatibilies are not supported!"""

        g1_vertex_index, g2_vertex_index = candidate
        g1_vertex = self.gv1[g1_vertex_index]
        g2_vertex = self.gv2[g2_vertex_index]

        if self.vertex_comparison_function:
            if not self.vertex_comparison_function(g1_vertex.get_label(), g2_vertex.get_label()):
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
            other_v_in_g1_index = self.gv1.index(other_v_in_g1)
            if self.core_1[other_v_in_g1_index] is not None:
                other_v_in_g2 = self.core_1[other_v_in_g1_index]
                if not self.graph2.has_edge(g2_vertex, other_v_in_g2) \
                        or (self.edge_comparison_function and not
                            self.edge_comparison_function(edge.get_label(),
                                                          self.graph2.get_edge(g2_vertex, other_v_in_g2).get_label())):
                    return False
            else:
                if self.in_1[other_v_in_g1_index] > 0:
                    temp_in1 += 1
                if self.out_1[other_v_in_g1_index] > 0:
                    temp_out1 += 1
                if self.in_1[other_v_in_g1_index] == 0 and \
                        self.out_1[other_v_in_g1_index] == 0:
                    temp_new1 += 1

        # Check 'in' edges of g1_vertex
        for edge in self.graph1.get_in_edge_list(g1_vertex):
            other_v_in_g1 = edge.get_start_and_end()[0]
            other_v_in_g1_index = self.gv1.index(other_v_in_g1)
            if self.core_1[other_v_in_g1_index] is not None:
                other_v_in_g2 = self.core_1[other_v_in_g1_index]
                if not self.graph2.has_edge(other_v_in_g2, g2_vertex) \
                        or (self.edge_comparison_function and not
                            self.edge_comparison_function(edge.get_label(),
                                                          self.graph2.get_edge(other_v_in_g2, g2_vertex).get_label())):
                    return False
            else:
                if self.in_1[other_v_in_g1_index] > 0:
                    temp_in1 += 1
                if self.out_1[other_v_in_g1_index] > 0:
                    temp_out1 += 1
                if self.in_1[other_v_in_g1_index] == 0 and \
                        self.out_1[other_v_in_g1_index] == 0:
                    temp_new1 += 1

        # Check 'out' edges of g2_vertex
        for edge in self.graph2.get_out_edge_list(g2_vertex):
            other_v_in_g2 = edge.get_start_and_end()[1]
            other_v_in_g2_index = self.gv2.index(other_v_in_g2)
            if self.core_2[other_v_in_g2_index] is not None:
                other_v_in_g1 = self.core_2[other_v_in_g2_index]
                if not self.graph1.has_edge(g1_vertex, other_v_in_g1) \
                        or (self.edge_comparison_function and not
                            self.edge_comparison_function(edge.get_label(),
                                                          self.graph1.get_edge(g1_vertex, other_v_in_g1).get_label())):
                    return False
            else:
                if self.in_2[other_v_in_g2_index] > 0:
                    temp_in2 += 1
                if self.out_2[other_v_in_g2_index] > 0:
                    temp_out2 += 1
                if self.in_2[other_v_in_g2_index] == 0 and \
                        self.out_2[other_v_in_g2_index] == 0:
                    temp_new2 += 1

        # Check 'in' edges of g2_vertex
        for edge in self.graph2.get_in_edge_list(g2_vertex):
            other_v_in_g2 = edge.get_start_and_end()[0]
            other_v_in_g2_index = self.gv2.index(other_v_in_g2)
            if self.core_2[other_v_in_g2_index] is not None:
                other_v_in_g1 = self.core_2[other_v_in_g2_index]
                if not self.graph1.has_edge(other_v_in_g1, g1_vertex) \
                        or (self.edge_comparison_function and not
                            self.edge_comparison_function(edge.get_label(),
                                                          self.graph1.get_edge(other_v_in_g1, g1_vertex).get_label())):
                    return False
            else:
                if self.in_2[other_v_in_g2_index] > 0:
                    temp_in2 += 1
                if self.out_2[other_v_in_g2_index] > 0:
                    temp_out2 += 1
                if self.in_2[other_v_in_g2_index] == 0 and \
                        self.out_2[other_v_in_g2_index] == 0:
                    temp_new2 += 1
        if self.subsub:
            return True
        else:
            return temp_in1 >= temp_in2 and temp_out1 >= temp_out2 and temp_new1 >= temp_new2

    def add_pair(self, candidate):
        # Function updates data structures according to the new pair of vertices to be added to the matching
        self.core_len += 1
        g1_vertex_index, g2_vertex_index = candidate
        g1_vertex = self.gv1[g1_vertex_index]
        g2_vertex = self.gv2[g2_vertex_index]
        self.core_1[g1_vertex_index] = g2_vertex
        self.core_2[g2_vertex_index] = g1_vertex
        for edge in self.graph1.get_out_edge_list(g1_vertex):
            other_v = edge.get_start_and_end()[1]
            other_v_index = self.gv1.index(other_v)
            if not self.out_1[other_v_index]:
                self.out_1[other_v_index] = self.core_len
                self.out_1_len += 1
                self.both_1_len += 1
        for edge in self.graph1.get_in_edge_list(g1_vertex):
            other_v = edge.get_start_and_end()[0]
            other_v_index = self.gv1.index(other_v)
            if not self.in_1[other_v_index]:
                self.in_1[other_v_index] = self.core_len
                self.in_1_len += 1
                self.both_1_len += 1
        for edge in self.graph2.get_out_edge_list(g2_vertex):
            other_v = edge.get_start_and_end()[1]
            other_v_index = self.gv2.index(other_v)
            if not self.out_2[other_v_index]:
                self.out_2[other_v_index] = self.core_len
                self.out_2_len += 1
                self.both_2_len += 1
        for edge in self.graph2.get_in_edge_list(g2_vertex):
            other_v = edge.get_start_and_end()[0]
            other_v_index = self.gv2.index(other_v)
            if not self.in_2[other_v_index]:
                self.in_2[other_v_index] = self.core_len
                self.in_2_len += 1
                self.both_2_len += 1
        return

    def restore_data_structures(self, previously_added):
        # Function updates shared data structures according to the current core_len and the previously added vertex
        # matching pair
        if previously_added:
            for key, value in self.out_1.items():
                if value == self.core_len:
                    self.out_1[key] = 0
                    self.out_1_len -= 1
                    self.both_1_len -= 1
            for key, value in self.in_1.items():
                if value == self.core_len:
                    self.in_1[key] = 0
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
