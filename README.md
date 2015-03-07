# Quake-like console for OpenBox

Python 3 script for displaying "quake-like" uRXVt console in OpenBox.


## How it works

Console has two states: visible or hidden. Visible console appears on top of a screen above all windows and on all desktops. Hidden console is completely invisible (its window is unmaped).


## How to run it

Code is written in Python 3 and uses:
 * uRXVt terminal,
 * python Xlib and EWMH packages (both in PIP),
 * xmessage command (i.e. Xorg utlity) for displaying error (can be omited).

Script is intended to be used from OpenBox's *rc.xml* file like this:

    <keybind key="W-t">
       <action name="Execute">
          <command>/path/to/quake_console.py</command>
       </action>
    </keybind>

This calls the script whenever Window key and "t" key are pressed together.


## Possible improvements

 - [ ] Avoiding linear search of all windows by caching window ID somewhere? (In root window as a property?)
 - [ ] Remembering window geometry when unmapping and seting it back when mapping.
 - [ ] Getting command to run as a script parameter instead of hard-coded uRXVt terminal.
 - [ ] Making it somehow work with all EWMH compliant window managers.

