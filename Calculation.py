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
        for i in self.information.keys():
            
        
    def field_conditions(self):
        '''Handle the nodes in the field of the matrix'''
        
if __name__=="__main__":
    Voltage_Calculation(100,100,100,100)
        