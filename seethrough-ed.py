#!/usr/bin/env python3
import sys, os, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from typing import Callable

css = b"""
textview {
  background-color: transparent;
  font: 150% 'Noto Sans CJK JP';
}
textview > text {
  background-color: rgba(0,0,0,0.4);
  color: white;
}
"""

text_path = sys.argv[1] if len(sys.argv) > 1 else ''

def connect_drag_data_received (widget :Gtk.Widget, act :Callable[..., None]) ->None:
    widget.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
    widget.drag_dest_add_text_targets()
    widget.connect('drag_data_received', act)

class TextView (Gtk.TextView):
    def __init__ (self):
        super(TextView, self).__init__()
        self.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.connect('key-press-event', self.key_press)
        connect_drag_data_received(self, self.drag_data_received)
        if os.path.isfile(text_path): self.load_text(text_path)
        self.drop = False #drag_data_receivedイベントが２度発火する為、フラグ管理用
    
    def key_press (self, widget, event :Gdk.EventKey) ->None:
        key = Gdk.keyval_name(event.get_keyval()[1])
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and key == 's': self.save_text()

    def drag_data_received (self, widget, ctx, x, y, data :Gtk.SelectionData, info, time) ->None:
        if self.drop:
            tlist = data.get_text().split('\n')[0:-1]
            self.load_text([t[7:-1] for t in tlist][0])
        self.drop = not self.drop
        self.stop_emission_by_name('drag_data_received')
    
    def load_text (self, path :str) ->None:
        with open(path) as f:
            data = f.read()
            self.get_buffer().set_text(data)
            global text_path
            text_path = path
        
    def save_text (self) ->None:
        buffer = self.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        with open(text_path, 'w') as f: f.write(text)

class ScrolledWindow (Gtk.ScrolledWindow):
    def __init__ (self):
        super(ScrolledWindow, self).__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

class Window (Gtk.Window):
    def __init__(self):
        super(Window, self).__init__(title= "opacity text editor")
        self.set_default_size(600, 600)
        self.connect("destroy", Gtk.main_quit)
        self.textview = TextView()
        self.scrollwindow = ScrolledWindow()
        self.scrollwindow.add(self.textview)
        self.add(self.scrollwindow)

def set_css (win :Gtk.Window) ->None:
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
      win.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

def set_alpha (win :Gtk.Window) ->None:
    visual = win.get_screen().get_rgba_visual()
    win.set_visual(visual)
    win.set_app_paintable(True)

win = Window()
set_css(win)
set_alpha(win)
win.show_all()
Gtk.main()
