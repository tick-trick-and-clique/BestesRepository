"""
This class implements a so called 'state' like described for the
matching-based algorithm by Cordella et al.
"""


class MB_State:
    def __init__(self, g1, g2, sortVertices):

        # DEV NOTE: core_1 and core_2 are supposed to be dictionaries with integers keys and VERTEX type values here
        # while the other four data structures
        self.graph1 = g1
        self.graph2 = g2
        self.core_1 = {}
        self.core_2 = {}
        self.in_1 = {}
        self.in_2 = {}
        self.out_1 = {}
        self.out_2 = {}
        self.vCount1 = g1.get_number_of_vertices()
        self.vCount2 = g2.get_number_of_vetices()

        # DEV NOTE: Unsure whether it is clever to store these values as attributes
        # Anyway I did not really understand how these values are used for compute_candidates()
        self.core_len = 0
        self.orig_core_len = 0
        self.t1_both_len = 0
        self.t2_both_len = 0
        self.t1_in_len = 0
        self.t2_in_len = 0
        self.t1_out_len = 0
        self.t2_out_len = 0

        for i in range(self.vCount1):
            self.core_1[i] = None
            self.in_1[i] = 0
            self.out_1[i] = 0
        for i in range(self.vCount2):
            self.core_2[i] = None
            self.in_2[i] = 0
            self.out_2[i] = 0

        # TODO: Implement Vertex sorting???

    def mb_algorithm(self):
        if self.all_vertices_of_g2_covered():
            print("Some output, to be annotated")
            return
        else:
            p = self.compute_candidates()
            for candidate in p:
                if self.is_feasible(candidate):
                    self.add_pair(candidate)
                    self.mb_algorithm()
            self.restore_data_structures()
            return

    def all_vertices_of_g2_covered(self):
        # TODO: Check g2 coverage
        return some_boolean

    def compute_candidates(self):
        # TODO: Implement function that produces a set of vertex tuples
        return p

    def is_feasible(self, candidate):
        # TODO: Check for feasibility of candidate pair
        g1_vertex, g2_vertex = candidate

        # NOTE: Attribute compatibility check of vertices and edges (below) is performed on graph1.
        # This may be important for non-symmetric compatibility attributes
        if not self.graph1.is_compatible(g1_vertex, g2_vertex):
            return False

        termout1 = 0
        termout2 = 0
        termin1 = 0
        termin2 = 0
        new1 = 0
        new2 = 0

        # Check 'out' edges of g1_vertex
        # DEV NOTE: IDs must be integers to index the MB_state data structures
        for edge in self.graph1.get_out_edge_list(g1_vertex):
            other_v_in_g1 = edge.get_start_and_end()[1]

            # DEV NOTE: EDGE label is interpreted as the edge compatibility attribute here
            g1_edge_label = edge.get_label()
            if self.core_1[other_v_in_g1.get_id()] is not None:
                other_v_in_g2 = self.core_1[other_v_in_g1.get_id()]
                if not self.graph2.has_edge(g2_vertex, other_v_in_g2) or \
                    not self.graph1.is_compatible_edge(g1_edge_label,
                                                       self.graph2.get_edge(g2_vertex, other_v_in_g2).get_label()):
                    return False
            else:
                if self.in_1[other_v_in_g1.get_id()] > 0:
                    termin1 += termin1
                if self.out_1[other_v_in_g1.get_id()] > 0:
                    termout1 += termout1
                if self.in_1[other_v_in_g1.get_id()] == 0 and \
                        self.out_1[other_v_in_g1.get_id()] == 0:
                    new1 += new1

        # Check 'in' edges of g1_vertex
        # DEV NOTE: IDs must be integers to index the MB_state data structures
        for edge in self.graph1.get_in_edge_list():
            other_v_in_g1 = edge.get_start_and_end()[0]

            # DEV NOTE: EDGE label is interpreted as the edge compatibility attribute here
            g1_edge_label = edge.get_label()
            if self.core_1[other_v_in_g1.get_id()] is not None:
                other_v_in_g2 = self.core_1[other_v_in_g1.get_id()]
                if not self.graph2.has_edge(other_v_in_g2, g2_vertex) or \
                        not self.graph1.is_compatible_edge(g1_edge_label,
                                                           self.graph2.get_edge(other_v_in_g2,
                                                                                g2_vertex).get_label()):
                    return False
            else:
                if self.in_1[other_v_in_g1.get_id()] > 0:
                    termin1 += termin1
                if self.out_1[other_v_in_g1.get_id()] > 0:
                    termout1 += termout1
                if self.in_1[other_v_in_g1.get_id()] == 0 and \
                        self.out_1[other_v_in_g1.get_id()] == 0:
                    new1 += new1

        # Check 'out' edges of g2_vertex
        # DEV NOTE: IDs must be integers to index the MB_state data structures
        for edge in self.graph2.get_out_edge_list(g2_vertex):
            other_v_in_g2 = edge.get_start_and_end()[1]
            if self.core_2[other_v_in_g2.get_id()] is not None:
                other_v_in_g1 = self.core_2[other_v_in_g2.get_id()]
                if not self.graph1.has_edge(g1_vertex, other_v_in_g1):
                    return False
            else:
                if self.in_2[other_v_in_g2.get_id()] > 0:
                    termin2 += termin2
                if self.out_2[other_v_in_g2.get_id()] > 0:
                    termout2 += termout2
                if self.in_2[other_v_in_g2.get_id()] == 0 and \
                        self.out_2[other_v_in_g2.get_id()] == 0:
                    new2 += new2

        # Check 'in' edges of g2_vertex
        # DEV NOTE: IDs must be integers to index the MB_state data structures
        for edge in self.graph2.get_in_edge_list():
            other_v_in_g2 = edge.get_start_and_end()[0]
            if self.core_2[other_v_in_g2.get_id()] is not None:
                other_v_in_g1 = self.core_2[other_v_in_g2.get_id()]
                if not self.graph1.has_edge(other_v_in_g1, g1_vertex):        g2_vertex).get_label()):
                    return False
            else:
                if self.in_2[other_v_in_g2.get_id()] > 0:
                    termin2 += termin2
                if self.out_2[other_v_in_g2.get_id()] > 0:
                    termout2 += termout2
                if self.in_2[other_v_in_g2.get_id()] == 0 and \
                        self.out_2[other_v_in_g2.get_id()] == 0:
                    new2 += new2
        return termin1 <= termin2 and termout1 <= termout2 and new1 <= new2

    def add_pair(self, candidate):
        # TODO: Implement function that adds a pair of vertices to the current state
        return

    def restore_data_structures(self):
        # TODO: Implement function that restores class attributes for backtracking
        return

