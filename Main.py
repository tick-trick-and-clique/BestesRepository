'''
Created on 07.05.2019

@author: chris
'''
import os, string, random, itertools
from Graph import GRAPH, density, retrieve_graph_from_clique, retrieve_original_subgraphs
from Vertex import VERTEX
from Edge import EDGE
from Command_Line_Parser import parse_command_line
from Modulares_Produkt import modular_product
from Graph_Builder import buildRndGraph
from MB_State import MB_State
from GuideTree import upgma, guide_tree_to_newick, save_newick, parse_newick_file_into_tree
from Neo4j import NEO4J


def parser(file, neo4j):
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
        if not len(edges_objects) / 2 == number_edges or len(edges_objects) == number_edges:
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
    
    # create Neo4J View
    if neo4j:
        neo4jProjekt = NEO4J("http://localhost:7474/db/data/", "neo4j", "1234", vertices_objects, edges_objects, graph_name)
    
    # create graph from class GRAPH
    graph = GRAPH(graph_name, vertices_objects, edges_objects, number_vertices, number_edges, directed,
                 is_labeled_nodes=vertices_labelled, is_labeled_edges=edges_labbelled)

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


def matching_using_bk(graph_left, graph_right, number_cliques, pivot, anchor_graph_parameters):
    """
    Helper function for graph alignment using bron-kerbosch algorithm. Takes two graphs and other bron-kerbosch
    matching parameters as input to perform graph alignment. 'number_cliques' specifies the maximum number of cliques
    that will be return as GRAPH object.
    Return type: [GRAPH, ...]
    """
    result = []
    if anchor_graph_parameters:
        if graph_left.get_name() == anchor_graph_parameters[1]:
            mp, anchor = modular_product(graph_left, graph_right, anchor_graph_parameters=anchor_graph_parameters)
        elif graph_right.get_name() == anchor_graph_parameters[1]:
            mp, anchor = modular_product(graph_right, graph_left, anchor_graph_parameters=anchor_graph_parameters)
    mp, anchor = modular_product(graph_left, graph_right)
    # Log statement for the console about Bron-Kerbosch
    print("Clique finding via Bron-Kerbosch...")
    clique_findings = mp.bron_kerbosch(anchor, mp.get_list_of_vertices(), [], pivot=pivot)
    duplicates_removed = []
    for clique in clique_findings:
        clique = sorted(clique, key=lambda x: x.get_id())
        duplicates_removed.append(tuple(clique))
    clique_findings = list(set(duplicates_removed))  # removes duplicates
    clique_findings.sort(key=lambda x: len(x), reverse=True)
    number_cliques = min(len(clique_findings), number_cliques)
    clique_findings = clique_findings[:number_cliques]
    for j in range(number_cliques):
        new_clique_as_graph = retrieve_graph_from_clique(clique_findings[j], graph_left)
        result.append(new_clique_as_graph)
    return result


def matching_using_mb(graph_left, graph_right):
    """
    Helper function for graph alignment using matching-based algorithm. Takes two graphs as input.
    Return type: [GRAPH, ...]
    """
    result = []
    if graph_left.get_number_of_vertices() >= graph_right.get_number_of_vertices():
        graph1 = graph_left
        graph2 = graph_right
    else:
        graph1 = graph_right
        graph2 = graph_left
    mb_state = MB_State(graph1, graph2)
    result_as_mappings = mb_state.mb_algorithm()
    for mapping in result_as_mappings:
        result.append(mb_mapping_to_graph(mapping, graph1, graph2))
    return result


def recursive_matching(cluster, matching_algorithm, pivot, number_cliques, anchor_graph_parameters=None, smaller=0.0):
    """
    Performs graph alignment according to the guide tree in 'cluster' and the given matching algorithm.
    'number_cliques' specifies the maximum number of cliques that will be considered for further graph alignment.
    Return type: [GRAPH, ...]
    """
    # If the children are not tree leaves (i.e. grandchildren exist), then call function for these children.
    # Left child.
    if cluster.get_left_child().children_exist():
        recursive_matching(cluster.get_left_child(), matching_algorithm, pivot, number_cliques)
    # Right child.
    if cluster.get_right_child().children_exist():
        recursive_matching(cluster.get_right_child(), matching_algorithm, pivot, number_cliques)
    # Else, the cluster is the root of two leaves, then:
    # Perform graph matching of the two leaf graphs (use the matching method provided by user)
    # Update the cluster with one new leaf, deleting the previous two
    # Return to the upper recursion level
    graphs_left = cluster.get_left_child().get_elements()
    graphs_right = cluster.get_right_child().get_elements()
    new_graphs = []
    if matching_algorithm == "bk":
        for gl in graphs_left:
            for gr in graphs_right:
                new_graphs += matching_using_bk(gl, gr, number_cliques, pivot,
                                                anchor_graph_parameters=anchor_graph_parameters)
    if matching_algorithm == "mb":
        for gl in graphs_left:
            for gr in graphs_right:
                new_graphs += matching_using_mb(gl, gr)
                if smaller:
                    if gl.get_number_of_vertices() < gr.get_number_of_vertices():
                        gl, gr = gr, gl
                    grn = gr.get_number_of_vertices()
                    margin = int(grn * smaller)
                    new_gs = []
                    combinations = []
                    for i in range(margin):
                        combinations += itertools.combinations(gr.get_list_of_vertices(), grn - i - 1)
                    for c in combinations:
                        new_g = gr.graph_from_vertex_combination(c)
                        new_gs.append(new_g)
                        for new_gr in new_gs:
                            new_graphs += matching_using_mb(gl, new_gr)
    cluster.set_elements(new_graphs)
    cluster.set_children(None, None)
    return new_graphs


def mb_mapping_to_graph(result_as_mapping, graph1, graph2):
    """
    Helper function for graph alignment using matching-based algorithm. Takes a mapping of the ID of vertices of
    'graph1' as key and the ID of vertices of 'graph2' as value. A GRAPH object is constructed with vertex IDs, vertex
    labels, edge IDs, edge labels, __is_directed attribute, __is_labelled_nodes attribute and __is_labelled_edges
    attribute taken from graph1 (so far!). A 8-letter random graph name is used. Each vertex of the new graph contains
    the mappings of the vertex of 'graph1' with the same ID and of its mapping partner in 'graph2'.
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
                        new_v1.append_neighbour(new_v2)
        graph_name = [random.choice(string.ascii_letters) for n in range(8)]
        graph = GRAPH(graph_name, lov, loe, len(lov), len(loe), graph1.get_is_directed(),
                      graph1.get_is_labelled_nodes(), graph1.get_is_labelled_edges())
    return graph


def import_file(filename):
    if not os.path.isdir(os.path.dirname(filename)) and not os.path.exists(filename):
        raise FileNotFoundError("No such file with given path or filename!")
    if not os.path.isdir(os.path.dirname(filename)):
        file_path = os.path.abspath(filename)
    else:
        file_path = args.input
    return


if __name__ == '__main__':

    # Command line parsing
    try:
        args = parse_command_line()
    except IOError("An error occured trying to read the file!"):
        args = None

    if args.syntax:
        raise SyntaxError("Please use proper syntax, use '-h' for more information!")

    # Initialization of necessary variables
    graph = None
    input_graphs = []
    selected_subgraphs = []
    anchor = []

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
        raise FileNotFoundError("Please provide input file(s) with preceding '-i' statement!")
    else:
        if args.random_graph and graph:
            input_graphs.append(graph)
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

            graph = parser(file_path, args.neo4j)
            if direction is None:
                direction = graph.get_is_directed()
            if direction != graph.get_is_directed():
                raise Exception("Input graphs have to be either all directed or all undirected!")
            input_graphs.append(graph)

    # Log statement for the console about the Pivot Mode!
    if args.pivot is None:
        print("Pivot Mode: None")
    else:
        print("Pivot Mode: " + args.pivot)

    # Checking for an anchor graph file and checking anchor for clique property. Anchor default is a list.
    # Log statement for the console about the anchor file!
    """
    if isinstance(args.anchor, list):
        print("Anchor File: --")
    else:
    """
    if not args.anchor:
        anchor_graph = None
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
        anchor_graph = parser(file_path, args.neo4j)
        if not anchor_graph.check_clique_properties() and args.bron_kerbosch:
            raise Exception("Anchor is not a clique nor empty! For clique finding on a modular product using an anchor "
                            "pass a subgraph of the modular product which is a clique!")
        elif args.bron_kerbosch:
            if len(input_graphs) != 1:
                raise Exception("For clique finding via bron-kerbosch, "
                                "please provide exactly one file path of a graph!")
            else:
                anchor = []
                for anchor_vertex in anchor_graph.get_list_of_vertices():
                    for input_vertex in input_graphs[0].get_list_of_vertices():
                        if anchor_vertex.get_id() == input_vertex.get_id():
                            anchor.append(input_vertex)
        print("Anchor File: " + args.anchor)

    # Checking for bron-kerbosch option
    if args.bron_kerbosch:
        if len(input_graphs) != 1:
            raise Exception("For clique finding via bron-kerbosch, please provide exactly one file path of a graph!")
        else:
            selected_cliques = input_graphs[0].bron_kerbosch(anchor, input_graphs[0].get_list_of_vertices(), [],
                                                             pivot=args.pivot)
            duplicates_removed = []
            for clique in selected_cliques:
                clique = sorted(clique, key=lambda x: x.get_id())
                duplicates_removed.append(tuple(clique))
            selected_cliques = list(set(duplicates_removed))                # removes duplicates
            selected_cliques.sort(key=lambda x: len(x), reverse=True)
            for i in range(len(selected_cliques)):
                matching_graph = retrieve_graph_from_clique(selected_cliques[i], input_graphs[0])
                original_subgraph = retrieve_original_subgraphs(matching_graph, input_graphs)
                selected_subgraphs.append(original_subgraph)
            # Log statement for the console about Bron-Kerbosch
            print("Clique finding via Bron-Kerbosch...")

    # Checking for modular product option
    if args.modular_product:
        if len(input_graphs) != 2:
            raise Exception("For formation of the modular product, please provide exactly two files containing a graph "
                            "each!")
        else:
            graph1_name = input_graphs[0].get_name()
            graph2_name = input_graphs[1].get_name()
            graph, anchor = modular_product(input_graphs[0], input_graphs[1])
            # if args.neo4j:
                # neo4jProjekt = NEO4J("http://localhost:7474/db/data/", "neo4j", "1234")
                # neo4jProjekt.create_graphs(neo4jProjekt.get_graph(), graph.get_list_of_vertices(), graph.get_list_of_edges(),graph.get_name())
            
            # Log statement for the console about the modular product
            print("Modular Product of " + graph1_name + " and " + graph2_name + " was calculated!")

    if isinstance(args.guide_tree, list) and len(args.guide_tree) == 0:
        raise Exception("For guide tree construction, please pass either a .newick file, a built-in comparison function"
                        " or 'custom <file.py>' for introducing you own comparison function!")
    # Checking for graph alignment option. This option performs graph alignment of a number of graphs given as input
    # files. The matching order is according to the guide tree option (passing a comaprison function or a '.newick' file
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
            if len(args.graph_alignment) == 2:
                try:
                    i = int(args.graph_alignment[1])
                    if i < 1:
                        raise Exception("Illegal value for the number of cliques to expand search on!")
                except ValueError("Illegal value for the number of cliques to expand search on!"):
                    pass
        if args.graph_alignment[0] == "mb":
            if len(args.graph_alignment) == 2:
                try:
                    smaller = float(args.graph_alignment[1])
                    if smaller <= 0.0 or smaller >= 1.0:
                        raise Exception("Illegal value for the allowed reduction of subgraph size!")
                except ValueError("Illegal value for the allowed reduction of subgraph size!"):
                    pass
        if args.guide_tree and input_graphs:
            if args.guide_tree[0] == "custom":
                pass
                import_file
                # TODO: Code that includes .py
            elif args.guide_tree[0][-7:] == ".newick":
                cluster_tree = parse_newick_file_into_tree(args.guide_tree, input_graphs)
            elif args.guide_tree[0] not in ["density"]:  # Other comparison function/attributes may be added
                cluster_tree = None
                raise Exception("Illegal identifier for comparison function!")
            else:
                cluster_tree = upgma(density, input_graphs, anchor_graph=anchor_graph)
        else:
            cluster_tree = upgma(density, input_graphs, anchor_graph=anchor_graph)
        matching_graphs = recursive_matching(cluster_tree, args.graph_alignment[0], args.pivot, i,
                                             anchor_graph_parameters=[anchor_graph, input_graphs[0].get_name()],
                                             smaller=smaller)
        for matching_graph in matching_graphs:
            if matching_graph:
                original_subgraphs = retrieve_original_subgraphs(matching_graph, input_graphs)
                selected_subgraphs.append(original_subgraphs)

    # If guide tree option is selected, construct a guide using the passed comparison function.
    newick = None
    if args.guide_tree:
        if args.guide_tree[0] == "custom":
            pass
            # TODO: Code that includes .py
        elif args.guide_tree[0][-7:] == ".newick":
            newick = args.guide_tree[0]
        elif input_graphs:
            cluster_tree = upgma(density, input_graphs, anchor_graph=anchor_graph)
            newick = guide_tree_to_newick(cluster_tree)

    # Checking for output options.
    # Output of newick string.
    if args.newick_output:
        if newick is None:
            raise Exception("Select guide tree option to create a newick string to save!")
        else:
            save_newick(newick, output_file=args.newick_output)
    # Output of graph from random graph building or modular product.
    if args.graph_output:
        if graph is None:
            raise Exception("No graph to save in memory!")
        else:
            graph.save_to_txt(output_file=args.graph_output)
            # if args.neo4j:
                # create Neo4J View
                # neo4jProjekt = NEO4J("http://localhost:7474/db/data/", "neo4j", "1234", graph.get_list_of_vertices(),graph.get_list_of_edges(), graph.get_name())
    
    # Output of subgraphs from graph alignment or bron-kerbosch algorithm on a modular product.
    if args.subgraph_output is not None and input_graphs and selected_subgraphs:
        if len(args.subgraph_output) > 2:
            raise Exception("Please provide a maximum of two arguments: First the output file path and second the "
                            "number of subgraphs to be exported!")
        elif len(args.subgraph_output) == 2:
            try:
                subgraph_number = int(args.subgraph_output[1])
                for i in range(min(len(selected_subgraphs), subgraph_number)):
                    for subgraph in selected_subgraphs[i]:
                        subgraph.save_to_txt(output_file=args.subgraph_output[0] + subgraph[i].get_name(), sequential_number=i)
                        # create Neo4J View
                        if args.neo4j:
                            neo4jProjekt = NEO4J("http://localhost:7474/db/data/", "neo4j", "1234",
                                                 subgraph.get_list_of_vertices(), subgraph.get_list_of_edges(),
                                                 subgraph.get_name())
            except ValueError("Please provide an integer value for the number of subgraphs to be exported as second "
                              "argument!"):
                pass
        elif len(args.subgraph_output) == 0:
            for i in range(len(selected_subgraphs)):
                for subgraph in selected_subgraphs[i]:
                    subgraph.save_to_txt(output_file=subgraph.get_name() + "_Subgraph_" + str(i + 1) + ".graph")
                    # create Neo4J View
                    if args.neo4j:
                        neo4jProjekt = NEO4J("http://localhost:7474/db/data/", "neo4j", "1234",
                                             subgraph.get_list_of_vertices(), subgraph.get_list_of_edges(),
                                             subgraph.get_name())
        elif len(args.subgraph_output) == 1:
            try:
                subgraph_number = int(args.subgraph_output[0])
                for i in range(min(len(selected_subgraphs), subgraph_number)):
                    for subgraph in selected_subgraphs[i]:
                        subgraph.save_to_txt(output_file=subgraph.get_name() + "_Subgraph_" + str(i + 1) + ".graph")
                        # create Neo4J View
                        if args.neo4j:
                            neo4jProjekt = NEO4J("http://localhost:7474/db/data/", "neo4j", "1234",
                                                 subgraph.get_list_of_vertices(), subgraph.get_list_of_edges(),
                                                 subgraph.get_name())
            except ValueError:
                for i in range(len(selected_subgraphs)):
                    for subgraph in selected_subgraphs[i]:
                        subgraph.save_to_txt(output_file=args.subgraph_output[0] + subgraph.get_name(), sequential_number=i)
                        # create Neo4J View
                        if args.neo4j:
                            neo4jProjekt = NEO4J("http://localhost:7474/db/data/", "neo4j", "1234",
                                                 subgraph.get_list_of_vertices(), subgraph.get_list_of_edges(),
                                                 subgraph.get_name())
                    
# TODO: Consider a vertex dictionary instead of list, with ids as keys, for better performance
# TODO: Consider different types of multiple alignment strategies concerning comparison of analogue attributes (e.g. a
# specific vertex/edge label); How should those attributes be handled for graphs resulting from the alignment during
# multiple alignments (create a mean value?)?
# TODO: Consider a mapping of edges in multiple alignment as well
# TODO: BK algorithm in graph alignment; until now the largest cliques are used for ongoing alignment, consider a
# different graph attribute for this
# TODO:
# TODO: Define anchor (graph) for matching-based algorithm. Probably need to initialize data structures differently.

# Notes:
# When performing bron-kerbosch on a molecular product as command line input, it is not possible to identify the
# vertices from the original graphs from which the molecular product was formed because this vertex mapping is not
# saved. The mapping cannot be save as ID because concatenation of IDs would not be unique (e.g. ID 123 from vertices
# 12 and 3 or 1 and 23)