#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from copy import copy

class Cluster:
    def __init__(self, e):
        self.elements = e
        self.right_child_cluster = None
        self.left_child_cluster = None

    def get_elements(self):
        return self.elements

    def set_elements(self, list_of_elements):
        self.elements = [element for element in list_of_elements]

    def set_children(self, left_child, right_child):
        self.right_child_cluster = right_child
        self.left_child_cluster = left_child

    def get_left_child(self):
        return self.left_child_cluster

    def get_right_child(self):
        return self.right_child_cluster

    def children_exist(self):
        if self.left_child_cluster is None and self.right_child_cluster is None:
            return False
        elif self.left_child_cluster is None or self.right_child_cluster is None:
            return True
        else:
            return True


def upgma(comp_function, graphs, anchor_graph=False):
    """
    Takes a comparison function for graphs and list of graphs as input and calculates a guide
    tree which is returned as a the top cluster of a binary tree of clusters.
    Return type: Cluster
    """
    n = len(graphs)

    # Initialize the distance matrix of graphs as dictionary of dictionaries with graph names as keys
    dist_matrix_graphs = {graphs[j].get_name(): {graphs[i].get_name(): comp_function(graphs[i], graphs[j])
                                                 for i in range(n)} for j in range(n)}

    # Initialize n clusters each containing one graph
    clusters = []
    for i in range(n):
        clusters.append(Cluster([graphs[i]]))

    # Initialize the distance matrix of clusters
    dist_matrix_clusters = [[comp_function(graphs[i], graphs[j]) for i in range(n)] for j in range(n)]

    # Until there is only one top cluster left, calculate the pairwise distance of each cluster, select the pair of
    # clusters with smallest distance and merge them.
    while n > 1:
        current_smallest_dist = float("inf")
        cluster1 = None
        cluster2 = None
        # This control structure makes sure that iff an anchor graph is passed, the anchor will be used in the first
        # pairwise graph alignment.
        if anchor_graph:
            anchor_graph = False
            i = 0
            for j in range(1, n):
                if dist_matrix_clusters[i][j] < current_smallest_dist:
                    current_smallest_dist = dist_matrix_clusters[i][j]
                    cluster1 = clusters[i]
                    cluster2 = clusters[j]
                    a = i
                    b = j
        else:
            for i in range(n - 1):
                for j in range(i + 1, n):
                    if dist_matrix_clusters[i][j] < current_smallest_dist:
                        current_smallest_dist = dist_matrix_clusters[i][j]
                        cluster1 = clusters[i]
                        cluster2 = clusters[j]
                        a = i
                        b = j
        new_cluster = Cluster(cluster1.get_elements() + cluster2.get_elements())
        new_cluster.set_children(cluster1, cluster2)

        # Update the list length and update the distance matrix according to the merge product cluster
        dist_matrix_clusters = update_distance_matrix(comp_function, clusters, dist_matrix_clusters, new_cluster, a, b,
                                                      dist_matrix_graphs)
        n -= 1

    # Return the top cluster (i.e. tree root).
    return clusters[0]


def distance_between_clusters(comp_function, cluster1, cluster2, distance_matrix_graphs):
    """
    Takes a comparison function and two clusters of clusters/graphs as input and calculates the distance between the
    two clusters.
    Return type: float
    """
    distance = None
    if cluster1.children_exist():
        a = len(cluster1.get_left_child().get_elements())
        b = len(cluster1.get_right_child().get_elements())
        distance = (distance_between_clusters(comp_function, cluster1.get_left_child(), cluster2,
                                              distance_matrix_graphs) * a +
                    distance_between_clusters(comp_function, cluster1.get_right_child(), cluster2,
                                              distance_matrix_graphs) * b) / (a + b)
    if cluster2.children_exist():
        a = len(cluster2.get_left_child().get_elements())
        b = len(cluster2.get_right_child().get_elements())
        distance = (distance_between_clusters(comp_function, cluster1, cluster2.get_left_child(),
                                              distance_matrix_graphs) * a +
                    distance_between_clusters(comp_function, cluster1, cluster2.get_right_child(),
                                              distance_matrix_graphs) * b) / (a + b)
    if not cluster1.children_exist() and not cluster2.children_exist():
        distance = distance_matrix_graphs[cluster1.get_elements()[0].get_name()][cluster2.get_elements()[0].get_name()]
    if distance is None:
        raise Exception("Error occurred in calculation of distance of clusters!")
    return distance


def update_distance_matrix(comp_function, clusters, dist_matrix, new_cluster, index_previous1, index_previous2,
                           distance_matrix_graphs):
    """
    Takes
        a list of clusters,
        their corresponding distance matrix,
        a new cluster that is not yet represented in the matrix and
        the indices of two previous clusters whose values have to be deleted
    as input and returns the updated
    distance matrix.
    Return type:[[int, ...], ...]
    """

    # Remove the previous two clusters and append the new cluster
    if index_previous1 < index_previous2:
        index_previous2 -= 1
    clusters.remove(clusters[index_previous1])
    clusters.remove(clusters[index_previous2])
    clusters.append(new_cluster)

    # Delete the entries of the previous two clusters in column and line
    del dist_matrix[index_previous1]
    del dist_matrix[index_previous2]
    for i in range(len(dist_matrix)):
        del dist_matrix[i][index_previous1]
        del dist_matrix[i][index_previous2]

    # Calculate the distance from the new cluster to all the remaining clusters and append to the matrix both as column
    # and as line
    for i in range(len(dist_matrix)):
        dist_matrix[i].append(distance_between_clusters(comp_function, clusters[i], new_cluster, distance_matrix_graphs))
    lastlist = [distance_between_clusters(comp_function, clusters[i], new_cluster, distance_matrix_graphs)
     for i in range(len(dist_matrix))]
    lastlist.append(0.0)
    dist_matrix.append(lastlist)
    return dist_matrix


def guide_tree_to_newick(cluster):
    """
    Takes a top cluster (i.e. tree root) as input and returns it in Newick format representation as string.
    Return type: String
    """
    result, direction = recursive_newick(cluster)
    return result


def recursive_newick(cluster, direction_left=True, direction_right=True):
    """
    Helper function for guide_tree_to_newick.
    Return type: String
    """
    # As long as direction is True, the algorithm has not touched the leaves yet.
    # If the children are not tree leaves (i.e. grandchildren exist), then call function for these children.
    # Left child.
    result, result1, result2 = None, None, None
    if cluster.get_left_child().children_exist():
        result1, direction_left = recursive_newick(cluster.get_left_child())
    # Right child.
    if cluster.get_right_child().children_exist():
        result2, direction_right = recursive_newick(cluster.get_right_child())
    # Else, the cluster is the root of two leaves, then:
    if direction_left and direction_right:
        result = "(" + cluster.get_left_child().get_elements()[0].get_name() + "," + \
                 cluster.get_right_child().get_elements()[0].get_name() + ")"
    elif not direction_left and direction_right:
        result = "(" + cluster.get_right_child().get_elements()[0].get_name() + "," + result1 + ")"
    elif direction_left and not direction_right:
        result = "(" + cluster.get_left_child().get_elements()[0].get_name() + "," + result2 + ")"
    cluster.set_children(None, None)
    # The first time the algorithm reaches the leaves and every step towards roots, the direction will be set to False
    return result, False


def save_newick(newick_string, output_file=1):
    """
    Saves a guide tree in newick format in the designated output file as one string in the first line.
    Return type: boolean
    """
    if output_file == "1":
        output_file = "Default_name.newick"
    if not os.path.isdir(os.path.dirname(output_file)) \
            and not os.path.isdir(os.path.dirname(os.path.abspath(output_file))):
        raise NotADirectoryError("Given path is not a directory!")
    if os.path.isdir(os.path.dirname(output_file)):
        filename = output_file
    else:
        filename = os.path.abspath(output_file)
    if output_file[-7:] != ".newick":
        raise NameError("Given path of filename must end with '.newick'")
    with open(filename, "w") as f:
        f.write(newick_string)
        f.close()
    return True


def parse_newick_file_into_tree(newick_file, graphs):
    """
    Takes as input a file of a guide tree in newick format and a list of graphs that are represented by their
    unique (!) names in the string. Returns a top cluster (i.e. tree root) of the guide tree.
    Return type: Cluster
    """
    # Find the position of the branch separator (here: comma)
    with open(newick_file[0], "r") as f:
        newick_string = f.readline()
    return parse_newick_string_into_tree(newick_string, graphs)


def parse_newick_string_into_tree(newick_string, graphs):
    """
    Helper function for parse_newick_file_into_tree.
    Return type: Cluster
    """
    newick_string = newick_string.rstrip("\n")
    count = 1
    i = 1   #FIXME: Why start at position 1, which is just the second character of the actual string?!
            #FIXME: You assume, that there is always "()" surrounding everything, right? Is it like that?!
            # AJ: Yes!
    if newick_string[i] == "(":
        count += 1
    i += 1
    while count != 1:
        if newick_string[i] == "(":
            count += 1
        if newick_string[i] == ")":
            count -= 1
        i += 1
    position = newick_string.find(",", i, len(newick_string))
    # Divide the string into its branches
    newick_string1 = newick_string[1:position]
    newick_string2 = newick_string[position + 1:len(newick_string)-1]
    # If neither of the branches is a leaf, then:
    if newick_string1[0] == "(" and newick_string2[0] == "(":
        cluster1 = parse_newick_string_into_tree(newick_string1, graphs)
        cluster2 = parse_newick_string_into_tree(newick_string2, graphs)
        top_cluster = Cluster([])
        top_cluster.set_children(cluster1, cluster2)
        return top_cluster
    # If one of the branches is a leaf (which must always be the left one), then:
    elif newick_string2[0] == "(":
        cluster2 = parse_newick_string_into_tree(newick_string2, graphs)
        cluster1 = None
        for graph in graphs:
            if graph.get_name() == newick_string1:
                cluster1 = Cluster([graph])
        if not cluster1:
            raise Exception("Error occurred parsing newick string into guide tree!")
        top_cluster = Cluster([])
        top_cluster.set_children(cluster1, cluster2)
        return top_cluster
    elif newick_string1[0] == "(":
        cluster1 = parse_newick_string_into_tree(newick_string1, graphs)
        cluster2 = None
        for graph in graphs:
            if graph.get_name() == newick_string2:
                cluster2 = Cluster([graph])
        if not cluster2:
            raise Exception("Error occurred parsing newick string into guide tree!")
        top_cluster = Cluster([])
        top_cluster.set_children(cluster1, cluster2)
        return top_cluster
    # If both branches are leaves, then:
    else:
        cluster1 = None
        cluster2 = None
        for graph in graphs:
            if graph.get_name() == newick_string1:
                cluster1 = Cluster([graph])
            if graph.get_name() == newick_string2:
                cluster2 = Cluster([graph])
        if not cluster1 or not cluster2:
            raise Exception("Error occurred parsing newick string into guide tree!")
        top_cluster = Cluster([])
        top_cluster.set_children(cluster1, cluster2)
        return top_cluster


def parse_list_of_scored_graph_pairs_into_newick(scoring):
    """
    Function takes a List[(INT, GRAPH, GRAPH),...], which is sorted in descending order by INT, as input and returns the
    respective newick string representation.
    Return Type: String
    """
    graph_names = []
    newick_string = ""
    for i in range(len(scoring)):
        t = scoring[i]
        graph1_name = t[1]
        graph2_name = t[2]
        if graph1_name not in graph_names and graph2_name not in graph_names:
            graph_names.append(graph1_name)
            graph_names.append(graph2_name)
            if newick_string == "":
                newick_string = "(" + graph1_name + "," + graph2_name + ")"
            else:
                newick_string += "(" + newick_string + "),(" + graph1_name + "," + graph2_name + "))"
        elif graph1_name in graph_names and graph2_name in graph_names:
            pass
        elif graph1_name in graph_names:
            graph_names.append(graph2_name)
            newick_string = "(" + newick_string + "," + graph2_name + ")"
        elif graph2_name in graph_names:
            graph_names.append(graph1_name)
            newick_string = "(" + newick_string + "," + graph1_name + ")"
    return newick_string
