from Modulares_Produkt import modular_product
from MB_State import MB_State
from Graph import retrieve_graph_from_clique


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


def upgma(comp_function, graphs):
    """ Takes a comparison function for graphs and list of graphs as input and calculates a guide
    tree which is returned as a the top cluster of a binary tree of clusters. List of graphs ordered by minimal distance?????"""
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
    """ Takes a comparison function and two clusters of clusters/graphs as input and calculates the distance between the
    two clusters. """
    distance = 0
    c1e = cluster1.get_elements()
    c2e = cluster2.get_elements()
    for i in range(len(c1e)):
        for j in range(len(c2e)):
            distance += comp_function(c1e[i], c2e[j])
    distance = distance/(len(c1e) * len(c2e))
    return distance


def update_distance_matrix(comp_function, clusters, dist_matrix, new_cluster, index_previous1, index_previous2):
    """ Takes
        a list of clusters,
        their corresponding distance matrix,
        a new cluster that is not yet represented in the matrix and
        the indices of two previous clusters whose values have to be deleted
    as input and returns the updated
    distance matrix. """

    # Remove the previous two clusters and append the new cluster
    clusters.remove(clusters[index_previous1])
    clusters.remove(clusters[index_previous2 - 1])
    clusters.append(new_cluster)

    # Delete the entries of the previous two clusters in column and line
    del dist_matrix[index_previous1]
    del dist_matrix[index_previous2 - 1]
    for i in range(len(dist_matrix)):
        del dist_matrix[i][index_previous1]
        del dist_matrix[i][index_previous2 - 1]

    # Calculate the distance from the new cluster to all the remaining clusters and append to the matrix both as column
    # and as line
    for i in range(len(dist_matrix)):
        dist_matrix[i].append(distance_between_clusters(comp_function, clusters[i], new_cluster))
    dist_matrix.append([distance_between_clusters(comp_function, clusters[i], new_cluster)
                        for i in range(len(dist_matrix))])
    return dist_matrix


def match_by_guide_tree(comp_function, graphs, matching_algorithm, anchor, pivot_mode):
    """Takes a comparison function and a list of graphs as input and performs graph matching according to the guide tree
    and the given matching algorithm. The guide tree is built bia UPGMA algorithm. This function does not perform
    element-wise matching of all or a selected number of graph matching products. Instead, the only one match is used
    whose selection is done by the matching algorithm function."""

    # Create the cluster guide tree via UPGMA, 'cluster' is the root.
    cluster = upgma(comp_function, graphs)
    graph = recursive_matching(cluster, matching_algorithm, anchor, pivot_mode)
    return graph


def recursive_matching(cluster, matching_algorithm, anchor, pivot_mode):

    # If the children are not tree leaves (i.e. grandchildren exist), then call function for these children.
    # Left child.
    if cluster.get_left_child().children_exist():
        recursive_matching(cluster.get_left_child(), matching_algorithm, anchor, pivot_mode)
    # Right child.
    if cluster.get_right_child().children_exist():
        recursive_matching(cluster.get_right_child(), matching_algorithm, anchor, pivot_mode)

    # Else, the cluster is the root of two leaves, then:
        # Perform graph matching of the two leaf graphs (use the matching method provided by user)
        # Update the cluster with one new leaf, deleting the previous two
        # Return to the upper recursion level
    graph1 = cluster.get_left_child().get_elements()[0]
    graph2 = cluster.get_right_child().get_elements()[0]
    new_graph = None
    if matching_algorithm == "bk":
        mp = modular_product(graph1, graph2)
        mapping = mp.get_mapping()
        clique_finding_result = mp.bron_kerbosch(anchor, mp.get_list_of_vertices(), [], pivot=pivot_mode)
        # TODO: Clique selection
        selected_clique = clique_finding_result[0]  # Should return only one graph
        new_graph = retrieve_graph_from_clique(selected_clique, mapping, graph1)
    if matching_algorithm == "mb":
        mb_state = MB_State(graph1, graph2)
        new_graph = mb_state.mb_algorithm()
    cluster.set_elements([new_graph])
    cluster.set_children(None, None)
    return new_graph


def guide_tree_to_newick(cluster):
    """Takes a top cluster (i.e. tree root) as input and returns it in Newick format representation as string."""
    result, direction = recursive_newick(cluster)
    return result


def recursive_newick(cluster, direction_left=True, direction_right=True):
    # As long as direction is True, the algorithm has not touched the leaves yet.
    # If the children are not tree leaves (i.e. grandchildren exist), then call function for these children.
    # Left child.
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
        result = "(" + result1 + "," + cluster.get_right_child().get_elements()[0].get_name() + ")"
    elif direction_left and not direction_right:
        result = "(" + cluster.get_left_child().get_elements()[0].get_name() + "," + result2 + ")"
    cluster.set_children(None, None)
    # The first time the algorithm reaches the leaves and every step towards roots, the direction will be set to False
    return result, False
