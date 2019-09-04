#the class used in calculation of the voltage matrix
import numpy as np
import matplotlib.pyplot as plt
import pylab

class Voltage_Calculation():
    '''Class used in calculation of potential'''
    def __init__(self,x_nodes,y_nodes,x_dim,y_dim,information=None):
        '''Initialize the class for use'''

        #initialize a matrix
        self.x_dim,self.y_dim,self.information=x_dim,y_dim,information
        self.a_matrix=np.zeros([x_nodes,y_nodes])
        #discertize the length into the given number of elements
        self.x_nodes=np.linspace(0,self.x_dim,x_nodes)
        self.y_nodes=np.linspace(0,self.y_dim,y_nodes)
        #generate matrices for x and y to plot the nodes
        data=[]
        for i in range(len(self.x_nodes)):
            for j in range(len(self.y_nodes)):
                data.append((self.x_nodes[i],self.y_nodes[j]))
        #plotting the scatter 
        plt.scatter(*zip(*data),s=0.1)
        plt.show()
        self.boundary_conditions()
        self.field_conditions()
    def boundary_conditions(self):
        '''Handle the boundary conditions'''
        #first extract the data from the information dictionary
        x_locator=0
        for i in self.information.keys():
            #calling the function to find the node corresponding to the
            #node value having a value than the starting point in of the given
            #dictionary list for given direction
            self.find_locations(self.information[i])
        
    def field_conditions(self):
        '''Handle the nodes in the field of the matrix'''
        
    def find_locations(self,geometry_list):
        '''Used to find the starting and ending indices of the matrix to
        and set the locations to the specified potential in the A matrix'''
        #first handle the possible terminals on the vertical sides
        if geometry_list[0]==self.x_dim or geometry_list[0]==0 and geometry_list[2]==0:
            #deterimine the starting point in the matrix going from top down
            start_location=0
            end_location=0
            for j in range(len(self.y_nodes)):
                if geometry_list[1]<=self.y_nodes[j]:
                    start_location=j
                elif geometry_list[1]+geometry_list[3]<=self.y_nodes[j]:
                    end_location=j
            
if __name__=="__main__":
    Voltage_Calculation(100,100,100,100)
        