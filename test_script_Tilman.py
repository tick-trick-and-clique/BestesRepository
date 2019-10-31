#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
### GRAPH Alignment with Bron-Kerbosch
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk
# print("1______________python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk_______________")
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -a <ANCHOR_GRAPH> (Anchor Graph muss Subgraph von <GRAPH1>!)
# print("2______________python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -a anchor.graph_______________")
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -a anchor.graph")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk <#MATCHINGS>
# print("3______________python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk 3_______________")
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk 3")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo
# print("4______________python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo_______________")
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo")
# -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo <#OUTPUTS>
print("5______________python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo 3_______________")
os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo 3")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo <NAME>
# print("6______________python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo sgo_name.graph_______________")
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo sgo_name.graph")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo <NAME> <#OUTPUTS>
# print("7______________python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo sgo_name.graph 3_______________")
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo sgo_name.graph 3")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -nsi
# print("8______________python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo -nsi_______________")
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo -nsi")

# ##  LABEL COMPARISON
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -vlc
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -vlc -sgo")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -elc
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -elc -sgo")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -vlc -elc
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -vlc -elc -sgo")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -vlc <FILE> <NAME>
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -vlc label_comp_functions.py vertices_are_compatible -sgo")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -elc <FILE> <NAME>
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -elc label_comp_functions.py edges_are_compatible -sgo")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -vlc <FILE> <NAME> -elc <FILE> <NAME>
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -vlc label_comp_functions.py vertices_are_compatible -elc label_comp_functions.py edges_are_compatible -sgo")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -no <FILE>
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -sgo -no guideTree_newick.new")

# ##  GUIDE TREE
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -gt <FILE>
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -gt given_guideTree.new -sgo")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -gt pairwise_align
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -gt pairwise_align -sgo")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -gt density
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -gt density -sgo")
# # -i <GRAPH1> <GRAPH2> <GRAPH3> -ga bk -sgo -gt custom <FILE> <FUNCTION_NAME>
# os.system("python3 Main.py -i klein.graph mittel.graph groß.graph -ga bk -gt custom difference_vertices_for_guide_tree.py vertices_number -sgo")
