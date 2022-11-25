#!/usr/bin/env python-sirius

from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys 

  
  
class Window(QMainWindow): 
    def __init__(self): 
        super().__init__() 
        self.setWindowTitle("Python ") 
        self.setGeometry(100, 100, 310, 200) 
        self.UiComponents() 
        self.show()
        
  
    
    def UiComponents(self): 
        button = QPushButton("Gerar Tabela", self) 
        button.setGeometry(200, 150, 100, 30)
        button.setStyleSheet('background-color: red')
        button.setStyleSheet('background-color:#ff0010;')
        button.setStyleSheet('background-color:rgb(200,0,0)')
        button.move(110, 160)
        button.clicked.connect(self.clickme)
        # button.clicked.connect(self.addAction{./proj_eff_inj_excel.py})
        self.textboxyyi = QLineEdit(self)
        self.textboxyyi.move(10, 15)
        self.textboxyyi.resize(40,20)
        self.textboxmi = QLineEdit(self)
        self.textboxmi.move(60, 15) 
        self.textboxmi.resize(40,20)
        self.textboxdi = QLineEdit(self)
        self.textboxdi.move(110, 15) 
        self.textboxdi.resize(40,20)
        self.textboxhhi = QLineEdit(self)
        self.textboxhhi.move(160, 15)
        self.textboxhhi.resize(40,20)
        self.textboxmmi = QLineEdit(self)
        self.textboxmmi.move(210, 15) 
        self.textboxmmi.resize(40,20)
        self.textboxssi = QLineEdit(self)
        self.textboxssi.move(260, 15) 
        self.textboxssi.resize(40,20)
        self.textboxyyf = QLineEdit(self)
        self.textboxyyf.move(10, 95)
        self.textboxyyf.resize(40,20)
        self.textboxmf = QLineEdit(self)
        self.textboxmf.move(60, 95) 
        self.textboxmf.resize(40,20)
        self.textboxdf = QLineEdit(self)
        self.textboxdf.move(110, 95) 
        self.textboxdf.resize(40,20)
        self.textboxhhf = QLineEdit(self)
        self.textboxhhf.move(160, 95)
        self.textboxhhf.resize(40,20)
        self.textboxmmf = QLineEdit(self)
        self.textboxmmf.move(210, 95) 
        self.textboxmmf.resize(40,20)
        self.textboxssf = QLineEdit(self)
        self.textboxssf.move(260, 95) 
        self.textboxssf.resize(40,20)
        self.layouti = QLabel(self)
        self.layouti.move (15, 5)
        self.layouti.resize (260, 100)
        self.layouti.setText('Data/hora inicial - yyyy:mm:dd:hh:mm:ss')
        self.layout = QLabel(self)
        self.layout.move (15, 80)
        self.layout.resize (260, 100)
        self.layout.setText('Data/hora final - yyyy:mm:dd:hh:mm:ss')


    def clickme(self): 
        print("pressed")
        
App = QApplication(sys.argv) 
window = Window() 
sys.exit(App.exec()) 