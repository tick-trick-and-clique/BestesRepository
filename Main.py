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
from Graph_Builder import buildRndGraph
from MB_State import MB_State
from GuideTree import match_by_guide_tree, upgma, guide_tree_to_newick


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

    f.close()
    vertices_objects = []
    if number_vertices != 0:
        # save vertices as objects
        for vertex in vertices:
            if vertices_labelled:  # if vertices are labelled
                vertex_splitted = vertex.split(";")
                if len(vertex_splitted) == 1:
                    raise Exception("Wrong format: Vertices should be labelled but aren't.")
                vertices_objects.append(VERTEX(int(vertex_splitted[0]), vertex_splitted[1]))
            else:  # if vertices arent labelled
                vertex_splitted = vertex.split(";")
                if len(vertex_splitted) == 2:
                    raise Exception("Wrong format: Vertices are labelled but header doesn't say so.")
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
                if len(edge_splitted) == 3:
                    raise Exception("Wrong format: Edges are labelled but header dont say so.")
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

    # create graph from class GRAPH
    return GRAPH("graph", vertices_objects, edges_objects, number_vertices, number_edges, directed,
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


if __name__ == '__main__':

    # Command line parsing
    try:
        args = parse_command_line()
    except IOError:
        print("An error occured trying to read the file!")

    # Check for random graph option
    if args.random_graph:
        if args.random_graph[2] == "True":
            directed = True
        else:
            directed = False
        try:
            graph = buildRndGraph(int(args.random_graph[0]), float(args.random_graph[1]), directed=directed)
        except IOError:
            print("Invalid number of arguments for random graph building!")
        except ValueError:
            print("invalid type of arguments for random graph building!")

    # If neither input file(s) not random graph option are given, raise Error. Else, parse input!
    elif not args.input and not args.random_graph:
        raise FileNotFoundError("Please provide input file(s)!")
    else:
        graphs = []
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
        if not anchor_graph.check_partial_graph_of(graphs[0]):
            raise Exception("Anchor is not a partial graph of the input graph!")
        anchor = anchor_graph.get_list_of_vertices()
        print("Anchor File: " + args.anchor)

    # Checking for bron-kerbosch option
    if args.bron_kerbosch:
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
    # selected. Then, a guide tree is constructed via UPGMA (default) using graph density as comparison attribute
    # (default). Matching is done either by forming the modular product and performing bron-kerbosch-algorithm or by
    # the matching-based VF2 algorithm (Cordella et al.)!
    if args.graph_alignment and args.guide_tree:
        if args.graph_alignment not in ["bk", "mb"]:
            raise Exception("Illegal identifier for matching algorithm!")
        if args.guide_tree not in ["density"]:      # Other comparison function/attributes may be added
            raise Exception("Illegal identifier for comparison function!")
        graph = match_by_guide_tree(density, graphs, args.graph_alignment, anchor, args.pivot_mode)
    elif args.graph_alignment:
        graph = graphs[0]
        if args.graph_alignment == "bk":
            for i in range(len(graphs) - 1):
                mp = modular_product(graph, graphs[i + 1])
                mapping = mp.get_mapping()
                # Dev Log statement for graph checking
                # print(mp)
                clique_finding_result = mp.bron_kerbosch(anchor, mp.get_list_of_vertices(), [], pivot=args.pivot_mode)
                # Select the biggest clique and retrieve graph
                # TODO: Clique selection
                clique = clique_finding_result[0]
                graph = retrieve_graph_from_clique(clique, mapping, graph)
                # Log statement for the console about Bron-Kerbosch
                print("Clique finding via Bron-Kerbosch...")
        if args.graph_alignment == "mb":
            for i in range(len(graphs)):
                mb_state = MB_State(graph, graphs[i + 1])
                graph = mb_state.mb_algorithm()
    elif args.guide_tree:
        cluster_tree = upgma(density, graphs)
        newick = guide_tree_to_newick(cluster_tree)

    # Checking for output option.
    # If no argument is provided (default = 0), graph will be saved using its name attribute
    # and the current working directory.
    if args.output_file is not None:
        if args.output_file == 0:
            graph.save_to_txt()
        else:
            graph.save_to_txt(args.output_file)
        # If bron-kerbosch option was selected, selected cliques from the result will be saved with default name of the
        # graph plus a counter as identifier (e.g. 'GraphName_Clique_23').
        try:
            for i in range(len(selected_cliques)):
                graph_from_clique = retrieve_graph_from_clique(selected_cliques[i], graphs[0].get_mapping(), graphs[0])
                graph_from_clique.save_to_txt(bk_graph_name + "_Clique_" + str(i + 1))
        except NameError:
            pass
        try:
            pass
            # TODO: Do something to save the newick
        except NameError:
            pass

# TODO: In graph alignment only the biggest clique from bron-kerbosch result is considered... overthink!
# TODO: In graph alignment with VF2 no check whether one of the graphs is partial of the other has been done yet...
# TODO: Introduce integer identifier and mapping for edges, similarly like it has been for vertices already
# TODO: Consider a vertex dictionary instead of list, with ids as keys
# TODO: Performing bron-kerbosch on a modular product which has been read from .graph file and saving the resulting
# cliques is not possible unless the matching can be saved as well.
# TODO: Check that Vertex IDs can be converted to integer when parsing from .graph
# TODO: Check that Edge IDs can be converted to integer when parsing from .graph
# TODO: Test saving guide tree in newick format