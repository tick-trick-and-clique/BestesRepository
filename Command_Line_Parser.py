#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser


parser = ArgumentParser(usage="Software for graph analysis")
parser.add_argument("-a", "--anchor", metavar="", default=[],
                    help="Supply anchor graph file (path) for an anchor to the first graph in the input graphs."
                         "NOTE: Anchor option is not available for anchor graphs in json format!")
parser.add_argument("-bk", "--bron-kerbosch", action="store_true",
                    help="Invokes maximal clique finding on input graph.")
parser.add_argument("-ga", "--graph_alignment", nargs="*", metavar="",
                    help="Choose matching algorithm: Either 'bk' for bron-kerbosch or 'mb' for matching-based. You may "
                         "also provide the number of matched subgraphs in previous pairwise alignments on which the "
                         "the alignment should be expanded (e.g. 'bk 5'). Default is one subgraph only. "
                         "If matching-based was chosen,you may provide a margin in percent to what extend the "
                         "smaller graph may be reduced for subgraph isomorhpism search (e.g. 'mb 5 0.2').")
parser.add_argument("-go", "--graph_output", metavar="", nargs='?', const=1,
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
                         "NOTE: Data in json files is supposed to be of the structure of PubChem 2D json files!")
parser.add_argument("-mp", "--modular_product", action="store_true", help="Forms the modular product of two graphs.")
parser.add_argument("-n", "--neo4j", action="store_true",
                    help="Visualize output using NEO4J!")
parser.add_argument("-nh", "--no_h_atoms", action="store_true",
                    help="Specifies json format parsing. If selected, all H-atoms will be neglected.")
parser.add_argument("-no", "--newick_output", metavar="", nargs='?', const=1,
                    help="Saves guide tree representation as Newick string to .newick file. If a path (in quotation "
                         "marks!) is provided, it will be saved there. If a .newick file name is provided, it will be "
                         "saved with that name in the current working directory. Else it will be saved in the current "
                         "working directory using a default name.")
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
parser.add_argument("-sgo", "--subgraph_output", metavar="", nargs='*',
                    help="Saves found subgraphs as .graph file. If a path (in quotation marks!) is provided, subgraphs "
                         "will be saved there with an additional sequential number. If a .graph file name is provided, "
                         "they will be saved with that name in the current working directory. Else they will be saved "
                         "in the current working directory using a default name.")
parser.add_argument("syntax", nargs="?")


def parse_command_line():
    args = parser.parse_args()
    return args

