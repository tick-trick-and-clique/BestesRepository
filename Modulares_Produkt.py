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
    g1_vn = g1.get_number_of_vertices()
    g2_vn = g2.get_number_of_vertices()

    for i in range(g1_vn):
        for j in range(g2_vn):
            v = VERTEX(i + j * g1_vn, "Default_Label")
            v.combine_mapping(g1_vertices[i])
            v.combine_mapping(g2_vertices[j])
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
                    vertex_label_compatibility = True   # Default
                    if vertex_comparison_import_para:
                        vertex_label_compatibility = vertex_comparison_function(v1.get_label(), v3.get_label()) and \
                                                     vertex_comparison_function(v2.get_label(), v4.get_label())
                    # Conditions for an edge
                    if neighbours_in_g1 == neighbours_in_g2 and vertex_label_compatibility:
                        """ INSERT CODE THAT SHOULD INCLUDE MORE CONDITIONALS e.g. SAME LABEL, DIRECTION etc. """

                        # Like this, two vertices in the modular product graph always have two or no edges connecting
                        # them. Once with each vertex being the start vertex.
                        # The information about type of connection is not conserved in this modular product!
                        # Possibly, this can be done by edge systematic edge labelling (not yet implemented).
                        ### SEARCH for corresponding edge in g1 and g2 to compare their labels

                        # Get Edges
                        edge_g1 = None
                        edge_g2 = None
                        if neighbours_in_g1[0] and neighbours_in_g1[1]:
                            # to check for just g1 is sufficient as neighbours_in_g1 is equal to neighbours_in_g2 (see above)
                            edge_g1 = [edge for edge in g1_edges if edge.get_start_and_end()[0] == v1 and \
                                       edge.get_start_and_end()[1] == v2][0]
                            edge_g2 = [edge for edge in g2_edges if edge.get_start_and_end()[0] == v3 and \
                                       edge.get_start_and_end()[1] == v4][0]

                        # check EDGE-labels on compatibility using the imported function
                        edge_label_compatibility = True     # Default
                        if edge_g1 and edge_g2 and edge_comparison_import_para:
                            edge_label_compatibility = edge_comparison_function(edge_g1.get_label(), edge_g2.get_label())
                        if edge_label_compatibility:
                            pass
                        else:
                            continue

                        #
                        start_vertex = None
                        end_vertex = None
                        for new_v in new_list_of_vertices:
                            if all([va in new_v.get_mapping().values() for va in v1.get_mapping().values()]) and \
                                    all([va in new_v.get_mapping().values() for va in v3.get_mapping().values()]):
                                start_vertex = new_v
                            if all([va in new_v.get_mapping().values() for va in v2.get_mapping().values()]) and \
                                    all([va in new_v.get_mapping().values() for va in v4.get_mapping().values()]):
                                end_vertex = new_v
                        new_list_of_edges.append(EDGE(edge_id, [start_vertex, end_vertex], "Default_Label"))
                        new_number_of_edges += 1
                        edge_id += 1
                        start_vertex.append_out_neighbour(end_vertex)
    # The modular product as undirected graph is returned with a default name.
    # Vertex and Edge labels are enabled, yet set to a default value for the moment, same as the edge id.
    return GRAPH("Modular Product of " + g1.get_name() + " and " + g2.get_name(),
                 new_list_of_vertices, new_list_of_edges, new_number_of_vertices, int(new_number_of_edges / 2),
                 False, is_labeled_edges=True, is_labeled_nodes=True), anchor
