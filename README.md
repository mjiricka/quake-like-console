# Quake-like console for OpenBox

**UPDATE: THIS SCRIPT HAS NEVER WORKED RELIABLY, I AM NOT SURE WHY, SO I STOPPED USING IT.**

---

Script for displaying uRXVt terminal as quake-like console. Written in Python3, works in OpenBox.

The script shows undecorated terminal window on top of all windows and on all desktops at top of a screen (hence "quake-like"). When the script is run again, the terminal becomes hidden. After another run, the terminal becomes visible again.

Script is intended to be used from OpenBox's *rc.xml* file like this:

    <keybind key="W-t">
       <action name="Execute">
          <command>/path/to/quake_console.py</command>
       </action>
    </keybind>
    
(This calls the script whenever Window key and "t" key are pressed together.)


## Why I find it useful

I find very useful to access a shell anytime from anywhere with just one key combination, without positioning terminal window. Moreover it is persistent (unless you end a shel).

I enjoy the console particularly in these cases:

 * Upgrading the system, because downloading packages take some time and I can quickly check a progress while I am doing other work.
 * Using a command line utilities like *cal*, *date* or *setxkbmap*.
 * Running some program when run script dialog is not enough.


## Dependencies

Code is written in Python 3 and uses:
 * *uRXVt* terminal,
 * python *Xlib* and *EWMH* packages (both in PIP),
 * Command *xmessage* (i.e. Xorg utlity) for displaying errors (can be omited).


## Implementation notes

Unfortunately, I do not know X11 protocol so well, so I had some problems with handling position and size of a terminal window. In code are two comments that say I do not know why things are done this way, but it works for me.


## Possible improvements

 - [X] Avoiding linear search of all windows by caching window ID somewhere? (In root window as a property?)
 - [X] Remembering window geometry when unmapping and seting it back when mapping.
 - [ ] Making it somehow work with all EWMH compliant window managers.
 - [ ] After start, console has full width (thanks to *_NET_WM_STATE_MAXIMIZED_HORZ* hint), but when a size is set via window.configure, window can be smaller than.
