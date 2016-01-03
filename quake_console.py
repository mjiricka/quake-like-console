#!/usr/bin/env python3

"""This script implements quake-like console in Openbox."""

from math import floor
from subprocess import Popen

from ewmh import EWMH

from Xlib.display import Display
from Xlib import X
from Xlib import Xatom
from Xlib.protocol.event import CreateNotify


MAPPED = 0
UNMAPPED = 1

CONSOLE_HEIGHT_RATIO = 0.38 # = Golden ratio.

CONSOLE_PROP_NAME = 'quake_console'
CONSOLE_GEOMETRY_PROP_NAME = 'quake_console_geometry'
CONSOLE_WINDOW_ID_PROP_NAME = 'quake_console_window_id'

DISPLAY = Display()
ROOT = DISPLAY.screen().root
E = EWMH()

CONSOLE_PROP = DISPLAY.intern_atom(CONSOLE_PROP_NAME)
CONSOLE_GEOMETRY_PROP = DISPLAY.intern_atom(CONSOLE_GEOMETRY_PROP_NAME)
CONSOLE_WINDOW_ID_PROP = DISPLAY.intern_atom(CONSOLE_WINDOW_ID_PROP_NAME)


def set_appearance(window, also_geometry):
    """Makes terminal's window look like a quake console."""

    # States: 0: remove, 1: add, 2: toggle.
    E.setWmState(window, 1, '_OB_WM_STATE_UNDECORATED')
    E.setWmState(window, 1, '_NET_WM_STATE_ABOVE')
    E.setWmDesktop(window, 0xFFFFFFFF) # All desktops.

    if also_geometry:
        height = floor(E.getDesktopGeometry()[1] * CONSOLE_HEIGHT_RATIO)
        E.setMoveResizeWindow(window, y=0, h=height)

        # It must be set here.
        E.setWmState(window, 1, '_NET_WM_STATE_MAXIMIZED_HORZ')

    # I do not know why, but this must be called to make all preceding
    # commands work. Probably it magically helps to "digest" all
    # X11 commands when they are mixed with commands from uRXVt itself.
    E.getDesktopGeometry()


def save_console_state(window, state):
    """Saves whether console is mapped (state=MAPPED)
       or unmapped (state=UNMAPPED)."""

    window.change_property(CONSOLE_PROP, Xatom.CARDINAL, 8, [state])


def get_console_state(window):
    """Gets previously saved state."""
    prop = window.get_full_property(CONSOLE_PROP, Xatom.CARDINAL)
    return ord(prop.value[0])


def save_console(window):
    """Saves console's window ID into root's window property."""

    window_id = str(window.id)
    ROOT.change_property(CONSOLE_WINDOW_ID_PROP, Xatom.STRING, 8, window_id)


def get_console():
    """Gets previously saved console's window (or None)."""

    try:
        # Get window.
        window_id_str = ROOT.get_full_property(
            CONSOLE_WINDOW_ID_PROP, Xatom.STRING).value
        window = DISPLAY.create_resource_object('window', int(window_id_str))

        # Also look for the state. This is useful because we check
        # that it is really console window. (It is very unlikely, but
        # somebody could close console and its window ID could get
        # another window.)
        state = get_console_state(window)
        return window, state
    except:
        # Nothing relevant was found.
        return None, None


def store_console_geometry(window):
    """Stores current console position and size into window property."""

    geo = window.get_geometry()
    # We want absolute coordinates on a screen.
    tgeo = window.translate_coords(ROOT, geo.x, geo.y)
    # Serialize geometry and save it.
    geo_str = '{0};{1};{2};{3}'.format(
        abs(tgeo.x), abs(tgeo.y), geo.width, geo.height)
    window.change_property(CONSOLE_GEOMETRY_PROP, Xatom.STRING, 8, geo_str)


def restore_console_geometry(window):
    """Restores last console position and size into window property.

       Function must be called after store_console_geometry."""

    geo_str = window.get_full_property(
        CONSOLE_GEOMETRY_PROP, Xatom.STRING).value
    # Deserialize the string.
    geo_str = [int(g) for g in geo_str.split(';')]
    window.configure(
        x=int(geo_str[0]),
        y=int(geo_str[1]),
        width=int(geo_str[2]),
        height=int(geo_str[3]))


def start_new_console():
    """Starts a new terminal, returns its window handle."""

    # Listen for events.
    ROOT.change_attributes(event_mask=X.SubstructureNotifyMask)

    # Start the console.
    pid = Popen(['urxvt']).pid

    # Wait for window.
    for _ in range(1, 1000):
        event = DISPLAY.next_event()
        if isinstance(event, CreateNotify) is True:
            prop = event.window.get_full_property(
                DISPLAY.intern_atom('_NET_WM_PID'), X.AnyPropertyType)
            if prop is not None:
                window_pid = prop.value[0]
                if window_pid == pid:
                    return event.window
    show_error('Unfortunately console did not start.')


def show_error(error_msg):
    """Displays error to user."""
    Popen(['xmessage', '-center', error_msg])


def main():
    """Module entry."""

    # I call set_appearance always twice, because for some reasons
    # I do not understand it is needed to work. At least for me
    # this way it works reliably.

    console, state = get_console()

    if console is None:
        console = start_new_console()
        set_appearance(console, also_geometry=True)
        set_appearance(console, also_geometry=True)
        save_console_state(console, MAPPED)
        save_console(console)
    else:
        if state is MAPPED:
            store_console_geometry(console)
            console.unmap()
            save_console_state(console, UNMAPPED)
        elif state is UNMAPPED:
            console.map()
            set_appearance(console, also_geometry=False)
            restore_console_geometry(console)
            set_appearance(console, also_geometry=False)
            save_console_state(console, MAPPED)
        else:
            show_error('Console data were corrupted!')

main()

# This is very important!
DISPLAY.flush()


# EOF
