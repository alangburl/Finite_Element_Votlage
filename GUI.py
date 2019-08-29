import matplotlib.pyplot as plt
from numpy import average
#prefined imports
import sys,os,time
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QPushButton,QWidget,QGridLayout,
                             QSizePolicy,QComboBox,QLineEdit,QTextEdit,
                             QMessageBox,QInputDialog,QMainWindow,QAction
                             ,QDockWidget,QTableWidgetItem,QVBoxLayout,
                             QFileDialog)
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from PyQt5.QtGui import QFont,QIcon, QImage, QPalette, QBrush,QPainter
from PyQt5.QtCore import Qt

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
        self.showMaximized()
        self.init()
        
        self.menu_bar()
    def init(self):
        self.x_total=QLineEdit(self)
        self.x_total.setFont(self.font)
        self.x_total.setSizePolicy(self.size_policy,self.size_policy)
        self.x_total.setText('X-Direction in microns')
        self.x_total.setToolTip('''Enter the total size in the horizontal
                            direction of the area in question in microns''')
        
        self.y_total=QLineEdit(self)
        self.y_total.setFont(self.font)
        self.y_total.setSizePolicy(self.size_policy,self.size_policy)
        self.y_total.setText('Y-Direction in microns')
        self.y_total.setToolTip('''Enter the total size in the vertical
                            direction of the area in question in microns''')
        
        self.x_nodes=QLineEdit(self)
        self.x_nodes.setFont(self.font)
        self.x_nodes.setSizePolicy(self.size_policy,self.size_policy)
        self.x_nodes.setText('Number of nodes in horizontal direction')
        self.x_nodes.setToolTip('Number of nodes to evaluate in X-Direction')
        
        self.y_nodes=QLineEdit(self)
        self.y_nodes.setFont(self.font)
        self.y_nodes.setSizePolicy(self.size_policy,self.size_policy)
        self.y_nodes.setText('Number of nodes in vertical direction')
        self.y_nodes.setToolTip('Number of nodes in the vertical direction')
        
        
        self.terminal_number=QLineEdit(self)
        self.terminal_number.setFont(self.font)
        self.terminal_number.setSizePolicy(self.size_policy,self.size_policy)
        self.terminal_number.setText('Number of terminals')
        self.terminal_number.setToolTip('''Number of terminals used as
                                        boundary conditions. Geometry and
                                        potential will be entered in
                                        the coming steps''')
        
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
#        self.calculate.clicked.connect(self.calcuation)
        self.calculate.setDisabled(True)
        
        self.layout=QGridLayout()
        self.layout.addWidget(self.x_total,0,0,1,2)
        self.layout.addWidget(self.y_total,1,0,1,2)
        self.layout.addWidget(self.x_nodes,2,0,1,2)
        self.layout.addWidget(self.y_nodes,3,0,1,2)
        self.layout.addWidget(self.terminal_number,4,0,1,2)
        self.layout.addWidget(self.geometry_entry,5,0)
        self.layout.addWidget(self.calculate,5,1)
        
        self.setLayout(self.layout)
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
    def paintEvent(self,event):
        '''Used when entering the geometry of the terminals'''
        #first make sure all the values are filled with correct values
        #and through and error if they are not
        try:
            self.total_x_=float(self.x_total.text())
            self.total_y_=float(self.y_total.text())
            self.nodes_x=float(self.x_nodes.text())
            self.nodes_y=float(self.y_nodes.text())
            self.number=float(self.terminal_number.text())
            #draw the base rectangular geomtery and apply a scaling factor to 
            #the sizes if need be
            painter=QPainter()
            painter.setPen(Qt.black)
            x=self.frameGeometry().width()
            y=self.frameGeometry().height()
            painter.drawRect(0,0,self.scalar(self.total_x_)*self.total_x_,
                             self.scalar(self.total_y_)*self.total_y_)
#           
#            #create a dictionary to store the information passed to the upcoming 
#            #widget to be stored in to later draw and analyze the geometry
#            self.boundary_conditions={}
#            for i in range(self.number):
#                self.boundary_conditions[i]=[]
        except:
            error_data=QMessageBox(self)
            error_data.setText('Please Enter either numeric values in all fields')
            error_data.setWindowTitle('Numeric Error')
            error_data.exec()
    def scalar(self,lenght):
        '''Determine the proper scaling to adjust the size to be visible'''
        return 1

        
if __name__=="__main__":
    app=QApplication(sys.argv)
    ex=Monitor()
    sys.exit(app.exec_())        