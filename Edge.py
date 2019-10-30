#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 07.05.2019

@author: chris
'''

class EDGE(object):
    def __init__(self, id, start_and_end, label):
        self.__id = id
        self.__start_and_end = start_and_end
        self.__label = label
        
    def __str__(self):
        res = "[" + str(self.__id) + ";" 
        start = self.__start_and_end[0]
        end = self.__start_and_end[1]
        res += "(" + str(start) + ";" + str(end) + ")" + ";"
        res += str(self.__label) + "] "
        return res

    def get_id(self):
        return self.__id

    def get_start_and_end(self):
        return self.__start_and_end

    def get_label(self):
        return self.__label


def is_compatible_edge(edge, other_edge):
    # Function returns whether two edges of are 'compatible'.
    # Here, this is performed by comparison of edge labels.
    if edge.get_label() == other_edge.get_label():
        return True
    else:
        return False
