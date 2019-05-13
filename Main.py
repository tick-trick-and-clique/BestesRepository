'''
Created on 07.05.2019

@author: chris
'''
import sys
from Graph import GRAPH
from Vertex import VERTEX
from Edge import EDGE
from Command_Line_Parser import parse_command_line
from Modulares_Produkt import modular_product

def parser(file):
    """
    Parsing the .graph format to the class Graph
    """
    with open(file,"r") as f:
        #Read header part
        try:
            number_vertices = int(f.readline().split(";")[1].rstrip())
            number_edges = int(f.readline().split(";")[1].rstrip())
            vertices_labelled = f.readline().split(";")[1].rstrip()
            vertices_labelled = check_true_or_false(vertices_labelled)
            edges_labbelled = f.readline().split(";")[1].rstrip()
            edges_labbelled = check_true_or_false(edges_labbelled)
            directed_graph = f.readline().split(";")[1].rstrip()
            directed = check_true_or_false(directed_graph)
        except:
            raise Exception("Wrong input file format: Mistake in header part.")
        #read empty line
        empty = f.readline()
        if empty is not "\n":
            raise Exception("Wrong input file format!")
        #read vertices part
        try:
            newline = f.readline()
            vertices = []
            while newline is not "\n":
                vertices.append(newline.rstrip())
                newline = f.readline()
        except:
            raise Exception("Wrong input file format: Mistake in vertices part.")
        #read empty line
        if newline is not "\n":
            raise Exception("Wrong input file format!")
        #read edges part
        try:
            lastlines = f.readlines()
            edges = []
            for elem in lastlines:
                edges.append(elem.rstrip())
        except:
            raise Exception("Wrong input file format: Mistake in edges part.")

    f.close()

    #save vertices as objects
    vertices_objets = []
    for vertex in vertices:
        if vertices_labelled: #if vertices are labelled
            vertex_splitted = vertex.split(";")
            if len(vertex_splitted) == 1:
                raise Exception("Wrong format: Vertices should be labelled but arent.")
            vertices_objets.append(VERTEX([vertex_splitted[0]],vertex_splitted[1]))
        else: #if vertices arent labelled
            vertex_splitted = vertex.split(";")
            if len(vertex_splitted) == 2:
                raise Exception("Wrong format: Vertices are labelled but header dont say so.")
            vertices_objets.append(VERTEX([vertex],""))

    #save edges as objects
    edges_objects = []
    identifier = 1 #each edge gets an id
    for edge in edges:
        edge_splitted = edge.split(";")
        #search for start vertex in vertices_objects and for end vertex
        start_and_end = [item for item in vertices_objets if (item.get_id() == [edge_splitted[0]])] \
                        + [item for item in vertices_objets if (item.get_id() == [edge_splitted[1]])]
        check_start_end_in_vertices(start_and_end, edge) #check if start and end vertex are in vertices list
        end_and_start = [item for item in vertices_objets if (item.get_id() == [edge_splitted[1]])] \
                        + [item for item in vertices_objets if (item.get_id() == [edge_splitted[0]])]

        if edges_labbelled: #if edges are labelled
            if len(edge_splitted) == 2:
                raise Exception("Wrong format: Edges should be labelled but arent.")
            if directed: #if graph is directed
                edges_objects.append(EDGE(identifier,start_and_end,edge_splitted[2]))
                identifier += 1
            else:  #if graph is undirected, insert both edges automtically
                edges_objects.append(EDGE(identifier,start_and_end,edge_splitted[2]))
                identifier += 1
                edges_objects.append(EDGE(identifier,end_and_start,edge_splitted[2]))
                identifier += 1
        else: #if edges arent labelled
            if len(edge_splitted) == 3:
                raise Exception("Wrong format: Edges are labelled but header dont say so.")
            if directed: #if graph is directed
                edges_objects.append(EDGE(identifier,start_and_end,""))
                identifier += 1
            else: #if graph is undirected, insert both edges automtically
                edges_objects.append(EDGE(identifier,start_and_end,""))
                identifier += 1
                edges_objects.append(EDGE(identifier,end_and_start,""))
                identifier += 1

    #Testing header fits actual number of vertices and edges
    if not len(vertices_objets) == number_vertices:
        raise Exception("Number of vertices doesn't fit predicted number in header!")
    if not directed:
        if not len(edges_objects)/2 == number_edges:
            raise Exception("Number of edges doesn't fit predicted number in header!")
    else:
        if not len(edges_objects) == number_edges:
            raise Exception("Number of edges doesn't fit predicted number in header!")

    #neighbours setting
    for vertex in vertices_objets:
        for edge in edges_objects:
            if edge.get_start_and_end()[0].get_id() == vertex.get_id():
                neighbour = edge.get_start_and_end()[1]
                vertex.append_neighbour(neighbour)

    #create graph from class GRAPH
    graph = GRAPH("graph",vertices_objets,edges_objects,number_vertices,number_edges,directed)
    return graph

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

    try:
        file = sys.argv[1]
        g1 = parser(file)
        g1.set_name("my cute Graphy MC Graphface")

        print(str(g1))

        file = sys.argv[2]
        g2 = parser(file)
        g2.set_name("Badass Graph")

        print(str(g2))



    except IOError:
        print("shit")


    #mod = modular_product(g1,g1)

    #print(str(mod))

    #print(mod.bron_kerbosch([],mod.get_list_of_vertices(),[]))

    print(g1.bron_kerbosch_pivot([],g1.get_list_of_vertices(),[]))



    '''
    try:
        file = sys.argv[1]
        graph = parser(file)
    except IOError:
        print('An error occured trying to read the file.')

    try:
        args = parse_command_line()
        print(args.input_file)
        print(args)
    except IOError:
        print("An error occured trying to read the file!")
    graph = parser(args.input_file)
    if args.modular_product is not None:
        second_graph = parser(args.modular_product)
        graph_result = modular_product(graph, second_graph)
    if args.bron_kerbosch:
        clique_finding_result = graph.bron_kerbosch_pivot(args.anchor, graph.get_list_of_vertices(), [],
                                                          pivot=args.pivot_mode)
    # if args.output_file:
        # Code to be added
    if args.graph_alignment is not None:
        second_graph = parser(args.graph_alignment)
        graph_result = modular_product(graph, second_graph)
        graph_result.bron_kerbosch_pivot(args.anchor, graph.get_list_of_vertices(), [], pivot=args.pivot_mode)
    '''