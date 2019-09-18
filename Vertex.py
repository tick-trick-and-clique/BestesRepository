#!/usr/bin/env python
# -*- coding: utf-8 -*-
class VERTEX(object):
    def __init__(self, id, label):
        self.__id = id
        self.__neighbours = []
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

    def get_neighbours(self):
        return self.__neighbours

    def get_label(self):
        return self.__label

    def set_neighbours(self, neighbours):
        self.__neighbours = neighbours

    def append_neighbours(self, new_neighbours):
        if not isinstance(new_neighbours, list):
            raise TypeError("\n Dude... passed parameter has to be a list! \n")
        else:
            if len(new_neighbours) == 1:
                self.__neighbours.append(new_neighbours)        # Hier wird eine Liste angefügt, oder?!
            elif len(new_neighbours) > 1:
                self.__neighbours.extend(new_neighbours)

    def append_neighbour(self, new_neighbour):
        if not isinstance(new_neighbour, type(self)):
            raise TypeError("\n Dude... passed parameter has to be of type 'VERTEX'! \n")
        else:
            self.__neighbours.append(new_neighbour)

    def add_vertex_to_mapping(self, vertex, graph_name):
        self.__mapping[graph_name] = vertex

    def get_mapping(self):
        return self.__mapping

    def combine_mapping(self, vertex):
        self.__mapping = {**self.__mapping, **vertex.get_mapping()}
