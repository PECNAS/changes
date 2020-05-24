# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_interface.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(799, 370)
		MainWindow.setStyleSheet("")
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setStyleSheet("QPushButton:hover {\n"
"    background-color: #B4B2B5\n"
"}")
		self.centralwidget.setObjectName("centralwidget")
		self.information_box = QtWidgets.QTextBrowser(self.centralwidget)
		self.information_box.setGeometry(QtCore.QRect(20, 10, 421, 301))
		font = QtGui.QFont()
		font.setFamily("Segoe UI Light")
		font.setPointSize(11)
		self.information_box.setFont(font)
		self.information_box.setReadOnly(True)
		self.information_box.setObjectName("information_box")
		self.url_box = QtWidgets.QLineEdit(self.centralwidget)
		self.url_box.setGeometry(QtCore.QRect(470, 20, 261, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI Light")
		font.setPointSize(11)
		self.url_box.setFont(font)
		self.url_box.setObjectName("url_box")
		self.check_box = QtWidgets.QCheckBox(self.centralwidget)
		self.check_box.setGeometry(QtCore.QRect(470, 90, 151, 41))
		font = QtGui.QFont()
		font.setFamily("Segoe UI Light")
		font.setPointSize(11)
		self.check_box.setFont(font)
		self.check_box.setTristate(False)
		self.check_box.setObjectName("check_box")
		self.start_button = QtWidgets.QPushButton(self.centralwidget)
		self.start_button.setGeometry(QtCore.QRect(620, 220, 141, 61))
		font = QtGui.QFont()
		font.setFamily("Segoe UI Light")
		font.setPointSize(11)
		self.start_button.setFont(font)
		self.start_button.setStyleSheet("")
		self.start_button.setObjectName("start_button")
		self.toolButton = QtWidgets.QToolButton(self.centralwidget)
		self.toolButton.setGeometry(QtCore.QRect(770, 0, 25, 19))
		self.toolButton.setObjectName("toolButton")
		font = QtGui.QFont()
		font.setFamily("Segoe UI Light")
		font.setPointSize(11)
		self.comparison_button = QtWidgets.QPushButton(self.centralwidget)
		self.comparison_button.setGeometry(QtCore.QRect(460, 220, 141, 61))
		font = QtGui.QFont()
		font.setFamily("Segoe UI Light")
		font.setPointSize(11)
		self.comparison_button.setFont(font)
		self.comparison_button.setStyleSheet("")
		self.comparison_button.setObjectName("comparison_button")
		self.comparison_name = QtWidgets.QLineEdit(self.centralwidget)
		self.comparison_name.setGeometry(QtCore.QRect(470, 140, 261, 31))
		font = QtGui.QFont()
		font.setFamily("Segoe UI Light")
		font.setPointSize(11)
		self.comparison_name.setFont(font)
		self.comparison_name.setObjectName("comparison_name")
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 799, 21))
		self.menubar.setObjectName("menubar")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
		self.information_box.setPlaceholderText(_translate("MainWindow", "Place for information..."))
		self.url_box.setPlaceholderText(_translate("MainWindow", "Enter url or urls with separator \';\'..."))
		self.check_box.setText(_translate("MainWindow", "Write in database"))
		self.start_button.setText(_translate("MainWindow", "Get"))
		self.toolButton.setText(_translate("MainWindow", "..."))
		self.comparison_button.setText(_translate("MainWindow", "Compare"))
		self.comparison_name.setPlaceholderText(_translate("MainWindow", "Group id or url for comparison..."))
