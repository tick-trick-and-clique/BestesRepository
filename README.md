# GraphDating

A python-based tool for progressive, multiple graph alignments

## Installation

git clone https://github.com/tick-trick-and-clique/BestesRepository

cd /BestesRepository
 
## Basic Usage
Make sure to use python3 as default python interpreter or change 'python' to 'python3'

Help messages:
python GraphDating.py -h

Exemplary graph aligning call: 
python GraphDating.py -i <Some Input File>.graph <Another Input File>.graph -ga mb -sgo

This aligns two graphs and outputs the alignment to the current working directory.

## Parameter Overview

Flag -i is mandatory.
If Flag is chosen, Values are mandatory if not stated otherwise.

| Flag | Values | Description |
| --- | --- | --- |
| -a | <FILE_PATH> | Anchor graph option, supply anchor graph file. Not available for JSON-Format! |
| -bk | <FILE_PATH> <FUNCTION_NAME> (both optional) | Invokes Bron-Kerbosch algorithm on single graph. Optionally, you may provide a file path together with a clique sorting function in that file. |
| -bm | ? | Writes benchmarking timestamps into file. |
| -cc | - | Only returns aligments if all input graph components are connected. |
| -ga | <MATCHING_ALGORITHM> (mandatory) <ALIGNMENT_COUNT> (optional) | Graph Alignment: Choose either 'bk' or 'mb' for bron-kerbosch or vf2 algorithm, respectively. You may also provide the number of alignments that should be considered in posterior alignment steps in multiple alignment (Default is 1). |
| -go | <FILE_PATH> (optional) | Saves input graphs and newly built graphs (not alignments/subgraphs!) as .graph at the given file path. (Current working directory is default). |
| -gt | <COMPARISON_FUNCTION> or <.NEWICK_FILE_PATH> (optional) | Choose a comparison function on graphs that will be used for guide tree construction. Alternatively, you may pass built-in comparison function keywords ('density', 'pairwise_align') or pass a .newick file containing guide tree information (Default is 'density'). |
| -i | <FILE_PATH> <FILEPATH> ... | Path(s) of input file(s). |
| -if | <INPUT_FORMAT> (optional) | You may choose between input graph formats 'graph' and 'json' for those formats, respectively (Default is 'graph') |
| -vlc | <FILE_PATH> <FUNCTION_NAME> (both optional) | Invokes vertex label checks. You may pass a file path together with the function name in that file for custom matching-conditions (Default is label identity). |
| -elc | <FILE_PATH> <FUNCTION_NAME> (both optional) | Invokes edge label checks. You may pass a file path together with the function name in that file for custom matching-conditions (Default is label identity). |
| -mp | - | Invokes modular product calculation on the two provided input graphs. |
| -ms | <FILE_PATH> <FUNCTION_NAME> | You may pass a file path together with the function name in that file for custom matching-sorting conditions, i.e. the manner in which the best matching/alignment will be determined among those found. |
| -n | <BOLT_URL> <USER> <PASSWORD> | Visualization using Neo4J database. You need to create a blank sandbox in neo4j and pass the respective credentials to this flag. |
| -nh | - | Invokes neglection of all H-Atoms, specifically all vertices with label '1'. |
| -no | <FILE_PATH> (optional) | Saves guide tree as .newick at the given file path. (Current working directory is default). |
| -nsi | - | Prevent output of multiple stereoisomers when aligning/matching. |
| -p | <PIVOT_METHOD> | You may choose between 'max' and 'random' as pivot element choosing methods. |
| -rg | SEE MANUAL | Random graph building (SEE MANUAL). |
| -rc | SEE MANUAL | Random clustered graph building (SEE MANUAL). | 
| -s | - | Alignment output will be given as subgraphs in seperate files for each input graph, with the order of vertices corresponding to the matching order. |
| -sgo | <ALIGNMENT_COUNT> (optional) | Maximal count of found alignments to be exported. Must not be higher than <ALIGNMENT_COUNT> in -ga option (Default is all alignments). |
| -sub | - | Select if you want the MB algorithm (VF2) to heuristically detect subgraph-subgraph isomorphisms. |

## Other

Please read the GraphDating_Manual.pdf for further information!
