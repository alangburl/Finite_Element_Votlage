#the class used in calculation of the voltage matrix
import numpy as np
import matplotlib.pyplot as plt
import pylab,time

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
#        plt.scatter(*zip(*data),s=0.1)
#        plt.show()
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
            
        #handle the remainder of the boundary conditions
        #take care of the top and bottom edges of the matrix
        #less the two corners as they are special cases
        delta_x=self.x_nodes[1]-self.x_nodes[0]
        delta_y=self.y_nodes[1]-self.y_nodes[0]
        for k in range(1,len(self.x_nodes)-1):
            if self.a_matrix[k][k]!=1:
                self.a_matrix[k][k]=1
                self.a_matrix[k][k+1]=-delta_y/(2*(delta_x+delta_y))
                self.a_matrix[k][k-1]=-delta_y/(2*(delta_x+delta_y))
                self.a_matrix[k][k+len(self.x_nodes)]=(-delta_x/
                            (delta_x+delta_y))
        #handles the boundary conditions for the bottom of the matrix
        for k in range(len(self.x_nodes)-1,1,-1):
            if self.a_matrix[-k][-k]!=1:
                self.a_matrix[-k][-k]=1
                self.a_matrix[-k][-k+1]=-delta_y/(2*(delta_x+delta_y))
                self.a_matrix[-k][-k-1]=-delta_y/(2*(delta_x+delta_y))
                self.a_matrix[-k][-k-len(self.x_nodes)]=(-delta_x/
                             (delta_x+delta_y))
        #handle the left side of the geometric boundary conditions
        mul=len(self.x_nodes)
        for k in range(1,len(self.y_nodes)-1):
            if self.a_matrix[k*mul][k*mul]!=1:
                self.a_matrix[k*mul][k*mul]=1
                self.a_matrix[k*mul][k*mul+1]=-delta_y/(delta_x+delta_y)
                self.a_matrix[k*mul][(k+1)*mul]=-delta_x/(2*(delta_x+delta_y))
                self.a_matrix[k*mul][(k-1)*mul]=-delta_x/(2*(delta_x+delta_y))
        #handle the right side geometric boundaries
        for k in range(1,len(self.y_nodes)-1):
            if self.a_matrix[(k+1)*mul-1][(k+1)*mul-1]!=1:
                self.a_matrix[(k+1)*mul-1][(k+1)*mul-1]=1
                self.a_matrix[(k+1)*mul-1][(k+1)*mul-2]=(-delta_y/
                              (delta_x+delta_y))
                self.a_matrix[(k+1)*mul-1][(k+2)*mul-1]=(-delta_x/
                              (2*(delta_x+delta_y)))
                self.a_matrix[(k+1)*mul-1][(k)*mul-1]=(-delta_x/
                              (2*(delta_x+delta_y)))
        #handle the boundary conditions at the four corners
        #corner_locations=[0,len(self.x_nodes)-1,-1,-len(self.x_nodes)]
        if self.a_matrix[0][0]!=1:
            self.a_matrix[0][0]=1
            self.a_matrix[0][1]=-delta_y/(delta_y+delta_x)
            self.a_matrix[0][len(self.x_nodes)]=-delta_x/(delta_y+delta_x)
        if self.a_matrix[len(self.x_nodes)-1][len(self.x_nodes)-1]!=1:
            self.a_matrix[len(self.x_nodes)-1][len(self.x_nodes)-1]=1
            self.a_matrix[len(self.x_nodes)-1][len(self.x_nodes)-2]=(-delta_y/
                          (delta_x+delta_y))
            self.a_matrix[len(self.x_nodes)-1][len(self.x_nodes)*2-1]=(-delta_x
                          /(delta_x+delta_y))
        if self.a_matrix[-1][-1]!=1:
            self.a_matrix[-1][-1]=1
            self.a_matrix[-1][-2]=-delta_y/(delta_x+delta_y)
            self.a_matrix[-1][-1-len(self.x_nodes)]=-delta_x/(delta_x+delta_y)
        if self.a_matrix[-len(self.x_nodes)][-len(self.x_nodes)]!=1:
            self.a_matrix[-len(self.x_nodes)][-len(self.x_nodes)]=1
            self.a_matrix[-len(self.x_nodes)][-len(self.x_nodes)+1]=(-delta_y/
                          (delta_x+delta_y))
            self.a_matrix[-len(self.x_nodes)][-2*len(self.x_nodes)+1]=(-delta_x
                          /(delta_y+delta_x))
    def field_conditions(self):
        '''Handle the nodes in the field of the matrix
           Using a finite difference simpliciation of Poisson's equations:
               V_w-del_y/(2(del_x+del_y))(V_(x-1)+V_(x+1))
               -del_x/(2(del_x+del_y))(V_(above)+V_(below))
               =-rho*del_x*del_y/(2e(del_x+del_y))
        '''
        #find delta x and delta y
        delta_x=self.x_nodes[1]-self.x_nodes[0]
        delta_y=self.y_nodes[1]-self.y_nodes[0]
        #since this function will be ran after the boundary conditions
        #have been handled, the only rows having a 0 on the diagonal
        #are the rows requiring information to be added
        for row in range(len(self.a_matrix)-1):
                if self.a_matrix[row][row]!=1:
                    self.a_matrix[row][row]=1 #set the node to be 1
                    #set the adjacent nodes 
                    self.a_matrix[row][row+1]=-delta_y/(2*(delta_x+delta_y))
                    self.a_matrix[row][row-1]=-delta_y/(2*(delta_x+delta_y))
                    #set the nodes above and below
                    self.a_matrix[row][row+len(self.x_nodes)]=-delta_x/(2*
                                 (delta_y+delta_x))

                    self.a_matrix[row][row-len(self.x_nodes)]=-delta_x/(2*
                                 (delta_y+delta_x))
        #once this is completed, the matrices are ready to be solved
        self.solve()
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
                    start_location=j
                    break
            for j in range(len(self.y_nodes)):
                if float(geometry_list[1]+geometry_list[3])<=self.y_nodes[j]:
                    #setting the last element with the given potential
                    end_location=j+1
                    break
            for j in range(start_location,end_location):
                self.a_matrix[j*len(self.x_nodes)][j*len(self.x_nodes)]=1
                self.b_matrix[j*len(self.x_nodes)]=geometry_list[4]
        elif geometry_list[0]==self.x_dim and geometry_list[2]==0:
            for j in range(len(self.y_nodes)):
                if geometry_list[1]<=self.y_nodes[j]:
                    start_location=j
                    break
            for j in range(len(self.y_nodes)):
                if geometry_list[1]+geometry_list[3]<=self.y_nodes[j]:
                    end_location=j
                    break
            for j in range(start_location,end_location+1):
                self.a_matrix[(j+1)*len(self.x_nodes)-1][(j+1)*len(self.x_nodes)-1]=1
                self.b_matrix[(j+1)*len(self.x_nodes)-1]=geometry_list[4]
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
                    break
            for j in range(start_location,end_location+1):
                self.a_matrix[j][j]=1
                self.b_matrix[j]=geometry_list[4]
                
        elif geometry_list[1]==self.y_dim and geometry_list[3]==0:
            rev_list=np.flip(self.x_nodes)
            for j in range(len(rev_list)):
                if geometry_list[0]>=rev_list[j]:
                    start_location=j+2
                    break
            for j in range(len(rev_list)):
                if geometry_list[0]+geometry_list[2]>=rev_list[j]:
                    end_location=j+1
                    break
            for j in range(end_location,start_location):
                self.a_matrix[-j][-j]=1
                self.b_matrix[-j]=geometry_list[4]
        return [start_location,end_location,geometry_list[4]]
    
    def solve(self):
        '''Sovle the equation Ax=b for the x vector, the potentilal voltages
        '''
        voltage_vector=np.linalg.solve(self.a_matrix,self.b_matrix)
        self.vector=voltage_vector.reshape(
                [len(self.y_nodes),len(self.x_nodes)])
        self.plotting()
        return self.vector
    def plotting(self):
        '''Plot the resulting voltages as a function of the position
        '''
        fig,ax=plt.subplots()
        contour=ax.contourf(self.x_nodes,self.y_nodes,self.vector,levels=20)
#        ax.clabel(contour,color='k')
        ax.set_title('Potential distribution across planar device')
        ax.set_xlabel(r'x Distance ($\mu m$)')
        ax.set_ylabel(r'y Distance ($\mu m$)')
        color_bar=fig.colorbar(contour)            
if __name__=="__main__":
    s=time.time()
    x=Voltage_Calculation(100,100,100,100,{0:[0,0,50,0,500],1:[0,100,20,0,200],
                                         2:[80,100,20,0,50]})
    run=time.time()-s