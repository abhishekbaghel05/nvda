import re
import comtypes.client
import comtypes.automation
import ctypes
import audio
import debug
from constants import *
from keyEventHandler import sendKey, key
from config import conf
import NVDAObjects
import _MSOffice

re_dollaredAddress=re.compile(r"^\$?([a-zA-Z]+)\$?([0-9]+)")

class appModule(_MSOffice.appModule):

	def __init__(self):
		_MSOffice.appModule.__init__(self)
		NVDAObjects.registerNVDAObjectClass("EXCEL6",ROLE_SYSTEM_CLIENT,NVDAObject_excelEditableCell)
		NVDAObjects.registerNVDAObjectClass("EXCEL7",ROLE_SYSTEM_CLIENT,NVDAObject_excelTable)

	def __del__(self):
		NVDAObjects.unregisterNVDAObjectClass("EXCEL6",ROLE_SYSTEM_CLIENT)
		NVDAObjects.unregisterNVDAObjectClass("EXCEL7",ROLE_SYSTEM_CLIENT)
		_MSOffice.appModule.__del__(self)

class NVDAObject_excelEditableCell(NVDAObjects.NVDAObject_edit):

	def getRole(self):
		return ROLE_SYSTEM_TEXT

class NVDAObject_excelTable(NVDAObjects.NVDAObject):

	def __init__(self,accObject):
		NVDAObjects.NVDAObject.__init__(self,accObject)
		ptr=ctypes.c_void_p()
		ctypes.windll.oleacc.AccessibleObjectFromWindow(self.getWindowHandle(),-16,ctypes.byref(comtypes.automation.IUnknown._iid_),ctypes.byref(ptr))
		ptr=ctypes.cast(ptr,ctypes.POINTER(comtypes.automation.IUnknown))
		self.excelObject=comtypes.client.wrap(ptr).Application
		self.keyMap.update({
key("ExtendedUp"):self.script_moveByCell,
key("ExtendedDown"):self.script_moveByCell,
key("ExtendedLeft"):self.script_moveByCell,
key("ExtendedRight"):self.script_moveByCell,
key("Control+ExtendedUp"):self.script_moveByCell,
key("Control+ExtendedDown"):self.script_moveByCell,
key("Control+ExtendedLeft"):self.script_moveByCell,
key("Control+ExtendedRight"):self.script_moveByCell,
key("ExtendedHome"):self.script_moveByCell,
key("ExtendedEnd"):self.script_moveByCell,
key("Control+ExtendedHome"):self.script_moveByCell,
key("Control+ExtendedEnd"):self.script_moveByCell,
key("Shift+ExtendedUp"):self.script_moveByCell,
key("Shift+ExtendedDown"):self.script_moveByCell,
key("Shift+ExtendedLeft"):self.script_moveByCell,
key("Shift+ExtendedRight"):self.script_moveByCell,
key("Shift+Control+ExtendedUp"):self.script_moveByCell,
key("Shift+Control+ExtendedDown"):self.script_moveByCell,
key("Shift+Control+ExtendedLeft"):self.script_moveByCell,
key("Shift+Control+ExtendedRight"):self.script_moveByCell,
key("Shift+ExtendedHome"):self.script_moveByCell,
key("Shift+ExtendedEnd"):self.script_moveByCell,
key("Shift+Control+ExtendedHome"):self.script_moveByCell,
key("Shift+Control+ExtendedEnd"):self.script_moveByCell,
})

	def getRole(self):
		return ROLE_SYSTEM_TABLE

	def getSelectedRange(self):
		return self.excelObject.Selection

	def getActiveCell(self):
		return self.excelObject.ActiveCell

	def getCellAddress(self,cell):
		return re_dollaredAddress.sub(r"\1\2",cell.Address())

	def getActiveCellAddress(self):
		return self.getCellAddress(self.getActiveCell())

	def getCellText(self,cell):
		return cell.Text

	def getActiveCellText(self):
		return self.getCellText(self.getActiveCell())

	def cellHasFormula(self,cell):
		return cell.HasFormula

	def activeCellHasFormula(self):
		return self.cellHasFormula(self.getActiveCell())

	def speakSelection(self):
		cells=self.getSelectedRange()
		if cells.Count>1:
			first=cells.Item(1)
			last=cells.Item(cells.Count)
			audio.speakMessage("Selected %s %s through %s %s"%(self.getCellAddress(first),self.getCellText(first),self.getCellAddress(last),self.getCellText(last)))
		else:
			audio.speakMessage("%s"%self.getActiveCellAddress())
			if self.activeCellHasFormula():
				audio.speakMessage("has formula")
			audio.speakText("%s"%self.getActiveCellText())

	def event_focusObject(self):
		if self.doneFocus:
			return
		NVDAObjects.NVDAObject.event_focusObject(self)
		self.speakSelection()

	def script_moveByCell(self,keyPress):
		"""Moves to a cell and speaks its coordinates and content"""
		sendKey(keyPress)
		self.speakSelection()

