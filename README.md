# Quake-like console for OpenBox

Python 3 script for displaying "quake-like" urxvt console in OpenBox.


## What it is

Console has two states: visible or hidden. Visible console appears on top of a screen above all windows and on all desktops. Hidden console is completely unmaped.


## How to run it

Code is written in Python 3 and uses:
 * urxvt terminal,
 * python Xlib and EWMH packages (both in PIP),
 * xmessage command (i.e. Xorg utlity) for displaying error (not necessary).

Script is intended to be used from Openbox's *rc.xml* file like this:

    <keybind key="W-t">
       <action name="Execute">
          <command>python /path/to/quake_console.py</command>
       </action>
    </keybind>


## Possible improvements

 * Avoiding linear search of all windows by caching window id somewhere? (In root window as a property?)
 * Remembering window geometry when unmapping and seting it back when mapping.
 * Getting command to run as a script parameter instead of hard-coded urxvt terminal.
