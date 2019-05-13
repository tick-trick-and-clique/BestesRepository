from argparse import ArgumentParser


parser = ArgumentParser(usage="Software for graph analysis")
parser.add_argument("input_file", help="Supply input file path")
parser.add_argument("-p", "--pivot_mode", choices=["max", "random"], help="Supply pivot mode, when selected")
parser.add_argument("-a", "--anchor", metavar="anchor", default=[], help="Supply anchor graph file, when selected")
parser.add_argument("-o", "--output_file", help="Supply output file path, when selected")
parser.add_argument("-mp", "--modular_product", help="Supply second graph file path, when selected")
parser.add_argument("-bk", "--bron_kerbosch", action="store_true", help="Invokes maximal clique finding on input graph")
parser.add_argument("-ga", "--graph_alignment", help="Supply second graph file, when selected. Maximal clique finding"
                                                     " is invoked on the modular product.")


def parse_command_line():
    args = parser.parse_args()
    return args

