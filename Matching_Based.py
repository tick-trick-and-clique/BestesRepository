'''
latest update: 13.05.2019

@author: johann

class for a matching based algorithm for aligning large graphs
refering to: "An Improved Algorithm for Matching Large Graphs", Cordella et al., 2001

'''

from Graph import GRAPH
from Vertex import VERTEX
from Edge import EDGE


class GRAPHMATCHER(object):
    def __init__(self, graph1: GRAPH, graph2: GRAPH):
        self.g1 = graph1
        self.g2 = graph2
        self.name = self.get_name()
        self.g1_vertices = graph1.get_list_of_vertices()
        self.g2_vertices = graph2.get_list_of_vertices()
        self.g2_node_order = {n: i for i, n in enumerate(graph2.get_list_of_vertices())}






    def get_name(self):
        name = "Matching with VF2 Algorithm of "
        name += self.g1.get_name()
        name += " and "
        name += self.g2.get_name()

        return name


'''
ROCEDURE Match(s)
    INPUT:an intermediate state s; the initial state s0 has M(s0)=∅
    OUTPUT:the mappings between the two graphs
    
    IF M(s) covers all the nodes of G2 THEN
        OUTPUT M(s)

    ELSE
        Compute the set P(s) of the pairs candidate for inclusion in M(s)
    
        FOREACH (n,m) ∈ P(s)
            IF F(s,n,m) THEN
                Compute the state s ́ obtained by adding (n,m) to M(s)
                CALL Match(s′)
            END IF
        END FOREACH
        Restore data structures
    END IF
END PROCEDURE
''' 
