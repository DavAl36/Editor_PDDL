import sys, os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PyQt5.QtSvg import *
from PyQt5.QtWebEngineWidgets import *

from LabeledSlider import *
from file_checker import *
from SVG_builder import *
from utils import *

from driver.FDmain import *
import argparse

from os import system

var = 0
f = ""
cs = False
wwo = False

class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)

        self._completer = None

    def setCompleter(self, c):
        if self._completer is not None:
            self._completer.activated.disconnect()

        self._completer = c

        c.setWidget(self)
        c.setCompletionMode(QCompleter.PopupCompletion)
        c.setCaseSensitivity(Qt.CaseInsensitive)
        c.activated.connect(self.insertCompletion)

    def completer(self):
        return self._completer

    def insertCompletion(self, completion):
        if self._completer.widget() is not self:
            return

        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        if (extra == 0):
            return
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)

        return tc.selectedText()

    def focusInEvent(self, e):
        if self._completer is not None:
            self._completer.setWidget(self)

        super(TextEdit, self).focusInEvent(e)

    def keyPressEvent(self, e):
        if self._completer is not None and self._completer.popup().isVisible():
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                e.ignore()
                return

        isShortcut = ((e.modifiers() & Qt.ControlModifier) != 0 and e.key() == Qt.Key_Tab)
        if self._completer is None or not isShortcut:
            super(TextEdit, self).keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)
        if self._completer is None or (ctrlOrShift and len(e.text()) == 0):
            return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="
        hasModifier = (e.modifiers() != Qt.NoModifier) and not ctrlOrShift
        completionPrefix = self.textUnderCursor()

        if (hasModifier or len(e.text()) == 0 or len(completionPrefix) < 3 or e.text()[-1] in eow):
            self._completer.popup().hide()
            return

        if completionPrefix != self._completer.completionPrefix():
            self._completer.setCompletionPrefix(completionPrefix)
            self._completer.popup().setCurrentIndex(
                    self._completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
        self._completer.complete(cr)



#---------------------------------------------------
#                   Find Dialog
#---------------------------------------------------
class Findus(QDialog):
    def __init__(self,parent = None):
        QDialog.__init__(self, parent)
         
        self.initUI()
 
    def initUI(self):
 
        self.lb1 = QLabel("Search for: ",self)
        self.lb1.setStyleSheet("font-size: 15px; ")
        self.lb1.move(10,10)
 
        self.te = QTextEdit(self)
        self.te.move(10,40)
        self.te.resize(250,25)

        self.findForward = QPushButton("\u2b06",self)
        self.findForward.move(280, 40)
        self.findForward.resize(40, 30)

        self.findBackward = QPushButton("\u2b07",self)
        self.findBackward.move(310, 40)
        self.findBackward.resize(40, 30)
 
        self.lb2 = QLabel("Replace all by: ",self)
        self.lb2.setStyleSheet("font-size: 15px; ")
        self.lb2.move(10,80)
 
        self.rp = QTextEdit(self)
        self.rp.move(10,110)
        self.rp.resize(250,25)
 
        self.rpb = QPushButton("Replace",self)
        self.rpb.move(270,110)

        self.setGeometry(300,300,360,180)



#---------------------------------------------------
#                   Main Window
#---------------------------------------------------
class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")

        self.flag_error = 0
        self.print_checker = 0
        self.flag_svg = 0

        file_completer_static = open("resources/static_list.txt", "r")
        static_string = ""
        for line in file_completer_static:
            static_string += line
        self.array_tendina = static_string.split("\n")
        file_completer_static.close()
        self.stringa_tendina = ""

        screenShape = QDesktopWidget().screenGeometry()
        width = screenShape.width()
        height = screenShape.height()
     
        MainWindow.resize(width, height)
        MainWindow.setMaximumSize(QtCore.QSize(width, height))
        MainWindow.setStyleSheet("d")
        
        initial_width = 1120
        initial_height = 925

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 671/initial_height*height))
        self.tabWidget.setFocusPolicy(QtCore.Qt.TabFocus)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setObjectName("tabWidget")

        # domain.pddl
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tab.setAutoFillBackground(True)
        self.textEdit_initDomain = TextEdit(self.tab)

        self.completer_initDomain = QCompleter()
        model = QStringListModel()
        self.completer_initDomain.setModel(model)
        model.setStringList(self.array_tendina)
        self.textEdit_initDomain.setCompleter(self.completer_initDomain)


        self.textEdit_initDomain.setGeometry(QtCore.QRect( 0, 0, 711/initial_width*width, 641/initial_height*height))
        self.textEdit_initDomain.setObjectName("textEdit_initDomain")
        self.textEdit_initDomain.setToolTip('This is a tab for domain file.')
        self.tabWidget.addTab(self.tab, "")

        # problem.pddl
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tab_2.setAutoFillBackground(True)
        self.textEdit_initProblem = TextEdit(self.tab_2)

        self.completer_initProblem = QCompleter()
        model = QStringListModel()
        self.completer_initProblem.setModel(model)
        model.setStringList(self.array_tendina)
        self.textEdit_initProblem.setCompleter(self.completer_initProblem)

        self.textEdit_initProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
        self.textEdit_initProblem.setObjectName("textEdit_initProblem")
        self.textEdit_initProblem.setToolTip('This is a tab for problem file.')
        self.tabWidget.addTab(self.tab_2, "")

        # New Empty tab
        self.tab_NewEmpty = QtWidgets.QWidget()
        self.tab_NewEmpty.setAutoFillBackground(True)
        self.textEdit_NewEmpty = TextEdit(self.tab_NewEmpty)

        self.completer_NewEmpty = QCompleter()
        model = QStringListModel()
        self.completer_NewEmpty.setModel(model)
        model.setStringList(self.array_tendina)
        self.textEdit_NewEmpty.setCompleter(self.completer_NewEmpty)

        self.textEdit_NewEmpty.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))

        # New Domain File
        self.tab_NewStructuredDomain = QtWidgets.QWidget()
        self.tab_NewStructuredDomain.setAutoFillBackground(True)
        self.textEdit_NewStructuredDomain = TextEdit(self.tab_NewStructuredDomain)

        self.completer_NewStructuredDomain = QCompleter()
        model = QStringListModel()
        self.completer_NewStructuredDomain.setModel(model)
        model.setStringList(self.array_tendina)
        self.textEdit_NewStructuredDomain.setCompleter(self.completer_NewStructuredDomain)

        self.textEdit_NewStructuredDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))

        # New Problm File
        self.tab_NewStructuredProblem = QtWidgets.QWidget()
        self.tab_NewStructuredProblem.setAutoFillBackground(True)
        self.textEdit_NewStructuredProblem = TextEdit(self.tab_NewStructuredProblem)

        self.completer_NewStructuredProblem = QCompleter()
        model = QStringListModel()
        self.completer_NewStructuredProblem.setModel(model)
        model.setStringList(self.array_tendina)
        self.textEdit_NewStructuredProblem.setCompleter(self.completer_NewStructuredProblem)

        self.textEdit_NewStructuredProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))

        # domain file loaded
        self.tab_LoadDomain = QtWidgets.QWidget()
        self.tab_LoadDomain.setAutoFillBackground(True)
        self.textEdit_LoadDomain = TextEdit(self.tab_LoadDomain)

        self.completer_LoadDomain = QCompleter()
        model = QStringListModel()
        self.completer_LoadDomain.setModel(model)
        model.setStringList(self.array_tendina)
        self.textEdit_LoadDomain.setCompleter(self.completer_LoadDomain)

        self.textEdit_LoadDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))

        # problem file loaded
        self.tab_LoadProblem = QtWidgets.QWidget()
        self.tab_LoadProblem.setAutoFillBackground(True)
        self.textEdit_LoadProblem = TextEdit(self.tab_LoadProblem)

        self.completer_LoadProblem = QCompleter()
        model = QStringListModel()
        self.completer_LoadProblem.setModel(model)
        model.setStringList(self.array_tendina)
        self.textEdit_LoadProblem.setCompleter(self.completer_LoadProblem)

        self.textEdit_LoadProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))

        # domain of example file
        self.tab_ExampleDomain = QtWidgets.QWidget()
        self.tab_ExampleDomain.setAutoFillBackground(True)
        self.textEdit_ExampleDomain = QtWidgets.QTextEdit(self.tab_ExampleDomain)
        self.textEdit_ExampleDomain.setReadOnly(True)
        self.textEdit_ExampleDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))

        # problem of example file
        self.tab_ExampleProblem = QtWidgets.QWidget()
        self.tab_ExampleProblem.setAutoFillBackground(True)
        self.textEdit_ExampleProblem = QtWidgets.QTextEdit(self.tab_ExampleProblem)
        self.textEdit_ExampleProblem.setReadOnly(True)
        self.textEdit_ExampleProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))

        # Domain File selected
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(730/initial_width*width, 680/initial_height*height, 171/initial_width*width, 22/initial_height*height))
        self.comboBox.setAcceptDrops(False)
        self.comboBox.setEditable(False)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setCurrentText("")
        self.comboBox.setItemText(0, "Domain File Selected ----")
        self.comboBox.setItemText(1, "initDomain.pddl")
        self.comboBox.setItemText(2, "initProblem.pddl")
        self.comboBox.setItemText(3, "")
        self.comboBox.setItemText(4, "")
        self.comboBox.setItemText(5, "")
        self.comboBox.setItemText(6, "")
        self.comboBox.setItemText(7, "")
        self.comboBox.setItemText(8, "")
        self.comboBox.setItemText(9, "")

        # Problem File selected
        self.comboBox_2 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(940/initial_width*width, 680/initial_height*height, 171/initial_width*width, 22/initial_height*height))
        self.comboBox_2.setAcceptDrops(False)
        self.comboBox_2.setEditable(False)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setCurrentText("")
        self.comboBox_2.setItemText(0, "Problem File Selected ---")
        self.comboBox_2.setItemText(1, "initDomain.pddl")
        self.comboBox_2.setItemText(2, "initProblem.pddl")
        self.comboBox_2.setItemText(3, "")
        self.comboBox_2.setItemText(4, "")
        self.comboBox_2.setItemText(5, "")
        self.comboBox_2.setItemText(6, "")
        self.comboBox_2.setItemText(7, "")
        self.comboBox_2.setItemText(8, "")
        self.comboBox_2.setItemText(9, "")

        # Algorithm Search selected
        self.comboBox_3 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_3.setGeometry(QtCore.QRect(730/initial_width*width, 770/initial_height*height, 381/initial_width*width, 22/initial_height*height))
        self.comboBox_3.setAcceptDrops(False)
        self.comboBox_3.setEditable(False)
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.setCurrentText("")
        self.comboBox_3.setItemText(0, "Algorithm Search Selected ---------------------------------------")
        self.comboBox_3.setItemText(1, "A*")
        self.comboBox_3.setItemText(2, "Eager Greedy search")
        self.comboBox_3.setItemText(3, "Eager weighted A* search")
        self.comboBox_3.setItemText(4, "Lazy enforced hill-climbing")
        self.comboBox_3.setItemText(5, "Lazy best-first search")
        self.comboBox_3.setItemText(6, "Lazy Greedy search")
        self.comboBox_3.setItemText(7, "Weighted A* search lazy")

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(0, 680/initial_height*height, 711/initial_width*width, 111/initial_height*height))
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 688/initial_width*width, 109/initial_height*height))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.textBrowser = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
        self.textBrowser.setPlainText("This TextEdit provides autocompletions for words that have more than 3 characters.")
        self.textBrowser.setGeometry(QtCore.QRect(0, 0, 691/initial_width*width, 111/initial_height*height))
        self.textBrowser.setObjectName("textBrowser")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.scrollArea_3 = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea_3.setGeometry(QtCore.QRect(730/initial_width*width, 30/initial_height*height, 381/initial_width*width, 641/initial_height*height))
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName("scrollArea_3")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 379/initial_width*width, 639/initial_height*height))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")

        # area di testo a destra per plan in search space
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents_3)
        self.textBrowser_2.setGeometry(QtCore.QRect(0, 0, 381/initial_width*width, 641/initial_height*height))
        self.textBrowser_2.setObjectName("textBrowser_2")
        font_textBrowser_2 = QtGui.QFont()
        font_textBrowser_2.setFamily("Arial")
        font_textBrowser_2.setItalic(True)
        font_textBrowser_2.setPointSize(15)
        self.textBrowser_2.setFont(font_textBrowser_2)
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(830/initial_width*width, 10/initial_height*height, 241/initial_width*width, 21/initial_height*height))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setScaledContents(False)
        self.label.setObjectName("label")
        self.label.setText("PLAN IN SEARCH SPACE")

        fontPlay = QtGui.QFont()
        fontPlay.setFamily("Arial")
        fontPlay.setPointSize(30)
        fontPlay.setBold(True)
        fontPlay.setWeight(75)

        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton.setGeometry(QtCore.QRect(800/initial_width*width, 710/initial_height*height,  51/initial_width*width, 51/initial_height*height))
        self.toolButton.setCheckable(False)
        self.toolButton.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolButton.setObjectName("toolButton")
        self.toolButton.setText("\u25b6")
        self.toolButton.setFont(fontPlay)

        self.radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton.setGeometry(QtCore.QRect(920/initial_width*width, 720/initial_height*height, 131/initial_width*width, 31/initial_height*height))
        self.radioButton.setObjectName("radioButton")
        self.radioButton.setText("SVG Animation")
        self.radioButton.setCheckable(False)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0,1117/initial_width*width, 26/initial_height*height))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFile.setTitle("File")
        self.menuNew = QtWidgets.QMenu(self.menuFile)
        self.menuNew.setObjectName("menuNew")
        self.menuNew.setTitle("New")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("Edit")
        self.menuEdit.setTitle("Edit")


        self.menuExamples = QtWidgets.QMenu(self.menubar)
        self.menuExamples.setObjectName("menuExamples")
        self.menuExamples.setTitle("Examples")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu.setTitle("?")
        self.menuColors_GUI = QtWidgets.QMenu(self.menu)
        self.menuColors_GUI.setObjectName("menuColors_GUI")
        self.menuColors_GUI.setTitle("Colors GUI")

        MainWindow.setMenuBar(self.menubar)

        self.status = self.statusBar()
        self.status.show()

        self.newAction = QtWidgets.QAction(MainWindow)
        self.newAction.setObjectName("newAction")
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.setStatusTip("Create a new empty document.")
        self.newAction.setText("New Empty")

        self.actionDomain_file = QtWidgets.QAction(MainWindow)
        self.actionDomain_file.setObjectName("actionDomain_file")
        self.actionDomain_file.setStatusTip("Create a new document for domain.")
        self.actionDomain_file.setText("Domain File")

        self.actionProblem_file = QtWidgets.QAction(MainWindow)
        self.actionProblem_file.setObjectName("actionProblem_file")
        self.actionProblem_file.setStatusTip("Create a new document for problem.")
        self.actionProblem_file.setText("Problem File")
        
        self.loadFiledomain = QtWidgets.QAction("&Load Domain File", self)
        self.loadFiledomain.setShortcut("Ctrl+D")
        self.loadFiledomain.setStatusTip("Load existing document for domain.")

        self.loadFileproblem = QtWidgets.QAction("&Load Problem File", self)
        self.loadFileproblem.setShortcut("Ctrl+P")
        self.loadFileproblem.setStatusTip("Load existing document for problem.")

        self.saveFile = QtWidgets.QAction("&Save File", self)
        self.saveFile.setShortcut("Ctrl+S")
        self.saveFile.setStatusTip("Save current document")

        self.saveFileAll = QtWidgets.QAction("&Save File All", self)
        self.saveFileAll.setStatusTip("Save all documents, either domain and problem one.")

        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionClose.setStatusTip('Close the editor')
        self.actionClose.setText("Close")

        self.screenSmallerAction = QtWidgets.QAction("Screen Smaller",self)
        self.screenSmallerAction.setStatusTip("Make screen smaller")
        self.screenSmallerAction.setShortcut("Ctrl+M")

        self.screenLargerAction = QtWidgets.QAction("Screen Larger",self)
        self.screenLargerAction.setStatusTip("Make screen larger")
        self.screenLargerAction.setShortcut("Shift+Ctrl+M")

        self.findAction = QtWidgets.QAction("Find",self)
        self.findAction.setStatusTip("Find words in your document")
        self.findAction.setShortcut("Ctrl+F")

        self.alignLeft = QtWidgets.QAction("Align left",self)
        self.alignLeft.setStatusTip("alignLeft")
 
        self.alignCenter = QtWidgets.QAction("Align center",self)
        self.alignCenter.setStatusTip("alignCenter")
 
        self.alignRight = QtWidgets.QAction("Align right",self)
        self.alignRight.setStatusTip("alignRight")
 
        self.indentAction = QtWidgets.QAction("Indent Area",self)
        self.indentAction.setStatusTip("indentAction")
 
        self.dedentAction = QtWidgets.QAction("Dedent Area",self)
        self.dedentAction.setStatusTip("dedentAction")

        self.menuExample_Robocup = QtWidgets.QAction("&Robot-cup", self)
        self.menuExample_Robocup.setStatusTip('Example Robocup')

        self.menuExample_Hospital = QtWidgets.QAction("&Hospital", self)
        self.menuExample_Hospital.setStatusTip('Example Hospital')

        self.menuExample_Envelope = QtWidgets.QAction("&Envelope", self)
        self.menuExample_Envelope.setStatusTip('Example Envelope')

        self.menuExample_Washcar = QtWidgets.QAction("&Wash car", self)
        self.menuExample_Washcar.setStatusTip('Example Washcar')

        self.menuExample_Over = QtWidgets.QAction("&Over", self)
        self.menuExample_Over.setStatusTip('Example Over')

        self.menuExample_BreakGlass = QtWidgets.QAction("&Break glass", self)
        self.menuExample_BreakGlass.setStatusTip('Example BreakGlass')

        self.menuExample_MoveHouse = QtWidgets.QAction("&Move house", self)
        self.menuExample_MoveHouse.setStatusTip('ExampleMoveHouse')

        self.actionHelp = QtWidgets.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionHelp.setStatusTip('This is a guide to use this editor')
        self.actionHelp.setText("Help")

        self.actionBackground = QtWidgets.QAction(MainWindow)
        self.actionBackground.setObjectName("actionBackground")
        self.actionBackground.setStatusTip('If you want to custom the background color of the windows')
        self.actionBackground.setText("Background")

        self.actionText = QtWidgets.QAction(MainWindow)
        self.actionText.setObjectName("actionText")
        self.actionText.setStatusTip('If you want to custom the color of the text in the windows')
        self.actionText.setText("Text")

        self.actionSet_of_font = QtWidgets.QAction(MainWindow)
        self.actionSet_of_font.setObjectName("actionSet_of_font")
        self.actionSet_of_font.setStatusTip('If you want to custom the font of the text in the windows')
        self.actionSet_of_font.setText("Set font")

        self.actionInfo = QtWidgets.QAction(MainWindow)
        self.actionInfo.setObjectName("actionInfo")
        self.actionInfo.setStatusTip('For information')
        self.actionInfo.setText("Info")

        self.aboutQtAct = QtWidgets.QAction("About &Qt", triggered=QApplication.instance().aboutQt)

        self.menuFile.addAction(self.menuNew.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.loadFiledomain)
        self.menuFile.addAction(self.loadFileproblem)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.saveFile)
        self.menuFile.addAction(self.saveFileAll)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuNew.addAction(self.newAction)
        self.menuNew.addSeparator()
        self.menuNew.addAction(self.actionDomain_file)
        self.menuNew.addAction(self.actionProblem_file)
        
        self.menuEdit.addAction(self.screenSmallerAction)
        self.menuEdit.addAction(self.screenLargerAction)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.findAction)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.alignLeft)
        self.menuEdit.addAction(self.alignCenter)
        self.menuEdit.addAction(self.alignRight)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.indentAction)
        self.menuEdit.addAction(self.dedentAction)

        self.menuExamples.addAction(self.menuExample_Robocup)
        self.menuExamples.addAction(self.menuExample_Hospital)
        self.menuExamples.addAction(self.menuExample_Envelope)
        self.menuExamples.addAction(self.menuExample_Washcar)
        self.menuExamples.addAction(self.menuExample_Over)
        self.menuExamples.addAction(self.menuExample_BreakGlass)
        self.menuExamples.addAction(self.menuExample_MoveHouse)

        self.menu.addAction(self.actionHelp)
        self.menu.addAction(self.menuColors_GUI.menuAction())
        self.menu.addAction(self.actionSet_of_font)
        self.menu.addAction(self.actionInfo)
        self.menu.addAction(self.aboutQtAct)
        self.menuColors_GUI.addAction(self.actionBackground)
        self.menuColors_GUI.addAction(self.actionText)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuExamples.menuAction())
        self.menubar.addAction(self.menu.menuAction())



        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

##################################################################################################################
        self.list_name_domain = []
        self.list_name_problem = []

    def close_Tabs(self, i):
        self.tabWidget.removeTab(i)

#---------------------------------------------------
#                   Update Window
#---------------------------------------------------
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("P&R")

        print(self.textEdit_initDomain.toPlainText())

# FILE -------------------------------------------------------
        def NewEmpty():
            if (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewEmpty))):
                self.tabWidget.setCurrentWidget(self.tab_NewEmpty)
                file_save()
            self.tabWidget.addTab(self.tab_NewEmpty, "New Empty tab")
            self.tabWidget.setCurrentWidget(self.tab_NewEmpty)
            QtWidgets.QTextEdit.setText(self.textEdit_NewEmpty, "")
            tab_name_NewEmpty = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewEmpty))
            self.comboBox.setItemText(3, tab_name_NewEmpty)
            self.comboBox_2.setItemText(3, tab_name_NewEmpty)

        self.newAction.triggered.connect(NewEmpty)


        # New --> (Structured) Domain File
        def structured_domainfile():
            if (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredDomain))):
                self.tabWidget.setCurrentWidget(self.tab_NewStructuredDomain)
                file_save()
            self.tabWidget.addTab(self.tab_NewStructuredDomain, "New Domain File")
            self.tabWidget.setCurrentWidget(self.tab_NewStructuredDomain)
            QtWidgets.QTextEdit.setText(self.textEdit_NewStructuredDomain, "(define (domain 'name_domain')"
                                                            "\n\t(:requirements :strips)"
                                                            "\n\t(:predicates ('...') ('...') ... )"

                                                            "\n\n\t(:action 'name_action_1'"
                                                                "\n\t:parameters ('...')"
                                                                "\n\t:precondition (and ('...') ('...') ... )"
                                                                "\n\t:effect (and (not ('...')) ('...') ('...') ... )"
                                                            "\n\t)"

                                                            "\n\n\t(:action 'name_action_2'"
                                                                "\n\t:parameters ('...')"
                                                                "\n\t:precondition (and ('...') ('...') ... )"
                                                                "\n\t:effect (and (not ('...')) ('...') ('...') ... )"
                                                            "\n\t)"

                                                            "\n\n\t..."
                                                            "\n\t..."
                                                            "\n\t..."
                                                         "\n)")
            tab_name_NewStructuredDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredDomain))
            self.comboBox.setItemText(4, tab_name_NewStructuredDomain)
            self.comboBox_2.setItemText(4, tab_name_NewStructuredDomain)

        self.actionDomain_file.triggered.connect(structured_domainfile)


        # New --> (Structured) Problem File
        def structured_problemfile():
            if (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredProblem))):
                self.tabWidget.setCurrentWidget(self.tab_NewStructuredProblem)
                file_save()
            self.tabWidget.addTab(self.tab_NewStructuredProblem, "New Problem File")
            self.tabWidget.setCurrentWidget(self.tab_NewStructuredProblem)
            QtWidgets.QTextEdit.setText(self.textEdit_NewStructuredProblem, "(define (problem 'name_problem')"
                                                            "\n\t(:domain 'name_domain')"
                                                          
                                                            "\n\n\t(:objects '...' '...' ... )"

                                                            "\n\n\t(:init ('...') ('...') ..."
                                                                    "\n\t\t(not('...')) (not('...')) ..."
                                                                "\n\t)"
                                                            "\n\n\t(:goal (and ('...') ('...') ... ))"
                                                         "\n)")
            tab_name_NewStructuredProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredProblem))
            self.comboBox.setItemText(5, tab_name_NewStructuredProblem)
            self.comboBox_2.setItemText(5, tab_name_NewStructuredProblem)

        self.actionProblem_file.triggered.connect(structured_problemfile)


        # Load Domain File
        def file_load_domain():
            try:
                file_load_domain = QtWidgets.QFileDialog.getOpenFileName(None, 'Load Domain File')
                lista_nome_file_domain = file_load_domain[0].split("/")
                if (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadDomain))):
                    self.tabWidget.setCurrentWidget(self.tab_LoadDomain)
                    file_save()
                self.tabWidget.addTab(self.tab_LoadDomain, lista_nome_file_domain[-1])
                self.tabWidget.setCurrentWidget(self.tab_LoadDomain)

                file = open(file_load_domain[0],'r')

                with file:
                    text = file.read()
                    QtWidgets.QTextEdit.setText(self.textEdit_LoadDomain, text.strip("ï»¿"))

                tab_name_LoadDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadDomain))
                self.comboBox.setItemText(6, tab_name_LoadDomain)
                self.comboBox_2.setItemText(6, tab_name_LoadDomain)
            except:
                None

        self.loadFiledomain.triggered.connect(file_load_domain)
        

        # Load Problem File
        def file_load_problem():
            try:
                file_load_problem = QtWidgets.QFileDialog.getOpenFileName(None, 'Load Problem File')
                lista_nome_file_problem = file_load_problem[0].split("/")
                if (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadProblem))):
                    self.tabWidget.setCurrentWidget(self.tab_LoadProblem)
                    file_save()
                self.tabWidget.addTab(self.tab_LoadProblem, lista_nome_file_problem[-1])
                self.tabWidget.setCurrentWidget(self.tab_LoadProblem)
                file = open(file_load_problem[0],'r')

                with file:
                    text = file.read()
                    QtWidgets.QTextEdit.setText(self.textEdit_LoadProblem, text.strip("ï»¿"))

                tab_name_LoadProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadProblem))
                self.comboBox.setItemText(7, tab_name_LoadProblem)
                self.comboBox_2.setItemText(7, tab_name_LoadProblem)
            except:
                None
            
        self.loadFileproblem.triggered.connect(file_load_problem)

###########################################################################################################################
        # Save File
        def file_save():
            try:
                if self.tabWidget.currentIndex() == 0: # DOMAIN
                    f_domain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                    self.list_name_domain.append(f_domain[0])
                    file_domain = open(f_domain[0],"w+")
                    text1 = QtWidgets.QTextEdit.toPlainText(self.textEdit_initDomain)
                    file_domain.write(text1)
                    file_domain.close()

                elif self.tabWidget.currentIndex() == 1: # PROBLEM
                    f_problem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                    self.list_name_problem.append(f_problem[0])
                    file_problem = open(f_problem[0],"w+")
                    text2 = QtWidgets.QTextEdit.toPlainText(self.textEdit_initProblem)
                    file_problem.write(text2)
                    file_problem.close()

                elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                    f_empty = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    file_empty = open(f_empty[0],"w+")
                    text_empty = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewEmpty)
                    file_empty.write(text_empty)
                    file_empty.close()

                elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                    f_NewStructuredDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                    file_NewStructuredDomain = open(f_NewStructuredDomain[0],"w+")
                    text_NewStructuredDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewStructuredDomain)
                    file_NewStructuredDomain.write(text_NewStructuredDomain)
                    file_NewStructuredDomain.close()

                elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                    f_NewStructuredProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                    file_NewStructuredProblem = open(f_NewStructuredProblem[0],"w+")
                    text_NewStructuredProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewStructuredProblem)
                    file_NewStructuredProblem.write(text_NewStructuredProblem)
                    file_NewStructuredProblem.close()

                elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                    f_LoadDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                    file_LoadDomain = open(f_LoadDomain[0],"w+")
                    text_LoadDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_LoadDomain)
                    file_LoadDomain.write(text_LoadDomain)
                    file_LoadDomain.close()

                elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                    f_LoadProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                    file_LoadProblem = open(f_LoadProblem[0],"w+")
                    text_LoadProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_LoadProblem)
                    file_LoadProblem.write(text_LoadProblem)
                    file_LoadProblem.close()

                elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                    f_ExampleDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                    file_ExampleDomain = open(f_ExampleDomain[0],"w+")
                    text_ExampleDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_ExampleDomain)
                    file_ExampleDomain.write(text_ExampleDomain)
                    file_ExampleDomain.close()

                elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                    f_ExampleProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                    file_ExampleProblem = open(f_ExampleProblem[0],"w+")
                    text_ExampleProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_ExampleProblem)
                    file_ExampleProblem.write(text_ExampleProblem)
                    file_ExampleProblem.close()
            except:
                None

            
        self.saveFile.triggered.connect(file_save)


        # Save File All
        def file_save_all():
            try:
                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab)):
                    f_domain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    self.list_name_domain.append(f_domain[0])
                    file_domain = open(f_domain[0],"w+")
                    text1 = QtWidgets.QTextEdit.toPlainText(self.textEdit_initDomain)
                    file_domain.write(text1)
                    file_domain.close()

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_2)):
                    f_problem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    self.list_name_problem.append(f_problem[0])
                    file_problem = open(f_problem[0],"w+")
                    text2 = QtWidgets.QTextEdit.toPlainText(self.textEdit_initProblem)
                    file_problem.write(text2)
                    file_problem.close()

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_NewEmpty)):
                    f_empty = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    file_empty = open(f_empty[0],"w+")
                    text_empty = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewEmpty)
                    file_empty.write(text_empty)
                    file_empty.close()

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_NewStructuredDomain)):
                    f_NewStructuredDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    file_NewStructuredDomain = open(f_NewStructuredDomain[0],"w+")
                    text_NewStructuredDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewStructuredDomain)
                    file_NewStructuredDomain.write(text_NewStructuredDomain)
                    file_NewStructuredDomain.close()

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_NewStructuredProblem)):
                    f_NewStructuredProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    file_NewStructuredProblem = open(f_NewStructuredProblem[0],"w+")
                    text_NewStructuredProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewStructuredProblem)
                    file_NewStructuredProblem.write(text_NewStructuredProblem)
                    file_NewStructuredProblem.close()

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_LoadDomain)):
                    f_LoadDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    file_LoadDomain = open(f_LoadDomain[0],"w+")
                    text_LoadDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_LoadDomain)
                    file_LoadDomain.write(text_LoadDomain)
                    file_LoadDomain.close()

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_LoadProblem)):
                    f_LoadProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    file_LoadProblem = open(f_LoadProblem[0],"w+")
                    text_LoadProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_LoadProblem)
                    file_LoadProblem.write(text_LoadProblem)
                    file_LoadProblem.close()

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_ExampleDomain)):
                    f_ExampleDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    file_ExampleDomain = open(f_ExampleDomain[0],"w+")
                    text_ExampleDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_ExampleDomain)
                    file_ExampleDomain.write(text_ExampleDomain)
                    file_ExampleDomain.close()

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_ExampleProblem)):
                    f_ExampleProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    file_ExampleProblem = open(f_ExampleProblem[0],"w+")
                    text_ExampleProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_ExampleProblem)
                    file_ExampleProblem.write(text_ExampleProblem)
                    file_ExampleProblem.close()
            except:
                None

        self.saveFileAll.triggered.connect(file_save_all)

        # Close window
        def Menu_close():
            close = QtWidgets.QMessageBox.question(self, "QUIT", "Have you already saved?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if close == QtWidgets.QMessageBox.Yes:
                sys.exit()
            else:
                file_save()

        self.actionClose.triggered.connect(Menu_close)
#-------------------------------------------------------------

# EDIT -------------------------------------------------------
        def ScreenSmaller():
            width = 1000
            height = 800
            MainWindow.resize(width, height)

            initial_width = 1117
            initial_height = 820

            self.tabWidget.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 671/initial_height*height))
            self.textEdit_initDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_initProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_NewEmpty.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_NewStructuredDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_NewStructuredProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_LoadDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_LoadProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_ExampleDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_ExampleProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.comboBox.setGeometry(QtCore.QRect(730/initial_width*width, 680/initial_height*height, 171/initial_width*width, 22/initial_height*height))
            self.comboBox_2.setGeometry(QtCore.QRect(940/initial_width*width, 680/initial_height*height, 171/initial_width*width, 22/initial_height*height))
            self.comboBox_3.setGeometry(QtCore.QRect(730/initial_width*width, 770/initial_height*height, 381/initial_width*width, 22/initial_height*height))
            self.scrollArea.setGeometry(QtCore.QRect(0, 680/initial_height*height, 711/initial_width*width, 111/initial_height*height))
            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 688/initial_width*width, 109/initial_height*height))
            self.textBrowser.setGeometry(QtCore.QRect(0, 0, 691/initial_width*width, 111/initial_height*height))
            self.scrollArea_3.setGeometry(QtCore.QRect(730/initial_width*width,  30/initial_height*height, 381/initial_width*width, 641/initial_height*height))
            self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 379/initial_width*width, 639/initial_height*height))
            self.textBrowser_2.setGeometry(QtCore.QRect(0, 0, 381/initial_width*width, 641/initial_height*height))
            self.label.setGeometry(QtCore.QRect(830/initial_width*width, 10/initial_height*height, 241/initial_width*width, 21/initial_height*height))
            self.toolButton.setGeometry(QtCore.QRect(800/initial_width*width, 710/initial_height*height,  51/initial_width*width, 51/initial_height*height))
            self.radioButton.setGeometry(QtCore.QRect(920/initial_width*width, 720/initial_height*height, 131/initial_width*width, 31/initial_height*height))
            self.menubar.setGeometry(QtCore.QRect(0, 0, 1117/initial_width*width, 26/initial_height*height))

            MainWindow.resize(width, height)

        self.screenSmallerAction.triggered.connect(ScreenSmaller)


        def ScreenLarger():
            screenShape = QDesktopWidget().screenGeometry()
            width = screenShape.width()
            height = screenShape.height()

            MainWindow.resize(width, height)
            MainWindow.showMaximized()

            initial_width = 1120
            initial_height = 915
            
            self.tabWidget.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 671/initial_height*height))
            self.textEdit_initDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_initProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_NewEmpty.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_NewStructuredDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_NewStructuredProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_LoadDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_LoadProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_ExampleDomain.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.textEdit_ExampleProblem.setGeometry(QtCore.QRect(0, 0, 711/initial_width*width, 641/initial_height*height))
            self.comboBox.setGeometry(QtCore.QRect(730/initial_width*width, 680/initial_height*height, 171/initial_width*width, 22/initial_height*height))
            self.comboBox_2.setGeometry(QtCore.QRect(940/initial_width*width, 680/initial_height*height, 171/initial_width*width, 22/initial_height*height))
            self.comboBox_3.setGeometry(QtCore.QRect(730/initial_width*width, 770/initial_height*height, 381/initial_width*width, 22/initial_height*height))
            self.scrollArea.setGeometry(QtCore.QRect(0, 680/initial_height*height, 711/initial_width*width, 111/initial_height*height))
            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 688/initial_width*width, 109/initial_height*height))
            self.textBrowser.setGeometry(QtCore.QRect(0, 0, 691/initial_width*width, 111/initial_height*height))
            self.scrollArea_3.setGeometry(QtCore.QRect(730/initial_width*width,  30/initial_height*height, 381/initial_width*width, 641/initial_height*height))
            self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 379/initial_width*width, 639/initial_height*height))
            self.textBrowser_2.setGeometry(QtCore.QRect(0, 0, 381/initial_width*width, 641/initial_height*height))
            self.label.setGeometry(QtCore.QRect(830/initial_width*width, 10/initial_height*height, 241/initial_width*width, 21/initial_height*height))
            self.toolButton.setGeometry(QtCore.QRect(800/initial_width*width, 710/initial_height*height,  51/initial_width*width, 51/initial_height*height))
            self.radioButton.setGeometry(QtCore.QRect(920/initial_width*width, 720/initial_height*height, 131/initial_width*width, 31/initial_height*height))
            self.menubar.setGeometry(QtCore.QRect(0, 0, 1117/initial_width*width, 26/initial_height*height))

        self.screenLargerAction.triggered.connect(ScreenLarger)
        

        def Find():
            global f

            if self.tabWidget.currentIndex() == 0: # DOMAIN
                find = Findus(self)
                find.show()
                
                def handleFindForward():
         
                    f = find.te.toPlainText()
                    self.textEdit_initDomain.find(f)

                def handleFindBackward():

                    f = find.te.toPlainText()
                    self.textEdit_initDomain.find(f, QTextDocument.FindBackward)
         
                def handleReplace():
                    f = find.te.toPlainText()
                    r = find.rp.toPlainText()
         
                    text = self.textEdit_initDomain.toPlainText()
                     
                    newText = text.replace(f,r)
         
                    self.textEdit_initDomain.clear()
                    self.textEdit_initDomain.append(newText)
                 
                find.findForward.clicked.connect(handleFindBackward)
                find.findBackward.clicked.connect(handleFindForward)
                find.rpb.clicked.connect(handleReplace)                

            elif self.tabWidget.currentIndex() == 1: # PROBLEM
                find = Findus(self)
                find.show()
                cursor = self.textEdit_initProblem.textCursor()

                
                def handleFindForward():

                    f = find.te.toPlainText()
                    self.textEdit_initProblem.find(f)

                def handleFindBackward():

                    f = find.te.toPlainText()
                    self.textEdit_initProblem.find(f, QTextDocument.FindBackward)


                def handleReplace():
                    f = find.te.toPlainText()
                    r = find.rp.toPlainText()
         
                    text = self.textEdit_initProblem.toPlainText()
                     
                    newText = text.replace(f,r)
         
                    self.textEdit_initProblem.clear()
                    self.textEdit_initProblem.append(newText)

                find.findForward.clicked.connect(handleFindBackward)
                find.findBackward.clicked.connect(handleFindForward)
                find.rpb.clicked.connect(handleReplace)
            
            elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                find = Findus(self)
                find.show()
                
                def handleFindForward():

                    f = find.te.toPlainText()
                    self.textEdit_NewEmpty.find(f)

                def handleFindBackward():

                    f = find.te.toPlainText()
                    self.textEdit_NewEmpty.find(f, QTextDocument.FindBackward)


                def handleReplace():
                    f = find.te.toPlainText()
                    r = find.rp.toPlainText()

                    text = self.textEdit_NewEmpty.toPlainText()

                    newText = text.replace(f,r)

                    self.textEdit_NewEmpty.clear()
                    self.textEdit_NewEmpty.append(newText)

                find.findForward.clicked.connect(handleFindBackward)
                find.findBackward.clicked.connect(handleFindForward)
                find.rpb.clicked.connect(handleReplace)

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                find = Findus(self)
                find.show()
                
                def handleFindForward():

                    f = find.te.toPlainText()
                    self.textEdit_NewStructuredDomain.find(f)

                def handleFindBackward():

                    f = find.te.toPlainText()
                    self.textEdit_NewStructuredDomain.find(f, QTextDocument.FindBackward)


                def handleReplace():
                    f = find.te.toPlainText()
                    r = find.rp.toPlainText()

                    text = self.textEdit_NewStructuredDomain.toPlainText()

                    newText = text.replace(f,r)

                    self.textEdit_NewStructuredDomain.clear()
                    self.textEdit_NewStructuredDomain.append(newText)

                find.findForward.clicked.connect(handleFindBackward)
                find.findBackward.clicked.connect(handleFindForward)
                find.rpb.clicked.connect(handleReplace)


            elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                find = Findus(self)
                find.show()
                
                def handleFindForward():

                    f = find.te.toPlainText()
                    self.textEdit_NewStructuredProblem.find(f)

                def handleFindBackward():

                    f = find.te.toPlainText()
                    self.textEdit_NewStructuredProblem.find(f, QTextDocument.FindBackward)


                def handleReplace():
                    f = find.te.toPlainText()
                    r = find.rp.toPlainText()

                    text = self.textEdit_NewStructuredProblem.toPlainText()

                    newText = text.replace(f,r)

                    self.textEdit_NewStructuredProblem.clear()
                    self.textEdit_NewStructuredProblem.append(newText)

                find.findForward.clicked.connect(handleFindBackward)
                find.findBackward.clicked.connect(handleFindForward)
                find.rpb.clicked.connect(handleReplace)

            elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                find = Findus(self)
                find.show()
                
                def handleFindForward():

                    f = find.te.toPlainText()
                    self.textEdit_LoadDomain.find(f)

                def handleFindBackward():

                    f = find.te.toPlainText()
                    self.textEdit_LoadDomain.find(f, QTextDocument.FindBackward)


                def handleReplace():
                    f = find.te.toPlainText()
                    r = find.rp.toPlainText()

                    text = self.textEdit_LoadDomain.toPlainText()

                    newText = text.replace(f,r)

                    self.textEdit_LoadDomain.clear()
                    self.textEdit_LoadDomain.append(newText)

                find.findForward.clicked.connect(handleFindBackward)
                find.findBackward.clicked.connect(handleFindForward)
                find.rpb.clicked.connect(handleReplace)

            elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                find = Findus(self)
                find.show()
                
                def handleFindForward():

                    f = find.te.toPlainText()
                    self.textEdit_LoadProblem.find(f)

                def handleFindBackward():

                    f = find.te.toPlainText()
                    self.textEdit_LoadProblem.find(f, QTextDocument.FindBackward)


                def handleReplace():
                    f = find.te.toPlainText()
                    r = find.rp.toPlainText()

                    text = self.textEdit_LoadProblem.toPlainText()

                    newText = text.replace(f,r)

                    self.textEdit_LoadProblem.clear()
                    self.textEdit_LoadProblem.append(newText)

                find.findForward.clicked.connect(handleFindBackward)
                find.findBackward.clicked.connect(handleFindForward)
                find.rpb.clicked.connect(handleReplace)

            elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                find = Findus(self)
                find.show()
                
                def handleFindForward():

                    f = find.te.toPlainText()
                    self.textEdit_ExampleDomain.find(f)

                def handleFindBackward():

                    f = find.te.toPlainText()
                    self.textEdit_ExampleDomain.find(f, QTextDocument.FindBackward)


                def handleReplace():
                    f = find.te.toPlainText()
                    r = find.rp.toPlainText()

                    text = self.textEdit_ExampleDomain.toPlainText()

                    newText = text.replace(f,r)

                    self.textEdit_ExampleDomain.clear()
                    self.textEdit_ExampleDomain.append(newText)

                find.findForward.clicked.connect(handleFindBackward)
                find.findBackward.clicked.connect(handleFindForward)
                find.rpb.clicked.connect(handleReplace)

            elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                find = Findus(self)
                find.show()
                
                def handleFindForward():

                    f = find.te.toPlainText()
                    self.textEdit_ExampleProblem.find(f)

                def handleFindBackward():

                    f = find.te.toPlainText()
                    self.textEdit_ExampleProblem.find(f, QTextDocument.FindBackward)


                def handleReplace():
                    f = find.te.toPlainText()
                    r = find.rp.toPlainText()

                    text = self.textEdit_ExampleProblem.toPlainText()

                    newText = text.replace(f,r)

                    self.textEdit_ExampleProblem.clear()
                    self.textEdit_ExampleProblem.append(newText)

                find.findForward.clicked.connect(handleFindBackward)
                find.findBackward.clicked.connect(handleFindForward)
                find.rpb.clicked.connect(handleReplace)

        self.findAction.triggered.connect(Find)


        def alignLeft():
            if self.tabWidget.currentIndex() == 0: # DOMAIN
                self.textEdit_initDomain.setAlignment(Qt.AlignLeft)
            elif self.tabWidget.currentIndex() == 1: # PROBLEM
                self.textEdit_initProblem.setAlignment(Qt.AlignLeft)
            elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                self.textEdit_NewEmpty.setAlignment(Qt.AlignLeft)
            elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                self.textEdit_NewStructuredDomain.setAlignment(Qt.AlignLeft)
            elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                self.textEdit_NewStructuredProblem.setAlignment(Qt.AlignLeft)
            elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                self.textEdit_LoadDomain.setAlignment(Qt.AlignLeft)
            elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                self.textEdit_LoadProblem.setAlignment(Qt.AlignLeft)
            elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                self.textEdit_ExampleDomain.setAlignment(Qt.AlignLeft)
            elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                self.textEdit_ExampleProblem.setAlignment(Qt.AlignLeft)

        self.alignLeft.triggered.connect(alignLeft)
     
     
        def alignRight():
            if self.tabWidget.currentIndex() == 0: # DOMAIN
                self.textEdit_initDomain.setAlignment(Qt.AlignRight)
            elif self.tabWidget.currentIndex() == 1: # PROBLEM
                self.textEdit_initProblem.setAlignment(Qt.AlignRight)
            elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                self.textEdit_NewEmpty.setAlignment(Qt.AlignRight)
            elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                self.textEdit_NewStructuredDomain.setAlignment(Qt.AlignRight)
            elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                self.textEdit_NewStructuredProblem.setAlignment(Qt.AlignRight)
            elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                self.textEdit_LoadDomain.setAlignment(Qt.AlignRight)
            elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                self.textEdit_LoadProblem.setAlignment(Qt.AlignRight)
            elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                self.textEdit_ExampleDomain.setAlignment(Qt.AlignRight)
            elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                self.textEdit_ExampleProblem.setAlignment(Qt.AlignRight)

        self.alignRight.triggered.connect(alignRight)

        
        def alignCenter():
            if self.tabWidget.currentIndex() == 0: # DOMAIN
                self.textEdit_initDomain.setAlignment(Qt.AlignCenter)
            elif self.tabWidget.currentIndex() == 1: # PROBLEM
                self.textEdit_initProblem.setAlignment(Qt.AlignCenter)
            elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                self.textEdit_NewEmpty.setAlignment(Qt.AlignCenter)
            elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                self.textEdit_NewStructuredDomain.setAlignment(Qt.AlignCenter)
            elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                self.textEdit_NewStructuredProblem.setAlignment(Qt.AlignCenter)
            elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                self.textEdit_LoadDomain.setAlignment(Qt.AlignCenter)
            elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                self.textEdit_LoadProblem.setAlignment(Qt.AlignCenter)
            elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                self.textEdit_ExampleDomain.setAlignment(Qt.AlignCenter)
            elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                self.textEdit_ExampleProblem.setAlignment(Qt.AlignCenter)

        self.alignCenter.triggered.connect(alignCenter)

     
        def Indent(): 
            tab = "\t"
            if self.tabWidget.currentIndex() == 0: # DOMAIN  
                cursor = self.textEdit_initDomain.textCursor()
         
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
         
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(tab)
                    cursor.movePosition(cursor.Down)
                    end += len(tab)

            elif self.tabWidget.currentIndex() == 1: # PROBLEM
                cursor = self.textEdit_initProblem.textCursor()
         
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
         
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(tab)
                    cursor.movePosition(cursor.Down)
                    end += len(tab)

            elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                cursor = self.textEdit_NewEmpty.textCursor()
         
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
         
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(tab)
                    cursor.movePosition(cursor.Down)
                    end += len(tab)

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                cursor = self.textEdit_NewStructuredDomain.textCursor()
         
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
         
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(tab)
                    cursor.movePosition(cursor.Down)
                    end += len(tab)

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                cursor = self.textEdit_NewStructuredProblem.textCursor()
         
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
         
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(tab)
                    cursor.movePosition(cursor.Down)
                    end += len(tab)

            elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                cursor = self.textEdit_LoadDomain.textCursor()
         
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
         
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(tab)
                    cursor.movePosition(cursor.Down)
                    end += len(tab)

            elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                cursor = self.textEdit_LoadProblem.textCursor()
         
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
         
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(tab)
                    cursor.movePosition(cursor.Down)
                    end += len(tab)

            elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                cursor = self.textEdit_ExampleDomain.textCursor()
         
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
         
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(tab)
                    cursor.movePosition(cursor.Down)
                    end += len(tab)

            elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                cursor = self.textEdit_ExampleProblem.textCursor()
         
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
         
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.insertText(tab)
                    cursor.movePosition(cursor.Down)
                    end += len(tab)
    
        self.indentAction.triggered.connect(Indent)
     
     
        def Dedent():
            tab = "\t"
            if self.tabWidget.currentIndex() == 0: # DOMAIN          
                cursor = self.textEdit_initDomain.textCursor()
     
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
                     
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.deleteChar()
                    cursor.movePosition(cursor.EndOfLine)
                    cursor.movePosition(cursor.Down)
                    end -= len(tab)

            elif self.tabWidget.currentIndex() == 1: # PROBLEM  
                cursor = self.textEdit_initProblem.textCursor()
     
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
                     
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.deleteChar()
                    cursor.movePosition(cursor.EndOfLine)
                    cursor.movePosition(cursor.Down)
                    end -= len(tab)

            elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                cursor = self.textEdit_NewEmpty.textCursor()
     
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
                     
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.deleteChar()
                    cursor.movePosition(cursor.EndOfLine)
                    cursor.movePosition(cursor.Down)
                    end -= len(tab)

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                cursor = self.textEdit_NewStructuredDomain.textCursor()
     
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
                     
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.deleteChar()
                    cursor.movePosition(cursor.EndOfLine)
                    cursor.movePosition(cursor.Down)
                    end -= len(tab)

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                cursor = self.textEdit_NewStructuredProblem.textCursor()
     
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
                     
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.deleteChar()
                    cursor.movePosition(cursor.EndOfLine)
                    cursor.movePosition(cursor.Down)
                    end -= len(tab)

            elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                cursor = self.textEdit_LoadDomain.textCursor()
     
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
                     
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.deleteChar()
                    cursor.movePosition(cursor.EndOfLine)
                    cursor.movePosition(cursor.Down)
                    end -= len(tab)

            elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                cursor = self.textEdit_LoadProblem.textCursor()
     
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
                     
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.deleteChar()
                    cursor.movePosition(cursor.EndOfLine)
                    cursor.movePosition(cursor.Down)
                    end -= len(tab)

            elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                cursor = self.textEdit_ExampleDomain.textCursor()
     
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
                     
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.deleteChar()
                    cursor.movePosition(cursor.EndOfLine)
                    cursor.movePosition(cursor.Down)
                    end -= len(tab)

            elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                cursor = self.textEdit_ExampleProblem.textCursor()
     
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
         
                cursor.setPosition(end)
                cursor.movePosition(cursor.EndOfLine)
                end = cursor.position()
         
                cursor.setPosition(start)
                cursor.movePosition(cursor.StartOfLine)
                start = cursor.position()
         
                while cursor.position() < end:
                    global var
                     
                    cursor.movePosition(cursor.StartOfLine)
                    cursor.deleteChar()
                    cursor.movePosition(cursor.EndOfLine)
                    cursor.movePosition(cursor.Down)
                    end -= len(tab)

        self.dedentAction.triggered.connect(Dedent)
#------------------------------------------------------------

# SYNTAX CHECKER ---------------------------------------------
        
# DOMAIN


        def changed_word_initDomain():

            if ((len(self.textEdit_initDomain.toPlainText()) > 0) and
                (self.textEdit_initDomain.toPlainText()[-1] == " " or
                self.textEdit_initDomain.toPlainText()[-1] == "\n")):

                text = self.textEdit_initDomain.toPlainText()

                text = text.replace('Write here ........ DOMAIN',' ')
                text = text.replace('(',' ')
                text = text.replace(')',' ')
                text = text.replace(':',' ')
                text = text.replace('-',' ')
                dynamic_list_words = text.strip().split()
                dynamic_list_words = set(dynamic_list_words)

                for element in dynamic_list_words:
                    self.stringa_tendina += element + "\n"
                for element in self.array_tendina:
                    self.stringa_tendina += element + "\n"

                dynamic_list_words = set(self.stringa_tendina.split("\n"))
                dynamic_list_words = sorted(dynamic_list_words)

                model = QStringListModel()
                self.completer_initDomain.setModel(model)
                model.setStringList(dynamic_list_words)
                self.textEdit_initDomain.setCompleter(self.completer_initDomain)

        self.textEdit_initDomain.textChanged.connect(changed_word_initDomain)


        def changed_word_initProblem():

            if ((len(self.textEdit_initProblem.toPlainText()) > 0) and
                (self.textEdit_initProblem.toPlainText()[-1] == " " or
                self.textEdit_initProblem.toPlainText()[-1] == "\n")):

                text = self.textEdit_initProblem.toPlainText()

                text = text.replace('Write here ........ PROBLEM',' ')
                text = text.replace('(',' ')
                text = text.replace(')',' ')
                text = text.replace(':',' ')
                text = text.replace('-',' ')
                dynamic_list_words = text.strip().split()
                dynamic_list_words = set(dynamic_list_words)

                for element in dynamic_list_words:
                    self.stringa_tendina += element + "\n"
                for element in self.array_tendina:
                    self.stringa_tendina += element + "\n"

                dynamic_list_words = set(self.stringa_tendina.split("\n"))
                dynamic_list_words = sorted(dynamic_list_words)

                model = QStringListModel()
                self.completer_initProblem.setModel(model)
                model.setStringList(dynamic_list_words)
                self.textEdit_initProblem.setCompleter(self.completer_initProblem)

        self.textEdit_initProblem.textChanged.connect(changed_word_initProblem)


        def changed_word_NewEmpty():

            if ((len(self.textEdit_NewEmpty.toPlainText()) > 0) and
                (self.textEdit_NewEmpty.toPlainText()[-1] == " " or
                self.textEdit_NewEmpty.toPlainText()[-1] == "\n")):

                text = self.textEdit_NewEmpty.toPlainText()

                text = text.replace('(',' ')
                text = text.replace(')',' ')
                text = text.replace(':',' ')
                text = text.replace('-',' ')
                dynamic_list_words = text.strip().split()
                dynamic_list_words = set(dynamic_list_words)

                for element in dynamic_list_words:
                    self.stringa_tendina += element + "\n"
                for element in self.array_tendina:
                    self.stringa_tendina += element + "\n"


                dynamic_list_words = set(self.stringa_tendina.split("\n"))
                dynamic_list_words = sorted(dynamic_list_words)

                model = QStringListModel()
                self.completer_NewEmpty.setModel(model)
                model.setStringList(dynamic_list_words)
                self.textEdit_NewEmpty.setCompleter(self.completer_NewEmpty)

        self.textEdit_NewEmpty.textChanged.connect(changed_word_NewEmpty)


        def changed_word_NewStructuredDomain():

            if ((len(self.textEdit_NewStructuredDomain.toPlainText()) > 0) and
                (self.textEdit_NewStructuredDomain.toPlainText()[-1] == " " or
                self.textEdit_NewStructuredDomain.toPlainText()[-1] == "\n")):

                text = self.textEdit_NewStructuredDomain.toPlainText()

                text = text.replace('(',' ')
                text = text.replace(')',' ')
                text = text.replace(':',' ')
                text = text.replace('-',' ')
                dynamic_list_words = text.strip().split()
                dynamic_list_words = set(dynamic_list_words)

                for element in dynamic_list_words:
                    self.stringa_tendina += element + "\n"
                for element in self.array_tendina:
                    self.stringa_tendina += element + "\n"


                dynamic_list_words = set(self.stringa_tendina.split("\n"))
                dynamic_list_words = sorted(dynamic_list_words)

                model = QStringListModel()
                self.completer_NewStructuredDomain.setModel(model)
                model.setStringList(dynamic_list_words)
                self.textEdit_NewStructuredDomain.setCompleter(self.completer_NewStructuredDomain)

        self.textEdit_NewStructuredDomain.textChanged.connect(changed_word_NewStructuredDomain)


        def changed_word_NewStructuredProblem():

            if ((len(self.textEdit_NewStructuredProblem.toPlainText()) > 0) and
                (self.textEdit_NewStructuredProblem.toPlainText()[-1] == " " or
                self.textEdit_NewStructuredProblem.toPlainText()[-1] == "\n")):

                text = self.textEdit_NewStructuredProblem.toPlainText()

                text = text.replace('(',' ')
                text = text.replace(')',' ')
                text = text.replace(':',' ')
                text = text.replace('-',' ')
                dynamic_list_words = text.strip().split()
                dynamic_list_words = set(dynamic_list_words)

                for element in dynamic_list_words:
                    self.stringa_tendina += element + "\n"
                for element in self.array_tendina:
                    self.stringa_tendina += element + "\n"


                dynamic_list_words = set(self.stringa_tendina.split("\n"))
                dynamic_list_words = sorted(dynamic_list_words)

                model = QStringListModel()
                self.completer_NewStructuredProblem.setModel(model)
                model.setStringList(dynamic_list_words)
                self.textEdit_NewStructuredProblem.setCompleter(self.completer_NewStructuredProblem)

        self.textEdit_NewStructuredProblem.textChanged.connect(changed_word_NewStructuredProblem)


        def changed_word_LoadDomain():

            if ((len(self.textEdit_LoadDomain.toPlainText()) > 0) and
                (self.textEdit_LoadDomain.toPlainText()[-1] == " " or
                self.textEdit_LoadDomain.toPlainText()[-1] == "\n")):

                text = self.textEdit_LoadDomain.toPlainText()

                text = text.replace('(',' ')
                text = text.replace(')',' ')
                text = text.replace(':',' ')
                text = text.replace('-',' ')
                dynamic_list_words = text.strip().split()
                dynamic_list_words = set(dynamic_list_words)

                for element in dynamic_list_words:
                    self.stringa_tendina += element + "\n"
                for element in self.array_tendina:
                    self.stringa_tendina += element + "\n"


                dynamic_list_words = set(self.stringa_tendina.split("\n"))
                dynamic_list_words = sorted(dynamic_list_words)

                model = QStringListModel()
                self.completer_LoadDomain.setModel(model)
                model.setStringList(dynamic_list_words)
                self.textEdit_LoadDomain.setCompleter(self.completer_LoadDomain)

        self.textEdit_LoadDomain.textChanged.connect(changed_word_LoadDomain)


        def changed_word_LoadProblem():

            if ((len(self.textEdit_LoadProblem.toPlainText()) > 0) and
                (self.textEdit_LoadProblem.toPlainText()[-1] == " " or
                self.textEdit_LoadProblem.toPlainText()[-1] == "\n")):

                text = self.textEdit_LoadProblem.toPlainText()

                text = text.replace('(',' ')
                text = text.replace(')',' ')
                text = text.replace(':',' ')
                text = text.replace('-',' ')
                dynamic_list_words = text.strip().split()
                dynamic_list_words = set(dynamic_list_words)

                for element in dynamic_list_words:
                    self.stringa_tendina += element + "\n"
                for element in self.array_tendina:
                    self.stringa_tendina += element + "\n"


                dynamic_list_words = set(self.stringa_tendina.split("\n"))
                dynamic_list_words = sorted(dynamic_list_words)

                model = QStringListModel()
                self.completer_LoadProblem.setModel(model)
                model.setStringList(dynamic_list_words)
                self.textEdit_LoadProblem.setCompleter(self.completer_LoadProblem)

        self.textEdit_LoadProblem.textChanged.connect(changed_word_LoadProblem)
#-------------------------------------------------------------

# EXAMPLES ---------------------------------------------------
        # Load Domain and Problem Files Example
        def file_load_Robocup():
            file_load_domain = "esempi_prof/domain.pddl"
            lista_nome_file_domain = file_load_domain.split("/")
            self.tabWidget.addTab(self.tab_ExampleDomain, lista_nome_file_domain[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleDomain), "domain.pddl")
            file_domain = open(file_load_domain, 'r')
            with file_domain:
                text = file_domain.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleDomain, text)
            tab_name_ExampleDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain))
            self.comboBox.setItemText(8, tab_name_ExampleDomain)
            self.comboBox_2.setItemText(8, tab_name_ExampleDomain)
            
            file_load_problem = "esempi_prof/problem.pddl"
            lista_nome_file_problem = file_load_problem.split("/")
            self.tabWidget.addTab(self.tab_ExampleProblem, lista_nome_file_problem[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleProblem), "problem.pddl")
            file_problem = open(file_load_problem,'r')
            with file_problem:
                text = file_problem.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleProblem, text)
            tab_name_ExampleProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem))
            self.comboBox.setItemText(9, tab_name_ExampleProblem)
            self.comboBox_2.setItemText(9, tab_name_ExampleProblem)

        self.menuExample_Robocup.triggered.connect(file_load_Robocup)


        # Load Domain and Problem Files Example
        def file_load_Hospital():
            file_load_domain = "esempi_prof/domain1.pddl"
            lista_nome_file_domain = file_load_domain.split("/")
            self.tabWidget.addTab(self.tab_ExampleDomain, lista_nome_file_domain[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleDomain), "domain1.pddl")
            file_domain = open(file_load_domain, 'r')
            with file_domain:
                text = file_domain.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleDomain, text)
            tab_name_ExampleDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain))
            self.comboBox.setItemText(8, tab_name_ExampleDomain)
            self.comboBox_2.setItemText(8, tab_name_ExampleDomain)
            
            file_load_problem = "esempi_prof/problem1.pddl"
            lista_nome_file_problem = file_load_problem.split("/")
            self.tabWidget.addTab(self.tab_ExampleProblem, lista_nome_file_problem[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleProblem), "problem1.pddl")
            file_problem = open(file_load_problem,'r')
            with file_problem:
                text = file_problem.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleProblem, text)
            tab_name_ExampleProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem))
            self.comboBox.setItemText(9, tab_name_ExampleProblem)
            self.comboBox_2.setItemText(9, tab_name_ExampleProblem)

        self.menuExample_Hospital.triggered.connect(file_load_Hospital)


        # Load Domain and Problem Files Example
        def file_load_Envelope():
            file_load_domain = "esempi_prof/domain2.pddl"
            lista_nome_file_domain = file_load_domain.split("/")
            self.tabWidget.addTab(self.tab_ExampleDomain, lista_nome_file_domain[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleDomain), "domain2.pddl")
            file_domain = open(file_load_domain, 'r')
            with file_domain:
                text = file_domain.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleDomain, text)
            tab_name_ExampleDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain))
            self.comboBox.setItemText(8, tab_name_ExampleDomain)
            self.comboBox_2.setItemText(8, tab_name_ExampleDomain)
            
            file_load_problem = "esempi_prof/problem2.pddl"
            lista_nome_file_problem = file_load_problem.split("/")
            self.tabWidget.addTab(self.tab_ExampleProblem, lista_nome_file_problem[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleProblem), "problem2.pddl")
            file_problem = open(file_load_problem,'r')
            with file_problem:
                text = file_problem.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleProblem, text)
            tab_name_ExampleProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem))
            self.comboBox.setItemText(9, tab_name_ExampleProblem)
            self.comboBox_2.setItemText(9, tab_name_ExampleProblem)

        self.menuExample_Envelope.triggered.connect(file_load_Envelope)


        # Load Domain and Problem Files Example
        def file_load_Washcar():
            file_load_domain = "esempi_prof/domain3.pddl"
            lista_nome_file_domain = file_load_domain.split("/")
            self.tabWidget.addTab(self.tab_ExampleDomain, lista_nome_file_domain[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleDomain), "domain3.pddl")
            file_domain = open(file_load_domain, 'r')
            with file_domain:
                text = file_domain.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleDomain, text)
            tab_name_ExampleDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain))
            self.comboBox.setItemText(8, tab_name_ExampleDomain)
            self.comboBox_2.setItemText(8, tab_name_ExampleDomain)
            
            file_load_problem = "esempi_prof/problem3.pddl"
            lista_nome_file_problem = file_load_problem.split("/")
            self.tabWidget.addTab(self.tab_ExampleProblem, lista_nome_file_problem[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleProblem), "problem3.pddl")
            file_problem = open(file_load_problem,'r')
            with file_problem:
                text = file_problem.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleProblem, text)
            tab_name_ExampleProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem))
            self.comboBox.setItemText(9, tab_name_ExampleProblem)
            self.comboBox_2.setItemText(9, tab_name_ExampleProblem)

        self.menuExample_Washcar.triggered.connect(file_load_Washcar)


        # Load Domain and Problem Files Example
        def file_load_Over():
            file_load_domain = "esempi_prof/domain4.pddl"
            lista_nome_file_domain = file_load_domain.split("/")
            self.tabWidget.addTab(self.tab_ExampleDomain, lista_nome_file_domain[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleDomain), "domain4.pddl")
            file_domain = open(file_load_domain, 'r')
            with file_domain:
                text = file_domain.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleDomain, text)
            tab_name_ExampleDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain))
            self.comboBox.setItemText(8, tab_name_ExampleDomain)
            self.comboBox_2.setItemText(8, tab_name_ExampleDomain)
            
            file_load_problem = "esempi_prof/problem4.pddl"
            lista_nome_file_problem = file_load_problem.split("/")
            self.tabWidget.addTab(self.tab_ExampleProblem, lista_nome_file_problem[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleProblem), "problem4.pddl")
            file_problem = open(file_load_problem,'r')
            with file_problem:
                text = file_problem.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleProblem, text)
            tab_name_ExampleProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem))
            self.comboBox.setItemText(9, tab_name_ExampleProblem)
            self.comboBox_2.setItemText(9, tab_name_ExampleProblem)

        self.menuExample_Over.triggered.connect(file_load_Over)


        # Load Domain and Problem Files Example
        def file_load_BreakGlass():
            file_load_domain = "esempi_prof/domain5.pddl"
            lista_nome_file_domain = file_load_domain.split("/")
            self.tabWidget.addTab(self.tab_ExampleDomain, lista_nome_file_domain[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleDomain), "domain5.pddl")
            file_domain = open(file_load_domain, 'r')
            with file_domain:
                text = file_domain.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleDomain, text)
            tab_name_ExampleDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain))
            self.comboBox.setItemText(8, tab_name_ExampleDomain)
            self.comboBox_2.setItemText(8, tab_name_ExampleDomain)
            
            file_load_problem = "esempi_prof/problem5.pddl"
            lista_nome_file_problem = file_load_problem.split("/")
            self.tabWidget.addTab(self.tab_ExampleProblem, lista_nome_file_problem[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleProblem), "problem5.pddl")
            file_problem = open(file_load_problem,'r')
            with file_problem:
                text = file_problem.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleProblem, text)
            tab_name_ExampleProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem))
            self.comboBox.setItemText(9, tab_name_ExampleProblem)
            self.comboBox_2.setItemText(9, tab_name_ExampleProblem)

        self.menuExample_BreakGlass.triggered.connect(file_load_BreakGlass)


        # Load Domain and Problem Files Example
        def file_load_MoveHouse():
            file_load_domain = "esempi_prof/domain6.pddl"
            lista_nome_file_domain = file_load_domain.split("/")
            self.tabWidget.addTab(self.tab_ExampleDomain, lista_nome_file_domain[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleDomain), "domain6.pddl")
            file_domain = open(file_load_domain, 'r')
            with file_domain:
                text = file_domain.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleDomain, text)
            tab_name_ExampleDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain))
            self.comboBox.setItemText(8, tab_name_ExampleDomain)
            self.comboBox_2.setItemText(8, tab_name_ExampleDomain)
            
            file_load_problem = "esempi_prof/problem6.pddl"
            lista_nome_file_problem = file_load_problem.split("/")
            self.tabWidget.addTab(self.tab_ExampleProblem, lista_nome_file_problem[-1])
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ExampleProblem), "problem6.pddl")
            file_problem = open(file_load_problem,'r')
            with file_problem:
                text = file_problem.read()
                QtWidgets.QTextEdit.setText(self.textEdit_ExampleProblem, text)
            tab_name_ExampleProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem))
            self.comboBox.setItemText(9, tab_name_ExampleProblem)
            self.comboBox_2.setItemText(9, tab_name_ExampleProblem)

        self.menuExample_MoveHouse.triggered.connect(file_load_MoveHouse)
#-------------------------------------------------------------

# ? ----------------------------------------------------------
        # Help
        def Menu_help():
            helpDialog = QtWidgets.QDialog(self)
            helpLabel = QtWidgets.QLabel(helpDialog)
            helpLabel.setText("More info on GitHub: Working Progress")
            helpDialog.setWindowTitle("HELP")
            helpLabel.move(50, 10)
            helpDialog.resize(300, 150)
            helpDialog.setWindowModality(QtCore.Qt.ApplicationModal)
            helpDialog.exec_()

        self.actionHelp.triggered.connect(Menu_help)
        

        # Colors GUI --> Background
        def ColorsGUI_background_colors():
            color = QtWidgets.QColorDialog.getColor()

            if self.tabWidget.currentIndex() == 0: # DOMAIN
                self.textEdit_initDomain.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser_2.setStyleSheet("QWidget { background-color: %s}" % color.name())

            elif self.tabWidget.currentIndex() == 1: # PROBLEM
                self.textEdit_initProblem.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser_2.setStyleSheet("QWidget { background-color: %s}" % color.name())

            elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                self.textEdit_NewEmpty.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser_2.setStyleSheet("QWidget { background-color: %s}" % color.name())

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                self.textEdit_NewStructuredDomain.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser_2.setStyleSheet("QWidget { background-color: %s}" % color.name())

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                self.textEdit_NewStructuredProblem.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser_2.setStyleSheet("QWidget { background-color: %s}" % color.name())

            elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                self.textEdit_LoadDomain.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser_2.setStyleSheet("QWidget { background-color: %s}" % color.name())

            elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                self.textEdit_LoadProblem.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser_2.setStyleSheet("QWidget { background-color: %s}" % color.name())

            elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                self.textEdit_ExampleDomain.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser_2.setStyleSheet("QWidget { background-color: %s}" % color.name())

            elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                self.textEdit_ExampleProblem.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser.setStyleSheet("QWidget { background-color: %s}" % color.name())
                self.textBrowser_2.setStyleSheet("QWidget { background-color: %s}" % color.name())

        self.actionBackground.triggered.connect(ColorsGUI_background_colors)
        

        # Colors GUI --> Text
        def ColorsGUI_text_colors():
            c = QColorDialog.getColor()

            if self.tabWidget.currentIndex() == 0: # DOMAIN
                self.textEdit_initDomain.setTextColor(c)

            elif self.tabWidget.currentIndex() == 1: # PROBLEM
                self.textEdit_initProblem.setTextColor(c)

            elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                self.textEdit_NewEmpty.setTextColor(c)

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                self.textEdit_NewStructuredDomain.setTextColor(c)

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                self.textEdit_NewStructuredProblem.setTextColor(c)

            elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                self.textEdit_LoadDomain.setTextColor(c)

            elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                self.textEdit_LoadProblem.setTextColor(c)

            elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                self.textEdit_ExampleDomain.setTextColor(c)

            elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                self.textEdit_ExampleProblem.setTextColor(c)

        self.actionText.triggered.connect(ColorsGUI_text_colors)


        # Set of font
        def Set_of_font():
            if self.tabWidget.currentIndex() == 0: # DOMAIN
                new_domain = QtWidgets.QFontDialog.getFont()[0]
                self.textEdit_initDomain.setFont(new_domain)
                self.textBrowser.setFont(new_domain)

            elif self.tabWidget.currentIndex() == 1: # PROBLEM
                new_problem = QtWidgets.QFontDialog.getFont()[0]
                self.textEdit_initProblem.setFont(new_problem)
                self.textBrowser.setFont(new_problem)

            elif self.tabWidget.currentWidget() == self.tab_NewEmpty:
                new_empty = QtWidgets.QFontDialog.getFont()[0]
                self.textEdit_NewEmpty.setFont(new_empty)
                self.textBrowser.setFont(new_empty)

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredDomain:
                new_StructuredDomain = QtWidgets.QFontDialog.getFont()[0]
                self.textEdit_NewStructuredDomain.setFont(new_StructuredDomain)
                self.textBrowser.setFont(new_StructuredDomain)

            elif self.tabWidget.currentWidget() == self.tab_NewStructuredProblem:
                new_StructuredProblem = QtWidgets.QFontDialog.getFont()[0]
                self.textEdit_NewStructuredProblem.setFont(new_StructuredProblem)
                self.textBrowser.setFont(new_StructuredProblem)

            elif self.tabWidget.currentWidget() == self.tab_LoadDomain:
                new_LoadDomain = QtWidgets.QFontDialog.getFont()[0]
                self.textEdit_LoadDomain.setFont(new_LoadDomain)
                self.textBrowser.setFont(new_LoadDomain)

            elif self.tabWidget.currentWidget() == self.tab_LoadProblem:
                new_LoadProblem = QtWidgets.QFontDialog.getFont()[0]
                self.textEdit_LoadProblem.setFont(new_LoadProblem)
                self.textBrowser.setFont(new_LoadProblem)

            elif self.tabWidget.currentWidget() == self.tab_ExampleDomain:
                new_ExampleDomain = QtWidgets.QFontDialog.getFont()[0]
                self.textEdit_ExampleDomain.setFont(new_ExampleDomain)
                self.textBrowser.setFont(new_ExampleDomain)

            elif self.tabWidget.currentWidget() == self.tab_ExampleProblem:
                new_ExampleProblem = QtWidgets.QFontDialog.getFont()[0]
                self.textEdit_ExampleProblem.setFont(new_ExampleProblem)
                self.textBrowser.setFont(new_ExampleProblem)

        self.actionSet_of_font.triggered.connect(Set_of_font)
        

        # Info
        def Menu_info():
            infoDialog = QtWidgets.QDialog(self)
            infoLabel = QtWidgets.QLabel(infoDialog)
            infoLabel.setText("\nWelcome in our PDDL editor !!! \n\nThe authors of this editor are: \nDavide Aloisi, \nLorenzo Saiella, \nLuca Santilli")
            infoDialog.setWindowTitle("INFO")
            infoLabel.move(50, 10)
            infoDialog.resize(300, 150)
            infoDialog.setWindowModality(QtCore.Qt.ApplicationModal)
            infoDialog.exec_()

        self.actionInfo.triggered.connect(Menu_info)
#-------------------------------------------------------------

#-------------------------------------------------------------
        # current line colored domain
        def highlightCurrentLineDomain():
            extraSelections = []
            if not self.textEdit_initDomain.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textEdit_initDomain.textCursor()
                selection.cursor.clearSelection()
                extraSelections.append(selection)
            self.textEdit_initDomain.setExtraSelections(extraSelections)

        self.textEdit_initDomain.cursorPositionChanged.connect(highlightCurrentLineDomain)


        # current line colored problem
        def highlightCurrentLineProblem():
            extraSelections = []
            if not self.textEdit_initProblem.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textEdit_initProblem.textCursor()
                selection.cursor.clearSelection()
                extraSelections.append(selection)
            self.textEdit_initProblem.setExtraSelections(extraSelections)

        self.textEdit_initProblem.cursorPositionChanged.connect(highlightCurrentLineProblem)


        # current line colored new empty
        def highlightCurrentLineNewEmpty():
            extraSelections = []
            if not self.textEdit_NewEmpty.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textEdit_NewEmpty.textCursor()
                selection.cursor.clearSelection()
                extraSelections.append(selection)
            self.textEdit_NewEmpty.setExtraSelections(extraSelections)

        self.textEdit_NewEmpty.cursorPositionChanged.connect(highlightCurrentLineNewEmpty)


        # current line colored new structured domain
        def highlightCurrentLineNewStructuredDomain():
            extraSelections = []
            if not self.textEdit_NewStructuredDomain.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textEdit_NewStructuredDomain.textCursor()
                selection.cursor.clearSelection()
                extraSelections.append(selection)
            self.textEdit_NewStructuredDomain.setExtraSelections(extraSelections)

        self.textEdit_NewStructuredDomain.cursorPositionChanged.connect(highlightCurrentLineNewStructuredDomain)


        # current line colored new structured problem
        def highlightCurrentLineNewStructuredProblem():
            extraSelections = []
            if not self.textEdit_NewStructuredProblem.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textEdit_NewStructuredProblem.textCursor()
                selection.cursor.clearSelection()
                extraSelections.append(selection)
            self.textEdit_NewStructuredProblem.setExtraSelections(extraSelections)

        self.textEdit_NewStructuredProblem.cursorPositionChanged.connect(highlightCurrentLineNewStructuredProblem)


        # current line colored load domain
        def highlightCurrentLineLoadDomain():
            extraSelections = []
            if not self.textEdit_LoadDomain.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textEdit_LoadDomain.textCursor()
                selection.cursor.clearSelection()
                extraSelections.append(selection)
            self.textEdit_LoadDomain.setExtraSelections(extraSelections)

        self.textEdit_LoadDomain.cursorPositionChanged.connect(highlightCurrentLineLoadDomain)


        # current line colored load domain
        def highlightCurrentLineLoadProblem():
            extraSelections = []
            if not self.textEdit_LoadProblem.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textEdit_LoadProblem.textCursor()
                selection.cursor.clearSelection()
                extraSelections.append(selection)
            self.textEdit_LoadProblem.setExtraSelections(extraSelections)

        self.textEdit_LoadProblem.cursorPositionChanged.connect(highlightCurrentLineLoadProblem)


        # current line colored example domain
        def highlightCurrentLineExampleDomain():
            extraSelections = []
            if not self.textEdit_ExampleDomain.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textEdit_ExampleDomain.textCursor()
                selection.cursor.clearSelection()
                extraSelections.append(selection)
            self.textEdit_ExampleDomain.setExtraSelections(extraSelections)

        self.textEdit_ExampleDomain.cursorPositionChanged.connect(highlightCurrentLineExampleDomain)


        # current line colored example problem
        def highlightCurrentLineExampleProblem():
            extraSelections = []
            if not self.textEdit_ExampleProblem.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(Qt.yellow).lighter(160)
                selection.format.setBackground(lineColor)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textEdit_ExampleProblem.textCursor()
                selection.cursor.clearSelection()
                extraSelections.append(selection)
            self.textEdit_ExampleProblem.setExtraSelections(extraSelections)

        self.textEdit_ExampleProblem.cursorPositionChanged.connect(highlightCurrentLineExampleProblem)

#-------------------------------------------------------------


#------ Cursor position on domain file
        def CursorPosition_Domain():
            line = self.textEdit_initDomain.textCursor().blockNumber()
            col = self.textEdit_initDomain.textCursor().columnNumber()
            linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
            self.status.showMessage(linecol)

        self.textEdit_initDomain.cursorPositionChanged.connect(CursorPosition_Domain)

#------ Cursor position on problem file
        def CursorPosition_Problem():
            line = self.textEdit_initProblem.textCursor().blockNumber()
            col = self.textEdit_initProblem.textCursor().columnNumber()
            linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
            self.status.showMessage(linecol)

        self.textEdit_initProblem.cursorPositionChanged.connect(CursorPosition_Problem)

#------ Cursor position on empty file
        def CursorPosition_NewEmpty():
            line = self.textEdit_NewEmpty.textCursor().blockNumber()
            col = self.textEdit_NewEmpty.textCursor().columnNumber()
            linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
            self.status.showMessage(linecol)

        self.textEdit_NewEmpty.cursorPositionChanged.connect(CursorPosition_NewEmpty)


#------ Cursor position on domain file
        def CursorPosition_NewStructuredDomain():
            line = self.textEdit_NewStructuredDomain.textCursor().blockNumber()
            col = self.textEdit_NewStructuredDomain.textCursor().columnNumber()
            linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
            self.status.showMessage(linecol)

        self.textEdit_NewStructuredDomain.cursorPositionChanged.connect(CursorPosition_NewStructuredDomain)

#------ Cursor position on problem file
        def CursorPosition_NewStructuredProblem():
            line = self.textEdit_NewStructuredProblem.textCursor().blockNumber()
            col = self.textEdit_NewStructuredProblem.textCursor().columnNumber()
            linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
            self.status.showMessage(linecol)

        self.textEdit_NewStructuredProblem.cursorPositionChanged.connect(CursorPosition_NewStructuredProblem)

#------ Cursor position on load domain file
        def CursorPosition_LoadDomain():
            line = self.textEdit_LoadDomain.textCursor().blockNumber()
            col = self.textEdit_LoadDomain.textCursor().columnNumber()
            linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
            self.status.showMessage(linecol)

        self.textEdit_LoadDomain.cursorPositionChanged.connect(CursorPosition_LoadDomain)

#------ Cursor position on load problem file
        def CursorPosition_LoadProblem():
            line = self.textEdit_LoadProblem.textCursor().blockNumber()
            col = self.textEdit_LoadProblem.textCursor().columnNumber()
            linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
            self.status.showMessage(linecol)

        self.textEdit_LoadProblem.cursorPositionChanged.connect(CursorPosition_LoadProblem)

#------ Cursor position on example domain file
        def CursorPosition_ExampleDomain():
            line = self.textEdit_ExampleDomain.textCursor().blockNumber()
            col = self.textEdit_ExampleDomain.textCursor().columnNumber()
            linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
            self.status.showMessage(linecol)

        self.textEdit_ExampleDomain.cursorPositionChanged.connect(CursorPosition_ExampleDomain)

#------ Cursor position on example problem file
        def CursorPosition_ExampleProblem():
            line = self.textEdit_ExampleProblem.textCursor().blockNumber()
            col = self.textEdit_ExampleProblem.textCursor().columnNumber()
            linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
            self.status.showMessage(linecol)

        self.textEdit_ExampleProblem.cursorPositionChanged.connect(CursorPosition_ExampleProblem)

#------ Close the current tab


        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.close_Tabs)

#------ Menu for the choice of the domain file
        def Choice_domain_file():
            tab_name = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab))
            self.comboBox.setItemText(1, tab_name)
            if (self.comboBox.currentText() == tab_name):
                self.tabWidget.setCurrentWidget(self.tab)

            tab2_name = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_2))
            self.comboBox.setItemText(2, tab2_name)
            if (self.comboBox.currentText() == tab2_name):
                self.tabWidget.setCurrentWidget(self.tab_2)

            tab_name_NewEmpty = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewEmpty))
            self.comboBox.setItemText(3, tab_name_NewEmpty)
            if (self.comboBox.currentText() == tab_name_NewEmpty):
                self.tabWidget.setCurrentWidget(self.tab_NewEmpty)

            tab_name_NewStructuredDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredDomain))
            self.comboBox.setItemText(4, tab_name_NewStructuredDomain)
            if (self.comboBox.currentText() == tab_name_NewStructuredDomain):
                self.tabWidget.setCurrentWidget(self.tab_NewStructuredDomain)

            tab_name_NewStructuredProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredProblem))
            self.comboBox.setItemText(5, tab_name_NewStructuredProblem)
            if (self.comboBox.currentText() == tab_name_NewStructuredProblem):
                self.tabWidget.setCurrentWidget(self.tab_NewStructuredProblem)

            tab_name_LoadDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadDomain))
            self.comboBox.setItemText(6, tab_name_LoadDomain)
            if (self.comboBox.currentText() == tab_name_LoadDomain):
                self.tabWidget.setCurrentWidget(self.tab_LoadDomain)

            tab_name_LoadProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadProblem))
            self.comboBox.setItemText(7, tab_name_LoadProblem)
            if (self.comboBox.currentText() == tab_name_LoadProblem):
                self.tabWidget.setCurrentWidget(self.tab_LoadProblem)

            tab_name_ExampleDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain))
            self.comboBox.setItemText(8, tab_name_ExampleDomain)
            if (self.comboBox.currentText() == tab_name_ExampleDomain):
                self.tabWidget.setCurrentWidget(self.tab_ExampleDomain)

            tab_name_ExampleProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem))
            self.comboBox.setItemText(9, tab_name_ExampleProblem)
            if (self.comboBox.currentText() == tab_name_ExampleProblem):
                self.tabWidget.setCurrentWidget(self.tab_ExampleProblem)

        self.comboBox.activated.connect(Choice_domain_file)

#------ Menu for the choice of the problem file
        def Choice_problem_file():
            tab_name = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab))
            self.comboBox_2.setItemText(1, tab_name)
            if (self.comboBox_2.currentText() == tab_name):
                self.tabWidget.setCurrentWidget(self.tab)

            tab2_name = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_2))
            self.comboBox_2.setItemText(2, tab2_name)
            if (self.comboBox_2.currentText() == tab2_name):
                self.tabWidget.setCurrentWidget(self.tab_2)

            tab_name_NewEmpty = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewEmpty))
            self.comboBox_2.setItemText(3, tab_name_NewEmpty)
            if (self.comboBox_2.currentText() == tab_name_NewEmpty):
                self.tabWidget.setCurrentWidget(self.tab_NewEmpty)

            tab_name_NewStructuredDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredDomain))
            self.comboBox_2.setItemText(4, tab_name_NewStructuredDomain)
            if (self.comboBox_2.currentText() == tab_name_NewStructuredDomain):
                self.tabWidget.setCurrentWidget(self.tab_NewStructuredDomain)

            tab_name_NewStructuredProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredProblem))
            self.comboBox_2.setItemText(5, tab_name_NewStructuredProblem)
            if (self.comboBox_2.currentText() == tab_name_NewStructuredProblem):
                self.tabWidget.setCurrentWidget(self.tab_NewStructuredProblem)

            tab_name_LoadDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadDomain))
            self.comboBox_2.setItemText(6, tab_name_LoadDomain)
            if (self.comboBox_2.currentText() == tab_name_LoadDomain):
                self.tabWidget.setCurrentWidget(self.tab_LoadDomain)

            tab_name_LoadProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadProblem))
            self.comboBox_2.setItemText(7, tab_name_LoadProblem)
            if (self.comboBox_2.currentText() == tab_name_LoadProblem):
                self.tabWidget.setCurrentWidget(self.tab_LoadProblem)

            tab_name_ExampleDomain = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain))
            self.comboBox_2.setItemText(8, tab_name_ExampleDomain)
            if (self.comboBox_2.currentText() == tab_name_ExampleDomain):
                self.tabWidget.setCurrentWidget(self.tab_ExampleDomain)

            tab_name_ExampleProblem = self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem))
            self.comboBox_2.setItemText(9, tab_name_ExampleProblem)
            if (self.comboBox_2.currentText() == tab_name_ExampleProblem):
                self.tabWidget.setCurrentWidget(self.tab_ExampleProblem)

        self.comboBox_2.activated.connect(Choice_problem_file)

#------ Menu for the choice of the search algorithm on Fast-Downward
        self.algorithmName = ""
        def Choice_algorithms():

            if self.comboBox_3.currentIndex() == 1:
                self.algorithmName = "astar(add())"
            elif self.comboBox_3.currentIndex() == 2:
                self.algorithmName = "eager_greedy([add(), ff()])"
            elif self.comboBox_3.currentIndex() == 3:
                self.algorithmName = "eager_wastar([add()], w=1)"
            elif self.comboBox_3.currentIndex() == 4:
                self.algorithmName = "ehc(blind())"
            elif self.comboBox_3.currentIndex() == 5:
                self.algorithmName = "lazy(single(blind(), pref_only=false))"
            elif self.comboBox_3.currentIndex() == 6:
                self.algorithmName = "lazy_greedy([blind(), ff()])"
            elif self.comboBox_3.currentIndex() == 7:
                self.algorithmName = "lazy_wastar([add(),ff()])"

        self.comboBox_3.activated.connect(Choice_algorithms)

#------ At the beginning this is written on the text editor
        self.textEdit_initDomain.append("Write here ........ DOMAIN")
        self.textEdit_initProblem.append("Write here ........ PROBLEM")

#------ Names of the tabs
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), "initDomain.pddl")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), "initProblem.pddl")

#------ Bottom window for tips
        self.textBrowser.append("Hints & Issues ........")
#------------------------------------------------------------

# BUTTONS ---------------------------------------------------
#------ Press the play button
        def tasto_play():
            
            self.textBrowser.clear()
            self.textBrowser_2.clear()
            self.print_checker = 0

            tab_name_tendina_domain_scelta = self.comboBox.currentText()
            tab_name_tendina_problem_scelta = self.comboBox_2.currentText()

            final_domain = ""
            final_problem = ""

            try:
                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab)) and self.tabWidget.tabText(self.tabWidget.indexOf(self.tab)) == tab_name_tendina_domain_scelta:
                    f_domain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                    self.list_name_domain.append(f_domain[0])
                    file_domain = open(f_domain[0],"w+")
                    text1 = QtWidgets.QTextEdit.toPlainText(self.textEdit_initDomain)
                    file_domain.write(text1)
                    file_domain.close()
                    final_domain = f_domain[0]

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_2)) and self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_2)) == tab_name_tendina_problem_scelta:
                    f_problem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                    self.list_name_problem.append(f_problem[0])
                    file_problem = open(f_problem[0],"w+")
                    text2 = QtWidgets.QTextEdit.toPlainText(self.textEdit_initProblem)
                    file_problem.write(text2)
                    file_problem.close()
                    final_problem = f_problem[0]

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_NewStructuredDomain)) and (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredDomain)) == tab_name_tendina_domain_scelta or self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredDomain)) == tab_name_tendina_problem_scelta):
                    f_NewStructuredDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                    file_NewStructuredDomain = open(f_NewStructuredDomain[0],"w+")
                    text_NewStructuredDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewStructuredDomain)
                    file_NewStructuredDomain.write(text_NewStructuredDomain)
                    file_NewStructuredDomain.close()
                    final_domain = f_NewStructuredDomain[0]

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_NewStructuredProblem)) and (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredProblem)) == tab_name_tendina_domain_scelta or self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewStructuredProblem)) == tab_name_tendina_problem_scelta):
                    f_NewStructuredProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                    file_NewStructuredProblem = open(f_NewStructuredProblem[0],"w+")
                    text_NewStructuredProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewStructuredProblem)
                    file_NewStructuredProblem.write(text_NewStructuredProblem)
                    file_NewStructuredProblem.close()
                    final_problem = f_NewStructuredProblem[0]

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_LoadDomain)) and (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadDomain)) == tab_name_tendina_domain_scelta or self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadDomain)) == tab_name_tendina_problem_scelta):
                    f_LoadDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                    file_LoadDomain = open(f_LoadDomain[0],"w+")
                    text_LoadDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_LoadDomain)
                    file_LoadDomain.write(text_LoadDomain)
                    file_LoadDomain.close()
                    final_domain = f_LoadDomain[0]

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_LoadProblem)) and (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadProblem)) == tab_name_tendina_domain_scelta or self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_LoadProblem)) == tab_name_tendina_problem_scelta):
                    f_LoadProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                    file_LoadProblem = open(f_LoadProblem[0],"w+")
                    text_LoadProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_LoadProblem)
                    file_LoadProblem.write(text_LoadProblem)
                    file_LoadProblem.close()
                    final_problem = f_LoadProblem[0]

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_ExampleDomain)) and (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain)) == tab_name_tendina_domain_scelta or self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleDomain)) == tab_name_tendina_problem_scelta):
                    f_ExampleDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                    file_ExampleDomain = open(f_ExampleDomain[0],"w+")
                    text_ExampleDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_ExampleDomain)
                    file_ExampleDomain.write(text_ExampleDomain)
                    file_ExampleDomain.close()
                    final_domain = f_ExampleDomain[0]

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_ExampleProblem)) and (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem)) == tab_name_tendina_domain_scelta or self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_ExampleProblem)) == tab_name_tendina_problem_scelta):
                    f_ExampleProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                    file_ExampleProblem = open(f_ExampleProblem[0],"w+")
                    text_ExampleProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_ExampleProblem)
                    file_ExampleProblem.write(text_ExampleProblem)
                    file_ExampleProblem.close()
                    final_problem = f_ExampleProblem[0]

                if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_NewEmpty)) and (self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewEmpty)) == tab_name_tendina_domain_scelta or self.tabWidget.tabText(self.tabWidget.indexOf(self.tab_NewEmpty)) == tab_name_tendina_problem_scelta):
                    f_empty = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                    file_empty = open(f_empty[0],"w+")
                    text_empty = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewEmpty)
                    file_empty.write(text_empty)
                    file_empty.close()
                    if (final_domain == ""):
                        final_domain = f_empty[0]
                    else:
                        final_problem = f_empty[0]
            except:
                None

            cursor = self.textBrowser.textCursor()
            cursor.clearSelection()
            self.textBrowser.setTextCursor(cursor)
            try:

                checker(self, final_domain, final_problem)

                if self.flag_error != 1:
                    # fastDownward

                    print("algorithmName", self.algorithmName)
                    args = argparse.Namespace(  alias=None,
                                                build='release',
                                                cleanup=False,
                                                components=['translate', 'search'],
                                                debug=False,
                                                filenames=[final_domain, final_problem],
                                                keep_sas_file=False,
                                                log_level='info',
                                                overall_memory_limit=None,
                                                overall_time_limit=None,
                                                plan_file='sas_plan',
                                                planner_args=[final_domain, final_problem, '--search', self.algorithmName],
                                                portfolio=None,
                                                portfolio_bound=None,
                                                portfolio_single_plan=False,
                                                run_all=False,
                                                sas_file='output.sas',
                                                search=False,
                                                search_input='output.sas',
                                                search_memory_limit=None,
                                                search_options=['--search', self.algorithmName, '--internal-plan-file', 'sas_plan'],
                                                search_time_limit=None,
                                                show_aliases=False,
                                                translate=False,
                                                translate_inputs=[final_domain, final_problem],
                                                translate_memory_limit=None,
                                                translate_options=['--sas-file', 'output.sas'],
                                                translate_time_limit=None,
                                                validate=False,
                                                validate_memory_limit=None,
                                                validate_time_limit=None,
                                                version=False)

                    mainFastDownward(args)

                    filePlan = open("sas_plan",  "r")
                    planString = ""
                    indexLine = 0
                    for line in filePlan:
                        line = line.replace("(", "").replace(")", "")
                        lineSplit = line.split(" ")
                        stringFinal = ""
                        for indexSplit in range(1, len(lineSplit)):
                            stringFinal += lineSplit[indexSplit]
                            if (indexSplit < len(lineSplit) - 1):
                                stringFinal += " "
                        if ";" in line:
                            break
                        indexLine += 1
                        planString += "Action #" + str(indexLine) + ":\n" + "\tName: " + lineSplit[0] + "\n" + "\tObject: " + stringFinal + "\n"
                    filePlan.close()

                    self.textBrowser_2.append(planString)

                    returnMain_SVGs = main_SVGs(self, final_domain, final_problem)
                    plan_SVGs(returnMain_SVGs)
                    self.flag_svg = 1
                    self.radioButton.setCheckable(True)


            except:
                self.textBrowser.append("Select domain, problem and algorithm first.")
                self.textBrowser.repaint()


        self.toolButton.clicked.connect(tasto_play)

#------ Press the SVG animation button
        def SVG_Animation():
            if (self.flag_svg == 0):
                return
            self.radioButton.setChecked(True)
            SVGDialog_1 = QtWidgets.QDialog()
            SVGDialog_1.setWindowTitle("SVG Animation Legend & Solution")
            SVGDialog_1.resize(1200, 800)
            SVGDialog_1.setMaximumSize(QtCore.QSize(1200, 800))
            SVGDialog_1.setMinimumSize(QtCore.QSize(1200, 800))
            SVGDialog_1.setWindowModality(QtCore.Qt.ApplicationModal)

            SVGSearchSpacePath = "SVGs/SVGSearchSpace.svg"
            SVGKeyStatePath = "SVGs/SVGKeyState.svg"
            SVGKeyActionPath = "SVGs/SVGKeyAction.svg"

            SVGSearchSpace = open(SVGSearchSpacePath)
            SVGKeyState = open(SVGKeyStatePath)
            SVGKeyAction = open(SVGKeyActionPath)
            SVGSearchSpaceString, SVGKeyStateString, SVGKeyActionString = "", "", ""
            for line in SVGSearchSpace: SVGSearchSpaceString += line
            for line in SVGKeyState: SVGKeyStateString += line
            for line in SVGKeyAction: SVGKeyActionString += line

            SVGSearchSpaceBytes = bytearray(SVGSearchSpaceString, encoding='utf-8')
            SVGKeyStateBytes = bytearray(SVGKeyStateString, encoding='utf-8')
            SVGKeyActionBytes = bytearray(SVGKeyActionString, encoding='utf-8')

            SVGSearchSpaceWidget = QWebEngineView(SVGDialog_1)
            SVGSearchSpaceWidget.setGeometry(10, 30, 400, 400)
            SVGSearchSpaceWidget.setContent(SVGSearchSpaceBytes, mimeType='image/svg+xml')
            SVGSearchSpaceLabel = QtWidgets.QLabel(SVGDialog_1)
            SVGSearchSpaceLabel.setText("SVG Search Space")
            SVGSearchSpaceLabel.move(150, 10)

            SVGKeyStateWidget = QWebEngineView(SVGDialog_1)
            SVGKeyStateWidget.setGeometry(10, 465, 240, 320)
            SVGKeyStateWidget.setContent(SVGKeyStateBytes, mimeType='image/svg+xml')
            SVGKeyStateLabel = QtWidgets.QLabel(SVGDialog_1)
            SVGKeyStateLabel.setText("SVG Key State")
            SVGKeyStateLabel.move(80, 440)

            SVGKeyActionWidget = QWebEngineView(SVGDialog_1)
            SVGKeyActionWidget.setGeometry(260, 465, 150, 320)
            SVGKeyActionWidget.setContent(SVGKeyActionBytes, mimeType='image/svg+xml')
            SVGKeyActionLabel = QtWidgets.QLabel(SVGDialog_1)
            SVGKeyActionLabel.setText("SVG Key Action")
            SVGKeyActionLabel.move(285, 440)

            SVGPlanPath = "SVGs/Plan/"
            SVGPlanBytes = []
            self.stepCounter = 0

            SVGPlanWidget = QWebEngineView(SVGDialog_1)
            SVGPlanWidget.setGeometry(430, 30, 600, 600)
            SVGPlanLabel = QtWidgets.QLabel(SVGDialog_1)
            SVGPlanLabel.setText("SVG Plan")
            SVGPlanLabel.move(700, 10)

            for SVGImage in sorted(os.listdir(SVGPlanPath)):
                currentSVGString = ""
                currentSVG = open(SVGPlanPath + SVGImage)
                for line in currentSVG: currentSVGString += line
                currentSVGBytes = bytearray(currentSVGString, encoding='utf-8')
                SVGPlanBytes.append(currentSVGBytes)

            SVGPlanWidget.setContent(SVGPlanBytes[0], mimeType='image/svg+xml')

            button_1 = QtWidgets.QPushButton("+ 1 step",SVGDialog_1)
            button_1.resize(100, 50)
            button_1.move(1070,150)
            button_5 = QtWidgets.QPushButton("+ 5 step",SVGDialog_1)
            button_5.resize(100, 50)
            button_5.move(1070,200)
            button_10 = QtWidgets.QPushButton("+ 10 step",SVGDialog_1)
            button_10.resize(100, 50)
            button_10.move(1070,250)

            button_minus1 = QtWidgets.QPushButton("- 1 step",SVGDialog_1)
            button_minus1.resize(100, 50)
            button_minus1.move(1070,330)
            button_minus5 = QtWidgets.QPushButton("- 5 step",SVGDialog_1)
            button_minus5.resize(100, 50)
            button_minus5.move(1070,380)
            button_minus10 = QtWidgets.QPushButton("- 10 step",SVGDialog_1)
            button_minus10.resize(100, 50)
            button_minus10.move(1070,430)

            frameSlider = QtWidgets.QWidget(SVGDialog_1)
            horizontalBox = QtWidgets.QHBoxLayout()
            frameSlider.move(570,650)
            frameSlider.setLayout(horizontalBox)

            slider = LabeledSlider(1, len(os.listdir(SVGPlanPath)), 1, orientation=Qt.Horizontal)
            slider.sl.resize(300, 100)

            horizontalBox.addWidget(slider)

            # +1
            def button1():
                self.stepCounter += 1

                if (self.stepCounter >= len(os.listdir(SVGPlanPath))):
                    self.stepCounter = len(os.listdir(SVGPlanPath)) - 1
                if (self.stepCounter < 0):
                    self.stepCounter = 0

                SVGPlanWidget.setContent(SVGPlanBytes[self.stepCounter], mimeType='image/svg+xml')
                SVGPlanWidget.repaint()

                slider.sl.setValue(self.stepCounter + 1)
                slider.sl.repaint()

            button_1.clicked.connect(button1)

            # +5
            def button5():
                self.stepCounter += 5

                if (self.stepCounter >= len(os.listdir(SVGPlanPath))):
                    self.stepCounter = len(os.listdir(SVGPlanPath)) - 1
                if (self.stepCounter < 0):
                    self.stepCounter = 0

                SVGPlanWidget.setContent(SVGPlanBytes[self.stepCounter], mimeType='image/svg+xml')
                SVGPlanWidget.repaint()

                slider.sl.setValue(self.stepCounter + 1)
                slider.sl.repaint()

            button_5.clicked.connect(button5)

            # +10
            def button10():
                self.stepCounter += 10

                if (self.stepCounter >= len(os.listdir(SVGPlanPath))):
                    self.stepCounter = len(os.listdir(SVGPlanPath)) - 1
                if (self.stepCounter < 0):
                    self.stepCounter = 0

                SVGPlanWidget.setContent(SVGPlanBytes[self.stepCounter], mimeType='image/svg+xml')
                SVGPlanWidget.repaint()

                slider.sl.setValue(self.stepCounter + 1)
                slider.sl.repaint()

            button_10.clicked.connect(button10)

            # -1
            def button_meno1():
                self.stepCounter -= 1

                if (self.stepCounter >= len(os.listdir(SVGPlanPath))):
                    self.stepCounter = len(os.listdir(SVGPlanPath)) - 1
                if (self.stepCounter < 0):
                    self.stepCounter = 0

                SVGPlanWidget.setContent(SVGPlanBytes[self.stepCounter], mimeType='image/svg+xml')
                SVGPlanWidget.repaint()

                slider.sl.setValue(self.stepCounter + 1)
                slider.sl.repaint()

            button_minus1.clicked.connect(button_meno1)

            # -5
            def button_meno5():
                self.stepCounter -= 5

                if (self.stepCounter >= len(os.listdir(SVGPlanPath))):
                    self.stepCounter = len(os.listdir(SVGPlanPath)) - 1
                if (self.stepCounter < 0):
                    self.stepCounter = 0

                SVGPlanWidget.setContent(SVGPlanBytes[self.stepCounter], mimeType='image/svg+xml')
                SVGPlanWidget.repaint()

                slider.sl.setValue(self.stepCounter + 1)
                slider.sl.repaint()

            button_minus5.clicked.connect(button_meno5)

            # -10
            def button_meno10():
                self.stepCounter -= 10

                if (self.stepCounter >= len(os.listdir(SVGPlanPath))):
                    self.stepCounter = len(os.listdir(SVGPlanPath)) - 1
                if (self.stepCounter < 0):
                    self.stepCounter = 0

                SVGPlanWidget.setContent(SVGPlanBytes[self.stepCounter], mimeType='image/svg+xml')
                SVGPlanWidget.repaint()

                slider.sl.setValue(self.stepCounter + 1)
                slider.sl.repaint()

            button_minus10.clicked.connect(button_meno10)

            # Slider
            def slider_plan_SVG():
                SVGPlanWidget.setContent(SVGPlanBytes[slider.sl.value() - 1], mimeType='image/svg+xml')
                self.stepCounter = slider.sl.value() - 1

            slider.sl.valueChanged.connect(slider_plan_SVG)

            self.radioButton.setChecked(False)
            SVGDialog_1.exec_()


        self.radioButton.clicked.connect(SVG_Animation)

#-------------------------------------------------------------

#-------------------------------------------------------------
    # Save files when you click on x to close the main window
    def save_close_exit(self):
        try:     
            if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab)):
                f_domain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                self.list_name_domain.append(f_domain[0])
                file_domain = open(f_domain[0],"w+")
                text1 = QtWidgets.QTextEdit.toPlainText(self.textEdit_initDomain)
                file_domain.write(text1)
                file_domain.close()

            if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_2)):
                f_problem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                self.list_name_problem.append(f_problem[0])
                file_problem = open(f_problem[0],"w+")
                text2 = QtWidgets.QTextEdit.toPlainText(self.textEdit_initProblem)
                file_problem.write(text2)
                file_problem.close()

            if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_NewEmpty)):
                f_empty = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')
                file_empty = open(f_empty[0],"w+")
                text_empty = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewEmpty)
                file_empty.write(text_empty)
                file_empty.close()

            if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_NewStructuredDomain)):
                f_NewStructuredDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                file_NewStructuredDomain = open(f_NewStructuredDomain[0],"w+")
                text_NewStructuredDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewStructuredDomain)
                file_NewStructuredDomain.write(text_NewStructuredDomain)
                file_NewStructuredDomain.close()

            if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_NewStructuredProblem)):
                f_NewStructuredProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                file_NewStructuredProblem = open(f_NewStructuredProblem[0],"w+")
                text_NewStructuredProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_NewStructuredProblem)
                file_NewStructuredProblem.write(text_NewStructuredProblem)
                file_NewStructuredProblem.close()

            if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_LoadDomain)):
                f_LoadDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                file_LoadDomain = open(f_LoadDomain[0],"w+")
                text_LoadDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_LoadDomain)
                file_LoadDomain.write(text_LoadDomain)
                file_LoadDomain.close()

            if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_LoadProblem)):
                f_LoadProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                file_LoadProblem = open(f_LoadProblem[0],"w+")
                text_LoadProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_LoadProblem)
                file_LoadProblem.write(text_LoadProblem)
                file_LoadProblem.close()

            if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_ExampleDomain)):
                f_ExampleDomain = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Domain File')
                file_ExampleDomain = open(f_ExampleDomain[0],"w+")
                text_ExampleDomain = QtWidgets.QTextEdit.toPlainText(self.textEdit_ExampleDomain)
                file_ExampleDomain.write(text_ExampleDomain)
                file_ExampleDomain.close()

            if self.tabWidget.isTabEnabled(self.tabWidget.indexOf(self.tab_ExampleProblem)):
                f_ExampleProblem = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Problem File')
                file_ExampleProblem = open(f_ExampleProblem[0],"w+")
                text_ExampleProblem = QtWidgets.QTextEdit.toPlainText(self.textEdit_ExampleProblem)
                file_ExampleProblem.write(text_ExampleProblem)
                file_ExampleProblem.close()
        except:
            None


#------------------ AUTOCOMPLETION
    def modelFromFile_initDomain(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            print("QStringListModel(self.completer_initDomain)", QStringListModel(self.completer_initDomain))
            return QStringListModel(self.completer_initDomain)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        words = []
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)
                words.append(line)
        QApplication.restoreOverrideCursor()

        return QStringListModel(words, self.completer_initDomain)


    def modelFromFile_initProblem(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            return QStringListModel(self.completer_initProblem)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        words = []
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)
                words.append(line)
        QApplication.restoreOverrideCursor()

        return QStringListModel(words, self.completer_initProblem)


    def modelFromFile_NewEmpty(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            return QStringListModel(self.completer_NewEmpty)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        words = []
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)
                words.append(line)
        QApplication.restoreOverrideCursor()

        return QStringListModel(words, self.completer_NewEmpty)


    def modelFromFile_NewStructuredDomain(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            return QStringListModel(self.completer_NewStructuredDomain)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        words = []
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)
                words.append(line)
        QApplication.restoreOverrideCursor()

        return QStringListModel(words, self.completer_NewStructuredDomain)


    def modelFromFile_NewStructuredProblem(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            return QStringListModel(self.completer_NewStructuredProblem)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        words = []
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)
                words.append(line)
        QApplication.restoreOverrideCursor()

        return QStringListModel(words, self.completer_NewStructuredProblem)


    def modelFromFile_LoadDomain(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            return QStringListModel(self.completer_LoadDomain)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        words = []
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)
                words.append(line)
        QApplication.restoreOverrideCursor()

        return QStringListModel(words, self.completer_LoadDomain)


    def modelFromFile_LoadProblem(self, fileName):
        f = QFile(fileName)
        if not f.open(QFile.ReadOnly):
            return QStringListModel(self.completer_LoadProblem)

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        words = []
        while not f.atEnd():
            line = f.readLine().trimmed()
            if line.length() != 0:
                try:
                    line = str(line, encoding='ascii')
                except TypeError:
                    line = str(line)
                words.append(line)
        QApplication.restoreOverrideCursor()

        return QStringListModel(words, self.completer_LoadProblem)


    def error_function(self,flag_error_name):
        self.flag_error = flag_error_name



#---------------------------------------------------------
#                   Run GUI Planning
#---------------------------------------------------------
class PddlEditor(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(PddlEditor, self).__init__(parent)
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = PddlEditor()

    form.showMaximized()

    def close_action():
        form.save_close_exit()

    app.aboutToQuit.connect(close_action)

    sys.exit(app.exec_())
