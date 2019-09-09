from numpy import average
#prefined imports
import sys,os,time
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QPushButton,QWidget,QGridLayout,
                             QSizePolicy,QComboBox,QLineEdit,QTextEdit,
                             QMessageBox,QInputDialog,QMainWindow,QAction
                             ,QDockWidget,QTableWidgetItem,QVBoxLayout,
                             QFileDialog, QSplitter, QFrame,QHBoxLayout,
                             QStyleFactory,QLabel)
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from PyQt5.QtGui import (QFont,QIcon,
                         QPainter,QPen)
from PyQt5.QtCore import Qt, QRect
from Calculation import Voltage_Calculation

class Monitor(QMainWindow):
    '''Sets up a GUI for finding the potentials using a finite difference 
        method. Geometric conditions are requried to be known otherwise 
        the software will fail to compute the required matrices.
        
        The current implementation in code will allow for variation in 
        dielectric constants for different material. However drawing the 
        geometry on screen proves to be difficult.
    '''
    def __init__(self,*kwargs):
        super().__init__()
        self.size_policy=QSizePolicy.Expanding
        self.font=QFont()
        self.font.setPointSize(12)
        self.showMaximized()
        self.setWindowIcon(QIcon('RSIL_Logo.png'))
        self.setWindowTitle('Finite difference solver')
#        self.showMaximized()
        self.setGeometry(100,100,1000,500)
        self.base_geometry=QRect()
        self.init()
        self.menu_bar()
    def init(self):
        '''Setting up the interface for basic information and drawing the 
        geometry
        '''
        self.x_total=QLineEdit(self)
        self.x_total.setFont(self.font)
        self.x_total.setSizePolicy(self.size_policy,self.size_policy)
        self.x_total.setText('0')
        self.x_total.setToolTip('''Enter the total size in the horizontal\ndirection of the area in question in microns''')
        
        self.y_total=QLineEdit(self)
        self.y_total.setFont(self.font)
        self.y_total.setSizePolicy(self.size_policy,self.size_policy)
        self.y_total.setText('0')
        self.y_total.setToolTip('''Enter the total size in the vertical direction of the area in question in microns''')
        
        self.x_nodes=QLineEdit(self)
        self.x_nodes.setFont(self.font)
        self.x_nodes.setSizePolicy(self.size_policy,self.size_policy)
        self.x_nodes.setText('0')
        self.x_nodes.setToolTip('Number of nodes to evaluate in the horizontal direction')
        
        self.y_nodes=QLineEdit(self)
        self.y_nodes.setFont(self.font)
        self.y_nodes.setSizePolicy(self.size_policy,self.size_policy)
        self.y_nodes.setText('0')
        self.y_nodes.setToolTip('Number of nodes in the vertical direction')
        
        self.terminal_number=QLineEdit(self)
        self.terminal_number.setFont(self.font)
        self.terminal_number.setSizePolicy(self.size_policy,self.size_policy)
        self.terminal_number.setText('0')
        self.terminal_number.setToolTip('''Number of terminals used as boundary conditions.\nGeometry and potential will be entered in coming steps''')
        
        #Labels for the geometry entry sections
        self.x_total_label=QLabel(self)
        self.x_total_label.setFont(self.font)
        self.x_total_label.setSizePolicy(self.size_policy,self.size_policy)
        self.x_total_label.setText('x-Direction(um):')

        self.y_total_label=QLabel(self)
        self.y_total_label.setFont(self.font)
        self.y_total_label.setSizePolicy(self.size_policy,self.size_policy)
        self.y_total_label.setText('y-Direction(um):')  
        
        self.x_nodes_label=QLabel(self)
        self.x_nodes_label.setFont(self.font)
        self.x_nodes_label.setSizePolicy(self.size_policy,self.size_policy)
        self.x_nodes_label.setText('# nodes in x:')
                                   
        self.y_nodes_label=QLabel(self)
        self.y_nodes_label.setFont(self.font)
        self.y_nodes_label.setSizePolicy(self.size_policy,self.size_policy)
        self.y_nodes_label.setText('# nodes in y:')    
        
        self.terminal_number_label=QLabel(self)
        self.terminal_number_label.setFont(self.font)
        self.terminal_number_label.setSizePolicy(self.size_policy,self.size_policy)
        self.terminal_number_label.setText('# of terminals:')
        
        self.geometry_entry=QPushButton('Terminal Geometry',self)
        self.geometry_entry.setSizePolicy(self.size_policy,self.size_policy)
        self.geometry_entry.setFont(self.font)
        self.geometry_entry.setToolTip(
                'Launches window to enter geometric conditions of terminals')
        self.geometry_entry.clicked.connect(self.geom_enter)
        self.geometry_entry.setEnabled(True)
        
        self.calculate=QPushButton('Calculate',self)
        self.calculate.setFont(self.font)
        self.calculate.setSizePolicy(self.size_policy,self.size_policy)
        self.calculate.setToolTip('Calculates the potential at each node and graphs')
        self.calculate.clicked.connect(self.calculation)
        self.calculate.setDisabled(True)
        
        #create the basic layout member
        self.layout=QHBoxLayout()
        #create a QWidget to use add all the basic information into
        basic_info_=QWidget()
        #create a layout for the basic info to be laid out in and put it there
        basic_layout=QGridLayout()
        basic_layout.addWidget(self.x_total_label,0,0)
        basic_layout.addWidget(self.x_total,0,1)
        basic_layout.addWidget(self.y_total_label,1,0)
        basic_layout.addWidget(self.y_total,1,1)
        basic_layout.addWidget(self.x_nodes_label,2,0)
        basic_layout.addWidget(self.x_nodes,2,1)
        basic_layout.addWidget(self.y_nodes_label,3,0)
        basic_layout.addWidget(self.y_nodes,3,1)
        basic_layout.addWidget(self.terminal_number_label,4,0)
        basic_layout.addWidget(self.terminal_number,4,1)
        basic_info_.setLayout(basic_layout)
        #setting up a frame for the drawing rectangle, will be blank
        #until the drawing begins
        self.geometry_visualization=QFrame(self)
        self.geometry_visualization.setFrameShape(QFrame.StyledPanel)
        #splitting the window horizontally and add the basic info and blank
        #area for the geometry to be drawn in
        geom_splitter=QSplitter(Qt.Horizontal)
        geom_splitter.addWidget(basic_info_)
        geom_splitter.addWidget(self.geometry_visualization)
        geom_splitter.setSizes([250,500])
        #set up a widget to add the buttons to control the execution
        controls=QWidget()
        #create a layout and add the buttons to it
        controls_layout=QHBoxLayout()
        controls_layout.addWidget(self.geometry_entry)
        controls_layout.addWidget(self.calculate)
        controls.setLayout(controls_layout)
        #add a vertical splitter and add the top splitter and the
        #bottom widget together and add them to the entire layout
        controls_spliter=QSplitter(Qt.Vertical)
        controls_spliter.addWidget(geom_splitter)
        controls_spliter.addWidget(controls)
        self.layout.addWidget(controls_spliter)
        #do some manipulation to get the layouts to play nicely
#        self.setLayout(self.layout)
        layout=QWidget()
        layout.setLayout(self.layout)
        self.setCentralWidget(layout)
        self.show()

    def menu_bar(self):
        '''Create the menu bar for the main window will include
                Name:       Shortcut:         Function called:
            File:
                New         CTRL+N            new_invoice_begin
                Open        CTRL+O            existing_invoice_open
                Save        CTRL+S            save_invoice
                Print       CTRL+P            print_invoice
                Quit        ALT+F4            exit_system
        '''        
        self.menuFile = self.menuBar().addMenu("&File")
        self.actionNew=QAction('&New',self)
        self.actionNew.setShortcut('Ctrl+N')
#        self.actionNew.triggered.connect(self.new_invoice_begin)        
        self.actionQuit=QAction('&Exit',self)
#        self.actionQuit.triggered.connect(self.exit_system)
        self.actionQuit.setShortcut('Alt+F4')
        self.menuFile.addActions([self.actionNew,
                                  self.actionQuit])

    def geom_enter(self):
        '''Used when entering the geometry of the terminals'''
        #first make sure all the values are filled with correct values
        #and through and error if they are not
#        try:
        self.total_x_=float(self.x_total.text())
        self.total_y_=float(self.y_total.text())
        self.nodes_x=int(self.x_nodes.text())
        self.nodes_y=int(self.y_nodes.text())
        self.number=int(self.terminal_number.text())
        #draw the base rectangular geomtery and apply a scaling factor to 
        #the sizes if need be
        x=self.frameGeometry().width()-self.geometry_visualization.frameGeometry().width()
        self.base_geometry=QRect(x,55,
                                 self.scalar(self.total_x_)*self.total_x_,
                                 self.scalar(self.total_y_)*self.total_y_)
        self.update()
        #create a dictionary to store the information passed to the upcoming 
        #widget to be stored in to later draw and analyze the geometry
        self.boundary_conditions={}
        for i in range(self.number):
            self.boundary_conditions[i]=[]
        self.win=PopUp(self.number)
        self.win.show()
        self.calculation_data=self.win.information
        self.calculate.setEnabled(True)
#        except:
#            error_data=QMessageBox(self)
#            error_data.setText('Please enter numeric values in all fields')
#            error_data.setWindowTitle('Numeric Error')
#            error_data.exec()
    def scalar(self,lenght):
        '''Determine the proper scaling to adjust the size to be visible by 
        taking the largest dimension of the input geometry and scaling it to
        fit the entire area fo the provided region'''
        if self.total_x_ or self.total_y_>100:
            return 1
    
    def paintEvent(self,event):
        QMainWindow.paintEvent(self, event)
        if not self.base_geometry.isNull():
            painter = QPainter(self)
            pen = QPen(Qt.black, 1)
            painter.setPen(pen)
            painter.drawRect(self.base_geometry)  
            
    def calculation(self):
        '''Call the calculation method and run it to get the results'''
        self.calculate.setDisabled(True)
        self.geometry_entry.setDisabled(True)
        self.values=Voltage_Calculation(self.nodes_x,self.nodes_y,
                             self.total_x_,self.total_y_,self.calculation_data)
        self.plot=PlotCanvas(self.values.x_nodes,
                             self.values.y_nodes,self.values.vector)
        self.calculate.setEnabled(True)
        self.geometry_entry.setEnabled(True)
        
#Create the class needed to pop open the widget to input 
#the terminal geometry
class PopUp(QWidget):
    def __init__(self,number_terminals):
        super().__init__()
        self.number_of_terminals=number_terminals
        self.setGeometry(100,100,500,300)
        self.size_policy=QSizePolicy.Expanding
        self.font=QFont()
        self.font.setPointSize(12)
        self.setWindowTitle('Terminal Geometry Entry')
        self.init()
    def init(self):
        '''Initialize all the widgets needed for inputting the geometry
        '''
        #define the dictionary values will be added to 
        self.information={}
        #set up the combo box to select the terminal to enter geometry for
        self.terminal_number=QComboBox(self)
        self.terminal_number.setFont(self.font)
        self.terminal_number.setSizePolicy(self.size_policy,self.size_policy)
        self.terminal_number.setToolTip('Select the terminal you wish to enter geometry for')
        for i in range(self.number_of_terminals):
            self.terminal_number.addItem(str(i))
        
        #widgets for getting the geometry and potential of the selected terminal
        self.x_start=QLineEdit(self)
        self.x_start.setFont(self.font)
        self.x_start.setSizePolicy(self.size_policy,self.size_policy)
        self.x_start.setToolTip('Enter the starting point given the bottom right most corner as the origin')
        self.x_start.setText('0')
        
        self.y_start=QLineEdit(self)
        self.y_start.setFont(self.font)
        self.y_start.setSizePolicy(self.size_policy,self.size_policy)
        self.y_start.setToolTip('Enter the starting point given the bottom right most corner as the origin')
        self.y_start.setText('0')
        
        self.x_length=QLineEdit(self)
        self.x_length.setFont(self.font)
        self.x_length.setSizePolicy(self.size_policy,self.size_policy)
        self.x_length.setToolTip(
                'Length in X direction from starting point, must be greater than 0')
        self.x_length.setText('0')
        
        self.y_length=QLineEdit(self)
        self.y_length.setFont(self.font)
        self.y_length.setSizePolicy(self.size_policy,self.size_policy)
        self.y_length.setToolTip(
                'Length in Y direction from starting point, must be greater than 0')
        self.y_length.setText('0')
        
        self.potential=QLineEdit(self)
        self.potential.setFont(self.font)
        self.potential.setSizePolicy(self.size_policy,self.size_policy)
        self.potential.setToolTip('Potential Voltage applied at the boundary')
        self.potential.setText('0')
        #labels for the individual boxes
        self.terminal_number_label=QLabel(self)
        self.terminal_number_label.setText('Terminal Number:')
        self.terminal_number_label.setSizePolicy(self.size_policy,self.size_policy)
        self.terminal_number_label.setFont(self.font)
        
        self.x_start_label=QLabel(self)
        self.x_start_label.setText('Starting x(um):')
        self.x_start_label.setSizePolicy(self.size_policy,self.size_policy)
        self.x_start_label.setFont(self.font)
        
        self.y_start_label=QLabel(self)
        self.y_start_label.setText('Starting y(um):')
        self.y_start_label.setSizePolicy(self.size_policy,self.size_policy)
        self.y_start_label.setFont(self.font)
        
        self.x_length_label=QLabel(self)
        self.x_length_label.setText('x Length(um):')
        self.x_length_label.setSizePolicy(self.size_policy,self.size_policy)
        self.x_length_label.setFont(self.font)
        
        self.y_length_label=QLabel(self)
        self.y_length_label.setText('y Length(um):')
        self.y_length_label.setSizePolicy(self.size_policy,self.size_policy)
        self.y_length_label.setFont(self.font)
        
        self.potential_label=QLabel(self)
        self.potential_label.setText('Terminal Potential(V):')
        self.potential_label.setSizePolicy(self.size_policy,self.size_policy)
        self.potential_label.setFont(self.font)
        
        self.next=QPushButton('Next Terminal',self)
        self.next.setFont(self.font)
        self.next.setSizePolicy(self.size_policy,self.size_policy)
        self.next.setToolTip('Proceed entering the next terminal')
        self.next.clicked.connect(self.next_terminal)
        
        self.finished=QPushButton('Finished', self)
        self.finished.setFont(self.font)
        self.finished.setSizePolicy(self.size_policy,self.size_policy)
        self.finished.setToolTip(
                'Exit this window and process with calculations')
        self.finished.clicked.connect(self.complete)
        self.finished.setDisabled(True)
        
        #add all the stuff into a layout
        layout=QGridLayout(self)
        layout.addWidget(self.terminal_number,0,1,1,3)
        layout.addWidget(self.terminal_number_label,0,0)
        layout.addWidget(self.x_start,1,1)
        layout.addWidget(self.x_start_label,1,0)
        layout.addWidget(self.y_start,2,1)
        layout.addWidget(self.y_start_label,2,0)
        layout.addWidget(self.potential,3,1)
        layout.addWidget(self.potential_label,3,0)
        layout.addWidget(self.x_length,1,3)
        layout.addWidget(self.x_length_label,1,2)
        layout.addWidget(self.y_length,2,3)
        layout.addWidget(self.y_length_label,2,2)
        layout.addWidget(self.next,3,2,1,2)
        layout.addWidget(self.finished,4,0,1,4)
        self.setLayout(layout)
        
    def next_terminal(self):
        '''Ingest the info from each of the fields and add it to the
        dictionary of values
        
        The list of values is in the following order:
                x_start, y_start, x_length,y_length, potential
        '''
        self.information[self.terminal_number.currentText()]=[
                float(self.x_start.text()),float(self.y_start.text()),
                float(self.x_length.text()),
                float(self.y_length.text()),float(self.potential.text())]
        
        self.terminal_number.removeItem(self.terminal_number.findText(
                self.terminal_number.currentText()))
        if self.terminal_number.count()==1:
            self.finished.setEnabled(True)
            self.next.setDisabled(True)
    def complete(self):
        '''Close the second window
        '''
        self.information[self.terminal_number.currentText()]=[
                float(self.x_start.text()),float(self.y_start.text()),
                float(self.x_length.text()),
                float(self.y_length.text()),float(self.potential.text())]        
        self.close()

class PlotCanvas(QtWidgets.QMainWindow):
    def __init__(self,x_values,y_values,voltages):
        super(PlotCanvas, self).__init__()
        self.setWindowTitle('Voltage Distribution')
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)
        fig=Figure(figsize=(8, 8))
        static_canvas = FigureCanvas(fig)
        layout.addWidget(static_canvas)
        self.addToolBar(NavigationToolbar(static_canvas, self))
        
        self.plots = static_canvas.figure.subplots()
        contour=self.plots.contourf(x_values, y_values,voltages,levels=20)
        fig.colorbar(contour)        
        self.plots.set_xlabel(r'x($\mu m$)')
        self.plots.set_ylabel(r'y($\mu m$)')
        self.plots.set_title('Potential distribution across planar device')
        self.show()
        
if __name__=="__main__":
    app=QApplication(sys.argv)
    ex=Monitor()
    sys.exit(app.exec_())        