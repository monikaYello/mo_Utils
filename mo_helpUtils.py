'''
# help#
#################### HELP ########################


help(pm.matchTransform)

# get source #
import inspect as inspect
inspect.getsourcefile(pm.matchTransform)


# grep functions of a module
module = pm.selected()[0]
for found in ([i for i in dir(module) if 'get' in i]): print found

'''

'''
#################### SOURCING ########################
# add path if not already there
import sys
myScriptPath = 'D:/Google Drive/PythonScripting/scripts'
if (not myScriptPath in sys.path):
    sys.path.insert(0,myScriptPath)

# ikFkSwitch
import mo_Tools.mog_ikFkSwitch as mog_ikFkSwitch
reload(mog_ikFkSwitch)
mog_ikFkSwitch.FkIk_UI()


import mo_Utils.mo_displayUtil as mo_displayUtil
reload(mo_displayUtil)
mo_displayUtil.layoutCleanScripting()


# third party
sys.path.append("D:\Google Drive\PythonScripting\\thirdParty")
import glTools.tools.removeReferenceEdits


'''
def convertUItoPython(filePath):
	'''
	PyQt Designer: Convert .ui file to .py file
	filePath: str 'D:\Google Drive\My3DWork\QtDesigner\bulletUi.ui'
	Returns:

	'''
	import sys, pprint
	from pysideuic import compileUi
	filePath = filePath.replace('\\', '/')
	print 'converting %s'%filePath
	pyfilePath = filePath.replace('.ui', '.py')
	pyfile = open(pyfilePath, 'w')
	compileUi(filePath, pyfile, False, 4,False)
	pyfile.close()


def callPyQtUI():
	from PySide import QtCore, QtGui
	import bulletUI as customUI
	from shiboken import wrapInstance
	import maya.OpenMayaUI as omui

	def maya_main_window():
		main_window_ptr = omui.MQtUtil.mainWindow()
		return wrapInstance(long(main_window_ptr), QtGui.QWidget)

	class ControlMainWindow(QtGui.QDialog):

		def __init__(self, parent=None):

			super(ControlMainWindow, self).__init__(parent)
			self.setWindowFlags(QtCore.Qt.Tool)
			self.ui =  customUI.Ui_Dialog()
			self.ui.setupUi(self)

			self.ui.pushButton.clicked.connect(self.someFunc)

		def someFunc(self):
			print 'Hello {0} !'

	myWin = ControlMainWindow(parent=maya_main_window())
	myWin.show()



class Pserson:
	def __init__(self, name):
		self.name = name


	def main(body=[]):
		pass

	if __name__ == '__main__':
		main()
