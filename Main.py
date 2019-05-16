'''
Created on 07.05.2019

@author: chris
'''
import os
from Graph import GRAPH
from Vertex import VERTEX
from Edge import EDGE
from Command_Line_Parser import parse_command_line
from Modulares_Produkt import modular_product
from Graph_Builder import buildRndGraph
from MP_Vertex import modular_product_MP_VERTEX


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
    
    vertices_objets = []
    if number_vertices != 0:
        # save vertices as objects
        for vertex in vertices:
            if vertices_labelled:  # if vertices are labelled
                vertex_splitted = vertex.split(";")
                if len(vertex_splitted) == 1:
                    raise Exception("Wrong format: Vertices should be labelled but arent.")
                vertices_objets.append(VERTEX([vertex_splitted[0]], vertex_splitted[1]))  # id consits of a list because
                # of modular product
            else:  # if vertices arent labelled
                vertex_splitted = vertex.split(";")
                if len(vertex_splitted) == 2:
                    raise Exception("Wrong format: Vertices are labelled but header doesn't say so.")
                vertices_objets.append(VERTEX([vertex], ""))

    # save edges as objects
    edges_objects = []
    if number_edges != 0:
        identifier = 1  # each edge gets an id
        for edge in edges:
            edge_splitted = edge.split(";")
            # search for start vertex in vertices_objects and for end vertex
            start_and_end = [item for item in vertices_objets if (item.get_id() == [edge_splitted[0]])] \
                            + [item for item in vertices_objets if (item.get_id() == [edge_splitted[1]])]
            check_start_end_in_vertices(start_and_end, edge)  # check if start and end vertex are in vertices list
            end_and_start = [item for item in vertices_objets if (item.get_id() == [edge_splitted[1]])] \
                            + [item for item in vertices_objets if (item.get_id() == [edge_splitted[0]])]
    
            if edges_labbelled:  # if edges are labelled
                if len(edge_splitted) == 2:
                    raise Exception("Wrong format: Edges should be labelled but aren't.")
                if directed:    # if graph is directed
                    edges_objects.append(EDGE(identifier, start_and_end, edge_splitted[2]))
                    identifier += 1
                else:   # if graph is undirected, insert both edges automatically
                    edges_objects.append(EDGE(identifier, start_and_end, edge_splitted[2]))
                    identifier += 1
                    edges_objects.append(EDGE(identifier, end_and_start, edge_splitted[2]))
                    identifier += 1
            else:   # if edges aren't labelled
                if len(edge_splitted) == 3:
                    raise Exception("Wrong format: Edges are labelled but header dont say so.")
                if directed:  # if graph is directed
                    edges_objects.append(EDGE(identifier, start_and_end, ""))
                    identifier += 1
                else:   # if graph is undirected, insert both edges automatically
                    edges_objects.append(EDGE(identifier, start_and_end, ""))
                    identifier += 1
                    edges_objects.append(EDGE(identifier, end_and_start, ""))
                    identifier += 1

    # Testing header fits actual number of vertices and edges
    if not len(vertices_objets) == number_vertices:
        raise Exception("Number of vertices doesn't fit predicted number in header!")
    if not directed:
        if not len(edges_objects)/2 == number_edges:
            raise Exception("Number of edges doesn't fit predicted number in header!")
    else:
        if not len(edges_objects) == number_edges:
            raise Exception("Number of edges doesn't fit predicted number in header!")

    # neighbours setting
    for vertex in vertices_objets:
        for edge in edges_objects:
            if edge.get_start_and_end()[0].get_id() == vertex.get_id():
                neighbour = edge.get_start_and_end()[1]
                vertex.append_neighbour(neighbour)

    # create graph from class GRAPH
    return GRAPH("graph", vertices_objets, edges_objects, number_vertices, number_edges, directed,
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
        raise Exception("One or both vertices of edge: " + currentEdge + " doenst exist in list of vertices")
    return


if __name__ == '__main__':

    # Command line parsing
    try:
        args = parse_command_line()
    except IOError:
        print("An error occured trying to read the file!")

    # The first command line arguments should either be a file (path) name (1 argument) or the two necessary parameters
    # for random graph building (2 arguments) with the third parameter (directed/undirected) being optional. 4 or more
    # arguments are illegal.

    # Too many arguments:
    third_arg = False
    if len(args.input_file) > 3:
        raise IOError("Illegal number of arguments!")
    # 0 Arguments:
    elif len(args.input_file) == 0:
        raise IOError("Please provide either a file (path) name or vertex number and connection probability for "
                      "random graph building")

    # 1 Argument:
    # If input_file argument is neither a valid path nor a file in the current working directory. If, raise
    # FileNotFoundError.
    elif len(args.input_file) == 1:
        if not os.path.isdir(os.path.dirname(args.input_file[0])) \
                and not os.path.exists(args.input_file[0]):
            raise FileNotFoundError("No such file with given path or filename!")

        # If input_file argument is a not a full path, add current working directory. Else, take what's given.
        if not os.path.isdir(os.path.dirname(args.input_file[0])):
            input_file = os.path.abspath(args.input_file[0])
        else:
            input_file = args.input_file

        # Log statement for the console about the input file
        print("First input file path: " + input_file)

        # Graph parsing
        graph = parser(input_file)

    # 3 Arguments:
    # Random graph building, third Argument mus be either 'true' or 'false'
    elif len(args.input_file) == 3:
        if not args.input_file[2] == "true" and not args.input_file[2] == "false":
            raise ValueError("Third positional argument must be either 'true' or 'false'!")
        third_arg = (args.input_file[2] == "true")

    # 2 Arguments:
    # Random graph building, arguments must be integer and real number, respectively.
    if len(args.input_file) >= 2:
        try:
            int(args.input_file[0])
        except ValueError:
            print("Provide integer value for the number of vertices for random graph building!")
        try:
            float(args.input_file[1])
        except ValueError:
            print("Provide real number for the connection probability for random graph building!")
        graph = buildRndGraph(int(args.input_file[0]), float(args.input_file[1]), directed=third_arg)

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
        anchor_graph = parser(args.anchor)
        if not anchor_graph.check_clique_properties():
            raise Exception("Anchor is not a clique nor empty!")
        if not anchor_graph.check_partial_graph_of(graph):
            raise Exception("Anchor is not a partial graph of the input graph!")
        anchor = anchor_graph.get_list_of_vertices()
        print("Anchor File: " + args.anchor)

    # Checking for modular product option
    if args.modular_product is not None:
        second_graph = parser(args.modular_product)
        graph1_name = graph.get_name()
        graph2_name = second_graph.get_name()
        graph = modular_product_MP_VERTEX(graph, second_graph)

        # Log statement for the console about the modular product
        print("Second input file path/name: " + args.modular_product)
        print("Modular Product of " + graph1_name + " and " + graph2_name + " was calculated!")

        # Dev Log statement for modular product graph checking
        print(graph)

    # Checking for bron-kerbosch option
    if args.bron_kerbosch:
        clique_finding_result = graph.bron_kerbosch(anchor, graph.get_list_of_vertices(), [], pivot=args.pivot_mode)

        # Log statement for the console about Bron-Kerbosch
        print("Clique finding via Bron-Kerbosch...")

    # Checking for graph alignment option. This option performs the modular product AND bron-kerbosch!
    if args.graph_alignment is not None:
        second_graph = parser(args.graph_alignment)
        graph1_name = graph.get_name()
        graph2_name = second_graph.get_name()
        graph = modular_product_MP_VERTEX(graph, second_graph)

        # Log statement for the console about the modular product
        print("Second input file path/name: " + args.graph_alignment)
        print("Modular Product of " + graph1_name + " and " + graph2_name + " was calculated!")

        # Dev Log statement for graph checking
        print(graph)

        clique_finding_result = graph.bron_kerbosch(anchor, graph.get_list_of_vertices(), [], pivot=args.pivot_mode)
        # Log statement for the console about Bron-Kerbosch
        print("Clique finding via Bron-Kerbosch...")

    # Checking for output option.
    # If no argument is provided (default = 0), graph will be saved using its name attribute
    # and the current working directory.
    if args.output_file is not None:
        if args.output_file == 0:
            graph.save_to_txt()
        else:
            graph.save_to_txt(args.output_file)
