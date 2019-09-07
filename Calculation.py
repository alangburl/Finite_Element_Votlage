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
        self.b_matrix=np.zeros([x_nodes*y_nodes,1])
        self.a_matrix=np.zeros([x_nodes*y_nodes,x_nodes*y_nodes])
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
        #and handle to terminals with known potential by setting
        #both the elements in 'a' and 'b' matrices
        for i in self.information.keys():
            #calling the function to find the nodes corresponding to the
            #terminals with a known potential on them and adding them to 
            #a dictionary to later be used to set the elements in the 'A' and 
            #'b' matrix
            matrix_locators=self.find_locations(self.information[i])
            counter=matrix_locators[0]
            while counter<=matrix_locators[1]:
                #set the potential in V for the 'b' matrix
                self.b_matrix[counter]=matrix_locators[2]
                #set the a matrix locations to be '1' signifying
                #a known boundary condition
                self.a_matrix[counter][counter]=1
                counter+=1
                
        #handle the remainder of the boundary conditions
        #take care of the top and bottom edges of the matrix
        for k in range(len(self.x_nodes)):
            if self.a_matrix[k][k]!=1:
                True 
    def field_conditions(self):
        '''Handle the nodes in the field of the matrix
           Using a finite difference simpliciation of Poisson's equations:
               V_w-del_y/(4(del_x+del_y))(V_(x-1)+V_(x+1))
               -del_x/(4(del_x+del_y))(V_(above)+V_(below))
               =-rho*del_x*del_y/(4e(del_x+del_y))
        '''
        #find delta x and delta y
        delta_x=self.x_nodes[1]-self.x_nodes[0]
        delta_y=self.y_nodes[1]-self.y_nodes[0]
        
        #since this function will be ran after the boundary conditions
        #have been handled, the only rows having a 0 on the diagonal
        #are the rows requiring information to be added
        for row in range(len(self.a_matrix)):
            for column in range(len(self.a_matrix)):
                if self.a_matrix[row][column]!=1:
                    self.a_matrix[row][column]=1 #set the node to be 1
                    #set the adjacent nodes 
                    self.a_matrix[row][column+1]=-delta_y/(4*(delta_x+delta_y))
                    self.a_matrix[row][column-1]=-delta_y/(4*(delta_x+delta_y))
                    #set the nodes above and below
                    self.a_matrix[row][column+len(self.x_nodes)]=-delta_x/(4*(delta_y+delta_x))
                    self.a_matrix[row][column-len(self.x_nodes)]=-delta_x/(4*(delta_y+delta_x))
    def find_locations(self,geometry_list):
        '''Used to find the starting and ending indices of the matrix to
        and set the locations to the specified potential in the A matrix
        
        Geometry arguments are as such:
            [x_start,y_start,x_len,y_len,potential]
        '''
        #first handle the possible terminals on the left vertical side
        start_location=0
        end_location=0
        if geometry_list[0]==0 and geometry_list[2]==0:
            #deterimine the starting point in the matrix going from top down
            for j in range(len(self.y_nodes)):
                if geometry_list[1]<=self.y_nodes[j]:
                    start_location=j*len(self.x_nodes) #setting the starting element
                    break
            for j in range(len(self.y_nodes)):
                if geometry_list[1]+geometry_list[3]<=self.y_nodes[j]:
                    #setting the last element with the given potential
                    end_location=j*len(self.x_nodes)
                    break
        elif geometry_list[0]==self.x_dim and geometry_list[2]==0:
            for j in range(len(self.y_nodes)):
                if geometry_list[1]<=self.y_nodes[j]:
                    if j!=0:
                        start_location=(j+1)*len(self.x_nodes)-1
                    else:
                        start_location=len(self.x_nodes)-1
                    break
            for j in range(len(self.y_nodes)):
                if geometry_list[1]+geometry_list[3]<=self.y_nodes[j]:
                    end_location=(j+1)*len(self.x_nodes)-1
        #handle the posibble horizontal terminals starting at y=0 and going 
        #down
        if geometry_list[1]==0 and geometry_list[3]==0:
            for j in range(len(self.x_nodes)):
                if geometry_list[0]<=self.x_nodes[j]:
                    start_location=j
                    break
            for j in range(len(self.x_nodes)):
                if geometry_list[0]+geometry_list[2]<=self.x_nodes[j]:
                    end_location=j
        elif geometry_list[1]==self.y_dim and geometry_list[3]==0:
            for j in range(len(self.x_nodes)-1,-1,-1):
                if geometry_list[0]>=self.x_nodes[j]:
                    start_location=j
                    break
            for j in range(len(self.x_nodes)-1,-1,-1):
                if geometry_list[0]+geometry_list[2]>=self.x_nodes[j]:
                    end_location=j
                    break
        return [start_location,end_location,geometry_list[4]]
                
if __name__=="__main__":
    Voltage_Calculation(100,100,100,100)
        