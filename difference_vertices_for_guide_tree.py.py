def vertices_number(graph1, graph2):
    """ function which returns the difference between the number of vertices """
    vn1 = graph1.get_number_of_vertices()
    vn2 = graph2.get_number_of_vertices()
    return(vn1 - vn2)