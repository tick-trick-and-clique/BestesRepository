from Neo4j import NEO4J
from Vertex import VERTEX
from Edge import EDGE
from Graph import GRAPH

def parse_graph(file, neo4j, no_h_atoms):
    """
    Parsing the .graph format to the class Graph
    """
    deleted_vertices = []
    deleted_edges = []
    # Extract information from file
    with open(file, "r") as f:
        # Read header part
        print("Parsing input file")
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

        #if no edges and no vertices 
        if number_vertices == 0 and number_edges == 0:
            vertices: List[string] = []
            edges: List[string] = []
        #if no vertices but edges
        elif number_vertices == 0:
            print("no vertices")
            vertices = []
            # read empty line
            empty = f.readline()
            if empty != "\n":
                raise Exception("Wrong input file format!")
            try:
                lastlines = f.readlines()
                edges = []
                for elem in lastlines:
                    if no_h_atoms:
                        if elem.rstrip().split(";")[1] == "1":
                            deleted_edges.append(elem.rstrip().split(";")[0])
                            pass
                        else:
                            edges.append(elem.rstrip())
                    else:
                        edges.append(elem.rstrip())
            except IOError:
                print("Wrong input file format: Mistake in edges part.")
            if no_h_atoms:
                print("number edges" + str(number_edges))
                number_edges = number_edges - len(deleted_edges) 
                print("number deleted edges "+ str(len(deleted_edges)))
                print("new number_edges" + str((number_edges)))
        #if no edges but vertices
        elif number_edges == 0:
            edges = []
            # read empty line
            empty = f.readline()
            if empty != "\n":
                raise Exception("Wrong input file format!")
            try:
                lastlines = f.readlines()
                vertices = []
                for elem in lastlines:
                    if no_h_atoms:
                        if elem.rstrip().split(";")[1] == "1":
                            deleted_vertices.append(elem.rstrip().split(";")[0])
                            pass
                        else:
                            vertices.append(elem.rstrip())
                    else:
                        vertices.append(elem.rstrip())
            except IOError:
                print("Wrong input file format: Mistake in vertices part.")
            if no_h_atoms:
                print("number vertices" + str(number_vertices))
                number_vertices = number_vertices - len(deleted_vertices)
                print("number deleted vertices "+ str(len(deleted_vertices)))
                print("new number_vertices" + str((number_vertices)))
        else:
            # read empty line
            empty = f.readline()
            if empty != "\n":
                raise Exception("Wrong input file format!")
            # read vertices part
            try:
                newline = f.readline()
                vertices = []
                while newline != "\n":
                    if no_h_atoms:
                        if newline.rstrip().split(";")[1] == "1":
                            deleted_vertices.append(newline.rstrip().split(";")[0])
                            pass
                        else:
                            vertices.append(newline.rstrip())
                    else:
                        vertices.append(newline.rstrip())
                    newline = f.readline()
            except IOError:
                print("Wrong input file format: Mistake in vertices part.")
            # read empty line
            if newline != "\n":
                raise Exception("Wrong input file format!")
            if no_h_atoms:
                print("number vertices" + str(number_vertices))
                number_vertices = number_vertices - len(deleted_vertices)
                print("number deleted vertices "+ str(len(deleted_vertices)))
                print("new number_vertices" + str((number_vertices)))
            # read edges part
            try:
                lastlines = f.readlines()
                edges = []
                for elem in lastlines:
                    if no_h_atoms:
                        # prüfen ob start oder endknoten teil von deleted_vertices ist 
                        start= elem.rstrip().split(";")[0]
                        end = elem.rstrip().split(";")[1]
                        if start in deleted_vertices or end in deleted_vertices:
                            deleted_edges.append(elem.rstrip())
                            pass
                        else:
                            edges.append(elem.rstrip())
                    else:
                        edges.append(elem.rstrip())
            except IOError:
                print("Wrong input file format: Mistake in edges part.")
            #change number_edges 
            if no_h_atoms:
                print("number edges" + str(number_edges))
                number_edges = number_edges - len(deleted_edges)
                print("number deleted edges "+ str(len(deleted_edges)))
                print("new number_edges" + str((number_edges)))
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
        neo4jProjekt = NEO4J(neo4j[0], neo4j[1], neo4j[2], vertices_objects, edges_objects, graph_name, False)
    
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