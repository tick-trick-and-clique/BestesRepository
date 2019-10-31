#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from runpy import run_path
from Graph import GRAPH
from Vertex import VERTEX
from Edge import EDGE


def import_file(filename, function_name):   # FIXME: evtl import von GRAPH oder so
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

def create_new_vertex(new_dict_of_vertices, actual_i, actual_k, cut,
                      vertex_g1, index_vert_g1, label_list_vert_g1, len_g1,
                      vertex_g2, index_vert_g2, label_list_vert_g2, len_g2):
    #print("got in there!!!")
    union_label_set = set(label_list_vert_g1).union(set(label_list_vert_g2))
    vertex_label_combined = ""
    for label in union_label_set:
        vertex_label_combined += label + "#"
    if vertex_label_combined.endswith("#"):
        vertex_label_combined = vertex_label_combined[:-1]

    if not cut or (cut and index_vert_g1 < actual_i and index_vert_g2 < actual_k):
        #print("case 1")
        vertex_key = index_vert_g1 + index_vert_g2 * (len_g1)
    elif cut and index_vert_g1 >= actual_i and index_vert_g2 < actual_k:
        #print("case 2")
        vertex_key = index_vert_g1 + 1 + index_vert_g2 * (len_g1 )
    elif cut and index_vert_g1 < actual_i and index_vert_g2 >= actual_k:
        vertex_key = index_vert_g1 + (index_vert_g2 + 1) * (len_g1)
        #print("case 3")
    else:
        vertex_key = index_vert_g1 + 1 + (index_vert_g2 + 1) * (len_g1)
        #print("case 4")
    #print("vertex_key", vertex_key)
    if not vertex_key in new_dict_of_vertices:

        v = VERTEX(vertex_key, vertex_label_combined)
        v.combine_mapping(vertex_g1)
        v.combine_mapping(vertex_g2)
        #print("NEW VERTEX: ", v)
        new_dict_of_vertices[vertex_key] = v



def modular_product(g1, g2, anchor_graph_parameters=None,
                    vertex_comparison_import_para=None, edge_comparison_import_para=None):
    """
    NOTE: For this function to work, each VERTEX of the input graphs needs to carry at least his own ID as mapping
    in the mapping attribute!
    Return Type: GRAPH
    """
    # Import Label-Comparison function
    vertex_comparison_function = None
    edge_comparison_function = None
    if isinstance(vertex_comparison_import_para, list):
        vertex_comparison_function = is_identical_label
    if vertex_comparison_import_para:
        vertex_comparison_function = import_file(vertex_comparison_import_para[0], vertex_comparison_import_para[1])
    if isinstance(edge_comparison_import_para, list):
        edge_comparison_function = is_identical_label
    if edge_comparison_import_para:
        edge_comparison_function = import_file(edge_comparison_import_para[0], edge_comparison_import_para[1])

    # Number of vertices is the product of the number of vertices of both graphs
    # new_number_of_vertices = g1.get_number_of_vertices() * g2.get_number_of_vertices()
    # Initialize all vertices of the modular product. For now, a
    # default label is passed. A mapping for each vertex is updated, serving as reference to the input vertices
    # including the mapping of those input vertices.
    anchor = []
    new_dict_of_vertices = {}
    g1_vertices = g1.get_list_of_vertices()
    g2_vertices = g2.get_list_of_vertices()
    g1_len = len(g1_vertices)
    g2_len = len(g2_vertices)
    g1_edges = g1.get_list_of_edges()
    g2_edges = g2.get_list_of_edges()
    new_list_of_edges = []
    new_number_of_edges = 0
    edge_id = 1

    for i, v1 in enumerate(g1_vertices):
        g1_cut = g1_vertices.copy()
        g1_cut.remove(v1)
        for j, v2 in enumerate(g1_cut):
            for k, v3 in enumerate(g2_vertices):
                g2_cut = g2_vertices.copy()
                g2_cut.remove(v3)
                for l, v4 in enumerate(g2_cut):
                    # If, for both graphs, a two-element list is identical, add an edge. The elements in this list
                    # correspond to booleans that are evaluated from ID check of vertex 1 with the IDs of the neighbours
                    # attribute of vertex 2 and vice versa.

                    #print("---------v1 ", i, v1, "v2 ", j, v2, "v3 ", k, v3, "v4 ", l, v4)
                    neighbours_in_g1 = [v1.get_id() in [vertex.get_id() for vertex in v2.get_out_neighbours()],
                                        v2.get_id() in [vertex.get_id() for vertex in v1.get_out_neighbours()]]
                    neighbours_in_g2 = [v3.get_id() in [vertex.get_id() for vertex in v4.get_out_neighbours()],
                                        v4.get_id() in [vertex.get_id() for vertex in v3.get_out_neighbours()]]

                    # Check vertex-label-compatibility using imported function or Default is_identical
                    vertex_label_compatibility_v1v3 = True
                    vertex_label_compatibility_v2v4 = True
                    label_list_v1, label_list_v2 = v1.get_label().split("#"), v2.get_label().split("#")
                    label_list_v3, label_list_v4 = v3.get_label().split("#"), v4.get_label().split("#")
                    if vertex_comparison_function:
                        # Check vertex-compatibility for pair v1v3
                        for label_v1 in label_list_v1:
                            for label_v3 in label_list_v3:
                                if not vertex_comparison_function(label_v1, label_v3):
                                    vertex_label_compatibility_v1v3 = False
                                    break
                            if not vertex_label_compatibility_v1v3:
                                break
                        #print("vertex_label_compatibility_v1v3", vertex_label_compatibility_v1v3)

                        # Check vertex-compatibility for pair v2v4
                        for label_v2 in label_list_v2:
                            for label_v4 in label_list_v4:
                                if not vertex_comparison_function(label_v2, label_v4):
                                    vertex_label_compatibility_v2v4 = False
                                    break
                            if not vertex_label_compatibility_v2v4:
                                break
                        #print("vertex_label_compatibility_v2v4", vertex_label_compatibility_v2v4)

                    if vertex_label_compatibility_v1v3:
                        #print("Try to create combination v1v3")
                        create_new_vertex(new_dict_of_vertices, i, k, False,
                                          v1, i, label_list_v1, g1_len,
                                          v3, k, label_list_v3, g2_len)

                    if vertex_label_compatibility_v2v4:
                        #print("Try to create combination v2v4")
                        create_new_vertex(new_dict_of_vertices, i, k, True,
                                          v2, j, label_list_v2, g1_len,
                                          v4, l, label_list_v4, g2_len)

                    vertex_label_compatibility = vertex_label_compatibility_v1v3 and vertex_label_compatibility_v2v4

                    # Conditions for an edge
                    if neighbours_in_g1 == neighbours_in_g2 and vertex_label_compatibility:
                        #print("conditions for an Edge are met!")
                        edge_label_combined = "Default"

                        # Find "Forward" Edges
                        union_edge_label_set_forward = set()
                        edge_label_compatibility_forward = True # Default
                        if neighbours_in_g1[1] and neighbours_in_g2[1]:  # There is a forward Edge ...
                            #print("There is an forward edge v1v2 and v3v4")
                            edge_g1_forward = [edge for edge in g1_edges if edge.get_start_and_end()[0] == v1 and \
                                               edge.get_start_and_end()[1] == v2][0]
                            edge_g2_forward = [edge for edge in g2_edges if edge.get_start_and_end()[0] == v3 and \
                                               edge.get_start_and_end()[1] == v4][0]
                            # Combine "Forward" labels
                            label_list_edge_g1_forward = edge_g1_forward.get_label().split("#")
                            label_list_edge_g2_forward = edge_g2_forward.get_label().split("#")
                            union_edge_label_set_forward = set(label_list_edge_g1_forward).union(
                                set(label_list_edge_g2_forward))

                        # Find "Backward" Edges
                        union_edge_label_set_backward = set()
                        edge_label_compatibility_backward = True
                        if neighbours_in_g1[0] and neighbours_in_g2[0]: # There is a backward Edge ...
                            edge_g1_backward = [edge for edge in g1_edges if edge.get_start_and_end()[1] == v1 and \
                                                edge.get_start_and_end()[0] == v2][0]
                            edge_g2_backward = [edge for edge in g2_edges if edge.get_start_and_end()[1] == v3 and \
                                                edge.get_start_and_end()[0] == v4][0]

                            # Combine "Backward" labels
                            label_list_edge_g1_backward = edge_g1_backward.get_label().split("#")
                            label_list_edge_g2_backward = edge_g2_backward.get_label().split("#")
                            union_edge_label_set_backward = set(label_list_edge_g1_backward).union(
                                set(label_list_edge_g2_backward))

                        # Check "Forward" edge-label compatibility
                        if edge_comparison_function and neighbours_in_g1[1] and neighbours_in_g2[1]:
                            for label_g1 in label_list_edge_g1_forward:
                                for label_g2 in label_list_edge_g2_forward:
                                    if not edge_comparison_function(label_g1, label_g2):
                                        edge_label_compatibility_forward = False
                                        break
                                if not edge_label_compatibility_forward:
                                    break

                        # Check "Backward" edge-label compatibility
                        if edge_comparison_function and neighbours_in_g1[0] and neighbours_in_g2[0]:
                            for label_g1 in label_list_edge_g1_backward:
                                for label_g2 in label_list_edge_g2_backward:
                                    if not edge_comparison_function(label_g1, label_g2):
                                        edge_label_compatibility_backward = False
                                        break
                                if not edge_label_compatibility_backward:
                                    break

                        # Check overall edge_label_compatibility
                        if edge_label_compatibility_forward and edge_label_compatibility_backward:
                            pass
                        else:
                            continue

                        # Combine edge-labels of forward and backward edges
                        if union_edge_label_set_forward or union_edge_label_set_backward:
                            union_edge_label_set = union_edge_label_set_forward.union(
                                union_edge_label_set_backward)
                            edge_label_combined = ""
                            for label in union_edge_label_set:
                                # print("label aus union_edge_label_set", label)
                                edge_label_combined += label + "#"
                            if edge_label_combined.endswith("#"):
                                edge_label_combined = edge_label_combined[:-1]

                    else:   # if conditions for an edge are not met
                        continue

                    # Pick right vertex from new_list_of_vertices to form edges
                    start_vertex = None
                    end_vertex = None
                    for new_v in new_dict_of_vertices.values():
                        if all([va in new_v.get_mapping().values() for va in v1.get_mapping().values()]) and \
                                all([va in new_v.get_mapping().values() for va in v3.get_mapping().values()]):
                            start_vertex = new_v
                        if all([va in new_v.get_mapping().values() for va in v2.get_mapping().values()]) and \
                                all([va in new_v.get_mapping().values() for va in v4.get_mapping().values()]):
                            end_vertex = new_v

                    new_list_of_edges.append(EDGE(edge_id, [start_vertex, end_vertex], edge_label_combined))
                    new_number_of_edges += 1
                    edge_id += 1
                    start_vertex.append_out_neighbour(end_vertex)

    if anchor_graph_parameters:
        for v_mp in new_dict_of_vertices.values():
            for v_anchor in list(anchor_graph_parameters[0].get_list_of_vertices()):
                if v_mp.get_mapping()[anchor_graph_parameters[1]].get_id() == v_anchor.get_id():
                    anchor.append(v_mp)
    new_number_of_vertices = len(new_dict_of_vertices.values())

    # The modular product as undirected graph is returned with a default name.
    # Vertex and Edge labels are enabled and combined
    return GRAPH("Modular Product of " + g1.get_name() + " and " + g2.get_name(),
                 list(new_dict_of_vertices.values()), new_list_of_edges, new_number_of_vertices, int(new_number_of_edges / 2),
                 False, is_labeled_edges=bool(isinstance(edge_comparison_import_para, list)),
                 is_labeled_nodes=bool(isinstance(vertex_comparison_import_para, list))), anchor
