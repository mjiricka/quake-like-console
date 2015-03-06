#!/usr/bin/env python

from math import floor
from subprocess import Popen
from time import sleep
from Xlib.display import Display
from Xlib import X, Xatom
from ewmh import EWMH


CONSOLE_PROPERTY_NAME = 'quake_console'
SLEEP_TIME = 0.03
CONSOLE_HEIGHT_RATIO = 0.38 # = Golden ratio.


# state: 1 = mapped, 0 = unmapped
def setConsoleProperty(console, state):
	console.change_property(console_property, Xatom.CARDINAL, 8, [state])


def setAppearance(console, alsoGeometry):
	# States: 0: remove, 1: add, 2: toggle.
	ewmh.setWmState(console, 1, '_OB_WM_STATE_UNDECORATED')
	ewmh.setWmState(console, 1, '_NET_WM_STATE_ABOVE')
	ewmh.setWmDesktop(console, 0xFFFFFFFF) # All desktops.

	if alsoGeometry:
		ewmh.setWmState(console, 1, '_NET_WM_STATE_MAXIMIZED_HORZ')
		height = floor(ewmh.getDesktopGeometry()[1] * CONSOLE_HEIGHT_RATIO)
		ewmh.setMoveResizeWindow(console, y=0, h=height)


def getWindowByPid(pid):
	windowIds = root.get_full_property(
		display.intern_atom('_NET_CLIENT_LIST'), X.AnyPropertyType).value

	# Find window with given PID.
	for windowId in windowIds:
		window = display.create_resource_object('window', windowId)
		prop = window.get_full_property(
			display.intern_atom('_NET_WM_PID'), X.AnyPropertyType)
		windowPid = prop.value[0]
		if windowPid == pid:
			return window

	return None # Window not found.


def waitForResult(f, param):
	result = None
	while result is None:
		sleep(SLEEP_TIME)
		result = f(param)
	return result


def searchWindows(window, consoles):
	children = window.query_tree().children
	for w in children:
		prop = w.get_full_property(console_property, Xatom.CARDINAL)
		if not prop is None:
			value = ord(prop.value[0])
			consoles.append((w, value))
		searchWindows(w, consoles)


def getConsoles():
	consoles = []
	searchWindows(root, consoles)
	return consoles



ewmh = EWMH()
display = ewmh.display
root = display.screen().root
console_property = display.intern_atom(CONSOLE_PROPERTY_NAME)



consoles = getConsoles()
consolesLen = len(consoles)

if consolesLen == 0:
	# Console is not running.

	# Start the console.
	pid = Popen(['urxvt']).pid
	console = waitForResult(getWindowByPid, pid)
	# Configure it.
	setAppearance(console, True)
	# Mark it and say it is mapped.
	setConsoleProperty(console, 1)
	# Focus it.
	ewmh.setActiveWindow(console)

elif consolesLen == 1:
	# Console is running.

	(console, value) = consoles[0]

	if value == 1:
		# Console is mapped. Unmap it.
		setConsoleProperty(console, 0)
		console.unmap()
	else:
		# Console is unmapped. Map it.
		setConsoleProperty(console, 1)
		console.map()
		# Configure it again.
		setAppearance(console, True)
		# And focus it.
		ewmh.setActiveWindow(console)

else:
	# This should not happen...
	subprocess.Popen(['xmessage', '-center', 'Error: More than one console found!'])


display.flush()

