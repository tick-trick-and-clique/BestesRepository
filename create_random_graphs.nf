#!/urs/bin/env nextflow

/* 
* author: Johann Wurz
* date:   October 2019
 */

/*
************************************************************************************************************************** 
* ATTENTION: TO USE THIS SCRIPT, PLEASE IMPORT THE PROVIDED YAML-FILE "create_random_graphs.yml" BY YOUR PACKAGE MANAGER 
*
*            TO RUN THIS SCRIPT, ACTIVATE THE IMPORTED CONDA ENVIRONMENT, CHANGE THE PARAMETERS AS WANTED AND TYPE IN
*            YOUR COMMAND-LINE "nextflow run create_random_graphs.nf --mode YOUR DESIRED MODE"
**************************************************************************************************************************
*/


/* 
* change mode to your wanted mode 
*/
params.mode = "undirected" // options: "directed", "undirected" or "clustered" (by default undirected)

/*
* change working directory to your working directory
*/
params.indir_graphDating = "./BestesRepository"

/*
* change output directory to your wanted output directory!
*/
params.outdir_random_graphs = "./data/random_graphs"

/* 
* change channels for your wanted parameters!
*/
vertices = Channel.from( 10, 30, 50 )                         // for all modes
connectivity_directed = Channel.from( 0.001, 0.005, 0.01 )    // only for "directed" and "undirected" mode
connectivity_undirected = Channel.from( 0.01, 0.02, 0.05 )    // only for "directed" and "undirected" mode
degree_clustered = Channel.from( 2, 3 )                       // only for "clustered" mode
deleted_vertices = Channel.from( 1, 3, 6 )                    // only for "clustered" mode
deleted_edges = Channel.from( 1, 3, 6 )                       // only for "clustered" mode


params.hello = "\n\n\n Hello, this is a nf-workflow for our graphalignment tool 'GraphDating', to generate a lot of random graphs simultanously.\n\n\n"
println "${params.hello}"


process create_random_graphs {
  input:
  each x from vertices
  each y_d from connectivity_directed
  each y_u from connectivity_undirected
  each d_c from degree_clustered
  each d_v from deleted_vertices
  each d_e from deleted_edges
  
  script:
  if( params.mode == "undirected")
    """
    python3 ${params.indir_graphDating}/Main.py -rg ${x} ${y_u} False \
    -go ${params.outdir_random_graphs}/random_graph_${x}_${y_u}_${params.mode}.graph
    """
    //break, return oder sowas

  else if( params.mode == "directed")
    """
    python3 ${params.indir_graphDating}/Main.py -rg ${x} ${y_u} True \
    -go ${params.outdir_random_graphs}/random_graph_${x}_${y_d}_${params.mode}.graph
    """
    //break, return oder sowas
  else if( params.mode == "clustered")
    """
    python3 ${params.indir_graphDating}/Main.py -rc ${x} ${d_c} ${d_v} ${d_e} \
    -go ${params.outdir_random_graphs}/random_graph_${x}_${d_c}_${d_v}_${d_e}_${params.mode}.graph
    """
    //break, return oder sowas
}
