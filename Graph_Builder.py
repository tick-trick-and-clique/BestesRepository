'''
Created on 10.05.2019

@author: tilman
'''
import random
import string
import math
from typing import List
from Graph import GRAPH
from Vertex import VERTEX
from Edge import EDGE
from itertools import combinations

def buildRndGraph(nr_nodes: int, p_connected: float, labeled_nodes=False, labeled_edges=False, directed=False,
                  name_graph="random_Graph"):
    """
    Creates random Graphs concerning given parameters and saves the graph to "<name_graph>.graph" format
    p_connected:= probability, that there is a connection (directed or undirected) between two arbitrarily chosen vertices
    """
    list_vertices = []
    list_edges = []
    label_edge_len = 3  #Default length of edge labels; Könnte man auch weglassen und den Default Wert der randomString() -Funktion nutzen

    # Create Vertices
    for vertex_id in range(1, nr_nodes+1): #
        if labeled_nodes:
            list_vertices.append(VERTEX(vertex_id, randomString()))
        else:
            list_vertices.append(VERTEX(vertex_id, ""))

    # Create Edges if arbitrarily number [0.0,1.0] <=p_connected
    list_combinations = combinations(list(range(len(list_vertices))),2)   #list of all possible combinations of length 2 ; lookup list for vertex combinations
    if labeled_edges:
        label_edge_length = label_edge_len  # Define LabelLength of edges
    else:
        label_edge_length = 0

    for combination in list_combinations:   #Example: Combination:= [0,1]
        edge_id = 1 #Initialise first edge id
        if directed:
            directed_edge_normal = (random.random() <= math.sqrt(p_connected))  #if TRUE: draw edge in "natural" direction of combination
            directed_edge_reverse = (random.random() <= math.sqrt(p_connected)) #if TRUE: draw edge in "reverse" direction of combination
            if directed_edge_normal or directed_edge_reverse:   #if one edge is do be drawn
                if directed_edge_normal:    #draw edge in "normal" direction of combination: 0->1
                    #print("1-direct, normal")
                    list_edges.append(EDGE(edge_id, [list_vertices[combination[0]], list_vertices[combination[1]]],
                                           randomString(label_edge_length)))
                    list_vertices[combination[0]].append_neighbour(list_vertices[combination[1]])
                    edge_id += 1
                if directed_edge_reverse: #draw edge in "reversed" direction of combination: 1->0
                    #print("1-direct, reverse")
                    list_edges.append(EDGE(edge_id, [list_vertices[combination[1]], list_vertices[combination[0]]],
                                           randomString(label_edge_length)))
                    list_vertices[combination[1]].append_neighbour(list_vertices[combination[0]])
                    edge_id += 1
        elif (directed is False) and (random.random() <= p_connected):
            #print("2-NON-direct")
            list_edges.append(EDGE(edge_id, [list_vertices[combination[0]], list_vertices[combination[1]]],
                                   randomString(label_edge_length)))
            # Edges have to be appended in both directions for undirected graphs
            edge_id += 1
            list_edges.append(EDGE(edge_id, [list_vertices[combination[1]], list_vertices[combination[0]]],
                                   randomString(label_edge_length)))
            edge_id += 1
            list_vertices[combination[0]].append_neighbour(list_vertices[combination[1]])
            list_vertices[combination[1]].append_neighbour(list_vertices[combination[0]])

    # Create Graph
    if not directed:
        # For undirected graphs, the number of edges is half the number of edges entries in the GRAPH object
        graph = GRAPH(name_graph, list_vertices, list_edges, len(list_vertices),
                      int(len(list_edges)/2), directed, labeled_nodes, labeled_edges)
    else:
        graph = GRAPH(name_graph, list_vertices, list_edges, len(list_vertices),
                      len(list_edges), directed, labeled_nodes, labeled_edges)
    return graph

def randomString(stringLength=3):
    """ Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def printListEdges(list: List[EDGE]):
    """ just for monitoring purpose of algorithm"""
    output = ""
    for edge in list:
        output += str(edge.get_id()) + ";" + str(edge.get_start_and_end()[0].get_id()) \
                + ";" + str(edge.get_start_and_end()[1].get_id()) + ";" + str(edge.get_label()) + "\t"
    print(output)


