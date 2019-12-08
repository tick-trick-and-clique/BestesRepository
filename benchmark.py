import subprocess
import platform
platform.architecture()

#### FUNKTIONEN
def benchmark_ga(benchmark_filename, input_graph_name, number_of_graphs,
                 commandstring_before_input, commandstring_after_input):
    i = 1
    while i <= number_of_graphs - 2:
        input_string_1 = input_graph_name + "_" + str(i) + ".graph"
        i += 1
        input_string_2 = input_graph_name + "_" + str(i) + ".graph"
        i += 1
        input_string_3 = input_graph_name + "_" + str(i) + ".graph"
        i += 1
        input_string = input_string_1 + " " + input_string_2 + " " + input_string_3
        # Concatenate command string and run command
        command_string = commandstring_before_input + input_string + commandstring_after_input + benchmark_filename
        print(command_string)
        subprocess.run(command_string, shell=True)


def benchmark_bk(benchmark_filename, input_specific_graph_name, repeats,
                 commandstring_before_input, commandstring_after_input):
    for i in range(1, repeats + 1):
        command_string = commandstring_before_input + input_specific_graph_name + \
                         commandstring_after_input + benchmark_filename
        print(command_string)
        subprocess.run(command_string, shell=True)


def create_random_graphs(nr_nodes, connectivity, directed, nr_graphs, graph_name):
    command_string_create = "python3 GraphDating.py -rg " + str(nr_nodes) + " " + str(connectivity) + " " + str(directed) + " -go"
    for i in range(1, nr_graphs+1):
        subprocess.run(command_string_create, shell=True)
        # rename standard output file
        filename_old = "'random_graph(" + str(nr_nodes) + ", " + str(connectivity) + ", " + str(directed) + ")_output.graph'"
        filename_new = str(graph_name) + "_" + str(i) + ".graph"
        command_string_rename = "mv " + str(filename_old) + " " + str(filename_new)
        subprocess.run(command_string_rename, shell=True)


#### BENCHMARKING
benchmark_filename = "" # name of file, where runtimes will be saved at
input_graph_name = ""   # trunk of input-file name
command_string = ""
commandstring_before_input = "python3 GraphDating.py -i "   # TODO: CHANGE TO "pypy3 ..." in case of using pypy
commandstring_after_input = ""  # depends on chosen algorithm

# ### CREATE RANDOM GRAPHS FOR DATASET SMALL, MIDDLE AND BIG
print("###\t0\t### Create random graphs for subsequent graph alignments")
# # Number of graphs has to be divisible by three (three input graphs per alignment) without rest
# ## Small random graphs
# number_of_small_graphs = 90 # TODO: Set number
# input_graph_name_small = "rg_small_4_0.4"   # TODO: Set name
# create_random_graphs(4, 0.4, False, number_of_small_graphs, input_graph_name_small)
## Middle random graphs
# number_of_middle_graphs = 3    # TODO: Set number
# input_graph_name_middle = "rg_middle_6_1.0" # TODO: Set name
# create_random_graphs(6, 1.0, False, number_of_middle_graphs, input_graph_name_middle)
# ## Big random graphs
number_of_big_graphs = 3   # TODO: Set number
input_graph_name_big = "rg_big_7_0.5" # TODO: Set name
create_random_graphs(7, 0.5, False, number_of_big_graphs, input_graph_name_big)

### GRAPH ALIGNMENT: BRON-KERBOSCH
commandstring_after_input = " -ga bk -bm "
# ##  Kleiner Datensatz
# print("###\t1.1\t### Benchmark: Graph-Alignment, Bron-Kerbosch, size small")
# benchmark_filename = "benchmark_ga_bk_small.txt"
# benchmark_ga(benchmark_filename, input_graph_name_small, number_of_small_graphs,
#              commandstring_before_input, commandstring_after_input)
#
# ##  Mittlerer Datensatz
# print("###\t1.2\t### Benchmark: Graph-Alignment, Bron-Kerbosch, size middle")
# benchmark_filename = "benchmark_ga_bk_middle.txt"
# benchmark_ga(benchmark_filename, input_graph_name_middle, number_of_middle_graphs,
#              commandstring_before_input, commandstring_after_input)
#
# ##  Grosser Datensatz
print("###\t1.3\t### Benchmark: Graph-Alignment, Bron-Kerbosch, size big")
benchmark_filename = "benchmark_ga_bk_big.txt"
benchmark_ga(benchmark_filename, input_graph_name_big, number_of_big_graphs,
             commandstring_before_input, commandstring_after_input)
#
#
# ### GRAPH ALIGNMENT: Cordella
commandstring_after_input = " -ga mb -bm "
# ##  Kleiner Datensatz
# # print("###\t2.1\t### Benchmark: Graph-Alignment, Cordella, size small")
# benchmark_filename = "benchmark_ga_mb_small.txt"
# benchmark_ga(benchmark_filename, input_graph_name_small, number_of_small_graphs,
#              commandstring_before_input, commandstring_after_input)
#
# ##  Mittlerer Datensatz
# print("###\t2.2\t### Benchmark: Graph-Alignment, Cordella, size middle")
# benchmark_filename = "benchmark_ga_mb_middle.txt"
# benchmark_ga(benchmark_filename, input_graph_name_middle, number_of_middle_graphs,
#              commandstring_before_input, commandstring_after_input)
#
##  Grosser Datensatz
print("###\t2.3\t### Benchmark: Graph-Alignment, Cordella, size big ###")
benchmark_filename = "benchmark_ga_mb_big.txt"
benchmark_ga(benchmark_filename, input_graph_name_big, number_of_big_graphs,
             commandstring_before_input, commandstring_after_input)



# ### CREATE RANDOM GRAPHS FOR Bron-Kerbosch    
# number_of_graphs = 5
# repeats_per_graph = 3
# size_of_graphs = 20
# connectivity = 0.5
# input_graph_name_bk = "rg_bk_50_0.5"
# create_random_graphs(size_of_graphs, connectivity, False, number_of_graphs, input_graph_name_bk)
#
# ## Bron-Kerbosch: Pivot random
# commandstring_after_input = " -bk -p random -bm "
# benchmark_filename = "benchmark_bk_p_random.txt"
# for i in range(1, number_of_graphs + 1):
#     input_graph_string = input_graph_name_bk + "_" + str(i) + ".graph"
#     benchmark_bk(benchmark_filename, input_graph_string, repeats_per_graph,
#                  commandstring_before_input, commandstring_after_input)
#     with open(benchmark_filename, 'a') as file:
#         file.write("\n")
#
# ## Bron-Kerbosch: Pivot max
# commandstring_after_input = " -bk -p max -bm "
# benchmark_filename = "benchmark_bk_p_max.txt"
# for i in range(1, number_of_graphs + 1):
#     input_graph_string = input_graph_name_bk + "_" + str(i) + ".graph"
#     benchmark_bk(benchmark_filename, input_graph_string, repeats_per_graph,
#                  commandstring_before_input, commandstring_after_input)
#     with open(benchmark_filename, 'a') as file:
#         file.write("\n")