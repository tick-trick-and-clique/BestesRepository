#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 07.05.2019

@author: chris
'''
import os
from Graph import GRAPH, density, retrieve_graph_from_clique
from Vertex import VERTEX
from Edge import EDGE
from Command_Line_Parser import parse_command_line
from Modulares_Produkt import modular_product
from Graph_Builder import buildRndGraph, buildRndCluster
from MB_State import MB_State
from GuideTree import upgma, guide_tree_to_newick, save_newick, parse_newick_file_into_tree


def parser(file):
    """
    Parsing the .graph format to the class Graph
    """
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
            vertices = []
            edges = []
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
    vertices_objects = []
    if number_vertices != 0:
        # save vertices as objects
        for vertex in vertices:
            if vertices_labelled:  # if vertices are labelled
                vertex_splitted = vertex.split(";")
                if len(vertex_splitted) == 1:
                    raise Exception("Wrong format: Vertices should be labelled but aren't.")
                try:
                    i = int(vertex_splitted[0])
                except TypeError:
                    print("Illegal type for vertex ID in .graph format, please provide integer!")
                vertices_objects.append(VERTEX(int(vertex_splitted[0]), vertex_splitted[1]))
            else:  # if vertices arent labelled
                vertex_splitted = vertex.split(";")
                if len(vertex_splitted) == 2 and vertex_splitted[1]:
                    raise Exception("Wrong format: Vertices are labelled but header doesn't say so.")
                try:
                    i = int(vertex_splitted[0])
                except TypeError:
                    print("Illegal type for vertex ID in .graph format, please provide integer!")
                vertices_objects.append(VERTEX(int(vertex_splitted[0]), ""))

    # save edges as objects
    edges_objects = []
    if number_edges != 0:
        identifier = 1  # each edge gets an id
        for edge in edges:
            edge_splitted = edge.split(";")
            # search for start vertex in vertices_objects and for end vertex
            start_and_end = [item for item in vertices_objects if (item.get_id() == int(edge_splitted[0]))] \
                            + [item for item in vertices_objects if (item.get_id() == int(edge_splitted[1]))]
            check_start_end_in_vertices(start_and_end, edge)  # check if start and end vertex are in vertices list
            end_and_start = [item for item in vertices_objects if (item.get_id() == int(edge_splitted[1]))] \
                            + [item for item in vertices_objects if (item.get_id() == int(edge_splitted[0]))]
    
            if edges_labbelled:  # if edges are labelled
                if len(edge_splitted) == 2:
                    raise Exception("Wrong format: Edges should be labelled but aren't.")
                if directed:    # if graph is directed
                    edges_objects.append(EDGE(identifier, start_and_end, edge_splitted[2]))
                    identifier += 1
                else:   # if graph is undirected, insert both edges automatically unless it is inserted already because
                        # the format includes unnecessarily all edges
                    if start_and_end not in [edge.get_start_and_end() for edge in edges_objects]:
                        edges_objects.append(EDGE(identifier, start_and_end, edge_splitted[2]))
                        identifier += 1
                    if end_and_start not in [edge.get_start_and_end() for edge in edges_objects]:
                        edges_objects.append(EDGE(identifier, end_and_start, edge_splitted[2]))
                        identifier += 1
            else:   # if edges aren't labelled
                if len(edge_splitted) == 3 and edge_splitted[2]:
                    raise Exception("Wrong format: Edges are labelled but header doesn't say so.")
                if directed:  # if graph is directed
                    edges_objects.append(EDGE(identifier, start_and_end, ""))
                    identifier += 1
                else:   # if graph is undirected, insert both edges automatically unless it is inserted already because
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
        if not len(edges_objects)/2 == number_edges or len(edges_objects) == number_edges:
            raise Exception("Number of edges doesn't fit predicted number in header!")
    else:
        if not len(edges_objects) == number_edges:
            raise Exception("Number of edges doesn't fit predicted number in header!")

    # neighbours setting
    for vertex in vertices_objects:
        for edge in edges_objects:
            if edge.get_start_and_end()[0].get_id() == vertex.get_id():
                neighbour = edge.get_start_and_end()[1]
                vertex.append_neighbour(neighbour)

    # Retrieving graph name from file_path_name
    pos = file_path_name.rfind("/")
    if pos == -1:
        pos = file_path_name.rfind("\\")
    graph_name = file_path_name[pos + 1: -6]

    # create graph from class GRAPH
    return GRAPH(graph_name, vertices_objects, edges_objects, number_vertices, number_edges, directed,
                 is_labeled_nodes=vertices_labelled, is_labeled_edges=edges_labbelled)


def check_true_or_false(statement):
    """
    Checks if header statements are "True" or "False"
    """
    if statement == "":
        raise Exception("Wrong input file format.")
    if statement == "True":
        return True
    elif statement == "False":
        return False
    else:
        raise Exception("Wrong input file format\n statement has to be 'True' or 'False.' Currently: " + statement )


def check_start_end_in_vertices(edge_start_end, currentEdge):
    """
    Check if the vertices of an edge already exists in the vertices list
    """
    if not len(edge_start_end) == 2:
        raise Exception("One or both vertices of edge: " + currentEdge + " don't exist in list of vertices")
    return


def recursive_matching_using_bk(graphs, number_cliques, anchor, pivot_mode, current_clique_as_graph=None):
    """Takes as input a list of graphs and other bron-kerbosch matching parameters to perform graph alignment for all
    graphs to be found in the list 'graphs'. 'number_cliques' specifies the number of cliques that will be considered
    for further matching after each iteration."""
    result = []
    if current_clique_as_graph is None:
        mp = modular_product(graphs[0], graphs[1])
        pos = 2
        current_clique_as_graph = graphs[0]
    else:
        mp = modular_product(current_clique_as_graph, graphs[0])
        pos = 1
    mapping = mp.get_mapping()
    # Dev Log statement for graph checking
    # print(mp)
    # Log statement for the console about Bron-Kerbosch
    print("Clique finding via Bron-Kerbosch...")
    clique_findings = mp.bron_kerbosch(anchor, mp.get_list_of_vertices(), [], pivot=pivot_mode)
    clique_findings.sort(key=lambda x: len(x), reverse=True)
    for j in range(number_cliques):
        new_clique_as_graph = retrieve_graph_from_clique(clique_findings[j], mapping,
                                                         current_clique_as_graph)
        if len(graphs) >= 2:
            result += recursive_matching_using_bk(graphs[pos:], number_cliques, anchor, pivot_mode,
                                                  new_clique_as_graph)
    return result


def recursive_matching(cluster, matching_algorithm, anchor, pivot_mode, number_cliques=None):
    """Performs graph matching according to the guide tree
        and the given matching algorithm. This function does not perform
        element-wise matching of all or a selected number of graph matching products until now."""
    # If the children are not tree leaves (i.e. grandchildren exist), then call function for these children.
    # Left child.
    if cluster.get_left_child().children_exist():
        recursive_matching(cluster.get_left_child(), matching_algorithm, anchor, pivot_mode,
                           number_cliques=number_cliques)
    # Right child.
    if cluster.get_right_child().children_exist():
        recursive_matching(cluster.get_right_child(), matching_algorithm, anchor, pivot_mode,
                           number_cliques=number_cliques)

    # Else, the cluster is the root of two leaves, then:
        # Perform graph matching of the two leaf graphs (use the matching method provided by user)
        # Update the cluster with one new leaf, deleting the previous two
        # Return to the upper recursion level
    graph1 = cluster.get_left_child().get_elements()[0]
    graph2 = cluster.get_right_child().get_elements()[0]
    new_graph = None
    if matching_algorithm == "bk":
        new_graph = recursive_matching_using_bk(graphs, number_cliques, anchor, pivot_mode)
    if matching_algorithm == "mb":
        mb_state = MB_State(graph1, graph2)
        new_graph = mb_state.mb_algorithm()
    cluster.set_elements([new_graph])
    cluster.set_children(None, None)
    return new_graph


if __name__ == '__main__':

    # Command line parsing
    try:
        args = parse_command_line()
    except IOError:
        print("An error occured trying to read the file!")

    if args.syntax is not None:
        raise SyntaxError("Please use proper syntax, use '-h' for more information!")

    #  Initialising list of graphs
    graphs = []

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
            print(len(graphs))
        except IOError:
            print("Invalid number of arguments for random cluster graph building!")
        except ValueError:
            print("invalid type of arguments for random cluster graph building!")

    # If neither input file(s) not random graph options are given, raise Error. Else, parse input!
    elif not args.input and not args.random_graph and not args.random_cluster:
        raise FileNotFoundError("Please provide input file(s) with preceding '-i' statement!")
    else:
        #graphs = [] #  TODO: Initialise one level above and append randomly generated graphs to this list too!
        direction = None
        for i in range(len(args.input)):

            # If input argument is neither a valid path nor a file in the current working directory. If, raise
            # FileNotFoundError.
            if not os.path.isdir(os.path.dirname(args.input[i])) and not os.path.exists(args.input[i]):
                raise FileNotFoundError("No such file with given path or filename!")

            # If input argument is a not a full path, add current working directory. Else, take what's given.
            if not os.path.isdir(os.path.dirname(args.input[i])):
                file_path = os.path.abspath(args.input[i])
            else:
                file_path = args.input

            # Log statement for the console about the input file
            print("Input file path of file " + str(i) + ": " + file_path)

            graph = parser(file_path)
            if direction is None:
                direction = graph.get_is_directed()
            if direction != graph.get_is_directed():
                raise Exception("Input graphs have to be either all directed or all undirected!")
            graphs.append(graph)

    # Dev Log statement for graph checking
    # print(graph)

    # Log statement for the console about the Pivot Mode!
    if args.pivot_mode is None:
        print("Pivot Mode: None")
    else:
        print("Pivot Mode: " + args.pivot_mode)

    # Checking for an anchor graph file and checking anchor for clique property. Anchor default is a list.
    # Log statement for the console about the anchor file!
    if isinstance(args.anchor, list):
        anchor = []
        print("Anchor File: --")
    else:
        # If input argument is neither a valid path nor a file in the current working directory. If, raise
        # FileNotFoundError.
        if not os.path.isdir(os.path.dirname(args.anchor)) and not os.path.exists(args.anchor):
            raise FileNotFoundError("No such file with given path or filename!")
        # If anchor argument is a not a full path, add current working directory. Else, take what's given.
        if not os.path.isdir(os.path.dirname(args.anchor)):
            file_path = os.path.abspath(args.anchor)
        else:
            file_path = args.anchor
        anchor_graph = parser(file_path)
        if not anchor_graph.check_clique_properties():
            raise Exception("Anchor is not a clique nor empty!")
        anchor = anchor_graph.get_list_of_vertices()
        print("Anchor File: " + args.anchor)

    # Checking for bron-kerbosch option
    if args.bron_kerbosch:
        print(len(graphs))
        if len(graphs) != 1:
            raise Exception("For clique finding via bron-kerbosch, please provide exactly one file path of a graph!")
        else:
            bk_graph_name = graphs[0].get_name()
            clique_finding_result = graphs[0].bron_kerbosch(anchor, graphs[0].get_list_of_vertices(), [],
                                                            pivot=args.pivot_mode)
            # TODO: Clique selection
            selected_cliques = clique_finding_result
            # Log statement for the console about Bron-Kerbosch
            print("Clique finding via Bron-Kerbosch...")

    # Checking for modular product option
    if args.modular_product:
        if len(graphs) != 2:
            raise Exception("For formation of the modular product, please provide exactly two files containing a graph "
                            "each!")
        else:
            graph1_name = graphs[0].get_name()
            graph2_name = graphs[1].get_name()
            graph = modular_product(graphs[0], graphs[1])
            # Log statement for the console about the modular product
            print("Modular Product of " + graph1_name + " and " + graph2_name + " was calculated!")
            # Dev Log statement for modular product graph checking
            # print(graph)

    # Checking for graph alignment option. This option performs graph alignment of a number of graphs given as input
    # files. The matching order is the order in which the graph file names were provided unless guide_tree option is
    # selected. Then, either a guide tree is constructed via UPGMA (default) using graph density as comparison attribute
    # (default), otherwise a given newick string will be parsed into a guide tree (graph names must be unique!).
    # Matching is done either by forming the modular product and performing bron-kerbosch-algorithm or by the
    # matching-based VF2 algorithm (Cordella et al.)!
    if args.graph_alignment == []:
        raise Exception("For graph alignment, please choose matching method!")
    if args.graph_alignment and args.guide_tree:
        if args.graph_alignment[0] not in ["bk", "mb"]:
            raise Exception("Illegal identifier for matching algorithm!")
        if args.graph_alignment[0] == "bk":
            try:
                i = int(args.graph_alignment[1])
                if i < 1:
                    raise Exception("Illegal value for the number of cliques to expand search on!")
            except IndexError("Please provide value for the number of cliques to expand search on!"):
                pass
            except ValueError("Illegal value for the number of cliques to expand search on!"):
                pass
        if args.guide_tree[-7:] == ".newick":
            cluster_tree = parse_newick_file_into_tree(args.guide_tree, graphs)
        elif args.guide_tree not in ["density"]:      # Other comparison function/attributes may be added
            raise Exception("Illegal identifier for comparison function!")
        else:
            cluster_tree = upgma(density, graphs)
        graph = recursive_matching(cluster_tree, args.graph_alignment[0], anchor, args.pivot_mode,
                                   int(args.graph_alignment[1]))
    elif args.graph_alignment:
        if args.graph_alignment[0] not in ["bk", "mb"]:
            raise Exception("Illegal identifier for matching algorithm!")
        if args.graph_alignment[0] == "bk":
            try:
                i = int(args.graph_alignment[1])
                if i < 1:
                    raise Exception("Illegal value for the number of cliques to expand search on!")
            except IndexError("Please provide value for the number of cliques to expand search on!"):
                pass
            except ValueError("Illegal value for the number of cliques to expand search on!"):
                pass
            graph = recursive_matching_using_bk(graphs, int(args.graph_alignment[1]), anchor, args.pivot_mode)
        if args.graph_alignment[0] == "mb":
            graph = graphs[0]
            for i in range(len(graphs) - 1):
                graph2 = graphs[i + 1]
                if graph2.get_number_of_vertices() > graph.get_number_of_vertices():
                    graph, graph2 = graph2, graph
                mb_state = MB_State(graph, graph2)
                print("Performing Cordella...\n")
                graph = mb_state.mb_algorithm()
    elif args.guide_tree:
        cluster_tree = upgma(density, graphs)
        newick = guide_tree_to_newick(cluster_tree)

    # Checking for output option.
    # If no argument is provided (default = 0), graph will be saved using its name attribute
    # and the current working directory. Considers case when only a guide tree that has been computed should be saved.
    if args.output_file is not None:
        if args.guide_tree and not args.graph_alignment:
            save_newick(newick, args.output_file)
        else:
            graph.save_to_txt(args.output_file)
            # If bron-kerbosch option was selected, selected cliques from the result will be saved with default name of
            # the graph plus a counter as identifier (e.g. 'GraphName_Clique_23').
            try:
                for i in range(len(selected_cliques)):
                    graph_from_clique = retrieve_graph_from_clique(selected_cliques[i], graphs[0].get_mapping(), graphs[0])
                    graph_from_clique.save_to_txt(bk_graph_name + "_Clique_" + str(i + 1))
            except NameError:
                pass



# TODO: In graph alignment only the biggest clique from bron-kerbosch result is considered... overthink!
# TODO: Consider a vertex dictionary instead of list, with ids as keys, for better performance
# TODO: Performing bron-kerbosch on a modular product which has been read from .graph file and saving the resulting
# cliques is not possible unless the matching can be saved as well --> Consider saving the matching in the vertex label
# TODO: Help message auf vordermann bringen...
