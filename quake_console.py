#!/usr/bin/env python3

from math import floor
from subprocess import Popen
from time import sleep
from Xlib.display import Display
from Xlib import X, Xatom
from ewmh import EWMH


CONSOLE_PROPERTY_NAME = 'quake_console'
SLEEP_TIME = 0.03 # How much time in second to wait until terminal opens its window.
MAX_ATTEMPTS = 10 # How many times try to look for opened terminal.
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
    else:
        setConsoleGeometry(console)

def rememberConsole(console):
    consoleId = str(console.id)
    root.change_property(console_pid, Xatom.STRING, 8, consoleId)

def getConsole():
    try:
        consoleId = root.get_full_property(console_pid, Xatom.STRING).value
        c = display.create_resource_object('window', int(consoleId))
        prop = c.get_full_property(console_property, Xatom.CARDINAL)
        value = ord(prop.value[0])
        return (c, value)
    except:
        return None

def getWindowByPid(pid):
    windowIds = root.get_full_property(
        display.intern_atom('_NET_CLIENT_LIST'), X.AnyPropertyType).value

    # Find window with given PID.
    for windowId in windowIds:
        window = display.create_resource_object('window', windowId)
        prop = window.get_full_property(
            display.intern_atom('_NET_WM_PID'), X.AnyPropertyType)
        if prop != None:
            windowPid = prop.value[0]
            if windowPid == pid:
                return window

    return None # Window not found.


def waitForResult(f, param):
    result = None
    attempt = 0
    while (result is None) and (attempt < MAX_ATTEMPTS):
        sleep(SLEEP_TIME)
        result = f(param)
        attempt += 1
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
    c = getConsole()

    if c is None:
        consoles = []
        searchWindows(root, consoles)
        return consoles
    else:
        print('yeah!')
        return [c]


def showError(errorMsg):
    Popen(['xmessage', '-center', errorMsg])


def saveConsoleGeometry(console):
    geometry = console.get_geometry()
    ooo = console.translate_coords(root, geometry.x, geometry.y)
    geometryStr = (str(-ooo.x)+';'+str(-ooo.y)+';')+ ';'.join(
        [str(getattr(geometry, p)) for p in ['width', 'height']])
    console.change_property(console_geometry, Xatom.STRING, 8, geometryStr)
    print('save', geometryStr)


def setConsoleGeometry(console):
    geometryStr = console.get_full_property(console_geometry, Xatom.STRING).value
    print('set', geometryStr)
    geometryStr = [int(g) for g in geometryStr.split(';')]
    console.configure(
        x=int(geometryStr[0]),
        y=int(geometryStr[1]),
        width=int(geometryStr[2]),
        height=int(geometryStr[3]))


def mapConsolePreserveSize(console):
    geometry = console.get_geometry()
    console.map()
    console.configure(
        x=geometry.x,
        y=geometry.y,
        width=geometry.width,
        height=501)



ewmh = EWMH()
display = ewmh.display
root = display.screen().root
console_property = display.intern_atom(CONSOLE_PROPERTY_NAME)
console_geometry = display.intern_atom('console_geometry') # TODO
console_pid = display.intern_atom('console_pid_cache') # TODO



consoles = getConsoles()
consolesLen = len(consoles)

if consolesLen == 0:
    # Console is not running.

    # Start the console.
    pid = Popen(['urxvt']).pid
    console = waitForResult(getWindowByPid, pid)
    attr = console.get_attributes()

    rememberConsole(console)

    print(vars(attr))
    print(vars(console.get_wm_hints()))
    geo = console.get_geometry()
    print(vars(console.get_geometry()))
    print(vars(console.get_geometry().root.get_geometry()))
    ooo = console.translate_coords(root, geo.x, geo.y)
    print()
    print (ooo)
    ooo2 = console.translate_coords(geo.root, geo.x, geo.y)
    print()
    print (ooo2)

    if console is None:
        showError('Error: Starting the console was not successful!')
    else:
        print(console.id)

        # Console is running - configure it.
        setAppearance(console, True)
        # Mark it and say it is mapped.
        setConsoleProperty(console, 1)
        # Focus it.
        ewmh.setActiveWindow(console)
        saveConsoleGeometry(console)

elif consolesLen == 1:
    # Console is running.

    print('conzolka:')
    print (getConsole())

    (console, value) = consoles[0]

    if value == 1:
        # Console is mapped. Unmap it.
        setConsoleProperty(console, 0)
        saveConsoleGeometry(console)
        console.unmap()
    else:
        # Console is unmapped. Map it.
        setConsoleProperty(console, 1)
        #mapConsolePreserveSize(console)
        console.map()
        # Configure it again, because it seems many properties
        # are lost after unmapping...
        setAppearance(console, False)
        # And focus it.
        ewmh.setActiveWindow(console)

else:
    # This should not happen...
    showError('Error: More than one console found!')


display.flush()
