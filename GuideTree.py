#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


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
            print("Has only one child!")
            return True
        else:
            return True


def upgma(comp_function, graphs, anchor_graph=False):
    """
    Takes a comparison function for graphs and list of graphs as input and calculates a guide
    tree which is returned as a the top cluster of a binary tree of clusters. List of graphs ordered by minimal
    distance?????
    Return type: Cluster
    """
    # Initialize n clusters each containing one graph
    clusters = []
    n = len(graphs)
    for i in range(n):
        clusters.append(Cluster([graphs[i]]))

    # Initialize the distance matrix
    dist_matrix = [[comp_function(graphs[i], graphs[j]) for i in range(n)] for j in range(n)]

    # Until there is only one top cluster left, calculate the pairwise distance of each cluster, select the pair of
    # clusters with smallest distance and merge them.
    while n > 1:
        current_smallest_dist = float("inf")
        cluster1 = None
        cluster2 = None
        if anchor_graph:
            anchor_graph = False
            i = 0
            for j in range(1, n):
                if dist_matrix[i][j] < current_smallest_dist:
                    current_smallest_dist = dist_matrix[i][j]
                    cluster1 = clusters[i]
                    cluster2 = clusters[j]
        else:
            for i in range(n):
                for j in range(i - n + 2):
                    if dist_matrix[i][j] < current_smallest_dist:
                        current_smallest_dist = dist_matrix[i][j]
                        cluster1 = clusters[i]
                        cluster2 = clusters[j]
        new_cluster = Cluster(cluster1.get_elements() + cluster2.get_elements())
        new_cluster.set_children(cluster1, cluster2)

        # Update the list length and update the distance matrix according to the merge product cluster
        dist_matrix = update_distance_matrix(comp_function, clusters, dist_matrix, new_cluster, i, j)
        n -= 1

    # Return the top cluster (i.e. tree root).
    return clusters[0]


def distance_between_clusters(comp_function, cluster1, cluster2):
    """
    Takes a comparison function and two clusters of clusters/graphs as input and calculates the distance between the
    two clusters.
    Return type: float
    """
    distance = 0
    c1e = cluster1.get_elements()
    c2e = cluster2.get_elements()
    for i in range(len(c1e)):
        for j in range(len(c2e)):
            distance += comp_function(c1e[i], c2e[j])
    distance = distance/(len(c1e) * len(c2e))
    return distance


def update_distance_matrix(comp_function, clusters, dist_matrix, new_cluster, index_previous1, index_previous2):
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
        dist_matrix[i].append(distance_between_clusters(comp_function, clusters[i], new_cluster))
    dist_matrix.append([distance_between_clusters(comp_function, clusters[i], new_cluster)
                        for i in range(len(dist_matrix))])
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
    if output_file == 1:
        output_file = "Default.newick"
    # If provided argument is not a valid directory and also is not a valid file name, raise NotADirectoryError
    if not os.path.isdir(os.path.dirname(output_file)) \
            and not os.path.isdir(os.path.dirname(os.path.abspath(output_file))):
        raise NotADirectoryError("Given path is not a directory!")
    # Provided argument is a directory, else it is a filename and the current working directory path is added
    if os.path.isdir(os.path.dirname(output_file)):
        filename = output_file
    else:
        filename = os.path.abspath(output_file)
    # If the provided argument does not end with '.newick
        raise NameError("Given path of filename must end with '.newick'")
    with open(filename, "w") as f:
        f.write(newick_string)
        f.close()
    # Log Statement
    print("Guide tree saved as Newick...")
    return True


def parse_newick_file_into_tree(newick_file, graphs):
    """
    Takes as input a file of a guide tree in newick format and a list of graphs that are represented by their
    unique (!) names in the string. Returns a top cluster (i.e. tree root) of the guide tree.
    Return type: Cluster
    """
    # Find the position of the branch separator (here: comma)
    with open(newick_file, "r") as f:
        newick_string = f.readline()
    return parse_newick_string_into_tree(newick_string, graphs)


def parse_newick_string_into_tree(newick_string, graphs):
    """
    Helper function for parse_newick_file_into_tree.
    Return type: Cluster
    """
    count = 1
    i = 1
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
    newick_string2 = newick_string[position + 1:-1]
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
        for graph in graphs:
            if graph.get_name() == newick_string1:
                graph1 = graph
        cluster1 = Cluster([graph1])
        top_cluster = Cluster([])
        top_cluster.set_children(cluster1, cluster2)
        return top_cluster
    # If both branches are leaves, then:
    else:
        for graph in graphs:
            if graph.get_name() == newick_string1:
                graph1 = graph
            if graph.get_name() == newick_string2:
                graph2 = graph
        cluster1 = Cluster([graph1])
        cluster2 = Cluster([graph2])
        top_cluster = Cluster([])
        top_cluster.set_children(cluster1, cluster2)
        return top_cluster

