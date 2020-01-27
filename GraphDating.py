#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 07.05.2019

@author: chris
'''
import os, string, random, itertools
from typing import List, Tuple
from Graph import GRAPH, density, retrieve_graph_from_clique, retrieve_original_subgraphs, \
    anchor_from_anchor_vertex_list, remaining_candidates, retrieve_fusion_graph
from Vertex import VERTEX
from Edge import EDGE
from Command_Line_Parser import parse_command_line
from Modulares_Produkt import modular_product
from Graph_Builder import buildRndGraph, buildRndCluster
from MB_State import MB_State
from GuideTree import upgma, guide_tree_to_newick, save_newick, parse_newick_file_into_tree, \
    parse_list_of_scored_graph_pairs_into_newick, parse_newick_string_into_tree
from Neo4j import NEO4J
from runpy import run_path
from Json_Parser import json_parser
from copy import deepcopy
import time


def parser(file, neo4j):
    """
    Parsing the .graph format to the class Graph
    """
    # Extract information from file
    with open(file, "r") as f:
        # Read header part
        try:
            number_vertices = int(f.readline().split(";")[1].rstrip())
            number_edges = int(f.readline().split(";")[1].rstrip())
            vertices_labelled = f.readline().split(";")[1].rstrip()
            vertices_labelled = check_true_or_false(vertices_labelled)
            edges_labbelled = f.readline().split(";")[1].rstrip()
            edges_labbelled = check_true_or_false(edges_labbelled)
            directed_graph = f.readline().split(";")[1].rstrip()
            directed = check_true_or_false(directed_graph)
        except IOError:
            print("Wrong input file format: Mistake in header part.")

        if number_vertices == 0 and number_edges == 0:
            vertices: List[string] = []
            edges: List[string] = []
        elif number_vertices == 0:
            vertices = []
            # read empty line
            empty = f.readline()
            if empty is not "\n":
                raise Exception("Wrong input file format!")
            try:
                lastlines = f.readlines()
                edges = []
                for elem in lastlines:
                    edges.append(elem.rstrip())
            except IOError:
                print("Wrong input file format: Mistake in edges part.")
        elif number_edges == 0:
            edges = []
            # read empty line
            empty = f.readline()
            if empty is not "\n":
                raise Exception("Wrong input file format!")
            try:
                lastlines = f.readlines()
                vertices = []
                for elem in lastlines:
                    vertices.append(elem.rstrip())
            except IOError:
                print("Wrong input file format: Mistake in vertices part.")
        else:
            # read empty line
            empty = f.readline()
            if empty is not "\n":
                raise Exception("Wrong input file format!")
            # read vertices part
            try:
                newline = f.readline()
                vertices = []
                while newline is not "\n":
                    vertices.append(newline.rstrip())
                    newline = f.readline()
            except IOError:
                print("Wrong input file format: Mistake in vertices part.")
            # read empty line
            if newline is not "\n":
                raise Exception("Wrong input file format!")
            # read edges part
            try:
                lastlines = f.readlines()
                edges = []
                for elem in lastlines:
                    edges.append(elem.rstrip())
            except IOError:
                print("Wrong input file format: Mistake in edges part.")
        file_path_name = file
    f.close()

    # save vertices as objects
    vertices_objects: List[VERTEX] = []
    if number_vertices != 0:
        for vertex in vertices:
            if vertices_labelled:
                vertex_splitted = vertex.split(";")
                if len(vertex_splitted) == 1:
                    raise Exception("Wrong format: Vertices should be labelled but aren't.")
                try:
                    i = int(vertex_splitted[0])
                except TypeError:
                    print("Illegal type for vertex ID in .graph format, please provide integer!")
                vertices_objects.append(VERTEX(int(vertex_splitted[0]), vertex_splitted[1]))
            else:
                vertex_splitted = vertex.split(";")
                if len(vertex_splitted) == 2 and vertex_splitted[1]:
                    raise Exception("Wrong format: Vertices are labelled but header doesn't say so.")
                try:
                    i = int(vertex_splitted[0])
                except TypeError:
                    print("Illegal type for vertex ID in .graph format, please provide integer!")
                vertices_objects.append(VERTEX(i, ""))

    # save edges as objects
    edges_objects: List[EDGE] = []
    if number_edges != 0:
        identifier = 1  # each edge gets an id
        for edge in edges:
            edge_splitted = edge.split(";")
            # search for start vertex in vertices_objects and for end vertex
            start_and_end: List[VERTEX] = [item for item in vertices_objects if (item.get_id() == int(edge_splitted[0]))] \
                            + [item for item in vertices_objects if (item.get_id() == int(edge_splitted[1]))]
            check_start_end_in_vertices(start_and_end, edge)  # check if start and end vertex are in vertices list
            end_and_start = [start_and_end[1], start_and_end[0]]

            if edges_labbelled:
                if len(edge_splitted) == 2:
                    raise Exception("Wrong format: Edges should be labelled but aren't.")
                if directed:  # if graph is directed
                    edges_objects.append(EDGE(identifier, start_and_end, edge_splitted[2]))
                    identifier += 1
                else:  # if graph is undirected, insert both edges automatically unless it is inserted already because
                    # the format includes unnecessarily all edges
                    if start_and_end not in [edge.get_start_and_end() for edge in edges_objects]:
                        edges_objects.append(EDGE(identifier, start_and_end, edge_splitted[2]))
                        identifier += 1
                    if end_and_start not in [edge.get_start_and_end() for edge in edges_objects]:
                        edges_objects.append(EDGE(identifier, end_and_start, edge_splitted[2]))
                        identifier += 1
            else:  # if edges aren't labelled
                if len(edge_splitted) == 3 and edge_splitted[2]:
                    raise Exception("Wrong format: Edges are labelled but header doesn't say so.")
                if directed:  # if graph is directed
                    edges_objects.append(EDGE(identifier, start_and_end, ""))
                    identifier += 1
                else:  # if graph is undirected, insert both edges automatically unless it is inserted already because
                    # the format includes unnecessarily all edges
                    if start_and_end not in [edge.get_start_and_end() for edge in edges_objects]:
                        edges_objects.append(EDGE(identifier, start_and_end, ""))
                        identifier += 1
                    if end_and_start not in [edge.get_start_and_end() for edge in edges_objects]:
                        edges_objects.append(EDGE(identifier, end_and_start, ""))
                        identifier += 1

    # Testing header fits actual number of vertices and edges
    if not len(vertices_objects) == number_vertices:
        raise Exception("Number of vertices doesn't fit predicted number in header!")
    if not directed:
        if not (len(edges_objects) / 2 == number_edges or len(edges_objects) == number_edges):
            raise Exception("Number of edges doesn't fit predicted number in header!")
    else:
        if not len(edges_objects) == number_edges:
            raise Exception("Number of edges doesn't fit predicted number in header!")

    # OUT-neighbours setting
    for vertex in vertices_objects:
        for edge in edges_objects:
            if edge.get_start_and_end()[0].get_id() == vertex.get_id():
                neighbour = edge.get_start_and_end()[1]
                vertex.add_out_neighbour(neighbour)

    # Retrieving graph name from file_path_name
    pos = file_path_name.rfind("/")
    if pos == -1:
        pos = file_path_name.rfind("\\")
    graph_name = file_path_name[pos + 1: -6]
    
    # create Neo4J View
    if neo4j:
        neo4jProjekt = NEO4J(args.neo4j[0], args.neo4j[1], args.neo4j[2], vertices_objects, edges_objects, graph_name, False)
    
    # create graph from class GRAPH
    graph = GRAPH(graph_name, vertices_objects, edges_objects, number_vertices, number_edges, directed,
                  has_labeled_nodes=vertices_labelled, has_labeled_edges=edges_labbelled)

    # for input graphs, each vertex needs to contain a mapping of itself
    for v in graph.get_list_of_vertices():
        v.add_vertex_to_mapping(v, graph.get_name())
    return graph


def check_true_or_false(statement):
    """
    Checks if header statements are "True" or "False".
    Return type: boolean
    """
    if statement == "":
        raise Exception("Wrong input file format.")
    if statement == "True":
        return True
    elif statement == "False":
        return False
    else:
        raise Exception("Wrong input file format\n statement has to be 'True' or 'False.' Currently: " + statement)


def check_start_end_in_vertices(edge_start_end, currentEdge):
    """
    Check if the vertices of an edge already exists in the vertices list.
    Return type: None
    """
    if not len(edge_start_end) == 2:
        raise Exception("One or both vertices of edge: " + currentEdge + " don't exist in list of vertices")
    return


def matching_using_bk(input_graphs, graph_left, graph_right, pivot, anchor_graph_parameters=None,
                      vertex_comparison_import_para=None, edge_comparison_import_para=None):
    """
    Helper function for graph alignment using bron-kerbosch algorithm. Takes two graphs and other bron-kerbosch
    matching parameters as input to perform graph alignment. 'number_matchings' specifies the maximum number of cliques
    that will be return as GRAPH object.
    Return type: [GRAPH, ...]
    """
    if anchor_graph_parameters:
        mp, anchor = modular_product(graph_left, graph_right, anchor_graph_parameters=anchor_graph_parameters,
                                     vertex_comparison_import_para=vertex_comparison_import_para,
                                     edge_comparison_import_para=edge_comparison_import_para)
    else:
        mp, anchor = modular_product(graph_left, graph_right,
                                     vertex_comparison_import_para=vertex_comparison_import_para,
                                     edge_comparison_import_para=edge_comparison_import_para)
    clique_findings = []
    p = mp.get_list_of_vertices()
    if anchor_graph_parameters:
        pre_findings = mp.bron_kerbosch(set(), set(anchor), set(), pivot=pivot)
        pre_findings.sort(key=lambda x: len(x), reverse=True)
        max_pre_findings = len(pre_findings[0])
        for pre_finding in pre_findings:
            if len(pre_finding) == max_pre_findings:
                p = mp.get_list_of_vertices()
                p = remaining_candidates(pre_finding, p)
                clique_findings += mp.bron_kerbosch(set(pre_finding), set(p), set(), pivot=pivot)
    else:
        clique_findings = mp.bron_kerbosch(set(), set(p), set(), pivot=pivot)
    clique_findings.sort(key=lambda x: len(x), reverse=True)
    orig_graph_name = [key for key in mp.get_list_of_vertices()[0].get_mapping().keys()][0]
    orig_graph = [graph for graph in input_graphs if graph.get_name() == orig_graph_name][0]
    result = []
    for clique in clique_findings:
        result.append([clique, orig_graph])
    return result


def matching_using_mb(graph1, graph2, vertex_comparison_import_para=None, edge_comparison_import_para=None):
    """
    Helper function for graph alignment using matching-based algorithm. Takes two graphs as input.
    Return type: [GRAPH, ...]
    """
    mb_state = MB_State(graph1, graph2, vertex_comparison_import_para=vertex_comparison_import_para,
                        edge_comparison_import_para=edge_comparison_import_para)
    result_as_mappings = mb_state.mb_algorithm()
    result = []
    for mapping in result_as_mappings:
        result.append([mapping, graph1, graph2])
    return result


def recursive_matching(input_graphs, cluster, matching_algorithm, pivot, number_matchings,
                       anchor_graph_parameters=[None, None], smaller=0.0,
                       no_stereo_isomers=False, check_connection=False, vertex_comparison_import_para=None,
                       edge_comparison_import_para=None):
    """
    Performs graph alignment according to the guide tree in 'cluster' and the given matching algorithm.
    'number_matchings' specifies the maximum number of cliques that will be considered for further graph alignment.
    Return type: [GRAPH, ...]
    """
    graphs_left = cluster.get_left_child().get_elements()
    graphs_right = cluster.get_right_child().get_elements()
    # If the children are not tree leaves (i.e. grandchildren exist), then call function for these children.
    # Left child.
    if cluster.get_left_child().children_exist():
        graphs_left = recursive_matching(input_graphs, cluster.get_left_child(), matching_algorithm, pivot,
                                         number_matchings, anchor_graph_parameters=anchor_graph_parameters,
                                         smaller=smaller, no_stereo_isomers=no_stereo_isomers,
                                         check_connection=check_connection,
                                         vertex_comparison_import_para=vertex_comparison_import_para,
                                         edge_comparison_import_para=edge_comparison_import_para)
    # Right child.
    if cluster.get_right_child().children_exist():
        graphs_right = recursive_matching(input_graphs, cluster.get_right_child(), matching_algorithm, pivot,
                                          number_matchings, anchor_graph_parameters=anchor_graph_parameters,
                                          smaller=smaller, no_stereo_isomers=no_stereo_isomers,
                                          check_connection=check_connection,
                                          vertex_comparison_import_para=vertex_comparison_import_para,
                                          edge_comparison_import_para=edge_comparison_import_para)
    # Else, the cluster is the root of two leaves, then:
    # Perform graph matching of the two leaf graphs (use the matching method provided by user)
    # Update the cluster with one new leaf, deleting the previous two
    # Return to the upper recursion level
    matching_graphs = []
    if matching_algorithm == "bk":
        clique_findings = []
        for gl in graphs_left:
            for gr in graphs_right:
                clique_findings += matching_using_bk(input_graphs, gl, gr, pivot,
                                                anchor_graph_parameters=anchor_graph_parameters,
                                                vertex_comparison_import_para=vertex_comparison_import_para,
                                                edge_comparison_import_para=edge_comparison_import_para)
        matching_graphs = process_clique_findings(clique_findings, number_matchings, check_connection,
                                                  no_stereo_isomers)
    if matching_algorithm == "mb":
        result_as_mappings = []
        for gl in graphs_left:
            for gr in graphs_right:
                if gl.get_number_of_vertices() >= gr.get_number_of_vertices():
                    graph1 = gl
                    graph2 = gr
                else:
                    graph1 = gr
                    graph2 = gl
                result_as_mappings += matching_using_mb(graph1, graph2,
                                                        vertex_comparison_import_para=vertex_comparison_import_para,
                                                        edge_comparison_import_para=edge_comparison_import_para)
                if smaller and graph2 in input_graphs:
                    result_as_mappings += mb_helper(graph1, graph2,
                                                    vertex_comparison_import_para=vertex_comparison_import_para,
                                                    edge_comparison_import_para=edge_comparison_import_para)
        matching_graphs = process_result_as_mappings(result_as_mappings, number_matchings, check_connection,
                                                     no_stereo_isomers)
    cluster.set_elements(matching_graphs)
    cluster.set_children(None, None)
    return matching_graphs


def process_clique_findings(clique_findings, number_matchings, check_connection, no_stereo_isomers):
    """
    Helper function for the processing from cliques to matching graphs considering different options.
    Return Type: [GRAPH, ...]
    """
    matching_graphs = []
    j = 0
    counter = number_matchings
    check_list = []
    clique_findings = sorted(clique_findings, key=lambda x: len(x[0]), reverse=True)
    while counter > 0 and j < len(clique_findings):
        matching_graph = retrieve_graph_from_clique(clique_findings[j][0], clique_findings[j][1])
        if check_connection:
            if matching_graph.is_connected():
                if no_stereo_isomers:
                    original_subgraphs = retrieve_original_subgraphs(matching_graph, input_graphs)
                    d = {}
                    for g in original_subgraphs:
                        lov = g.get_list_of_vertices()
                        lov = sorted(lov, key=lambda x: x.get_id())
                        d[g.get_name()] = lov
                    new = True
                    for already in check_list:
                        true_list = []
                        for key in already.keys():
                            if already[key] == d[key]:
                                true_list.append(True)
                            else:
                                true_list.append(False)
                        if all(true_list):
                            new = False
                    if new:
                        check_list.append(d)
                        matching_graphs.append(matching_graph)
                        counter -= 1
                else:
                    matching_graphs.append(matching_graph)
                    counter -= 1
        else:
            if no_stereo_isomers:
                original_subgraphs = retrieve_original_subgraphs(matching_graph, input_graphs)
                d = {}
                for g in original_subgraphs:
                    lov = g.get_list_of_vertices()
                    lov = sorted(lov, key=lambda x: x.get_id())
                    d[g.get_name()] = lov
                new = True
                for already in check_list:
                    true_list = []
                    for key in already.keys():
                        if already[key] == d[key]:
                            true_list.append(True)
                        else:
                            true_list.append(False)
                    if all(true_list):
                        new = False
                if new:
                    check_list.append(d)
                    matching_graphs.append(matching_graph)
                    counter -= 1
            else:
                matching_graphs.append(matching_graph)
                counter -= 1
        j += 1
    return matching_graphs


def process_result_as_mappings(result_as_mappings, number_matchings, check_connection, no_stereo_isomers):
    """
    Helper function for the processing from mappings coming from matching-based algorithm core structures
    to matching graphs considering different options.
    Return Type: [GRAPH, ...]
    """
    matching_graphs = []
    j = 0
    counter = number_matchings
    check_list = []
    result_as_mappings = sorted(result_as_mappings, key=lambda x: len(x[0].keys()), reverse=True)
    while counter > 0 and j < len(result_as_mappings):
        matching_graph = mb_mapping_to_graph(result_as_mappings[j][0], result_as_mappings[j][1],
                                             result_as_mappings[j][2])
        if check_connection:
            if matching_graph.is_connected():
                if no_stereo_isomers:
                    original_subgraphs = retrieve_original_subgraphs(matching_graph, input_graphs)
                    d = {}
                    for g in original_subgraphs:
                        lov = g.get_list_of_vertices()
                        lov = sorted(lov, key=lambda x: x.get_id())
                        d[g.get_name()] = lov
                    new = True
                    for already in check_list:
                        true_list = []
                        for key in already.keys():
                            if already[key] == d[key]:
                                true_list.append(True)
                            else:
                                true_list.append(False)
                        if all(true_list):
                            new = False
                    if new:
                        check_list.append(d)
                        matching_graphs.append(matching_graph)
                        counter -= 1
                else:
                    matching_graphs.append(matching_graph)
                    counter -= 1
        else:
            if no_stereo_isomers:
                original_subgraphs = retrieve_original_subgraphs(matching_graph, input_graphs)
                d = {}
                for g in original_subgraphs:
                    lov = g.get_list_of_vertices()
                    lov = sorted(lov, key=lambda x: x.get_id())
                    d[g.get_name()] = lov
                new = True
                for already in check_list:
                    true_list = []
                    for key in already.keys():
                        if already[key] == d[key]:
                            true_list.append(True)
                        else:
                            true_list.append(False)
                    if all(true_list):
                        new = False
                if new:
                    check_list.append(d)
                    matching_graphs.append(matching_graph)
                    counter -= 1
            else:
                matching_graphs.append(matching_graph)
                counter -= 1
        j += 1
    return matching_graphs


def mb_mapping_to_graph(result_as_mapping, graph1, graph2):
    """
    Helper function for graph alignment using matching-based algorithm. Takes a mapping of the ID of vertices of
    'graph1' as key and the ID of vertices of 'graph2' as value. A GRAPH object is constructed with vertex IDs, vertex
    labels, edge IDs, edge labels, __is_directed attribute, __is_labelled_nodes attribute and __is_labelled_edges
    attribute taken from graph1 (so far!). A 8-letter random graph name is used. Each vertex of the new graph contains
    the mappings of the vertex of 'graph1' with the same ID and of its mapping partner in 'graph2'. This function is
    analogous to 'retrieve_graph_from_clique' for bron-kerbosch algorithm.
    Return type: GRAPH
    """
    gv1 = graph1.get_list_of_vertices()
    gv2 = graph2.get_list_of_vertices()
    ge1 = graph1.get_list_of_edges()
    graph = None
    if result_as_mapping:
        lov = []
        for k, v in result_as_mapping.items():
            for v1 in gv1:
                if k == v1.get_id():
                    new_v = VERTEX(v1.get_id(), v1.get_label())
                    new_v.combine_mapping(v1)
                    for v2 in gv2:
                        if v == v2.get_id():
                            new_v.combine_mapping(v2)
                            lov.append(new_v)
        loe = []
        for edge in ge1:
            for new_v1 in lov:
                for new_v2 in lov:
                    if edge.get_start_and_end()[0].get_id() == new_v1.get_id() and \
                            edge.get_start_and_end()[1].get_id() == new_v2.get_id():
                        new_e = EDGE(edge.get_id(), [new_v1, new_v2], edge.get_label())
                        loe.append(new_e)
                        new_v1.add_out_neighbour(new_v2)
        graph_name = "".join([random.choice(string.ascii_letters) for n in range(8)])
        graph = GRAPH(graph_name, lov, loe, len(lov), len(loe), graph1.get_is_directed(),
                      graph1.get_has_labeled_nodes(), graph1.get_has_labeled_edges())
    return graph


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


def pairwise_alignment(input_graphs, matching_method, pivot, number_matchings, check_connection=False,
                       no_stereo_isomers=False, vertex_comparison_import_para=None,
                       edge_comparison_import_para=None):
    """
    Function takes a List[GRAPH, ...] and several other parameters necessary for graph matching and constructs a guide
    tree based on pairwise alignment of the input graphs. The scoring parameter is the size the greatest subgraph
    isomorphism between two graphs relative to the number of vertices of the bigger graph, i.e. that contains the
    maximal number of nodes.
    Return Type: Cluster
    """ 
    combinations_of_graphs = itertools.combinations(input_graphs, 2)
    scoring: List[Tuple] = []
    for c in combinations_of_graphs:
        score = 0
        graph1 = c[0]
        graph2 = c[1]
        if graph2.get_number_of_vertices() > graph1.get_number_of_vertices():
            graph1, graph2 = graph2, graph1
        graph1_name = graph1.get_name()
        graph2_name = graph2.get_name()
        if matching_method == "bk":
            clique_findings = matching_using_bk(input_graphs, c[0], c[1],
                                                pivot, vertex_comparison_import_para=vertex_comparison_import_para,
                                                edge_comparison_import_para=edge_comparison_import_para)
            matching_graphs = process_clique_findings(clique_findings, number_matchings, check_connection,
                                                      no_stereo_isomers)
        else:
            result_as_mappings = matching_using_mb(graph1, graph2,
                                                   vertex_comparison_import_para=vertex_comparison_import_para,
                                                   edge_comparison_import_para=edge_comparison_import_para)
            if smaller:
                result_as_mappings += mb_helper(graph1, graph2,
                                                vertex_comparison_import_para=vertex_comparison_import_para,
                                                edge_comparison_import_para=edge_comparison_import_para)
            matching_graphs = process_result_as_mappings(result_as_mappings, number_matchings, check_connection,
                                                         no_stereo_isomers)
        if len(matching_graphs) == 0:
            raise Exception("No matchings in pairwise alignment, please adjust graph reduction parameter (see help"
                            "message for '-ga' command line option!")
        for graph in matching_graphs:
            if graph.get_number_of_vertices()/graph1.get_number_of_vertices() > score:
                score = graph.get_number_of_vertices()/graph1.get_number_of_vertices()
        scoring.append((score, graph1_name, graph2_name))
    scoring.sort(key=lambda x: x[2], reverse=True)
    newick_string = parse_list_of_scored_graph_pairs_into_newick(scoring)
    cluster_tree = parse_newick_string_into_tree(newick_string, input_graphs)
    return cluster_tree


def mb_helper(gl, gr, vertex_comparison_import_para=None,
              edge_comparison_import_para=None):
    """
    Helper function for the matching using pruned input graphs
    Return Type: [GRAPH, ...]
    """
    result_as_mappings = []
    if gl.get_number_of_vertices() > gr.get_number_of_vertices():
        gn = gr.get_number_of_vertices()
        margin = int(gn * smaller)
        new_gs = []
        combinations = []
        for i in range(margin):
            combinations += itertools.combinations(gr.get_list_of_vertices(), gn - i - 1)
        for c in combinations:
            new_g = gr.graph_from_vertex_combination(c)
            new_gs.append(new_g)
        for new_g in new_gs:
            result_as_mappings += matching_using_mb(gl, new_g,
                                                    vertex_comparison_import_para=vertex_comparison_import_para,
                                                    edge_comparison_import_para=edge_comparison_import_para)
    else:
        gn = gl.get_number_of_vertices()
        margin = int(gn * smaller)
        new_gs = []
        combinations = []
        for i in range(margin):
            combinations += itertools.combinations(gr.get_list_of_vertices(), gn - i - 1)
        for c in combinations:
            new_g = gr.graph_from_vertex_combination(c)
            new_gs.append(new_g)
        for new_g in new_gs:
            result_as_mappings += matching_using_mb(gl, new_g,
                                                    vertex_comparison_import_para=vertex_comparison_import_para,
                                                    edge_comparison_import_para=edge_comparison_import_para)
    return result_as_mappings


if __name__ == '__main__':

    # Command line parsing
    try:
        args = parse_command_line()
    except IOError:
        args = {}
        raise Exception("Error occurred passing the command line arguments!")

    if args.syntax:
        raise Exception("Please use proper syntax, use '-h' for more information!")

    # Initialization of necessary variables
    graph = None
    input_graphs = []
    selected_subgraphs = []
    anchor = []
    p = []
    newick = None
    graphs = []
    if args.benchmark:
        ts_mp_1, ts_mp_2, ts_bk_1, ts_bk_2, ts_ga_1, ts_ga_2 = None, None, None, None, None, None

    # Check if user what to make a new Neo4J Upload
    # create Neo4J View
    if args.neo4j:
        # Delete old Neo4j database entries
        neo4jProjekt = NEO4J(args.neo4j[0], args.neo4j[1], args.neo4j[2], [],  [], "", True)

    # Console output for passed parameters
    print("Input format: ." + args.input_format)

    #  Check for random graph option
    if args.random_graph:
        if args.random_graph[2] == "True":
            directed = True
        else:
            directed = False
        try:
            graph = buildRndGraph(int(args.random_graph[0]), float(args.random_graph[1]), directed=directed)
            graphs.append(graph)
        except IOError:
            print("Invalid number of arguments for random graph building!")
        except ValueError:
            print("invalid type of arguments for random graph building!")
    elif args.random_cluster:
        print("random_cluster")
        print(args.random_cluster)
        try:
            graph = buildRndCluster(args.random_cluster[0], args.random_cluster[1],
                                    args.random_cluster[2], args.random_cluster[3])
            graphs.append(graph)
        except IOError:
            print("Invalid number of arguments for random cluster graph building!")
        except ValueError:
            print("invalid type of arguments for random clfuster graph building!")

    # If neither input file(s) not random graph option are given, raise Exception. Else, parse input!
    elif not args.input and not args.random_graph and not args.random_cluster:
        raise Exception("Please provide input file(s) with preceding '-i' statement!")
    else:
        direction = None
        for i in range(len(args.input)):
            if not os.path.isdir(os.path.dirname(args.input[i])) and not os.path.exists(args.input[i]):
                raise Exception("No such file with given path or filename!")
            if not os.path.isdir(os.path.dirname(args.input[i])):
                file_path = os.path.abspath(args.input[i])
            else:
                file_path = os.path.abspath(args.input[i])

            # Log statement for the console about the input file
            print("Input file path of file " + str(i) + ": " + file_path)

            if args.input_format == "graph":
                graph = parser(file_path, args.neo4j)
            elif args.input_format == "json":
                graph = json_parser(file_path, args.neo4j, args.no_h_atoms)

            if direction is None:
                direction = graph.get_is_directed()
            if direction != graph.get_is_directed():
                raise Exception("Input graphs have to be either all directed or all undirected!")
            input_graphs.append(graph)
            if not args.modular_product and not args.random_graph and not args.random_cluster:
                graphs.append(graph)
        p = input_graphs[0].get_list_of_vertices()

    # Log statement for the console about the Pivot Mode!
    if args.bron_kerbosch or args.graph_alignment and args.graph_alignment[0] == "bk":
        if args.pivot is None:
            print("Pivot Mode: --")
        else:
            print("Pivot Mode: " + args.pivot)

    # Checking for an anchor graph file and checking anchor for clique property. Anchor default is a list.
    if not args.anchor:
        anchor_graph = None
        if (isinstance(args.graph_alignment, list) and args.graph_alignment[0] == "bk") or \
                isinstance(args.bron_kerbosch, list):
            print("Anchor File: --")
    else:
        if not os.path.isdir(os.path.dirname(args.anchor)) and not os.path.exists(args.anchor):
            raise Exception("No such file with given path or filename!")
        if not os.path.isdir(os.path.dirname(args.anchor)):
            file_path = os.path.abspath(args.anchor)
        else:
            file_path = args.anchor
        anchor_graph = parser(file_path, args.neo4j)
        if not anchor_graph.check_clique_properties() and args.bron_kerbosch:
            raise Exception("Anchor is not a clique nor empty! For clique finding on a modular product using an anchor "
                            "pass a subgraph of the modular product which is a clique!")
        elif args.bron_kerbosch is not None:
            if len(input_graphs) != 1:
                raise Exception("For clique finding via bron-kerbosch, "
                                "please provide exactly one file path of a graph!")
            else:
                anchor, p = anchor_from_anchor_vertex_list(anchor_graph.get_list_of_vertices(), p)

    # Checking for bron-kerbosch option
    if args.bron_kerbosch is not None:
        print("Matching algorithm: Bron-kerbosch")
        if len(input_graphs) != 1:
            raise Exception("For clique finding via bron-kerbosch, please provide exactly one file path of a graph!")
        elif len(args.bron_kerbosch) > 2 or len(args.bron_kerbosch) == 1:
            raise Exception("You may optionally pass a file name together with a function name in that file for custom"
                            "clique sorting!")
        else:
            selected_cliques = []
            print("Clique finding via Bron-Kerbosch...")
            if len(p) == 0:
                selected_cliques.append(anchor)
            else:
                ts_bk_1 = time.time()
                selected_cliques = input_graphs[0].bron_kerbosch(set(anchor), set(p), set(), pivot=args.pivot)
                ts_bk_2 = time.time()
            matching_graphs = []
            for i in range(len(selected_cliques)):
                matching_graph = retrieve_graph_from_clique(selected_cliques[i], input_graphs[0])
                matching_graphs.append(matching_graph)
            print("Single Bron-kerbosch: Found " + str(len(matching_graphs)) + " cliques!")
            matching_graphs = sorted(matching_graphs, key=lambda x: x.get_number_of_vertices(), reverse=True)
            for matching_graph in matching_graphs:
                original_subgraph = retrieve_original_subgraphs(matching_graph, input_graphs)
                selected_subgraphs.append(original_subgraph)

    # Checking for modular product option
    if args.modular_product:
        if len(input_graphs) != 2:
            raise Exception("For formation of the modular product, please provide exactly two files containing a graph "
                            "each!")
        else:
            graph1_name = input_graphs[0].get_name()
            graph2_name = input_graphs[1].get_name()
            ts_mp_1 = time.time()
            graph, anchor = modular_product(input_graphs[0], input_graphs[1],
                                            vertex_comparison_import_para=args.vertex_label_comparison,
                                            edge_comparison_import_para=args.edge_label_comparison)
            ts_mp_2 = time.time()
            graphs.append(graph)
            # if args.neo4j:
                # neo4jProjekt = NEO4J("http://localhost:11003/db/data/", "neo4j", "1234")
                # neo4jProjekt.create_graphs(neo4jProjekt.get_graph(), graph.get_list_of_vertices(), graph.get_list_of_edges(),graph.get_name())
            
            # Log statement for the console about the modular product
            if args.vertex_label_comparison and args.edge_label_comparison:
                print("Modular Product of " + graph1_name + " and " + graph2_name +
                      " was calculated with custom vertex and edge label-comparison-functions " +
                      args.vertex_label_comparison[1] + " and " + args.edge_label_comparison[1] + "!")
            elif args.vertex_label_comparison:
                print("Modular Product of " + graph1_name + " and " + graph2_name +
                      " was calculated with custom vertex-label-comparison-function: " +
                      args.vertex_label_comparison[1] + "!")
            elif args.edge_label_comparison:
                print("Modular Product of " + graph1_name + " and " + graph2_name +
                      " was calculated with custom edge-label-comparison-function: " +
                      args.edge_label_comparison[1] + "!")
            else:
                print("Modular Product of " + graph1_name + " and " + graph2_name + " was calculated!")

    if isinstance(args.guide_tree, list) and len(args.guide_tree) == 0:
        raise Exception("For guide tree construction, please pass either a .newick file, a built-in keyword (see "
                        "help message) or 'custom <file.py>' for introducing you own comparison function!")

    # Checking for graph alignment option. This option performs graph alignment of a number of graphs given as input
    # files. The matching order is according to the guide tree option (passing a comparison function or a '.newick' file
    # , using graph density for guide tree construction is default. The graph names in the '.newick' file must be
    # unique!.
    # Matching is done either by forming the modular product and performing bron-kerbosch-algorithm or by the
    # matching-based VF2 algorithm (Cordella et al.)!
    if isinstance(args.graph_alignment, list) and len(args.graph_alignment) == 0:
        raise Exception("For graph alignment, please choose matching method!")
    if args.graph_alignment:
        i = 1
        smaller = 0.0
        if args.graph_alignment[0] not in ["bk", "mb"]:
            raise Exception("Illegal identifier for matching algorithm!")
        if args.graph_alignment[0] == "bk":
            print("Matching algorithm: Bron-kerbosch")
        if args.graph_alignment[0] == "mb":
            print("Matching algorithm: Matching-based")
            if len(args.graph_alignment) == 3:
                try:
                    smaller = float(args.graph_alignment[2])
                    if smaller <= 0.0 or smaller >= 1.0:
                        raise Exception("Illegal value for the allowed reduction of subgraph size!")
                    print("Relative size reduction: " + str(smaller))
                except ValueError("Illegal value for the allowed reduction of subgraph size!"):
                    pass
        if len(args.graph_alignment) >= 2: #if e.g. bk 2 
            try:
                i = int(args.graph_alignment[1])
                if i < 1:
                    raise Exception("Illegal value for the number of matchings to expand search on!")
                print("Number of matchings forwarded: " + str(i))
            except ValueError("Illegal value for the number of matchings to expand search on!"):
                pass
        else:
            print("Number of matchings forwarded: 1 (Default)")

        if anchor_graph:
            anchor_graph_parameters = [anchor_graph, input_graphs[0].get_name()]
        else:
            anchor_graph_parameters = None

        if args.guide_tree and input_graphs:
            if args.guide_tree[0] == "custom":
                print("Guide tree construction: Custom function passed")
                f = import_file(args.guide_tree[1], args.guide_tree[2])
                cluster_tree = upgma(f, input_graphs, anchor_graph=anchor_graph)
                copy = deepcopy(cluster_tree)
                newick = guide_tree_to_newick(copy)
            elif args.guide_tree[0][-7:] == ".newick":
                print("Guide tree construction: Newick string file passed")
                cluster_tree = parse_newick_file_into_tree(args.guide_tree, input_graphs)
                newick = args.guide_tree[0]
            elif args.guide_tree[0] == "pairwise_align":
                print("Guide tree construction: Pairwise alignment")
                cluster_tree = pairwise_alignment(input_graphs, args.graph_alignment[0], args.pivot, i,
                                                  check_connection=args.check_connection,
                                                  no_stereo_isomers=args.no_stereo_isomers,
                                                  vertex_comparison_import_para=args.vertex_label_comparison,
                                                  edge_comparison_import_para=args.edge_label_comparison)
                copy = deepcopy(cluster_tree)
                newick = guide_tree_to_newick(copy)
            elif args.guide_tree[0] not in ["density", "pairwise_align"]:
                cluster_tree = None
                raise Exception("Illegal identifier for comparison function!")
            else:
                print("Guide tree construction: Graph density selected")
                cluster_tree = upgma(density, input_graphs, anchor_graph=anchor_graph)
                copy = deepcopy(cluster_tree)
                newick = guide_tree_to_newick(copy)
        else:
            print("Guide tree construction: Graph density (Default)")
            cluster_tree = upgma(density, input_graphs, anchor_graph=anchor_graph)
            copy = deepcopy(cluster_tree)
            newick = guide_tree_to_newick(copy)
        if args.guide_tree and len(args.guide_tree) == 2 and args.guide_tree[1] == "only":
            print("Graph alignment not performed.")
            pass
        else:
            if args.graph_alignment[0] == "mb":
                print("Matching-based algorithm performing...")
            elif args.graph_alignment[0] == "bk":
                print("Bron-kerbosch algorithm performing...")
            ts_ga_1 = time.time()   #timestamp before alignment
            matching_graphs = recursive_matching(input_graphs, cluster_tree, args.graph_alignment[0], args.pivot, i,
                                                 anchor_graph_parameters=anchor_graph_parameters,
                                                 smaller=smaller,
                                                 no_stereo_isomers=args.no_stereo_isomers,
                                                 check_connection=args.check_connection,
                                                 vertex_comparison_import_para=args.vertex_label_comparison,
                                                 edge_comparison_import_para=args.edge_label_comparison)
            ts_ga_2 = time.time()   #timestamp after alignment
            print("Graph Alignment: Found " + str(len(matching_graphs)) + " matching(s)! Maximum of " + str(i) + " "
                  "matching(s) have been forwarded...")
            for matching_graph in matching_graphs:
                if args.seperate:
                    if matching_graph:
                        original_subgraphs = retrieve_original_subgraphs(matching_graph, input_graphs)
                        selected_subgraphs.append(original_subgraphs)
                else:
                    if matching_graph:
                        fusion_graph = retrieve_fusion_graph(matching_graph, input_graphs)
                        selected_subgraphs.append([fusion_graph])

    # If guide tree option is selected, construct a guide using the passed comparison function.
    if args.guide_tree:
        if args.guide_tree[0] == "custom":
            print("Guide tree construction: Custom function passed")
            f = import_file(args.guide_tree[1], args.guide_tree[2])
            cluster_tree = upgma(f, input_graphs, anchor_graph=anchor_graph)
            newick = guide_tree_to_newick(cluster_tree)
        elif args.guide_tree[0][-7:] == ".newick":
            print("Guide tree construction: Newick string file passed")
            newick = args.guide_tree[0]
        elif input_graphs:
            if args.guide_tree[0] == "density":
                print("Guide tree construction: Graph density")
                cluster_tree = upgma(density, input_graphs, anchor_graph=anchor_graph)
                newick = guide_tree_to_newick(cluster_tree)

    # Checking for output options.
    # Output of newick string.
    if args.newick_output:
        if args.newick_output == "1":
            print("Newick string output: True (Default name)")
        else:
            print("Newick string output: True (" + args.newick_output + ")")
        if newick is None:
            raise Exception("Select guide tree and/or graph alignment option to create a newick string to save!")
        else:
            save_newick(newick, output_file=args.newick_output)
    else:
        print("Newick string output: False")

    # Output of graph from random graph building or modular product.
    if args.graph_output is not None:
        print("Graph output: True")
        if len(graphs) == 0:
            raise Exception("No graph to save in memory!")
        else:
            for i in range(len(graphs)):
                if len(graphs) != len(args.graph_output) and not len(args.graph_output) == 0:
                    raise Exception("The number of graphs to save and provided graph output names do not match! NOTE: "
                                    "Random graph generation, modular product calculation and format conversion can "
                                    "only be performed in seperate calls!")
                elif len(args.graph_output) == 0:
                    graphs[i].save_to_txt(output_file=graphs[i].get_name() + "_output.graph")
                else:
                    graphs[i].save_to_txt(output_file=args.graph_output[i] + "_output.graph")
                if args.neo4j:
                    # create Neo4J View
                    neo4jProjekt = NEO4J(args.neo4j[0], args.neo4j[1], args.neo4j[2], graphs[i].get_list_of_vertices(),
                                         graphs[i].get_list_of_edges(), graphs[i].get_name(), False)
    else:
        print("Graph output: False")

    # Output of subgraphs from graph alignment or bron-kerbosch algorithm on a modular product.
    if args.subgraph_output is not None and (input_graphs or graph):
        number_output = len(selected_subgraphs)
        default_num_sgo = False
        try:
            number_output = int(args.subgraph_output[0])
        except:
            try:
                number_output = int(args.subgraph_output[1])
            except:
                default_num_sgo = True
        if default_num_sgo:
            print("Subgraph output: Maximal number of matchings to be exported is " + str(number_output) + " "
                  ", i.e. every matching that has been forwarded to output (default).")
        else:
            print("Subgraph output: Maximal number of matchings to be exported is " + str(number_output) + ".")
        if len(args.subgraph_output) > 2:
            raise Exception("Please provide a maximum of two arguments: First the output file path and second the "
                            "number of subgraphs to be exported!")
        elif len(args.subgraph_output) == 2:
            try:
                subgraph_number = int(args.subgraph_output[1])
                for i in range(min(len(selected_subgraphs), subgraph_number)):
                    for subgraph in selected_subgraphs[i]:
                        subgraph.save_to_txt(output_file=subgraph.get_name() + "_" + args.subgraph_output[0],
                                             sequential_number=i)
                        # create Neo4J View
                        if args.neo4j:
                            neo4jProjekt = NEO4J(args.neo4j[0], args.neo4j[1], args.neo4j[2], subgraph.get_list_of_vertices(), subgraph.get_list_of_edges(),
                                                 subgraph.get_name() + "_Subgraph_" + str(i + 1) + ".graph", False)
            except ValueError("Please provide an integer value for the number of subgraphs to be exported as second "
                              "argument!"):
                pass
        elif len(args.subgraph_output) == 0:
            for i in range(len(selected_subgraphs)):
                for subgraph in selected_subgraphs[i]:
                    subgraph.save_to_txt(output_file=subgraph.get_name() + "_Subgraph_" + str(i + 1) + ".graph")
                    # create Neo4J View
                    if args.neo4j:
                        neo4jProjekt = NEO4J(args.neo4j[0], args.neo4j[1], args.neo4j[2], subgraph.get_list_of_vertices(), subgraph.get_list_of_edges(),
                                             subgraph.get_name() + "_Subgraph_" + str(i + 1) + ".graph",False)
        elif len(args.subgraph_output) == 1:
            if args.subgraph_output[0].isdigit():
                subgraph_number = int(args.subgraph_output[0])
                for i in range(min(len(selected_subgraphs), subgraph_number)):
                    for subgraph in selected_subgraphs[i]:
                        subgraph.save_to_txt(output_file=subgraph.get_name() + "_Subgraph_" + str(i + 1) + ".graph")
                        # create Neo4J View
                        if args.neo4j:
                            neo4jProjekt = NEO4J(args.neo4j[0], args.neo4j[1], args.neo4j[2], subgraph.get_list_of_vertices(), subgraph.get_list_of_edges(),
                                                 subgraph.get_name() + "_Subgraph_" + str(i + 1) + ".graph",False)
            else:
                for i in range(len(selected_subgraphs)):
                    for subgraph in selected_subgraphs[i]:
                        subgraph.save_to_txt(output_file= subgraph.get_name() + "_" + args.subgraph_output[0],
                                             sequential_number=i)
                        # create Neo4J View
                        if args.neo4j:
                            neo4jProjekt = NEO4J(args.neo4j[0], args.neo4j[1], args.neo4j[2], subgraph.get_list_of_vertices(), subgraph.get_list_of_edges(),
                                                 subgraph.get_name() + "_Subgraph_" + str(i + 1) + ".graph",False)
    else:
        print("Subgraph output: False")

    if args.benchmark:
        if args.graph_alignment:
            runtime_ga = ts_ga_2 - ts_ga_1
        if args.bron_kerbosch is not None:
            runtime_bk = ts_bk_2 - ts_bk_1
        if args.modular_product:
            runtime_mp = ts_mp_2 - ts_mp_1

        file_name = args.benchmark[0]   # works as benchmark-descriptor, eg. "ga_bk_3graphs_10nodes_connect0.1)
        algo_name = ""
        with open(file_name, 'a') as file:
            if args.graph_alignment:
                if args.graph_alignment[0] == "bk":
                    algo_name = "ga_bk"
                    file.write(str(runtime_ga) + ";")
                elif args.graph_alignment[0] == "mb":
                    algo_name = "ga_mb"
                    file.write(str(runtime_ga) + ";")
            elif args.modular_product:
                algo_name = "mp"
                file.write(str(runtime_mp) + ";")
            elif args.bron_kerbosch is not None:
                algo_name = "bk"
                file.write(str(runtime_bk) + ";")



