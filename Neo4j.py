'''
Created on 10.09.2019

@author: chrissi
'''
from py2neo import Graph, Node, Relationship, NodeMatcher, cypher

class NEO4J(object):
    '''
    classdocs
    '''

    def __init__(self,uri, user_name, pwd, vertices_objects, edges_objects, graph_id):
        '''
        Constructor
        '''
        self.__uri= uri
        self.__user =  user_name
        self.__pwd = pwd
        try: 
            self.__graph = Graph(uri, user=user_name, password=pwd)
            self.create_graphs(vertices_objects, edges_objects, graph_id)
        except:
            print("Please connect with Neo4J Server")
            print("URI: " + self.uri)
            print("USER_NAME: " + self.user)
            print("PASSWORD: " + self.pwd)
    
    def set_uri(self,uri):
        '''
        sets uri(string) of the neo4j database
        '''
        self.__uri = uri
        return

    def get_uri(self):
        '''
        returns uri(String) of the neo4j database
        '''
        return self.__uri
    
    def set_user(self, user):
        '''
        sets user(string) of the neo4j database
        '''
        self.__user = user
        return
    
    def get_user(self):
        '''
        returns user(String) of the neo4j database
        '''
        return self.__user
    
    def set_pwd(self, pwd):
        '''
        sets pwd(string) of the neo4j database
        '''
        self.__pwd = pwd
        return
    
    def get_pwd(self):
        '''
        returns pwd(String) of the neo4j database
        '''
        return self.__pwd
    
    def get_graph(self):
        '''
        returns graph(Object) of the neo4j database
        '''
        return self.__graph
    
    def create_graphs(self, vertices_objects, edges_objects, graph_id):
        """
        creates the graph in currentGraph-Session 
        edges_objectes -- A list of edge objects
        vertices_objectes -- A list of vertices objects
        graph_id -- specfic graph id to differentiate the graphs
        """
        #clear old Graphs
        #currentGraph.delete_all()
        print("Creating Neo4J View for '" + graph_id + "' ...")
        
        tx = self.get_graph().begin()#begin transaction
         
        #for each vertex create a Node in Neo4J
        for vertex in vertices_objects:
            if vertex.get_label() != "":
                currentNode = Node(vertex.get_label(), id=vertex.get_id(), label=vertex.get_label(), graph_id = graph_id)
            else:#if vertices doesnt have labels take id as label
                currentNode = Node(str(vertex.get_id()), id=vertex.get_id(), label=str(vertex.get_id()), graph_id = graph_id)
            tx.create(currentNode)
            
        tx.commit()#commit transaction
        
        tx = self.get_graph().begin()#begin new transaction
           
        #for each egde create relationship in Neo4J
        for edge in edges_objects:
            
            relationship = edge.get_label() #get relationship from edge
            start = edge.get_start_and_end()[0] #get start node
            end = edge.get_start_and_end()[1] #get end node
                        
            matcher = NodeMatcher(self.get_graph()) #find nodes in existing graph
            if start.get_label() != "":
                startNode = matcher.match(start.get_label(), id=start.get_id(),label=start.get_label(), graph_id = graph_id).first()
                endNode = matcher.match(end.get_label(), id=end.get_id(),label= end.get_label(), graph_id = graph_id).first()
            else:#if edeges doesnt have labels take id as label
                startNode = matcher.match(str(start.get_id()), id=start.get_id(),label=str(start.get_id()), graph_id = graph_id).first()
                endNode = matcher.match(str(end.get_id()), id=end.get_id(),label= str(end.get_id()), graph_id = graph_id).first()
            if relationship != "":
                relation = Relationship(startNode, relationship, endNode)
            else:
                relation = Relationship(startNode, " ", endNode)
            
            tx.create(relation)
                        
        tx.commit()
            
        return
