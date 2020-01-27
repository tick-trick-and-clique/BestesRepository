#!/usr/bin/env python
# -*- coding: utf-8 -*-


class VERTEX(object):
    def __init__(self, id, label):
        self.__id = id
        self.__out_neighbours = set()
        self.__label = label
        self.__mapping = {}

    def __str__(self):
        '''
        builds a string representation of a vertex
        '''
        res = "[" + str(self.__id) + ";" + str(self.__label) + "]"
        return res

    def get_id(self):
        return self.__id

    def get_out_neighbours(self):
        return self.__out_neighbours

    def get_label(self):
        return self.__label

    def set_id(self, id):
        self.__id = id

    def set_out_neighbours(self, neighbours):
        self.__out_neighbours = set(neighbours)

    def add_out_neighbour(self, new_neighbour):
        if not isinstance(new_neighbour, type(self)):
            raise TypeError("\n Dude... passed parameter has to be of type 'VERTEX'! \n")
        else:
            self.__out_neighbours.add(new_neighbour)

    def add_vertex_to_mapping(self, vertex, graph_name):
        self.__mapping[graph_name] = vertex

    def get_mapping(self):
        return self.__mapping

    def combine_mapping(self, vertex):
        self.__mapping = {**self.__mapping, **vertex.get_mapping()}
