#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from runpy import run_path
from Graph import GRAPH
# from Main import import_file # hat irgendwie nicht geklappt, hab die Funktion jetzt hier reinkopiert
from Vertex import VERTEX
from Edge import EDGE


def import_file(filename, function_name):
    if not os.path.isdir(os.path.dirname(filename)) and not os.path.exists(filename):
        raise Exception("No such file with given path or filename!")
    if not os.path.isdir(os.path.dirname(filename)):
        file_path = os.path.abspath(filename)
    # else:
    #    file_path = args.input # FIXME: DO I need this?!
    settings = run_path(file_path)
    f = settings[function_name]
    return f




def modular_product(g1, g2, anchor_graph_parameters=None,
                    vertex_comparison_import_para=None, edge_comparison_import_para=None):
    """
    NOTE: For this function to work, each VERTEX of the input graphs needs to carry at least his own ID as mapping
    in the mapping attribute!
    Return Type: GRAPH
    """
    # Number of vertices is the product of the number of vertices of both graphs
    new_number_of_vertices = g1.get_number_of_vertices() * g2.get_number_of_vertices()
    # Initialize all vertices of the modular product. For now, a
    # default label is passed. A mapping for each vertex is updated, serving as reference to the input vertices
    # including the mapping of those input vertices.
    anchor = []
    new_list_of_vertices = []
    g1_vertices = g1.get_list_of_vertices()
    g2_vertices = g2.get_list_of_vertices()
    g1_edges = g1.get_list_of_edges()
    g2_edges = g2.get_list_of_edges()

    for i, vertex_g1 in enumerate(g1_vertices):
        for j, vertex_g2 in enumerate(g2_vertices):
            vertex_label_combined = None
            if vertex_g1.get_label() == vertex_g2.get_label():
                vertex_label_combined = vertex_g1.get_label()
            else:
                label_list_vert_g1 = vertex_g1.get_label().split("#")
                label_list_vert_g2 = vertex_g2.get_label().split("#")
                union_label_set = set(label_list_vert_g1).union(set(label_list_vert_g2))
                vertex_label_combined = ""
                for label in union_label_set:
                    vertex_label_combined += label + "#"
                if vertex_label_combined.endswith("#"):
                    vertex_label_combined = vertex_label_combined[:-1]
            v = VERTEX(i + j * g1.get_number_of_vertices(), vertex_label_combined)
            v.combine_mapping(vertex_g1)
            v.combine_mapping(vertex_g2)
            new_list_of_vertices.append(v)

    if anchor_graph_parameters:
        for v_mp in new_list_of_vertices:
            for v_anchor in anchor_graph_parameters[0].get_list_of_vertices():
                if v_mp.get_mapping()[anchor_graph_parameters[1]].get_id() == v_anchor.get_id():
                    anchor.append(v_mp)
    # Initialize an empty list of edges and an edge counter.
    # Iterate over all pairs of vertices (twice --> both directions) for both graphs.
    # Skip cases where vertices are identical.
    new_list_of_edges = []
    new_number_of_edges = 0
    edge_id = 1

    # Import Label-Comparison function
    if vertex_comparison_import_para:
        vertex_comparison_function = import_file(vertex_comparison_import_para[0], vertex_comparison_import_para[1])
    if edge_comparison_import_para:
        edge_comparison_function = import_file(edge_comparison_import_para[0], edge_comparison_import_para[1])
    for v1 in g1_vertices:
        g1_cut = g1_vertices.copy()
        g1_cut.remove(v1)
        for v2 in g1_cut:
            for v3 in g2_vertices:
                g2_cut = g2_vertices.copy()
                g2_cut.remove(v3)
                for v4 in g2_cut:
                    # If, for both graphs, a two-element list is identical, add an edge. The elements in this list
                    # correspond to booleans that are evaluated from ID check of vertex 1 with the IDs of the neighbours
                    # attribute of vertex 2 and vice versa.
                    neighbours_in_g1 = [v1.get_id() in [vertex.get_id() for vertex in v2.get_out_neighbours()],
                                        v2.get_id() in [vertex.get_id() for vertex in v1.get_out_neighbours()]]
                    neighbours_in_g2 = [v3.get_id() in [vertex.get_id() for vertex in v4.get_out_neighbours()],
                                        v4.get_id() in [vertex.get_id() for vertex in v3.get_out_neighbours()]]
                    # Check vertex-label-compatibility using imported function
                    vertex_label_compatibility = True   # Default
                    if vertex_comparison_import_para:
                        label_list_v1, label_list_v2 = v1.get_label().split("#"), v2.get_label().split("#")
                        label_list_v3, label_list_v4 = v3.get_label().split("#"), v4.get_label().split("#")

                        for label_v1 in label_list_v1:
                            for label_v3 in label_list_v3:
                                if not vertex_comparison_function(label_v1, label_v3):
                                    vertex_label_compatibility = False
                                    break
                            if not vertex_label_compatibility:
                                break

                        if vertex_label_compatibility:
                            for label_v2 in label_list_v2:
                                for label_v4 in label_list_v4:
                                    if not vertex_comparison_function(label_v2, label_v4):
                                        vertex_label_compatibility = False
                                        break
                                if not vertex_label_compatibility:
                                    break

                    # Conditions for an edge
                    if neighbours_in_g1 == neighbours_in_g2 and vertex_label_compatibility:

                        edge_label_combined = "Default"
                        # if there is an edge-label-comparison function provided
                        if edge_comparison_import_para:
                            # Get Edges
                            edge_g1_forward = None
                            edge_g2_forward = None
                            edge_g1_backward = None
                            edge_g2_backward = None

                            # Find "Forward" Edges
                            union_edge_label_set_forward = set()
                            edge_label_compatibility_forward = True
                            if neighbours_in_g1[1] and neighbours_in_g2[1]: # Forward Edges
                                edge_g1_forward = [edge for edge in g1_edges if edge.get_start_and_end()[0] == v1 and \
                                           edge.get_start_and_end()[1] == v2][0]
                                edge_g2_forward = [edge for edge in g2_edges if edge.get_start_and_end()[0] == v3 and \
                                           edge.get_start_and_end()[1] == v4][0]
                                # Combine "Forward" labels
                                label_list_edge_g1_forward = edge_g1_forward.get_label().split("#")
                                label_list_edge_g2_forward = edge_g2_forward.get_label().split("#")
                                union_edge_label_set_forward = set(label_list_edge_g1_forward).union(
                                    set(label_list_edge_g2_forward))

                                # Check "Forward" edge-label compatibility
                                for label_g1 in label_list_edge_g1_forward:
                                    for label_g2 in label_list_edge_g2_forward:
                                        if not edge_comparison_function(label_g1, label_g2):
                                            edge_label_compatibility_forward = False
                                            continue

                            # Find "Backward" Edges
                            union_edge_label_set_backward = set()
                            edge_label_compatibility_backward = True
                            if neighbours_in_g1[0] and neighbours_in_g2[0]:
                                edge_g1_backward = [edge for edge in g1_edges if edge.get_start_and_end()[1] == v1 and \
                                                   edge.get_start_and_end()[0] == v2][0]
                                edge_g2_backward = [edge for edge in g2_edges if edge.get_start_and_end()[1] == v3 and \
                                                   edge.get_start_and_end()[0] == v4][0]

                                # Combine "Backward" labels
                                label_list_edge_g1_backward = edge_g1_backward.get_label().split("#")
                                label_list_edge_g2_backward = edge_g2_backward.get_label().split("#")
                                union_edge_label_set_backward = set(label_list_edge_g1_backward).union(
                                    set(label_list_edge_g2_backward))

                                # Check "Backward" edge-label compatibility
                                for label_g1 in label_list_edge_g1_backward:
                                    for label_g2 in label_list_edge_g2_backward:
                                        if not edge_comparison_function(label_g1, label_g2):
                                            edge_label_compatibility_backward = False
                                            continue
                                        else:
                                            pass
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
                                    print("label aus union_edge_label_set", label)
                                    edge_label_combined += label + "#"
                                if edge_label_combined.endswith("#"):
                                    edge_label_combined = edge_label_combined[:-1]

                        # Pick right vertex from new_list_of_vertices to form edges
                        start_vertex = None
                        end_vertex = None
                        for new_v in new_list_of_vertices:
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
    # The modular product as undirected graph is returned with a default name.
    # Vertex and Edge labels are enabled, yet set to a default value for the moment, same as the edge id.
    return GRAPH("Modular Product of " + g1.get_name() + " and " + g2.get_name(),
                 new_list_of_vertices, new_list_of_edges, new_number_of_vertices, int(new_number_of_edges / 2),
                 False, is_labeled_edges=True, is_labeled_nodes=True), anchor
