#!/usr/bin/python
import sys
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

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

def connect_drag_data_received (widget, act):
    widget.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
    widget.drag_dest_add_text_targets()
    widget.connect('drag_data_received', act)

class TextView (Gtk.TextView):
    def __init__ (self):
        super(TextView, self).__init__()
        self.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.connect('key-press-event', self.key_press)
        self.connect('key-release-event', self.key_release)
        connect_drag_data_received(self, self.drag_data_received)
        if os.path.isfile(text_path): self.set_text(text_path)
        self.drop = False #drag_data_receivedイベントが２度発火する為、フラグ管理用
        self.press_ctrl = False
    
    def key_press (self, widget, event):
        keyname = self.get_keyname(event)
        self.press_ctrl = self.press_ctrl or self.ctrl_check(keyname)
        if self.press_ctrl and keyname == 's': self.save_text()

    def key_release (self, widget, event):
        if self.ctrl_check(self.get_keyname(event)) and self.press_ctrl:
            self.press_ctrl = False

    def drag_data_received (self, widget, ctx, x, y, data, info, time):
        if self.drop:
            tlist = data.get_text().split('\n')[0:-1]
            self.set_text([t[7:-1] for t in tlist][0])
        self.drop = not self.drop
        widget.stop_emission_by_name('drag_data_received')
    
    def set_text (self, path):
        with open(path) as f:
            data = f.read()
            self.get_buffer().set_text(data)
            global text_path
            text_path = path
        
    def save_text (self):
        buffer = self.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        with open(text_path, 'w') as f: f.write(text)

    get_keyname = lambda self, event: Gdk.keyval_name(event.get_keyval()[1])
    ctrl_check = lambda self, key: key == 'Control_L' or key == 'Control_R'

class ScrolledWindow (Gtk.ScrolledWindow):
    def __init__ (self):
        super(ScrolledWindow, self).__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

class Window (Gtk.Window):
    def __init__(self):
        super(Window, self).__init__(title= "opacity text editer")
        self.set_default_size(600, 600)
        self.connect("destroy", Gtk.main_quit)
        self.textview = TextView()
        self.scrollwindow = ScrolledWindow()
        self.scrollwindow.add(self.textview)
        self.add(self.scrollwindow)
        set_css(self)
        set_alpha(self)

def set_css (win):
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
      win.get_screen(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

def set_alpha (win):
    visual = win.get_screen().get_rgba_visual()
    win.set_visual(visual)
    win.set_app_paintable(True)

Window().show_all()
Gtk.main()