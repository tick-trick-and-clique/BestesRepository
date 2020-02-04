#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser


parser = ArgumentParser(usage="Software for graph analysis")
parser.add_argument("-a", "--anchor", metavar="", default=[],
                    help="Supply anchor graph file (path) for an anchor to the first graph in the input graphs."
                         "NOTE: Anchor option is not available for anchor graphs in json format!")
parser.add_argument("-bk", "--bron-kerbosch", nargs="*",
                    help="Invokes maximal clique finding on input graph. Optionally, you may pass a file name together "
                         "clique sorting function name in that file.")
parser.add_argument("-bm", "--benchmark", nargs="*",
                    help="Writes benchmark-timestamps into file")
parser.add_argument("-cc", "--check_connection", action="store_true",
                    help="If selected, only connected subgraphs will be the output of graph alignment!")
parser.add_argument("-ga", "--graph_alignment", nargs="*", metavar="",
                    help="Choose matching algorithm: Either 'bk' for bron-kerbosch or 'mb' for matching-based. You may "
                         "also provide the number of matched subgraphs in previous pairwise alignments on which the "
                         "the alignment should be expanded, i.e. the number of matchings that should be forwarded to "
                         "the next alignment step and/or output (e.g. 'bk 5'). Default is one subgraph only. "
                         "If matching-based was chosen,you may provide a margin in percent to what extend the "
                         "smaller graph may be reduced for subgraph isomorhpism search (e.g. 'mb 5 0.2').")
parser.add_argument("-go", "--graph_output", metavar="", nargs='*',
                    help="Saves graph as .graph file. If a path (in quotation marks!) is provided, graph will be saved "
                         "there. If a .graph file name is provided, it will be saved with that name in the current "
                         "working directory. Else it will be saved in the current working directory using its name "
                         "attribute.")
parser.add_argument("-gt", "--guide_tree", nargs='*', metavar="",
                    help="Choose either a comparison function/attribute for guide tree construction (Keywords for "
                         "available graph characteristics to base the comparison on: 'density' for graph density, "
                         "'pairwise_align' for greatest subgraph isomorphisms, i.e. maximal number of nodes in "
                         "subgraphs). Alternatively, pass a preconstructed guide tree as '.newick' file or pass the "
                         "keyword 'custom' together with a .py file and the name of the comparison function in that "
                         "file. For detailed requirements of the custom comparison functions see the manual! "
                         "If not selected, default is a heuristic construction of a guide tree by graph density."
                         "NOTE: For pairwise alignment add a second argument 'only' ('pairwise_align' 'only'). "
                         "Also, you need to pass the '-ga' command line keyword and required parameters.")
parser.add_argument("-i", "--input", metavar="", nargs='*', help="Supply input path(s) of input file(s).")
parser.add_argument("-if", "--input_format", choices=["graph", "json"], default="graph",
                    help="Specify type of input files. For .graph files pass 'graph' and for .json files pass 'json'."
                         "'graph' is default. NOTE: Data in json files is supposed to be of the structure of PubChem "
                         "2D json files!")


parser.add_argument("-vlc", "--vertex_label_comparison", nargs="*",
                    help="For custom matching-conditions of vertex-labels, pass a file name together with a function "
                         "in that file that will take two strings (see manual) and returns a boolean value."
                         "If return is TRUE, two two distinct VERTEX-objects with relative strings as labels are "
                         "possible matches.")
parser.add_argument("-elc", "--edge_label_comparison", nargs="*",
                    help="For custom matching-conditions of edge-labels, pass a file name together with a function "
                         "in that file that will take two strings (labels) and returns a boolean value."
                         "If return is TRUE, two distinct EDGE-objects with relative strings as labels are "
                         "possible matches.")

parser.add_argument("-mp", "--modular_product", action="store_true", help="Forms the modular product of two graphs.")
parser.add_argument("-ms", "--matching_sort", nargs="*",
                    help="For custom sorting of matching graphs, pass a file name together with a function in that file"
                         "that will take a matching-GRAPH object (see manual) and returns a floating point value."
                         "Matching graphs will then be sorted in descending order. Default is sorting by descending"
                         "number of vertices!")
parser.add_argument("-n", "--neo4j", nargs=3, 
                    help="Visualize output using NEO4J!")
parser.add_argument("-nh", "--no_h_atoms", action="store_true",
                    help="Specifies json format parsing. If selected, all H-atoms will be neglected.")
parser.add_argument("-no", "--newick_output", metavar="", nargs='?', const="1",
                    help="Saves guide tree representation as Newick string to .newick file. If a path (in quotation "
                         "marks!) is provided, it will be saved there. If a .newick file name is provided, it will be "
                         "saved with that name in the current working directory. Else it will be saved in the current "
                         "working directory using a default name.")
parser.add_argument("-nsi", "--no_stereo_isomers", action="store_true",
                    help="If selected and if input is a molecule graph, output will be reduced neglecting multiple "
                         "stereo isomers, i.e. matchings where the subset of vertices is the same for each input"
                         "graph, respectively. Only one stereoisomer will be forwarded!")
parser.add_argument("-p", "--pivot", metavar="", choices=["max", "random"],
                    help="Choose pivot mode: Either 'max' or 'random'.")
parser.add_argument("-rg", "--random_graph", nargs=3, metavar="",
                    help="Create a random graph. Supply the number of vertices (N, integer), the mean relative "
                         "connectivity (p, float) and whether it should be directed (either 'True' or 'False') as "
                         "e.g. '10 0.8 True'.")
parser.add_argument("-rc", "--random_cluster", nargs=4, type=int,
                         help="Create a random clustered graph. Supply the number of vertices (N, integer), the desired"
                              "degree at each node (d, integer), how many vertices you want to delete from the cluster"
                              "(del_vert, int) and finally how mandy edges you want to delete(del_edges, int)"
                              "e.g. '20 3 2 2'.")
parser.add_argument("-s", "--seperate", action="store_true", help="Select if you like output to subgraphs of "
                                                                  "input graphs.")
parser.add_argument("-sgo", "--subgraph_output", metavar="", nargs='*',
                    help="Saves found subgraphs as .graph file. You may specifiy the number of matchings in your output"
                         "(e.g. -sgo 5), default is all matchings. If a path (in quotation marks!) is provided, subgraphs "
                         "will be saved there with an additional sequential number. If a .graph file name is provided, "
                         "they will be saved with that name in the current working directory. Else they will be saved "
                         "in the current working directory using a default name.")
parser.add_argument("-sub", "--subsub", action="store_true", help="Select if you like the VF2 algorithm to "
                                                                  "heuristically detect subgraph-subgraph isomorphisms"
                                                                  "as well.")
parser.add_argument("syntax", nargs="?")


def parse_command_line():
    args = parser.parse_args()
    return args

