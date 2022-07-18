import units
import obgen
import math
import json
import platform
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import *
from tkinter import ttk, filedialog, StringVar
import ttkwidgets
from ttkwidgets.autocomplete import AutocompleteCombobox as acc
from PIL import Image, ImageTk

#the main window
root = tk.Tk()
root.title('Obstacle Studio')
root.geometry('2000x1000')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

menubar = Menu(root)
root.config(menu=menubar)

def default(obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')
    
def new_file(main_window, canvas, terrain_dict, loc_dict, num_locs, ob, current_file, event):
    canvas.clear()
    ob.count = 1
    ob.num_counts = 1
    ob.timing = {1:1}
    ob.explosions = {1: {}}
    ob.recycle_explosions = {1: {}}
    ob.walls.clear()
    ob.show_count(1)
    terrain_dict.clear()
    loc_dict.clear()
    num_locs.replace(0)
    current_file.set('')
    
def open_file(main_window, canvas, terrain_dict, tile_dict, loc_dict, num_locs, ob, ob_num, tool, event):
    file = filedialog.askopenfile(mode='r', initialdir = './', title = 'File name:', filetypes = [('JavaScript Object Notation file', '*.json')], defaultextension='.json')
    if file is not None:
        str_dict = file.read()
        JSON_dict = json.loads(str_dict)
        canvas.clear()
        ob_num.set(JSON_dict['ob_num'])
        ob.timing.clear()
        ob.count = 1
        
        terrain_dict.clear()
        JSON_terrain_dict = json.loads(JSON_dict['terrain'])
        for coords in JSON_terrain_dict.keys():
            x = int(coords.split()[0])
            y = int(coords.split()[1])
            index = int(JSON_terrain_dict[coords])
            terrain_dict[coords] = terrain_tile(x, y, canvas, index, tile_dict)
            
        loc_dict.clear()
        JSON_loc_dict = json.loads(JSON_dict['locations'])
        for n in JSON_loc_dict.keys():
            loc_data = JSON_loc_dict[n]
            number = int(loc_data['number'])
            x = int(loc_data['x'])
            y = int(loc_data['y'])
            width = int(loc_data['width'])
            height = int(loc_data['height'])
            loc = Location((x,y), (width, height), number)
            loc.ID = int(loc_data['ID'])
            loc.highlighted = True
            loc.unmouseover()
            loc.highlighted = False
            loc_dict[number] = loc
        num_locs.replace(int(JSON_dict['num locs']))
        for n in range(1, len(loc_dict) + 1):
            loc_dict[n].write_name(len(loc_dict))
        
        JSON_ob_dict = json.loads(JSON_dict['obstacle'])
        ob.num_counts = int(JSON_ob_dict['num counts'])
        timing = JSON_ob_dict['timing']
        for c in timing.keys():
            count = int(c)
            ob.timing[count] = int(timing[c])
            
        explosions = JSON_ob_dict['explosions']
        for c in explosions.keys():
            count = int(c)
            ob.explosions[count] = ob.explosions.get(count, {})
            for l in explosions[c].keys():
                loc = loc_dict[int(l)]
                for item in explosions[c][l]:
                    name = item[0]
                    player = item[1]
                    sprite = item[2]
                    explosion = Explosion(name, player, sprite)
                    ob.explosions[count][loc] = ob.explosions[count].get(loc, []) + [(explosion, canvas.create_image(loc.x + 16*loc.width, loc.y + 16*loc.height, anchor='center', tag='explosion', image=explosion.img))]
            ob.hide_count()
            ob.count += 1
            
        ob.count = 1
        recycle_explosions = JSON_ob_dict['recycle_explosions']
        for c in recycle_explosions.keys():
            count = int(c)
            ob.recycle_explosions[count] = ob.recycle_explosions.get(count, {})
            for l in recycle_explosions[c].keys():
                loc = loc_dict[int(l)]
                for coord in recycle_explosions[c][l].keys():
                    ob.recycle_explosions[count][loc] = ob.recycle_explosions[count].get(loc, {})
                    for item in recycle_explosions[c][l][coord]:
                        name = item[0]
                        player = item[1]
                        sprite = item[2]
                        explosion = Explosion(name, player, sprite)
                        x = int(coord.split('_')[0])
                        y = int(coord.split('_')[1])
                        ob.recycle_explosions[count][loc][(x,y)] = ob.recycle_explosions[count][loc].get((x,y), []) + [(explosion, canvas.create_image(x + 16*loc.width, y + 16*loc.height, anchor='center', tag='explosion', image=explosion.img))]
            ob.hide_count()
            ob.count += 1
         
        ob.count = 1
        walls = JSON_ob_dict['walls']
        for c in walls.keys():
            count = int(c)
            ob.walls[count] = ob.walls.get(count, {})
            for l in walls[c].keys():
                loc = loc_dict[int(l)]
                item = walls[c][l]
                action = item[0]
                name = item[1]
                player = item[2]
                wall = Wall(name, player)
                if action == 'c':
                    value = ('c', wall, canvas.create_image(loc.x + 16*loc.width, loc.y + 16*loc.height, anchor='center', tag='wall', image=wall.img))
                if action == 'r':
                    value = ('r', wall)
                ob.walls[count][loc] = value
            ob.hide_count()
            ob.count += 1
            
        ob.count = 1
        if tool.num == 3:
            ob.show_count(ob.timing[1])

        canvas.rename_locations(num_locs, loc_dict) 
        canvas.organize_layers()
        canvas.load(tool.num)
        
current_save_file = StringVar()
current_save_file.set('')
        
def save(main_window, canvas, terrain_dict, loc_dic, num_locs, ob, ob_num, current_file, event):
    if current_file.get() == '':
        save_as(main_window, canvas, terrain_dict, loc_dic, num_locs, ob, ob_num, current_file, None)
    else:
        file = open(current_file.get(), 'w')
        dictionary = {}
        dictionary['terrain'] = json.dumps(terrain_dict, default=default)
        
        dictionary['locations'] = json.dumps(loc_dic, default=default)
        dictionary['num locs'] = num_locs.num
        
        dictionary['obstacle'] = json.dumps(ob, default=default)
        
        dictionary['ob_num'] = ob_num.get()
        
        file.write(json.dumps(dictionary))
        file.close()

def save_as(main_window, canvas, terrain_dict, loc_dic, num_locs, ob, ob_num, current_file, event):
    file = filedialog.asksaveasfile(mode='w', initialdir = './', title = 'File name:', filetypes = [('JavaScript Object Notation file', '*.json')], defaultextension='*.json')
    if file is not None:
        current_file.set(file.name)
        dictionary = {}
        dictionary['terrain'] = json.dumps(terrain_dict, default=default)
        
        dictionary['locations'] = json.dumps(loc_dic, default=default)
        dictionary['num locs'] = num_locs.num
        
        dictionary['obstacle'] = json.dumps(ob, default=default)
        
        dictionary['ob_num'] = ob_num.get()
        
        file.write(json.dumps(dictionary))
        file.close()

root.bind('<Control-Key-n>', lambda event: new_file(root, display, terrain_tiles, locations_numerical, loc_count, OBSTACLE, current_save_file, event))
root.bind('<Control-Key-o>', lambda event: open_file(root, display, terrain_tiles, tileimages, locations_numerical, loc_count, OBSTACLE, ob_number, selected_tool, event))
root.bind('<Control-Key-s>', lambda event: save(root, display, terrain_tiles, locations_numerical, loc_count, OBSTACLE, ob_number, current_save_file, event))
root.bind('<Control-Shift-KeyPress-S>', lambda event: save_as(root, display, terrain_tiles, locations_numerical, loc_count, OBSTACLE, ob_number, current_save_file, event))

file_menu = Menu(menubar, tearoff=False)
menubar.add_cascade(label="File", menu=file_menu, underline=0)
file_menu.add_command(label="New", underline=0, command=lambda: new_file(root, display, terrain_tiles, locations_numerical, loc_count, OBSTACLE, current_save_file, None), accelerator="Ctrl+N")
file_menu.add_command(label="Open", underline=0, command=lambda: open_file(root, display, terrain_tiles, tileimages, locations_numerical, loc_count, OBSTACLE, ob_number, selected_tool, None), accelerator="Ctrl+O")
file_menu.add_command(label="Save", underline=0, command=lambda: save(root, display, terrain_tiles, locations_numerical, loc_count, OBSTACLE, ob_number, current_save_file, None), accelerator="Ctrl+S")
file_menu.add_command(label="Save As", underline=1, command=lambda: save_as(root, display, terrain_tiles, locations_numerical, loc_count, OBSTACLE, ob_number, current_save_file, None), accelerator="Ctrl+Shift+S")
file_menu.add_command(label="Exit", underline=0, command=root.destroy, accelerator="Alt+F4")

help_menu = Menu(menubar, tearoff=False)
menubar.add_cascade(label="Help", menu=help_menu, underline=0)
help_menu.add_command(label="Instructions", underline=0, accelerator="F1")
help_menu.add_command(label="About", underline=0, accelerator="F4")

operating_system = platform.system()

#the data_number class stores an int object self.num and has methods for modifying self.num
class data_number:
    def __init__(self, num):
        self.num = num
        self.tr = IntVar()
        self.tr.set(self.num)
    
    def add(self, x):
        self.num += x
        self.tr.set(self.num)
    
    def replace(self, x):
        self.num = x
        self.tr.set(self.num)
   
#the tooltip class is used to show information about widgets when you mouse over them, particularly button hotkeys   
class tooltip:
    def __init__(self, window, widget, label, offset, mouseover_highlight=False, default_color='white', default_color_child='white', mouse_color='white', mouse_color_child='white'):
        self.window = window
        self.widget = widget
        self.tooltip = ttk.Label(window, font=('Segoe UI', 10), background='white', borderwidth=2, padding=(2,2,2,2), relief='groove', text=label)
        self.widget.bind('<Enter>', self.show)
        self.widget.bind('<Leave>', self.hide)
        self.x = offset[0]
        self.y = offset[1]
        self.mouseover_highlight = mouseover_highlight
        self.default_color = default_color
        self.default_color_child = default_color_child
        self.mouse_color = mouse_color
        self.mouse_color_child = mouse_color_child
    
    def show(self, event=None):
        state = True
        try:
            if str(self.widget['state']) == 'disabled':
                state = False
        except:
            pass
        if state:
            if self.mouseover_highlight:
                self.widget.config(bg=self.mouse_color)
                for child in self.widget.winfo_children():
                    child.config(bg=self.mouse_color_child)
            self.tooltip.place(x=self.window.winfo_pointerx() - self.window.winfo_rootx() + self.x, y=self.window.winfo_pointery() - self.window.winfo_rooty() + self.y)
        
    def hide(self, event=None):
        if self.mouseover_highlight:
            self.widget.config(bg=self.default_color)
            for child in self.widget.winfo_children():
                child.config(bg=self.default_color_child)
        self.tooltip.place_forget()
        

#the save_settings class contains methods for reading and writing user options to a text file
class save_settings:
    def __init__(self, tracevar=None, settings='', option=''):
        self.tracevar = tracevar
        self.settings = settings
        self.option = option
        tracevar.trace('w', lambda *args, tracevar=tracevar: self.save())
        
    def load(self):
        f = open(self.settings, 'r')
        value = ''
        for line in f:
            var = line.split('=')[0]
            val = line.split('=')[1].rstrip()
            if var == self.option:
                if val == 'True':
                    value = True
                elif val == 'False':
                    value = False
                else:
                    value = val
        f.close()
        return value
                
    def save(self):
        f = open(self.settings, 'r')
        lines = f.readlines()
        l = 0
        while l < len(lines):
            var = lines[l].split('=')[0]
            if var == self.option:
                value = str(self.tracevar.get())
                lines[l] = var + '=' + value + '\n'
            l += 1
        f = open(self.settings, 'w')
        f.writelines(lines)
        f.close()

#the following classes are used to create various types of widgets whose values are loaded on boot-up from a save file
#this is mostly used for preferences in trigger generation (such as death count units used) which the user will likely wish to set permanently
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Combobox_save(ttk.Combobox, save_settings):
    def __init__(self, *args, tracevar=None, settings='', option='', **kwargs):
        ttk.Combobox.__init__(self, *args, **kwargs)
        save_settings.__init__(self, tracevar, settings, option)
        self.set(self.load())
        
class acc_save(acc, save_settings):
    def __init__(self, *args, tracevar=None, settings='', option='', **kwargs):
        acc.__init__(self, *args, **kwargs)
        save_settings.__init__(self, tracevar, settings, option)
        self.set(self.load())
    
class Entry_save(Entry, save_settings):
    def __init__(self, *args, tracevar=None, settings='', option='', **kwargs):
        Entry.__init__(self, *args, **kwargs)
        save_settings.__init__(self, tracevar, settings, option)
        self.insert(0, self.load())
        
class Checkbutton_save(ttk.Checkbutton, save_settings):
    def __init__(self, *args, tracevar=BooleanVar(), settings='', option='', **kwargs):
        ttk.Checkbutton.__init__(self, *args, **kwargs)
        save_settings.__init__(self, tracevar, settings, option)
        tracevar.set(self.load())
        
class Radiobutton_save(ttk.Radiobutton, save_settings):
    def __init__(self, *args, tracevar=None, settings='', option='', **kwargs):
        ttk.Radiobutton.__init__(self, *args, **kwargs)
        save_settings.__init__(self, tracevar, settings, option)
        tracevar.set(self.load())
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#the following classes
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class indexed_btn(tk.Button):
    def __init__(self, *args, index_data_num, index, default_color, mouse_color, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self.index = index
        self.index_data_num = index_data_num
        self.bind('<Enter>', lambda event: self.mouseover(mouse_color, self.index == self.index_data_num.num, event))
        self.bind('<Leave>', lambda event: self.mouseover(default_color, self.index == self.index_data_num.num, event))
    
    def mouseover(self, color, flag, event=None):
        if not flag:
            self.config(bg=color)

class widget_hotkey():
    def __init__(self, window, hotkey, callback):
        self.window = window
        self.hotkey = hotkey
        self.callback = callback
        
    def keybind(self):
        self.window.bind(self.hotkey, self.callback)
    
    def unkeybind(self):
        self.window.unbind(self.hotkey)
        
    def cmd(self, callback):
        self.callback = callback

class hotkey_btn(tk.Button, widget_hotkey):
    def __init__(self, *args, window, hotkey, callback, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        widget_hotkey.__init__(self, window, hotkey, callback)
        
class hotkey_ttkBtn(ttk.Button, widget_hotkey):
    def __init__(self, *args, window, hotkey, callback, **kwargs):
        ttk.Button.__init__(self, *args, **kwargs)
        widget_hotkey.__init__(self, window, hotkey, callback)
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

transparent_pixel = tk.PhotoImage(file='./Images/Misc/blank.png')

#container widget which holds all of the widgets used to view and design obstacles
Editor = ttk.Frame(root)
Editor.columnconfigure(0,weight=1)
Editor.rowconfigure(0, weight=1000)
Editor.rowconfigure(1, weight=1)
Editor.rowconfigure(2, weight=1)
Editor.grid(row=0, column=0, sticky='NESW')

#style with a light gray background used for some frames
graystyle = ttk.Style()
graystyle.configure('gray.TFrame', background = '#dbe0e3')
darkgraystyle = ttk.Style()
darkgraystyle.configure('darkgray.TFrame', background = '#484c4f')
buttonStyle = ttk.Style()
buttonStyle.map('Highlight.TButton')

class ob_canvas(tk.Canvas):
    def __init__(self, blank, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.loc_in_recycle = None
        self.loc_recycling = BooleanVar()
        self.loc_recycling.set(False)
        self.gridsize = 32
        self.blank = blank
        self.layers = ('terrain', 'location', 'wall', 'explosion', 'highlight', 'grid', 'locationMouseover', 'locationExtras')
        self.create_layers(self.layers)
        self.highlight_resizes = {}
        for width in range(1,20):
            for height in range(1,20):
                highlight_tile = Image.open('./Images/Misc/gridhighlight.png')
                highlight_tile_resized = highlight_tile.resize((32*width,32*height), Image.ANTIALIAS)
                self.highlight_resizes[(width, height)] = ImageTk.PhotoImage(highlight_tile_resized)
        
    def create_layers(self, layers):
        for layer in layers:
            if len(self.find_withtag(layer)) == 0:
                self.create_image(0, 0, anchor='nw', tag=layer, image=self.blank)
        self.organize_layers()
        
    #a new object placed on the canvas will appear at the top layer by default, so the layers need to be reorderable
    def organize_layers(self):
        for layer in self.layers:
            if len(self.find_withtag(layer)) == 0:
                self.create_image(0, 0, anchor='nw', tag=layer, image=self.blank)
        self.tag_raise('locationExtras')
        self.tag_lower('grid', 'locationExtras')
        self.tag_lower('locationMouseover', 'grid')
        self.tag_lower('highlight', 'locationMouseover')
        self.tag_lower('explosion', 'highlight')
        self.tag_lower('wall', 'explosion')
        self.tag_lower('location', 'wall')
        self.tag_lower('terrain', 'location')

    def clear(self):
        for layer in ('terrain', 'location', 'wall', 'explosion', 'highlight', 'locationMouseover', 'locationExtras'):
            self.delete(layer)
        self.create_layers(self.layers)
        
    def load(self, tool):
        for layer in ('terrain', 'location', 'wall', 'explosion', 'highlight', 'locationMouseover', 'locationExtras'):
            self.itemconfig(layer, state='hidden')
        if tool > 0:
            self.itemconfig('terrain', state='normal')
        if tool > 1:
            self.itemconfig('location', state='normal')
            self.itemconfig('locationExtras', state='normal')
            
    def rename_locations(self, num_locs, loc_dict):
        for i in range(1, num_locs.num + 1):
            loc_dict[i].write_name(num_locs)
            
    def snap(self, d, width, height):
        def rounding(p, parity):
            q = round(p/d)*d
            if parity == 1 and d == 32:
                if abs(p - (q - 16)) <= abs(p - (q + 16)):
                    q -= 16
                else:
                    q += 16
            return q
        x = rounding(self.winfo_pointerx() - self.winfo_rootx(), width % 2)
        y = rounding(self.winfo_pointery() - self.winfo_rooty(), height % 2)
        return (x - 16*width, y - 16*height)
        
    def draw_grid(self, d):
        self.delete('grid')
        width = self.winfo_width()
        height = self.winfo_height()

        #draw vertical lines
        for i in range(d, width, d):
            L = self.create_line([(i, 0), (i, height)], tag='grid', fill='#808080')

        #draw horizontal lines
        for i in range(d, height, d):
            L = self.create_line([(0, i), (width, i)], tag='grid', fill='#808080')
            
        self.organize_layers()
    
    def resize_grid(self, d):
        #self.draw_grid(d)
        self.gridsize = d
        
    def highlight_location(self, tool, loc_dict):
        num = -1
        for n in range(1, len(loc_dict) + 1):
            loc = loc_dict[n]
            try:
                if loc.motion or loc.resizing[0] or loc.resizing[1]:
                    num = loc.number
                else:
                    loc.unmouseover()
            except:
                pass
        if num == -1:
            flag = False
            for n in reversed(range(1, len(loc_dict) + 1)):
                loc = loc_dict[n]
                if loc.mouseover()[0] > 0 and loc.mouseover()[1] > 0:
                    flag = True
                    loc.mouseover_highlight()
                    if loc.mouseover()[0] > 1 and loc.mouseover()[1] > 1:
                        if tool.num == 2:
                            self.config(cursor='fleur')
                    elif loc.mouseover()[0] > 1 and loc.mouseover()[1] == 1:
                        if tool.num == 2:
                            self.config(cursor='sb_h_double_arrow')
                    elif loc.mouseover()[0] == 1 and loc.mouseover()[1] > 1:
                        if tool.num == 2:
                            self.config(cursor='sb_v_double_arrow')
                    else:
                        if tool.num == 2:
                            self.config(cursor='hand2')
                    break
            if not flag:
                self.config(cursor='arrow')
            
    def mouse_highlight(self, tool, d, w, h, loc_dict, event):
        if tool.num < 3:
            self.delete('highlight')
            x = self.snap(d, w, h)[0]
            y = self.snap(d, w, h)[1]
            self.create_image(x, y, anchor = 'nw', tag='highlight', image=self.highlight_resizes[(w, h)])
        if tool.num > 1:
            self.highlight_location(tool, loc_dict)
        
    def recycle_loc(self, tool, ob, loc_dict, gridsize, event):
        if self.loc_recycling:
            n = len(loc_dict)
            while n > 0:
                loc = loc_dict[n]
                if loc.highlighted:
                    self.loc_in_recycle = loc
                    self.bind('<Motion>', lambda event: self.mouse_highlight(tool, self.gridsize, loc.width, loc.height, loc_dict, event))
                    break
                else:
                    n -= 1
                    
        
#the display on which terrain, locations, and explosions can be placed
display = ob_canvas(transparent_pixel, Editor, bg="black")
display['borderwidth'] = 2
display['relief'] = 'groove'
display.grid(column=0, row=0, sticky='NESW')

#this allows the user to mouseover the display to unfocus text entry boxes so that subsequent key presses won't get typed in
def mouseover_display(event):
    display.focus_set()
    
display.bind('<Enter>', mouseover_display)

#recreates a layer on the display in case it's deleted
def recreate_layer(layer):
    if len(display.find_withtag(layer)) == 0:
        display.create_image(0, 0, anchor='nw', tag=layer, image=transparent_pixel)
    
gridsize = data_number(32) #the side length of the grid tiles in pixels
(W, H) = (data_number(2), data_number(2)) #controls the dimensions of locations/terrain one places (set by default to 2x2 tiles)

#draws a grid with cells of size d x d pixels
def draw_grid(d, event):
    d = d.num
    display.delete('grid')
    width = display.winfo_width()
    height = display.winfo_height()

    #draw vertical lines
    for i in range(d, width, d):
        L = display.create_line([(i, 0), (i, height)], tag='grid', fill='#808080')

    #draw horizontal lines
    for i in range(d, height, d):
        L = display.create_line([(0, i), (width, i)], tag='grid', fill='#808080')
        
    display.tag_lower('grid', 'locationExtras')

#calculation used to snap objects to the grid
def snap(d, width, height):
    def rounding(p, parity):
        q = round(p/d)*d
        if parity == 1 and d == 32:
            if abs(p - (q - 16)) <= abs(p - (q + 16)):
                q -= 16
            else:
                q += 16
        return q
    x = rounding(display.winfo_pointerx() - display.winfo_rootx(), width % 2)
    y = rounding(display.winfo_pointery() - display.winfo_rooty(), height % 2)
    return (x - 16*width, y - 16*height)

#creates and stores the gray overlays used to indicate where objects will be placed
highlight_resizes = {} #hashes dimensions (w,h) to the overlay of resolution 32*w x 32*h used to indicate where terrain/locations will be placed
for width in range(1,20):
    for height in range(1,20):
        highlight_tile = Image.open('./Images/Misc/gridhighlight.png')
        highlight_tile_resized = highlight_tile.resize((32*width,32*height), Image.ANTIALIAS)
        highlight_resizes[(width, height)] = ImageTk.PhotoImage(highlight_tile_resized)

#places overlays used to indicate where locations/terrain will be placed and when the mouse cursor is on a location
def highlight_atCursor(d, w, h, tool, event):
    d = d.num
    w = w.num
    h = h.num
    if 0 < tool < 3:
        display.delete('highlight')
        x = snap(d, w, h)[0]
        y = snap(d, w, h)[1]
        display.create_image(x, y, anchor = 'nw', tag='highlight', image=highlight_resizes[(w, h)])
    if tool > 1:
        highlight_location(locations_numerical, loc_count)
    display.organize_layers()
   

#container widget which holds the widgets used to edit obstacles
editor_controls = ttk.Frame(Editor, style='gray.TFrame')
editor_controls['borderwidth'] = 2
editor_controls['relief'] = 'sunken'
editor_controls.columnconfigure(0, weight = 1)
editor_controls.columnconfigure(1, weight = 10)
editor_controls.columnconfigure(2, weight = 1) 
editor_controls.grid(column=0, row=1, sticky='ESW', padx=4, pady=4)

#MODE SELECTION MENU
mode_select = ttk.LabelFrame(editor_controls, text='Mode:')
mode_select['borderwidth'] = 2
mode_select['relief'] = 'sunken'
mode_select.grid(column = 0, row = 0, sticky='NW')

selected_tool = data_number(-1)

def arrange_UIs(showUI, hideUIs):
    for UI in hideUIs:
        for widget in UI:
            widget.grid_remove()
    for widget in showUI:
        widget.grid()

def hide_UI(UI):
    for widget in UI:
        widget.grid_remove()
        
def rebind_hotkeys(widgets):
    for widget in widgets:
        widget.keybind()
        
def unbind_hotkeys(widget_lists):
    for widget_list in widget_lists:
        for widget in widget_list:
            widget.unkeybind()
        

#MODE SELECTION BUTTON FUNCTIONS
def press_Terrain_btn(thisUI, otherUIs, hotkey_widgets, unhotkey_widgets, mode_btn, other_mode_btns, canvas, tool, d, w, h, tile_choice, loc_dictionary, OS, event=None):
    if OS == 'Darwin':
        right_mouse = '2'
    else:
        right_mouse = '3'
    highlight_atCursor(d, w, h, 1, None)
    tool.replace(1)
    canvas.bind('<Motion>', lambda event: highlight_atCursor(d, w, h, 1, event))
    d.replace(32)
    canvas.bind('<Button-1>', lambda event: place_terrain(canvas, tile_choice, w, h, event))
    canvas.bind('<B1-Motion>', lambda event: place_terrain(canvas, tile_choice, w, h, event))
    canvas.bind('<Button-' + right_mouse + '>', lambda event: delete_terrain(canvas, w, h, event))
    canvas.bind('<B' + right_mouse + '-Motion>', lambda event: delete_terrain(canvas, w, h, event))
    canvas.unbind('<ButtonRelease-1>')
    canvas.unbind('<Key-w>')
    canvas.unbind('<Key-r>')
    canvas.unbind('<Key-d>')
    hide_locations(loc_dictionary)
    hide_obstacle()
    arrange_UIs(thisUI, otherUIs)
    unbind_hotkeys(unhotkey_widgets)
    rebind_hotkeys(hotkey_widgets)
    for btn in other_mode_btns:
        btn.config(state='normal')
    mode_btn.config(state='disabled')
    
def press_Location_btn(thisUI, otherUIs, hotkey_widgets, unhotkey_widgets, mode_btn, other_mode_btns, canvas, tool, gridsize_choice, d, w, h, loc_dictionary, num_locs, OS, event=None):
    if OS == 'Darwin':
        right_mouse = '2'
    else:
        right_mouse = '3'
    highlight_atCursor(d, w, h, 2, None)
    tool.replace(2)
    d.replace(gridsize_choice)
    canvas.bind('<Motion>', lambda event: highlight_atCursor(d, w, h, 2, event))
    canvas.bind('<ButtonRelease-1>', lambda event: place_location(d, w, h, loc_dictionary, num_locs, event))
    canvas.bind('<Button-' + right_mouse + '>', lambda event: delete_location(loc_dictionary, num_locs, event))
    canvas.bind('<B1-Motion>', lambda event: move_location(d, w, h, loc_dictionary, event))
    canvas.unbind('<B' + right_mouse + '-Motion>')
    canvas.unbind('<Button-1>')
    canvas.unbind('<Key-w>')
    canvas.unbind('<Key-r>')
    canvas.unbind('<Key-d>')
    show_locations(loc_dictionary)
    hide_obstacle()
    arrange_UIs(thisUI, otherUIs)
    unbind_hotkeys(unhotkey_widgets)
    rebind_hotkeys(hotkey_widgets)
    for btn in other_mode_btns:
        btn.config(state='normal')
    mode_btn.config(state='disabled')

def press_Obstacle_btn(thisUI, otherUIs, hotkey_widgets, unhotkey_widgets, mode_btn, other_mode_btns, main_window, canvas, tool, d, w, h, loc_dictionary, num_locs, loc_ID_dict, ob, count_display, expl_menus, expl_player, wall_menu, wall_player, OS, event=None):
    if OS == 'Darwin':
        right_mouse = '2'
    else:
        right_mouse = '3'
    tool.replace(3)
    canvas.delete('highlight')
    recreate_layer('highlight')
    canvas.bind('<Motion>', lambda event: highlight_atCursor(d, w, h, 3, event))
    canvas.bind('<Button-1>', lambda event: ob.place_explosion(event, canvas, loc_dictionary, expl_menus, expl_player))
    canvas.bind('<Button-' + right_mouse + '>', lambda event: ob.delete_explosion(event, loc_dictionary))
    canvas.bind('<Key-w>', lambda event: ob.place_wall(event, wall_menu, wall_player, loc_dictionary))
    canvas.bind('<Key-r>', lambda event: ob.remove_wall(event, loc_dictionary))
    canvas.bind('<Key-d>', lambda event: ob.delete_wall(event, loc_dictionary))
    canvas.bind('<Key-i>', lambda event: set_loc_ID(event, main_window, loc_ID_dict, loc_dictionary))
    canvas.unbind('<ButtonRelease-1>')
    canvas.unbind('<B1-Motion>')
    canvas.unbind('<B' + right_mouse + '-Motion>')
    arrange_UIs(thisUI, otherUIs)
    show_locations(loc_dictionary)
    ob.show_count(ob.timing[ob.count])
    unbind_hotkeys(unhotkey_widgets)
    rebind_hotkeys(hotkey_widgets)
    for btn in other_mode_btns:
        btn.config(state='normal')
    mode_btn.config(state='disabled')

#MODE SELECTION BUTTONS
Terrain_btn = hotkey_ttkBtn(mode_select, text="Terrain", takefocus=False, window=root, hotkey='<Alt-KeyPress-t>', callback=None)
Location_btn = hotkey_ttkBtn(mode_select, text="Location", takefocus=False, window=root, hotkey='<Alt-KeyPress-l>', callback=None)
Obstacle_btn = hotkey_ttkBtn(mode_select, text="Obstacle", takefocus=False, window=root, hotkey='<Alt-KeyPress-o>', callback=None)
                        
Terrain_btn.config(command=lambda: press_Terrain_btn(Terrain_UI, [Location_UI, Obstacle_UI], Terrain_hotkeys, [Location_hotkeys, Obstacle_hotkeys], Terrain_btn, [Location_btn, Obstacle_btn], display, selected_tool, gridsize, W, H, selected_tile, locations_numerical, operating_system))
Terrain_btn.cmd(lambda event: press_Terrain_btn(Terrain_UI, [Location_UI, Obstacle_UI], Terrain_hotkeys, [Location_hotkeys, Obstacle_hotkeys], Terrain_btn, [Location_btn, Obstacle_btn], display, selected_tool, gridsize, W, H, selected_tile, locations_numerical, operating_system, event))
Terrain_btn.keybind()
Terrain_btn_tip = tooltip(root, Terrain_btn, '(Alt+T)', (20,10))
Terrain_btn.grid(row=0, column=0)

Location_btn.config(command=lambda: press_Location_btn(Location_UI, [Terrain_UI, Obstacle_UI], Location_hotkeys,  [Terrain_hotkeys, Obstacle_hotkeys], Location_btn, [Terrain_btn, Obstacle_btn], display, selected_tool, int(gridsize_changed.get()), gridsize, W, H, locations_numerical, loc_count, operating_system))
Location_btn.cmd(lambda event: press_Location_btn(Location_UI, [Terrain_UI, Obstacle_UI], Location_hotkeys, [Terrain_hotkeys, Obstacle_hotkeys], Location_btn, [Terrain_btn, Obstacle_btn], display, selected_tool, int(gridsize_changed.get()), gridsize, W, H, locations_numerical, loc_count, operating_system, event))
Location_btn.keybind()
Location_btn_tip = tooltip(root, Location_btn, '(Alt+L)', (20,10))
Location_btn.grid(row=1, column=0)

Obstacle_btn.config(command=lambda: press_Obstacle_btn(Obstacle_UI, [Terrain_UI, Location_UI], Obstacle_hotkeys, [Terrain_hotkeys, Location_hotkeys], Obstacle_btn, [Location_btn, Terrain_btn],
    root, display, selected_tool, gridsize, W, H,
    locations_numerical, loc_count, loc_ID_windows,
    OBSTACLE, count_display, explosion_menus, selected_player, wall_units_menu, selected_wall_player, operating_system))
Obstacle_btn.cmd(lambda event: press_Obstacle_btn(Obstacle_UI, [Terrain_UI, Location_UI], Obstacle_hotkeys, [Terrain_hotkeys, Location_hotkeys], Obstacle_btn, [Location_btn, Terrain_btn], root, display, selected_tool, gridsize, W, H, locations_numerical, loc_count, loc_ID_windows, OBSTACLE, count_display, explosion_menus, selected_player, wall_units_menu, selected_wall_player, operating_system, event))
Obstacle_btn.keybind()
Obstacle_btn_tip = tooltip(root, Obstacle_btn, '(Alt+O)', (20,10))
Obstacle_btn.grid(row=2, column=0)

#TOOLKIT
toolkit = ttk.Frame(editor_controls, style='gray.TFrame')
toolkit.grid(column=1,row=0)



        


#TERRAIN TILE SELECTION
tile_options = ttk.LabelFrame(toolkit, text='Tiles:')
tile_options.grid(column=0, row=0, rowspan=2, pady =(2,0), sticky='N')

#highlights the currently selected button within a group of mutually exclusive buttons and unhighlights the other buttons
def highlight_button(btn, btn_group, highlight_color, default_color):
    if btn is not None:
        btn.config(bg=highlight_color)
    for button in btn_group:
        if button != btn:
            button.config(bg=default_color)

selected_tile = data_number(0)
def select_tile(index, tile_choice, buttons):
    tile_choice.replace(index)
    highlight_button(buttons[index], buttons, '#69fa4f', 'white')

tilebuttons = []
tileimages = []
c = 0
r = 0
for i in range(0,16):
    tileimages.append(tk.PhotoImage(file='./Images/Tiles/tile' + str(i+1) + '.png'))
    tilebuttons.append(indexed_btn(tile_options, index_data_num = selected_tile, index=i, default_color = 'white', mouse_color = '#74c7ff', image=tileimages[i], bg='white', takefocus=False, padx=1, pady=1))
    tilebuttons[i].grid(column=c, row=r)
    c = (c + 1) % 4
    if i % 4 == 3:
        r += 1
        
tilebuttons[0].configure(bg='#69fa4f', command=lambda: select_tile(0, selected_tile, tilebuttons))
tilebuttons[1].configure(command=lambda: select_tile(1, selected_tile, tilebuttons))
tilebuttons[2].configure(command=lambda: select_tile(2, selected_tile, tilebuttons))
tilebuttons[3].configure(command=lambda: select_tile(3, selected_tile, tilebuttons))
tilebuttons[4].configure(command=lambda: select_tile(4, selected_tile, tilebuttons))
tilebuttons[5].configure(command=lambda: select_tile(5, selected_tile, tilebuttons))
tilebuttons[6].configure(command=lambda: select_tile(6, selected_tile, tilebuttons))
tilebuttons[7].configure(command=lambda: select_tile(7, selected_tile, tilebuttons))
tilebuttons[8].configure(command=lambda: select_tile(8, selected_tile, tilebuttons))
tilebuttons[9].configure(command=lambda: select_tile(9, selected_tile, tilebuttons))
tilebuttons[10].configure(command=lambda: select_tile(10, selected_tile, tilebuttons))
tilebuttons[11].configure(command=lambda: select_tile(11, selected_tile, tilebuttons))
tilebuttons[12].configure(command=lambda: select_tile(12, selected_tile, tilebuttons))
tilebuttons[13].configure(command=lambda: select_tile(13, selected_tile, tilebuttons))
tilebuttons[14].configure(command=lambda: select_tile(14, selected_tile, tilebuttons))
tilebuttons[15].configure(command=lambda: select_tile(15, selected_tile, tilebuttons))

class fixed_sizes(Frame):
    def __init__(self, *args, window, d, w, h, tool, **kwargs):
        super().__init__(*args, **kwargs)
        self.buttons = []
        self.tips = []
        self.d = d
        self.W = w
        self.H = h
        self.fixed_W = w.num
        self.fixed_H = h.num
        self.window = window
        self.tool = tool
        
    def press(self, w, h, event=None):
        self.W.replace(w)
        self.H.replace(h)
        self.fixed_W = w
        self.fixed_H = h
        highlight_atCursor(self.d, self.W, self.H, self.tool.num, None)
        index = 3*(h - 1) + w - 1
        highlight_button(self.buttons[index], self.buttons, '#86f171', '#dfdfdf')
        self.tips[index].mouseover_highlight=False
        for tip in self.tips[0:index] + self.tips[index+1:9]:
            tip.mouseover_highlight=True
    def add_btn(self, w, h, r, c, tooltip_text, key):
        btn = hotkey_btn(self, text=str(w) + 'x' + str(h), takefocus=False, relief='groove', bg = '#dfdfdf', image=transparent_pixel, width=32*w, height=32*h, compound='left',
                            window=self.window, hotkey=key, callback=lambda event: self.press(w, h, event), command=lambda: self.press(w,h))
        tip = tooltip(self.window, btn, tooltip_text, (20, 10), mouseover_highlight=True, default_color='#dfdfdf', mouse_color='#c6f1fb')
        self.tips.append(tip)
        btn.grid(row=r, column=c, sticky='N')
        self.buttons.append(btn)

class custom_dim(ttk.Entry):
    def __init__(self, *args, max_size, w_data_num, h_data_num, w, h, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_size = max_size
        self.w_data_num = w_data_num
        self.h_data_num = h_data_num
        self.w = w
        self.h = h
        
    def set(self):
        try:
            w = int(self.w.get())
            h = int(self.h.get())
            if w > 0 and h > 0:
                self.w_data_num.replace(min(20,w))
                self.h_data_num.replace(min(20,h))
                if w > 20:
                    self.w.set(20)
                if h > 20:
                    self.h.set(20)
        except:
            pass
            
def enable_custom_size(enabled, w_btn, h_btn, fixed_btns):
    if enabled:
        highlight_button(None, fixed_btns.buttons, 'white', '#dfdfdf')
        try:
            w_btn.set()
        except:
            pass
        w_btn.config(state='enabled')
        h_btn.config(state='enabled')
        for btn in fixed_btns.buttons:
            btn.config(state='disabled')
            btn.unkeybind()
    else:
        for btn in fixed_btns.buttons:
            btn.config(state='normal')
            btn.keybind()
        w_btn.config(state='disabled')
        h_btn.config(state='disabled')
        fixed_btns.press(fixed_btns.fixed_W, fixed_btns.fixed_H)

sizes = ttk.LabelFrame(toolkit, text='Size:')
sizes.grid(row=0, column=1, rowspan=2)
fixed_sizes_options = fixed_sizes(sizes, window=root, d=gridsize, w=W, h=H, tool=selected_tool)
fixed_sizes_options.grid(row=0,column=0, sticky='NW', padx = (2,0))
fixed_sizes_options.add_btn(1, 1, 0, 0, '(1)', '1')
fixed_sizes_options.add_btn(2, 1, 0, 1, '(Shift+1)', '!')
fixed_sizes_options.add_btn(3, 1, 0, 2, '(Shift+3)', '<#>')
fixed_sizes_options.add_btn(1, 2, 1, 0, '(Shift+2)', '@')
fixed_sizes_options.add_btn(2, 2, 1, 1, '(2)', '2')
fixed_sizes_options.add_btn(3, 2, 1, 2, '(Alt+3)', '<Alt-KeyPress-3>')
fixed_sizes_options.add_btn(1, 3, 2, 0, '(Alt+1)', '<Alt-KeyPress-1>')
fixed_sizes_options.add_btn(2, 3, 2, 1, '(Alt+2)', '<Alt-KeyPress-2>')
fixed_sizes_options.add_btn(3, 3, 2, 2, '(3)', '3')

custom_sizes = ttk.Frame(sizes)
custom_sizes.grid(column=0, row=1, pady=(10,0))

custom_width = StringVar()
custom_height = StringVar()

custom_width.trace('w', lambda *args, custom_width=custom_width: custom_width_btn.set())
custom_width_btn = custom_dim(custom_sizes, max_size=20, w_data_num=W, h_data_num=H, w=custom_width, h=custom_height, textvariable=custom_width, width=4)
custom_width_tip = tooltip(root, custom_width_btn, 'Enter width (max ' + str(custom_width_btn.max_size) + ')', (20, 10))
custom_width_btn.grid(row=0, column=1, padx=(4,0))
custom_width_btn.config(state='disabled')

custom_size_x = tk.Label(custom_sizes, width=2, height=2, text='x', bg='#f0f0f0')
custom_size_x.grid(row=0, column=2)

custom_height.trace('w', lambda *args, custom_height=custom_height: custom_height_btn.set())
custom_height_btn = custom_dim(custom_sizes, max_size=20, w_data_num=W, h_data_num=H, w=custom_width, h=custom_height, textvariable=custom_height, width=4)
custom_height_tip = tooltip(root, custom_height_btn, 'Enter height (max ' + str(custom_height_btn.max_size) + ')', (20, 10))
custom_height_btn.grid(row=0, column=3, padx=(4,0))
custom_height_btn.config(state='disabled')

use_custom_size = BooleanVar()
use_custom_size.set(False)
custom_size_btn = ttk.Checkbutton(custom_sizes, text='Custom size:', takefocus=False, variable=use_custom_size)
use_custom_size.trace('w', lambda *args, use_custom_size=use_custom_size: enable_custom_size(use_custom_size.get(), custom_width_btn, custom_height_btn, fixed_sizes_options))
custom_size_btn.grid(column=0,row=0, sticky='W')

delete_terrain_btn = hotkey_ttkBtn(toolkit, window=root, hotkey='<Control-KeyPress-BackSpace>', text='Delete all terrain', takefocus=False, callback=lambda event: delete_all_terrain(display, terrain_tiles, event), command=lambda: delete_all_terrain(display, terrain_tiles))
delete_terrain_tip = tooltip(root, delete_terrain_btn, '(Ctrl+BackSpace)', (20, 10))
delete_terrain_btn.grid(row=1, column=0)

class terrain_tile:
    def __init__(self, x, y, canvas, index, imgs):
        self.img = canvas.create_image(x, y, anchor='nw', tag='terrain', image=imgs[index])
        self.index = index
        
    def to_json(self):
        return str(self.index)

terrain_tiles = {} #hashes coordinates (x,y) to the terrain tile whose top left corner is at (x,y)

#places terrain tiles in the highlighted region when the left mouse button is pressed
def place_terrain(canvas, tile_choice, w, h, event):
    width = w.num
    height = h.num
    tile_index = tile_choice.num
    if tile_index >= 0:
        for i in range(0,width):
            for j in range(0,height):
                (a,b) = (snap(32, width, height)[0] + 32*i, snap(32, width, height)[1] + 32*j)
                try:
                    canvas.delete(terrain_tiles[str(a) + ' ' + str(b)].img)
                    del terrain_tiles[(a,b)]
                except:
                    pass
                tile = terrain_tile(a, b, canvas, tile_index, tileimages)
                terrain_tiles[str(a) + ' ' + str(b)] = tile
    highlight_atCursor(data_number(32), w, h, 1, None)
    canvas.tag_lower('terrain', 'location')

#deletes terrain tiles in the highlighted region when the right mouse button is pressed
def delete_all_terrain(canvas, tileMap, event=None):
    for tile in list(tileMap.keys()):
        canvas.delete(tileMap[tile].img)
        del tileMap[tile]

def delete_terrain(canvas, w, h, event):
    width = w.num
    height = h.num
    highlight_atCursor(data_number(32), w, h, 1, None)
    for i in range(0, width):
        for j in range(0, height):
            (a,b) = (snap(32, width, height)[0] + 32*i, snap(32, width, height)[1] + 32*j)
            try:
                canvas.delete(terrain_tiles[str(a) + ' ' + str(b)].img)
                del terrain_tiles[str(a) + ' ' + str(b)]
            except:
                pass
#/////////////////////////////////////////////////////////////////////////////////////////

Terrain_UI = []
Terrain_UI.append(tile_options)
Terrain_UI.append(sizes)
Terrain_UI.append(delete_terrain_btn)
hide_UI(Terrain_UI)

Terrain_hotkeys = [delete_terrain_btn]
for btn in fixed_sizes_options.buttons:
    Terrain_hotkeys.append(btn)


#creates and stores the blue location overlay images 
location_overlays = {} #hashes dimensions (w,h) to the blue location overlay images of resolution 32*w x 32*h
location_overlays = {}
location_overlays[(1,1)] = tk.PhotoImage(file='./Images/Misc/location_mouseover.png')
for i in range(1,11):
    for j in range(1,11):
        img = Image.open('./Images/Misc/location.png')
        img_resized = img.resize((32*i,32*j), Image.ANTIALIAS)
        location_overlays[(i,j)] = ImageTk.PhotoImage(img_resized)

#hashes dimensions (w,h) to the green location overlay images of resolution 32*w x 32*h used to show when the cursor is on top of a location
location_mouseover_overlays = {}
location_mouseover_overlays[(1,1)] = tk.PhotoImage(file='./Images/Misc/location_mouseover.png')
for i in range(1,11):
    for j in range(1,11):
        img = Image.open('./Images/Misc/location_mouseover.png')
        img_resized = img.resize((32*i,32*j), Image.ANTIALIAS)
        location_mouseover_overlays[(i,j)] = ImageTk.PhotoImage(img_resized)

locations_numerical = {} #hashes numbers n to the nth location placed
loc_count = data_number(0) #tracks the number of locations currently placed


def delete_all_locations(loc_dict, num_locs, event=None):
    n = num_locs.num
    while n > 0:
        loc_dict[n].delete(loc_dict, num_locs)
        n -= 1
        
def resize_grid(d, gridsize_changed):
    new_d = int(gridsize_changed.get())
    d.replace(new_d)
    draw_grid(d, event=None)

#Location Mode UI
location_naming_options = ttk.LabelFrame(toolkit, text='Naming convention:')
location_naming_options.grid(row=0, column=0, sticky = 'NW')

location_prefix = StringVar()
location_prefix.trace('w', lambda name, index, mode, location_prefix=location_prefix: display.rename_locations(loc_count, locations_numerical))
location_prefix_entry = ttk.Entry(location_naming_options, textvariable=location_prefix)
location_prefix_entry.grid(row=0, column=0)

naming_convention = StringVar()
naming_convention.trace('w', lambda *args, naming_convention=naming_convention: display.rename_locations(loc_count, locations_numerical))
naming_conventions = ('Numeric (no leading 0\'s)', 'Numeric (leading 0\'s)', 'Alphabetic (A,B,C,...)')
naming_conventions_menu = ttk.OptionMenu(location_naming_options, naming_convention, naming_conventions[0], naming_conventions[0], naming_conventions[1], naming_conventions[2])
naming_conventions_menu.grid(row=1, column=0)

delete_locations_btn = hotkey_ttkBtn(toolkit, text='Delete all locations', takefocus=False, window=root, hotkey='<Control-KeyPress-BackSpace>', callback=lambda event: delete_all_locations(locations_numerical, loc_count, event), command=lambda: delete_all_locations(locations_numerical, loc_count))
delete_locations_tip = tooltip(root, delete_locations_btn, '(Ctrl+BackSpace)', (20, 10))
delete_locations_btn.grid(row=1, column=0, sticky='S')

grid_resize_frame = ttk.LabelFrame(toolkit, text='Grid size (px):')
grid_resize_frame.grid(row=1, column=0, sticky='N')
gridsize_changed = StringVar()
gridsize_changed.trace('w', lambda name, index, mode, gridsize_changed=gridsize_changed : resize_grid(gridsize, gridsize_changed))
grid_sizes = ('32', '16', '8')
grid_resize_menu = ttk.OptionMenu(grid_resize_frame, gridsize_changed, '32', '32', '16', '8')
grid_resize_menu.grid(row=0, column=0)

Location_UI = []
Location_UI.append(location_naming_options)
Location_UI.append(sizes)
Location_UI.append(delete_locations_btn)
Location_UI.append(grid_resize_frame)
hide_UI(Location_UI)

Location_hotkeys = [delete_locations_btn]
for btn in fixed_sizes_options.buttons:
    Location_hotkeys.append(btn)


#Location class ////////////////////////////////////////////////////////////////////////////////////////////////////
#The location class stores the graphical elements of a location (the blue overlay, the borders, and the text label),
#as well as the explosions placed on it ////////////////////////////////////////////////////////////////////////////
class Location:
    def __init__(self, topleft_corner, dim, number):
        self.number = number
    
        self.topleft_corner = topleft_corner
        self.x = topleft_corner[0]
        self.y = topleft_corner[1]
        
        self.dim = dim
        self.width = dim[0]
        self.height = dim[1]

        self.borders = []
        
        self.highlighted = False
        self.mouseover_overlay = None
        self.motion = False
        self.resizing = [False, False]
        
        self.explosions = {}
        self.recycle_explosions = {}
        self.walls = {}
        
        self.draw_borders()
        
        self.ID = 0
        
    def draw_borders(self):
        for border in self.borders:
            display.delete(border)
        self.borders.append(display.create_line((self.x, self.y), (self.x + 32*self.width, self.y), tag='locationExtras', fill='#20ff26'))
        self.borders.append(display.create_line((self.x + 32*self.width, self.y), (self.x + 32*self.width, self.y + 32*self.height), tag='locationExtras', fill='#20ff26'))
        self.borders.append(display.create_line((self.x, self.y + 32*self.height), (self.x + 32*self.width, self.y + 32*self.height), tag='locationExtras', fill='#20ff26'))
        self.borders.append(display.create_line((self.x, self.y), (self.x, self.y + 32*self.height), tag='locationExtras', fill='#20ff26'))
        
    def write_name(self, num_locs):
        try:
            display.delete(self.name)
        except:
            pass
        numbering = ''
        if naming_convention.get() == naming_conventions[0]:
            numbering = str(self.number)
        elif naming_convention.get() == naming_conventions[1]:
            numbering = '0'*(len(str(num_locs.num)) - len(str(self.number))) + str(self.number)
        elif naming_convention.get() == naming_conventions[2]:
            alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            if num_locs.num <= 26:
                numbering = alphabet[self.number - 1]
            else:
                first_letter = max(0, int((self.number - 1)/26))
                numbering = alphabet[first_letter] + alphabet[(self.number % 26 - 1) % 26]
        prefix = location_prefix.get()
        self.label = prefix[0:min(4,len(prefix))] + numbering
        self.name = display.create_text(self.x + 2, self.y + 2, anchor = 'nw', font = 'Arial 10', text=self.label, tag='locationExtras', fill='white')
        
    def mouseover(self):
        x = display.winfo_pointerx() - display.winfo_rootx()
        y = display.winfo_pointery() - display.winfo_rooty()
        bounds_x = 0
        bounds_y = 0
        x_sensitivity = min(8, self.width*4)
        y_sensitivity = min(8, self.height*4)
        if self.x < x < self.x + 32*self.width:
            if self.x < x <= self.x + x_sensitivity:
                bounds_x = 2
            elif self.x + 32*self.width - x_sensitivity <= x < self.x + 32*self.width:
                bounds_x = 3
            else:
                bounds_x = 1
        if self.y < y < self.y + 32*self.height:
            if self.y < y <= self.y + y_sensitivity:
                bounds_y = 2
            elif self.y + 32*self.height - y_sensitivity <= y < self.y + 32*self.height:
                bounds_y = 3
            else:
                bounds_y = 1
        return (bounds_x, bounds_y)
            
    def mouseover_highlight(self):
        if not self.highlighted:
            self.highlighted = True
            try:
                display.delete(self.overlay)
            except:
                pass
            self.mouseover_overlay = display.create_image(self.x, self.y, anchor='nw', tag='locationMouseover', image=location_mouseover_overlays[(self.width,self.height)])
            display.organize_layers()
            
    def unmouseover(self):
        if self.highlighted:
            self.highlighted = False
            try:
                display.delete(self.mouseover_overlay)
            except:
                pass
            self.overlay = display.create_image(self.x, self.y, anchor='nw', tag='location', image=location_overlays[(self.width,self.height)])
            display.organize_layers()
            
    def delete(self, loc_dict, num_locs):
        display.delete(self.name)
        try:
            display.delete(self.mouseover_overlay)
        except:
            pass
        try:
            display.delete(self.overlay)
        except:
            pass
        for border in self.borders:
            display.delete(border)
        for key in set(self.explosions.keys()):
            try:
                OBSTACLE.locs[key].remove(self)
            except:
                pass
            del self.explosions[key]
        del loc_dict[self.number]
        for i in range(self.number + 1, num_locs.num + 1):
            loc = loc_dict[i]
            loc.number -= 1
            loc.write_name(num_locs)
            loc_dict[loc.number] = loc
        num_locs.add(-1)
            
    def move(self, d):
        if (self.mouseover()[0] == 1 and self.mouseover()[1] == 1 and not self.motion and self.resizing == [False, False]) or self.motion:
            x = snap(d, self.width, self.height)[0]
            y = snap(d, self.width, self.height)[1]
            self.motion = True
            self.x = x
            self.y = y
            self.topleft_corner = (x,y)
            
        if ((self.mouseover()[0] > 1 or self.mouseover()[1] > 1) and self.resizing == [False,False] and not self.motion) or (self.resizing[0] or self.resizing[1]):
            x = round((display.winfo_pointerx() - display.winfo_rootx())/32)*32 + (self.x % 32)
            y = round((display.winfo_pointery() - display.winfo_rooty())/32)*32 + (self.y % 32)
            if self.resizing == [False, False]:
                self.center = (self.x + 16*self.width, self.y + 16*self.height)
                if self.mouseover()[0] > 1:
                    self.resizing[0] = True
                if self.mouseover()[1] > 1:
                    self.resizing[1] = True

            if self.resizing[0]:
                if x < self.center[0]:
                    self.width += int((self.x - x)/32)
                    self.x = x
                else:
                    self.width = int(max(1, abs(self.x - x)/32))
                    
            if self.resizing[1]:
                if y < self.center[1]:
                    self.height += int((self.y - y)/32)
                    self.y = y
                else:
                    self.height = int(max(1, abs(self.y - y)/32))

        self.topleft_corner = (self.x, self.y)
        self.dim = (self.width, self.height)
        
        for count in self.explosions.keys():
            for explosion in self.explosions[count]:
                display.coords(explosion[1], self.x + 16*self.width, self.y + 16*self.height)
        for count in self.walls.keys():
            try:
                display.coords(self.walls[count][1], self.x + 16*self.width, self.y + 16*self.height)
            except:
                pass

        display.delete('highlight')
        display.delete(self.mouseover_overlay)
        self.mouseover_overlay = display.create_image(self.x, self.y, anchor='nw', tag='locationMouseover', image=location_mouseover_overlays[(self.width,self.height)])
        display.coords(self.name, self.x + 2, self.y + 2)
        self.draw_borders()
        recreate_layer('highlight')
        display.organize_layers()
                    
    def set_ID(self, ID):
        self.ID = ID
                    
    def to_json(self):
        return {'number': self.number, 'x': self.x, 'y': self.y, 'width': self.width, 'height': self.height, 'ID': self.ID}
            
def move_location(d, w, h, loc_dictionary, event):
    highlight_atCursor(d, w, h, 2, event=None)
    n = loc_count.num
    while n > 0:
        loc = loc_dictionary[n]
        if loc.highlighted:
            break
        else:
            n -= 1
    if n > 0:
        loc.move(d.num)
            
def show_locations(dictionary):
    display.itemconfig('location', state='normal')
    display.itemconfig('locationMouseover', state='normal')
    display.itemconfig('locationExtras', state='normal')
            
def hide_locations(dictionary):
    display.itemconfig('location', state='hidden')
    display.itemconfig('locationMouseover', state='hidden')
    display.itemconfig('locationExtras', state='hidden')


#highlights (in green) the top location underneath the mouse cursor           
def highlight_location(dictionary, num_locs):
    num = -1
    for n in range(1, num_locs.num + 1):
        loc = dictionary[n]
        try:
            if loc.motion or loc.resizing[0] or loc.resizing[1]:
                num = loc.number
            else:
                loc.unmouseover()
        except:
            pass
    if num == -1:
        flag = False
        for n in reversed(range(1, num_locs.num + 1)):
            loc = dictionary[n]
            if loc.mouseover()[0] > 0 and loc.mouseover()[1] > 0:
                flag = True
                loc.mouseover_highlight()
                if loc.mouseover()[0] > 1 and loc.mouseover()[1] > 1:
                    if selected_tool.num == 2:
                        display.config(cursor='fleur')
                elif loc.mouseover()[0] > 1 and loc.mouseover()[1] == 1:
                    if selected_tool.num == 2:
                        display.config(cursor='sb_h_double_arrow')
                elif loc.mouseover()[0] == 1 and loc.mouseover()[1] > 1:
                    if selected_tool.num == 2:
                        display.config(cursor='sb_v_double_arrow')
                else:
                    if selected_tool.num == 2:
                        display.config(cursor='hand2')
                break
        if not flag:
            display.config(cursor='arrow')
            
def open_text_window(string):
    text_window = tk.Toplevel(root)
    message = ttk.Label(text_window, text=string)
    message.pack()

#places a location of size w*h tiles at the highlighted region when the left mouse button is clicked
def place_location(d, w, h, loc_dict, num_locs, event):

    #checks if the user is currently moving a location. if so, a new location will not be placed
    flag = False
    for n in loc_dict.keys():
        if loc_dict[n].motion or loc_dict[n].resizing != [False,False]:
            flag = True
            
    if not flag:
        width = w.num
        height = h.num
        x = snap(d.num, width, height)[0]
        y = snap(d.num, width, height)[1]
        if num_locs.num < 255 and ((x,y),(width,height)):
            num_locs.add(1)
            loc = Location((x,y), (width, height), num_locs.num)
            loc.write_name(num_locs)
            loc_dict[num_locs.num] = loc
            
            #renames the locations after placing the 10th or 100th location if using the leading 0's convention
            if naming_convention.get() == naming_conventions[1] and num_locs.num in (10,100):
                display.rename_locations(num_locs, loc_dict)
            
            #renames the locations after placing the 27th location if using the alphabetic convention
            if naming_convention.get() == naming_conventions[2] and num_locs.num == 27:
                display.rename_locations(num_locs, loc_dict)
            
            elif num_locs.num == 255:
                open_text_window('You have reached the 255 location limit.')
                
    for n in loc_dict.keys():
        loc_dict[n].motion = False
        loc_dict[n].resizing = [False,False]
    highlight_atCursor(d, w, h, 2, None)
    display.tag_lower('location', 'explosion')
                    
def delete_location(loc_dict, num_locs, event):
    for n in reversed(range(1, num_locs.num + 1)):
        if loc_dict[n].mouseover()[0] > 0 and loc_dict[n].mouseover()[1] > 0:
            loc_dict[n].delete(loc_dict, num_locs)
            #renames the locations after placing the 10th or 100th location if using the leading 0's convention
            if naming_convention.get() == naming_conventions[1] and num_locs.num in (9,999):
                display.rename_locations(num_locs, loc_dict)
            
            #renames the locations after placing the 27th location if using the alphabetic convention
            if naming_convention.get() == naming_conventions[2] and num_locs.num == 26:
                display.rename_locations(num_locs, loc_dict)
            break
        else:
           continue
           



#///////////////////////////////////////////////////////////////////////////
#****************************** OBSTACLE MODE ******************************
#///////////////////////////////////////////////////////////////////////////

#lists of Starcraft units
terran_units = units.terran_units
zerg_units = units.zerg_units
protoss_units = units.protoss_units
other_units = units.other_units
wall_units = units.wall_units

#lists of Starcraft sprites
spell_sprites = units.spell_sprites
attack_sprites = units.attack_sprites
unit_sprites = units.unit_sprites
other_sprites = units.other_sprites
image_indices = units.image_indices #image indices of sprites

explosion_images = {}
wall_images = {}

for unit in zerg_units:
    if unit != 'Infested Terran':
        unit = 'Zerg ' + unit
    explosion_images[unit] = tk.PhotoImage(file='./Images/Explosions/placeholder/' + unit + '.png')
    
for unit in terran_units:
    if unit == 'Spider Mine':
        unit = 'Vulture ' + unit
    else:
        unit = 'Terran ' + unit
    explosion_images[unit] = tk.PhotoImage(file='./Images/Explosions/placeholder/' + unit + '.png')
    
for unit in protoss_units:
    explosion_images['Protoss ' + unit] = tk.PhotoImage(file='./Images/Explosions/placeholder/Protoss ' + unit + '.png')
    
for unit in other_units:
    explosion_images[unit] = tk.PhotoImage(file='./Images/Explosions/placeholder/' + unit + '.png')
    
for wall in wall_units:
    wall_images[wall] = tk.PhotoImage(file='./Images/Walls/' + wall + '.png')
    
for sprite in spell_sprites:
    explosion_images[sprite] = tk.PhotoImage(file='./Images/Explosions/placeholder/' + sprite + '.png')
    
for sprite in attack_sprites:
    explosion_images[sprite] = tk.PhotoImage(file='./Images/Explosions/placeholder/' + sprite + '.png')
    
for sprite in unit_sprites:
    explosion_images[sprite] = tk.PhotoImage(file='./Images/Explosions/placeholder/' + sprite + '.png')
    
for sprite in other_sprites:
    explosion_images[sprite] = tk.PhotoImage(file='./Images/Explosions/placeholder/' + sprite + '.png')


players = ['Current Player']
for i in range(1,9):
    players.append('Player ' + str(i))

wall_controls = ttk.LabelFrame(toolkit, text='Walls:')
wall_controls.grid(row=0, column=1, sticky='N')
wall_units_label = ttk.LabelFrame(wall_controls, text='Units:')
wall_units_label.grid(row=0, column=0, columnspan=2)
wall_units_menu = acc(wall_units_label, completevalues=wall_units)
wall_units_menu.grid(row=0, column=0)

wall_remove_options = ttk.LabelFrame(wall_controls, text='Removal Type:')
wall_remove_options.grid(row=1, column=0)
wall_remove_type = StringVar()
wall_kill_btn = ttk.Radiobutton(wall_remove_options, text='Kill Unit', takefocus=False, value='kill', variable=wall_remove_type)
wall_kill_btn.grid(row=0, column=0)
wall_remove_btn = ttk.Radiobutton(wall_remove_options, text='Remove Unit', takefocus=False, value='remove', variable=wall_remove_type)
wall_remove_btn.grid(row=0, column=1)
wall_remove_type.set('remove')

wall_player_frame = ttk.LabelFrame(wall_controls, text='Player:')
wall_player_frame.grid(row=2, column=0)
selected_wall_player = StringVar()
wall_player_menu = acc_save(wall_player_frame, completevalues=players, textvariable=selected_wall_player, tracevar=selected_wall_player, settings='settings.txt', option='wall_player')
selected_wall_player.trace('w', lambda *args, selected_wall_player=selected_wall_player: wall_player_menu.save())
wall_player_menu.grid(row=0, column=0)


class Wall:
    def __init__(self, name, player):
        self.name = name
        self.img = wall_images[self.name]
        self.player = player

class Explosion:
    def __init__(self, name, player, sprite):
        self.name = name
        self.img = explosion_images[self.name]
        self.player = player
        self.sprite = sprite
        
    def to_json(self):
        return {'name': self.name, 'player': self.player, 'sprite': self.sprite}
        
class Obstacle:
    def __init__(self, canvas, count_display, timing_UI):
        self.count = 1
        self.num_counts = 1
        self.timing = {1: 1}
        self.explosions = {1: {}}
        self.recycle_explosions = {}
        self.walls = {}
        
        self.canvas = canvas
        self.count_display = count_display
        self.timing_UI = timing_UI

    def hide_count(self):
        try:
            for loc in self.explosions[self.count].keys():
                for explosion in self.explosions[self.count][loc]:
                    self.canvas.itemconfigure(explosion[1], state='hidden')
        except:
            pass
        try:
            for loc in self.recycle_explosions[self.count].keys():
                for coord in self.recycle_explosions[self.count][loc].keys():
                    for explosion in self.recycle_explosions[self.count][loc][coord]:
                        self.canvas.itemconfigure(explosion[1], state='hidden')
        except:
            pass
        wall_count = 0
        i = self.count
        while i > 0:
            try:
                for loc in self.walls[i].keys():
                    if self.walls[i][loc][0] == 'c':
                        self.canvas.itemconfigure(self.walls[i][loc][2], state='hidden')
                        wall_count = i
                        break
            except:
                pass
            i -= 1
            if i == 0:
                i = self.num_counts
            if i == self.count:
                break
        if wall_count != self.count and wall_count > 0:
            j = self.count
            while j > 0:
                try:
                    for loc in self.walls[j].keys():
                        if self.walls[j][loc][0] == 'r':
                            display.itemconfigure(self.walls[wall_count][loc][2], state='hidden')
                            break
                except:
                    pass
                j -= 1
                if j == 0:
                    j = self.num_counts
                if j == wall_count:
                    break
        
    def show_count(self, delay):
        try:
            for loc in self.explosions[self.count].keys():
                for explosion in self.explosions[self.count][loc]:
                    self.canvas.itemconfigure(explosion[1], state='normal')
        except:
            pass
        try:
            for loc in self.recycle_explosions[self.count].keys():
                for coord in self.recycle_explosions[self.count][loc].keys():
                    for explosion in self.recycle_explosions[self.count][loc][coord]:
                        self.canvas.itemconfigure(explosion[1], state='normal')
        except:
            pass
        self.timing_UI.set_delay(self, delay)
        self.count_display.configure(text='Count #' + str(self.count))
        for count in range(1, self.num_counts + 1):
            try:
                for loc in self.walls[count].keys():
                    wall_count = 0
                    i = self.count
                    while i > 0:
                        try:
                            if self.walls[i][loc][0] == 'c':
                                self.canvas.itemconfigure(self.walls[i][loc][2], state='normal')
                                wall_count = i
                                break
                        except:
                            pass
                        i -= 1
                        if i == 0:
                            i = self.num_counts
                        if i == self.count:
                            break
                    if wall_count != self.count and wall_count > 0:
                        j = self.count
                        while j > 0:
                            try:
                                if self.walls[j][loc][0] == 'r':
                                    display.itemconfigure(self.walls[wall_count][loc][2], state='hidden')
                                    break
                            except:
                                pass
                            j -= 1
                            if j == 0:
                                j = self.num_counts
                            if j == wall_count:
                                break
            except:
                pass

    def waits_to_frames(self):
        for n in self.timing.keys():
            wait = self.timing[n]
            self.timing[n] = math.ceil(int(wait/42)) - 1
            
    def frames_to_waits(self):
        for n in self.timing.keys():
            frames = self.timing[n]
            self.timing[n] = 42*(frames - 1)

    def place_explosion(self, event, canvas, loc_dict, menus, player):
        n = len(loc_dict)
        while n > 0:
            loc = loc_dict[n]
            if loc.highlighted:
                for menu in menus:
                    name = menu.menu.get()
                    if name != '':
                        if name == 'Spider Mine':
                            name = 'Vulture ' + name
                        elif name != 'Infested Terran':
                            name = menu.prefix + name
                        explosion = Explosion(name, player.get(), menu.sprite)
                        flag = False
                        try:
                            for item in self.explosions[self.count][loc]:
                                if item[0].name == explosion.name:
                                    flag = True
                        except:
                            pass
                        if not flag:
                            try:
                                self.explosions[self.count] = self.explosions.get(self.count, {})
                                self.explosions[self.count][loc] = self.explosions[self.count].get(loc, []) + [(explosion, canvas.create_image(loc.x + 16*loc.width, loc.y + 16*loc.height, anchor='center', tag='explosion', image=explosion.img))]
                                self.canvas.organize_layers()
                            except:
                                pass
                break
            else:
                n -= 1

    #used for placing multiple explosions in a single frame using a single location
    def place_explosion_recycle(self, canvas, menus, player, event):
        if canvas.loc_in_recycle is not None:
            loc = canvas.loc_in_recycle
            x = canvas.snap(canvas.gridsize, loc.width, loc.height)[0]
            y = canvas.snap(canvas.gridsize, loc.width, loc.height)[1]
            for menu in menus:
                name = menu.menu.get()
                if name != '':
                    if name == 'Spider Mine':
                        name = 'Vulture ' + name
                    elif name != 'Infested Terran':
                        name = menu.prefix + name
                    explosion = Explosion(name, player.get(), menu.sprite)
                    flag = False
                    try:
                        for item in self.recycle_explosions[self.count][loc][(x,y)]:
                            if item[0].name == explosion.name:
                                flag = True
                    except:
                        pass
                    if not flag:
                        try:
                            self.recycle_explosions[self.count] = self.recycle_explosions.get(self.count, {})
                            self.recycle_explosions[self.count][loc] = self.recycle_explosions[self.count].get(loc, {})
                            self.recycle_explosions[self.count][loc][(x,y)] = self.recycle_explosions[self.count][loc].get((x,y), []) + [(explosion, canvas.create_image(x + 16*loc.width, y + 16*loc.height, anchor='center', tag='explosion', image=explosion.img))]
                            self.canvas.organize_layers()
                        except:
                            pass
                        
    def delete_explosion(self, event, loc_dict):
        n = len(loc_dict)
        while n > 0:
            loc = loc_dict[n]
            if loc.highlighted:
                try:
                    explosion = self.explosions[self.count][loc][-1]
                    self.canvas.delete(explosion[1])
                    self.explosions[self.count][loc].pop(-1)
                    if len(self.explosions[self.count][loc]) == 0:
                        del self.explosions[loc]
                except:
                    pass
                break
            else:
                n -= 1
    
    def delete_explosion_recycle(self, canvas, event):
        if canvas.loc_in_recycle is not None:
            loc = canvas.loc_in_recycle
            x = canvas.snap(canvas.gridsize, loc.width, loc.height)[0]
            y = canvas.snap(canvas.gridsize, loc.width, loc.height)[1]
            try:
                explosions = self.recycle_explosions[self.count][loc][(x,y)]
                canvas.delete(explosions[-1][1])
                explosions.pop(-1)
                if len(explosions) == 0:
                    del self.recycle_explosions[self.count][loc][(x,y)]
                if len(self.recycle_explosions[self.count][loc]) == 0:
                    del self.recycle_explosions[self.count][loc]
            except:
               pass
               
    def place_wall(self, event, wall_menu, player, loc_dict):
        n = len(loc_dict)
        while n > 0:
            loc = loc_dict[n]
            if loc.highlighted:
                name = wall_menu.get()
                if name != '':
                    flag = False
                    m = self.count
                    while m > 0:
                        try:
                            if self.walls[m][loc][0] == 'c':
                                flag = True
                                break
                            if self.walls[m][loc][0] == 'r':
                                if m == self.count:
                                    flag = True
                                break
                        except:
                            pass
                        m -= 1
                        if m == 0:
                            m = self.num_counts
                        if m == self.count:
                            break
                    if not flag:
                        wall = Wall(name, player.get())
                        self.walls[self.count] = self.walls.get(self.count, {})
                        self.walls[self.count][loc] = ('c', wall, self.canvas.create_image(loc.x + 16*loc.width, loc.y + 16*loc.height, anchor='center', tag='wall', image=wall.img))
                        self.canvas.organize_layers()
                break
            else:
                n -= 1
                
    def remove_wall(self, event, loc_dict):
        n = len(loc_dict)
        wall = None
        while n > 0:
            loc = loc_dict[n]
            if loc.highlighted:
                flag = False
                if self.count not in loc.walls.keys():
                    m = (self.count - 1) % (self.num_counts)
                    if m == 0:
                        m = self.num_counts
                    while m != self.count:
                        try:
                            if self.walls[m][loc][0] == 'r':
                                break
                            if self.walls[m][loc][0] == 'c':
                                wall = self.walls[m][loc][1]
                                flag = True
                                break
                        except:
                            pass
                        m -= 1
                        if m == 0:
                            m = self.num_counts
                if flag:
                    self.walls[self.count] = self.walls.get(self.count, {})
                    self.walls[self.count][loc] = ('r', wall)
                    self.show_count(self.timing[self.count])
                break
            else:
                n -= 1
            
    def delete_wall(self, event, loc_dict):
        wall = None
        graphic = None
        n = len(loc_dict)
        while n > 0:
            loc = loc_dict[n]
            if loc.highlighted:
                m = self.count
                while m > 0:
                    flag = False
                    try:
                        if self.walls[m][loc][0] == 'c':
                            flag = True
                            wall = self.walls[m][loc][1]
                            graphic = self.walls[m][loc][2]
                            break
                        if self.walls[m][loc][0] == 'r':
                            break
                    except:
                        pass
                    m -= 1
                    if m == 0:
                        m = self.num_counts
                    if m == self.count:
                        break
                if flag:
                    k = m
                    while k > 0:
                        try:
                            if self.walls[k][loc][0] == 'r':
                                break
                        except:
                            pass
                        k += 1
                        if k == self.num_counts + 1:
                            k = 1
                        if k == m:
                            break
                    self.canvas.delete(self.walls[m][loc][2])
                    del self.walls[m][loc]
                    if k != m:
                        del self.walls[k][loc]
                    if len(self.walls[k]) == 0:
                        del self.walls[k]
                    self.show_count(self.timing[self.count])
                break
            else:
                n -= 1

    def to_json(self):
        explosions = {}
        for count in self.explosions.keys():
            explosions[count] = explosions.get(count, {})
            for loc in self.explosions[count].keys():
                for item in self.explosions[count][loc]:
                    explosion = item[0]
                    explosions[count][loc.number] = explosions[count].get(loc.number, []) + [(explosion.name, explosion.player, explosion.sprite)]
        recycle_explosions = {}
        for count in self.recycle_explosions.keys():
            recycle_explosions[count] = recycle_explosions.get(count, {})
            for loc in self.recycle_explosions[count].keys():
                recycle_explosions[count][loc.number] = recycle_explosions[count].get(loc.number, {})
                for coord in self.recycle_explosions[count][loc].keys():
                    for item in self.recycle_explosions[count][loc][coord]:
                        explosion = item[0]
                        recycle_explosions[count][loc.number][str(coord[0]) + '_' + str(coord[1])] = recycle_explosions[count][loc.number].get(coord, []) + [(explosion.name, explosion.player, explosion.sprite)]
        walls = {}
        for count in self.walls.keys():
            walls[count] = walls.get(count, {})
            for loc in self.walls[count].keys():
                wall = self.walls[count][loc]
                walls[count][loc.number] = (wall[0], wall[1].name, wall[1].player)
        return {'num counts': self.num_counts, 'timing': self.timing, 'explosions': explosions, 'recycle_explosions': recycle_explosions, 'walls': walls}
          
class hotkey_btn(tk.Button, widget_hotkey):
    def __init__(self, *args, window, hotkey, callback, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        widget_hotkey.__init__(self, window, hotkey, callback)
        
class loc_ID_frame(Toplevel):
    def __init__(self, *args, location, **kwargs):
        super().__init__(*args, **kwargs)
        self.title=('Location ' + location.label)
        self.frame = ttk.Frame(self)
        self.frame.grid(row=0, column=0)
        self.location = location
        numbers = []
        for i in range(1,256):
            numbers.append(str(i))
        self.label = ttk.Label(self.frame, text='Location ID:')
        self.label.grid(row=0, column=0)
        self.ID = StringVar()
        self.menu = ttk.Entry(self.frame, textvariable=self.ID)
        self.menu.grid(row=0, column=1)
        self.button = ttk.Button(self.frame, text='Ok', command=lambda: self.set_ID())
        self.button.grid(row=1,column=1)
        
    def set_ID(self):
        try:
            self.location.set_ID(int(self.ID.get()))
            self.withdraw()
        except:
            pass

loc_ID_windows = {}

def set_loc_ID(event, main_window, loc_ID_dict, loc_dict):
    n = loc_count.num
    while n > 0:
        loc = loc_dict[n]
        if loc.highlighted:
            try:
                loc_ID_dict[n].deiconify()
            except:
                window = loc_ID_frame(main_window, location=loc)
                loc_ID_dict[n] = window
            break
        else:
            n -= 1
           

def hide_obstacle():
    display.itemconfigure('explosion', state='hidden')
    display.itemconfigure('wall', state='hidden')
    
def show_obstacle(canvas, ob):
    for loc in ob.explosions[ob.count].keys():
        for explosion in ob.explosions[ob.count][loc]:
            canvas.itemconfigure(explosion[1], state='normal')
    for loc in ob.recycle_explosions[ob.count].keys():
        for coord in ob.recycle_explosions[ob.count][loc].keys():
            for explosion in ob.recycle_explosions[ob.count][loc][coord]:
                canvas.itemconfigure(explosion[1], state='normal')
            

explosion_selection = ttk.LabelFrame(toolkit, text='Explosions:')
explosion_selection.grid(row=0, column=2)

selected_unit = {}
image_index = 0


class explosion_menu(ttk.Frame):
    def choose():
        global selected_unit
        if self.selection.get() != '':
            selected_unit = self.prefix + self.selection.get()
        
    def __init__(self, *args, options=[], prefix='', label='', sprite=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = options
        self.prefix = prefix
        self.sprite = sprite
        self.selection = StringVar()
        self.text_label = ttk.Label(self, text=label)
        self.text_label.grid(row=0, column=0)
        self.menu = acc(self, textvariable=self.selection, completevalues = self.options)
        self.menu.grid(row=0, column=1)
        
def reset_unit_selections(variables):
    for var in variables:
        if var.get() != '':
            var.set('')

unit_selection = ttk.LabelFrame(explosion_selection, text='Units:')
unit_selection.grid(row=0,column=0, sticky='N')

terran_unit_selection = explosion_menu(unit_selection, options=terran_units, prefix='Terran ', label='Terran')
terran_unit_selection.grid(row=0, column=0, sticky='E', pady=1)

zerg_unit_selection = explosion_menu(unit_selection, options=zerg_units, prefix='Zerg ', label='Zerg')
zerg_unit_selection.grid(row=1, column=0, sticky='E', pady=1)

protoss_unit_selection = explosion_menu(unit_selection, options=protoss_units, prefix='Protoss ', label='Protoss')
protoss_unit_selection.grid(row=2, column=0, sticky='E', pady=1)

other_unit_selection = explosion_menu(unit_selection, options=other_units, label='Other')
other_unit_selection.grid(row=3, column=0, sticky='E', pady=1)


def clear_unit_selection(changed_var, unit_variables):
    global t_unit, z_unit, p_unit, o_unit
    if changed_var.get() != '':
        for variable in unit_variables:
            if variable != changed_var:
                variable.set('')

t_unit = terran_unit_selection.selection
z_unit = zerg_unit_selection.selection
p_unit = protoss_unit_selection.selection
o_unit = other_unit_selection.selection
unit_variables = [t_unit, z_unit, p_unit, o_unit]
for changed_var in unit_variables:
    changed_var.trace('w', lambda *args, changed_var=changed_var: clear_unit_selection(changed_var, unit_variables))


sprite_selection = ttk.LabelFrame(explosion_selection, text='Sprites:')
sprite_selection.grid(row=0, column=1)

spell_sprite_selection = explosion_menu(sprite_selection, options=spell_sprites, sprite=True, label='Spells')
spell_sprite_selection.grid(row=0, column=0, sticky='E', pady=1)

attack_sprite_selection = explosion_menu(sprite_selection, options=attack_sprites, sprite=True, label='Attacks')
attack_sprite_selection.grid(row=1, column=0, sticky='E', pady=1)

unit_sprite_selection = explosion_menu(sprite_selection, options=unit_sprites, sprite=True, label='Units')
unit_sprite_selection.grid(row=2, column=0, sticky='E', pady=1)

other_sprite_selection = explosion_menu(sprite_selection, options=other_sprites, sprite=True, label='Other')
other_sprite_selection.grid(row=3, column=0, sticky='E', pady=1)


explosion_menus = [terran_unit_selection, zerg_unit_selection, protoss_unit_selection, other_unit_selection, spell_sprite_selection, attack_sprite_selection, unit_sprite_selection, other_sprite_selection]


def reset_selections(menus, i, j):
    for index in range(i,j+1):
        menus[index].selection.set('')

unit_reset_btn = ttk.Button(unit_selection, text='Reset', command=lambda: reset_selections(explosion_menus, 0, 3))
unit_reset_btn.grid(row=4, column=0, sticky='E')

sprite_reset_btn = ttk.Button(sprite_selection, text='Reset', command=lambda: reset_selections(explosion_menus, 4, 7))
sprite_reset_btn.grid(row=4, column=0, sticky='E')


explosion_options = ttk.Frame(explosion_selection)
explosion_options.grid(row=1, column=0, columnspan=2, pady=2, sticky='W')

player_options_label = ttk.Label(explosion_options, text='Player:')
player_options_label.grid(row=0, column=0)

selected_player = StringVar()
player_number_menu = acc_save(explosion_options, completevalues=players, textvariable=selected_player, tracevar=selected_player, settings='settings.txt', option='explosion_player')
selected_player.trace('w', lambda *args, selected_player=selected_player: player_number_menu.save())
player_number_menu.grid(row=0, column=1, padx=4)


sound_controls = ttk.LabelFrame(toolkit, text='Sound:')
sound_controls.grid(row=0,column=3, sticky='N')
sound_menus_frame = ttk.LabelFrame(sound_controls, text='Units:')
sound_menus_frame.grid(row=0,column=0, sticky='N')

explosion1_m_sounds_label = ttk.Label(sound_menus_frame, text='Explosion1 (Medium)')
explosion1_m_sounds_label.grid(row=0, column=0, sticky='W', pady=1)
explosion1_m_sounds = acc(sound_menus_frame, completevalues = ['Protoss Archon', 'Protoss Carrier', 'Protoss Observer', 'Protoss Reaver'])
explosion1_m_sounds.grid(row=0, column=1, pady=1)

explosion1_s_sounds_label = ttk.Label(sound_menus_frame, text='Explosion1 (Small)')
explosion1_s_sounds_label.grid(row=1, column=0, sticky='W', pady=1)
explosion1_s_sounds = acc(sound_menus_frame, completevalues = ['Protoss Arbiter', 'Protoss Corsair', 'Protoss Probe', 'Protoss Scout', 'Protoss Shuttle'])
explosion1_s_sounds.grid(row=1, column=1, pady=1)

explosion2_m_sounds_label = ttk.Label(sound_menus_frame, text='Explosion2 (Medium)')
explosion2_m_sounds_label.grid(row=2, column=0, sticky='W', pady=1)
explosion2_m_sounds = acc(sound_menus_frame, completevalues = ['Terran Battlecruiser', 'Terran Science Vessel', 'Terran Siege Tank (Siege Mode)', 'Terran Siege Tank (Tank Mode)'])
explosion2_m_sounds.grid(row=2, column=1, pady=1)

explosion2_s_sounds_label = ttk.Label(sound_menus_frame, text='Explosion2 (Small)')
explosion2_s_sounds_label.grid(row=3, column=0, sticky='W', pady=1)
explosion2_s_sounds = acc(sound_menus_frame, completevalues = ['Terran Dropship', 'Terran Goliath', 'Terran SCV', 'Terran Valkyrie', 'Terran Vulture', 'Terran Wraith'])
explosion2_s_sounds.grid(row=3, column=1, pady=1)

zerg_air_death_explosion_large_sounds_label = ttk.Label(sound_menus_frame, text='Zerg Air Death Explosion (Large)')
zerg_air_death_explosion_large_sounds_label.grid(row=4, column=0, sticky='W', pady=1)
zerg_air_death_explosion_large_sounds = acc(sound_menus_frame, completevalues = ['Zerg Devourer', 'Zerg Guardian', 'Zerg Overlord'])
zerg_air_death_explosion_large_sounds.grid(row=4, column=1, pady=1)

zerg_air_death_explosion_small_sounds_label = ttk.Label(sound_menus_frame, text='Zerg Air Death Explosion (Small)')
zerg_air_death_explosion_small_sounds_label.grid(row=5, column=0, sticky='W', pady=1)
zerg_air_death_explosion_small_sounds = acc(sound_menus_frame, completevalues = ['Zerg Mutalisk', 'Zerg Scourge'])
zerg_air_death_explosion_small_sounds.grid(row=5, column=1, pady=1)

sound_menus_dict = {'Explosion1 (Medium)': explosion1_m_sounds,
    'Explosion1 (Small)': explosion1_s_sounds,
    'Explosion2 (Medium)': explosion2_m_sounds,
    'Explosion2 (Small)': explosion2_s_sounds,
    'Zerg Air Death Explosion (Large)': zerg_air_death_explosion_large_sounds,
    'Zerg Air Death Explosion (Small)': zerg_air_death_explosion_small_sounds}


obstacle_controls = ttk.Frame(toolkit, style='gray.TFrame')
obstacle_controls.grid(row=0, column=4, sticky='N')


def change_timing_type():
    global timing_type, timing_type_btn, timing_entry_label, OBSTACLE
    flag = False
    if timing_type == 'frames':
        timing_type = 'waits'
        timing_type_btn.configure(text='Use frames')
        timing_entry_label.configure(text='Wait:')
        OBSTACLE.frames_to_waits()
        flag = True
        wait = 42*(int(current_delay.get()) - 1)
        current_delay.set(str(wait))
    if timing_type == 'waits' and not flag:
        timing_type = 'frames'
        timing_type_btn.configure(text='Use waits')
        timing_entry_label.configure(text='Frames:')
        OBSTACLE.waits_to_frames()
        frames = int(int(current_delay.get())/42) + 1
        current_delay.set(str(frames))
            
class ob_timing_UI(LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.display = tk.Label(self, background ='#484c4f', foreground='white', font=('Times New Roman', 12), text='1 frames', anchor='center', width=20, height=1)
        self.display.grid(row=0, column=0, columnspan=2)

        self.delay = StringVar()
        self.delay.set('1')

        self.entry_label = ttk.Label(self, text='Frames:')
        self.entry_label.grid(row=1, column=0, sticky='w')
        self.entry = ttk.Entry(self, textvariable=self.delay)
        self.entry.grid(row=1, column=1)

        self.mode = 'frames'
        self.mode_btn = ttk.Button(self, text='Use waits')
        self.mode_btn.grid(row=2, column=0, sticky='w')
        
    def display_delay(self, delay):
        if self.mode == 'frames':
            string = str(delay) + ' frame'
            if delay > 1:
                string += 's'
            self.display.configure(text=string)
        if self.mode == 'wait':
            self.display.configure(text=str(delay) + ' ms')
            
    def change_mode(self, ob):
        flag = False
        if self.mode == 'frames':
            self.mode = 'waits'
            self.mode_btn.configure(text='Use frames')
            self.entry_label.configure(text='Wait:')
            ob.frames_to_waits()
            flag = True
            wait = 42*(int(self.delay.get()) - 1)
            self.delay.set(str(wait))
        if self.mode == 'waits' and not flag:
            self.mode = 'frames'
            self.mode_btn.configure(text='Use waits')
            self.entry_label.configure(text='Frames:')
            ob.waits_to_frames()
            frames = int(int(self.delay.get())/42) + 1
            self.delay.set(str(frames))
            
    def set_delay(self, ob, delay):
        if self.mode == 'frames':
            try:
                frames = int(delay)
                ob.timing[ob.count] = frames
                self.delay.set(frames)
                self.display_delay(frames)
            except:
                pass
        if self.mode == 'waits':
            try:
                wait = math.ceil(int(delay)/42)*42
                ob.timing[ob.count] = wait
                self.delay.set(wait)
                self.display_delay(wait)
            except:
                pass

timing_controls = ob_timing_UI(obstacle_controls, text='Timing:')
timing_controls.grid(row=0, column=0, sticky='N')
timing_controls.mode_btn.configure(command=lambda: timing_controls.change_mode(OBSTACLE))
current_delay = timing_controls.delay
current_delay.trace('w', lambda *args, current_delay=current_delay: timing_controls.set_delay(OBSTACLE, current_delay.get()))

# COUNT CONTROLS ############################################################################################################################################################################################################################
# -------------- these buttons allow the user to navigate through the different counts of their obstacle
#hotkey_ttkBtn(mode_select, text="Terrain", takefocus=False, window=root, hotkey='<Alt-KeyPress-t>', callback=None)
class count_btn(hotkey_ttkBtn):
    def __init__(self, *args, win, key, cb, ob, delay, loc_dict, tooltip_text, **kwargs):
        super().__init__(*args, window=win, hotkey=key, callback=cb, **kwargs)
        self.ob = ob
        self.delay = delay
        self.hotkey = key
        self.config(command=self.press)
        self.loc_dict = loc_dict
        self.tooltip = tooltip(win, self, tooltip_text, (20, 10))
        
    def next_count(self):
        new_count = {'_': 1, '-': max(1, self.ob.count - 1), ']': self.ob.count, '=': self.ob.count + 1, '+': self.ob.num_counts, '[': max(1,min(self.ob.count, self.ob.num_counts - 1))}
        return new_count[self.hotkey]
    
    def press(self, event=None):
        self.ob.hide_count()
        if self.hotkey == ']':
            self.ob.explosions = dict_shift(self.ob.explosions, self.ob.count, self.ob.num_counts, {})
            self.ob.recycle_explosions = dict_shift(self.ob.recycle_explosions, self.ob.count, self.ob.num_counts, {})
            self.ob.timing = dict_shift(self.ob.timing, self.ob.count, self.ob.num_counts, int(self.delay.get()))
        if self.hotkey == '[':
            try:
                self.ob.explosions = dict_delete(self.ob.explosions, self.ob.count, self.ob.num_counts)
                self.ob.recycle_explosions = dict_delete(self.ob.recycle_explosions, self.ob.count, self.ob.num_counts)
                self.ob.timing = dict_delete(self.ob.timing, self.ob.count, self.ob.num_counts)
            except:
                pass
        self.ob.count = self.next_count()
        flag = False
        if self.ob.count <= self.ob.num_counts:
            flag = True
        if self.hotkey == ']' or self.ob.count > self.ob.num_counts:
            self.ob.num_counts += 1
        elif self.hotkey == '[':
            self.ob.num_counts = max(1, self.ob.num_counts - 1)
        if flag:
            try:
                self.ob.show_count(self.ob.timing[self.ob.count])
            except:
                pass
        else:
            self.ob.timing[self.ob.count] = self.delay.get()
            self.ob.show_count(self.delay.get())
            
#takes a dictionary whose keys are integers and shifts the keys between (inclusive) "shift_point" and "max_point" up by 1, then assigns "value" to the key "shift_point"
def dict_shift(dictionary, shift_point, max_point, value):
    i = max_point
    while i >= shift_point:
        try:
            dictionary[i+1] = dictionary[i]
        except:
            pass
        i -= 1
    try:
        value = int(value)
    except:
        pass
    if value == None:
        try:
            del dictionary[shift_point]
        except:
            pass
    else:
        dictionary[shift_point] = value
    return dictionary
    
#takes a dictionary whose keys are integers and shifts the keys between (inclusive) "shift_point" and "max_point" down by 1, then deletes the key "max_point"
def dict_delete(dictionary, delete_point, max_point):
    for i in range(delete_point, max_point):
        try:
            dictionary[i] = dictionary[i+1]
        except:
            pass
    try:
        del dictionary[max_point]
    except:
        pass
    return dictionary

count_controls = ttk.LabelFrame(obstacle_controls, text='Count:') #container widget for the various count navigation buttons
count_controls.grid(row=0, column=1, sticky='N')

count_display = tk.Label(count_controls, background ='#484c4f', foreground='white', font=('Times New Roman', 12), text='Count #1', anchor='center', width=15, height=1) #displays the # of the count currently being viewed
count_display.grid(row=0, column=0, columnspan=5, sticky='N')

OBSTACLE = Obstacle(display, count_display, timing_controls)

first_count_btn = count_btn(count_controls, win=root, key='_', cb=None, ob=OBSTACLE, delay=timing_controls.delay, loc_dict=locations_numerical, tooltip_text='First Count (_)', text='<<', width=3)
first_count_btn.cmd(first_count_btn.press)
first_count_btn.grid(row=1, column=0)

prev_count_btn = count_btn(count_controls, win=root, key='-', cb=None, ob=OBSTACLE, delay=timing_controls.delay, loc_dict=locations_numerical, tooltip_text='Previous Count (-)', text='<', width=3)
prev_count_btn.cmd(prev_count_btn.press)
prev_count_btn.grid(row=1, column=1)

insert_count_btn = count_btn(count_controls, win=root, key=']', cb=None, ob=OBSTACLE, delay=timing_controls.delay, loc_dict=locations_numerical, tooltip_text='Insert Count (])', text='*', width=2)
insert_count_btn.cmd(insert_count_btn.press)
insert_count_btn.grid(row=1, column=2)

next_count_btn = count_btn(count_controls, win=root, key='=', cb=None, ob=OBSTACLE, delay=timing_controls.delay, loc_dict=locations_numerical, tooltip_text='Next Count (=)', text='>', width=3)
next_count_btn.cmd(next_count_btn.press)
next_count_btn.grid(row=1, column=3)

last_count_btn = count_btn(count_controls, win=root, key='+', cb=None, ob=OBSTACLE, delay=timing_controls.delay, loc_dict=locations_numerical, tooltip_text='Last Count (+)', text='>>', width=3)
last_count_btn.cmd(last_count_btn.press)
last_count_btn.grid(row=1, column=4)

play_btn = ttk.Button(count_controls, text='Play', width=4) #button to animate the counts in sequence
play_btn.grid(row=2, column=2)

delete_count_btn = count_btn(count_controls, win=root, key='[', cb=None, ob=OBSTACLE, delay=timing_controls.delay.get(),loc_dict=locations_numerical, tooltip_text='Delete Count ([)', text='Delete', width=6)
delete_count_btn.cmd(delete_count_btn.press)
delete_count_btn.grid(row=2, column=3, columnspan = 2)

########## MOVING LOCATIONS ################

def bind_loc_recycling(OS, tool, ob, canvas, loc_dict, menus, player):
    global loc_count
    if canvas.loc_recycling.get():
        canvas.bind('<Key-c>', lambda event: canvas.recycle_loc(data_number(2.5), ob, loc_dict, canvas.gridsize, event))
        canvas.bind('<Button-1>', lambda event: ob.place_explosion_recycle(canvas, menus, player, event))
        if OS == 'Darwin':
            right_mouse = '2'
        else:
            right_mouse = '3'
        canvas.bind('<Button-' + right_mouse + '>', lambda event: ob.delete_explosion_recycle(canvas, event))
    else:
        canvas.unbind('<Key-c>')
        canvas.delete('highlight')
        canvas.bind('<Motion>', lambda event: canvas.mouse_highlight(tool, canvas.gridsize, 2, 2, loc_dict, event))
        canvas.bind('<Button-1>', lambda event: ob.place_explosion(event, canvas, loc_dict, menus, player))

display.loc_recycling.trace('w', lambda *args, display=display: bind_loc_recycling(operating_system, selected_tool, OBSTACLE, display, locations_numerical, explosion_menus, selected_player))

def resize_grid_loc(canvas, d):
    gridsize_changed.set(str(d))
    canvas.resize_grid(d)
    
location_moving_controls = ttk.LabelFrame(toolkit, text='Location Moving:')
location_moving_controls.grid(row=0, column=0, sticky='N')

grid_resize_frame_loc = ttk.LabelFrame(location_moving_controls, text='Grid size (px):')
grid_resize_frame_loc.grid(row=0, column=0)
gridsize_changed_loc = StringVar()
gridsize_changed_loc.set('32')
gridsize_changed_loc.trace('w', lambda *args, gridsize_changed_loc=gridsize_changed_loc: resize_grid_loc(display, int(gridsize_changed_loc.get())))
grid_resize_menu_loc = ttk.OptionMenu(grid_resize_frame_loc, gridsize_changed_loc, '32', '32', '16', '8')
grid_resize_menu_loc.grid(row=0, column=0, sticky='N')

recycle_loc_btn = ttk.Checkbutton(location_moving_controls, text='Location recycling', takefocus=False, variable=display.loc_recycling)
recycle_loc_btn.grid(row=1, column=0, sticky='W')

###################################################################################################################################################################################################################################################

Obstacle_UI = []
Obstacle_UI.append(explosion_selection)
Obstacle_UI.append(obstacle_controls)
Obstacle_UI.append(wall_controls)
Obstacle_UI.append(sound_controls)
Obstacle_UI.append(location_moving_controls)
for widget in Obstacle_UI:
    widget.grid_remove()
    
Obstacle_hotkeys=[first_count_btn, prev_count_btn, insert_count_btn, next_count_btn, last_count_btn, delete_count_btn]

#///////////////////////////////////////////////////////////////////////////////
#****************************** TRIGGER GENERATOR ******************************
#///////////////////////////////////////////////////////////////////////////////

def press_triggen_btn(thisUI, otherUIs):
    arrange_UIs(thisUI, otherUIs)
    root.unbind('<Configure>')

triggen_btn = ttk.Button(Editor, text = 'Trigger Generator', takefocus=False, command=lambda: press_triggen_btn([trig_generator], [[Editor]]))
triggen_btn.grid(column=0, row=2, sticky = 'WE')

trig_generator = ttk.Frame(root, borderwidth=4, relief='sunken')
trig_generator.grid(row=0, column=0, padx=2, pady=2, sticky='NESW')
trig_generator.columnconfigure(0, weight=1)
trig_generator.rowconfigure(0, weight=1)
trig_generator.grid_remove()

trig_text_display = ScrolledText(trig_generator, takefocus=False)
trig_text_display.grid(row=0, column=0, sticky = 'NESW')


trig_controls = ttk.Frame(trig_generator, style='gray.TFrame')
trig_controls.grid(row=1, column=0, sticky='WE')

DC_units = units.DC_units

DC_options = ttk.LabelFrame(trig_controls, text='Death count options:')
DC_options.grid(row=0, column=0)

DC_units_options = ttk.LabelFrame(DC_options, text='Units:')
DC_units_options.grid(row=0, column=0, sticky='W')

ob_DC_label = ttk.Label(DC_units_options, text='Obstacle #:')
ob_DC_label.grid(row=0, column=0, sticky='W')
ob_DC = StringVar()
ob_DC_menu = Combobox_save(DC_units_options, takefocus=False, values=DC_units, textvariable=ob_DC, tracevar=ob_DC, settings='settings.txt', option='ob_DC')
ob_DC_menu.grid(row=0, column=1)

count_DC_label = ttk.Label(DC_units_options, text='Count #:')
count_DC_label.grid(row=1, column=0, sticky='W')
count_DC = StringVar()
count_DC_menu = Combobox_save(DC_units_options, takefocus=False, values=DC_units, textvariable=count_DC, tracevar=count_DC, settings='settings.txt', option='count_DC')
count_DC_menu.grid(row=1, column=1)

frame_DC_label = ttk.Label(DC_units_options, text='Frames:')
frame_DC_label.grid(row=2, column=0, sticky='W')
frame_DC = StringVar()
frame_DC_menu = Combobox_save(DC_units_options, takefocus=False, values=DC_units, textvariable=frame_DC, tracevar=frame_DC, settings='settings.txt', option='frame_DC')
frame_DC_menu.grid(row=2, column=1)

DC_units_player_frame = ttk.LabelFrame(DC_options, text='Unit Owner:')
DC_units_player_frame.grid(row=1, column=0, sticky='W')
DC_units_player = StringVar()
DC_units_player_menu = acc_save(DC_units_player_frame, takefocus=False, completevalues = players, textvariable=DC_units_player, tracevar=DC_units_player, settings='settings.txt', option='DC_units_player')
DC_units_player_menu.grid(row=0, column=0)


player_options = ttk.LabelFrame(trig_controls, text='Player options:')
player_options.grid(row=0, column=1, sticky='N')

trigger_owner_player_label = ttk.Label(player_options, text='Trigger owner:')
trigger_owner_player_label.grid(row=0, column=0)
trigger_owner_player = StringVar()
trigger_owner_player_menu = acc_save(player_options, takefocus=False, completevalues = players[1:9], textvariable=trigger_owner_player, tracevar=trigger_owner_player, settings='settings.txt', option='trigger_player')
trigger_owner_player_menu.grid(row=0, column=1)

player_force_label = ttk.Label(player_options, text='Player Force name:')
player_force_label.grid(row=1, column=0)
player_force = StringVar()
player_force_entry = Entry_save(player_options, textvariable=player_force, takefocus=False, tracevar=player_force, settings='settings.txt', option='player_force')
player_force_entry.grid(row=1, column=1)


comment_options = ttk.LabelFrame(trig_controls, text='Comment options:')
comment_options.grid(row=0, column=2, sticky='N')

comment_ob = BooleanVar()
comment_ob_btn = Checkbutton_save(comment_options, text='Ob', takefocus=False, variable=comment_ob, tracevar=comment_ob, settings='settings.txt', option='comment_ob')
comment_ob_btn.grid(row=0, column=0, sticky='W')

comment_count = BooleanVar()
comment_count_btn = Checkbutton_save(comment_options, text='Count', takefocus=False, variable=comment_count, tracevar=comment_count, settings='settings.txt', option='comment_count')
comment_count_btn.grid(row=1, column=0, sticky='W')

comment_part = BooleanVar()
comment_part_btn = Checkbutton_save(comment_options, text='Part', takefocus=False, variable=comment_part, tracevar=comment_part, settings='settings.txt', option='comment_part')
comment_part_btn.grid(row=2, column=0, sticky='W')

misc_options = ttk.LabelFrame(trig_controls, text='Miscellaneous options:')
misc_options.grid(row=0, column=3, sticky='N')


def change_ob_number(ob_number, button):
    try:
        n = int(ob_number.get())
        ob_number.set(str(n))
        button.configure(state='enabled')
    except:
        button.configure(state='disabled')

ob_number_label = ttk.Label(misc_options, text='Obstacle #:')
ob_number_label.grid(row=0, column=0, sticky='W')
ob_number = StringVar()
ob_number_entry = ttk.Entry(misc_options, textvariable=ob_number)
ob_number_entry.grid(row=0, column=1)
ob_number.set('1')

death_options = ttk.LabelFrame(misc_options, text='Death type:')
death_options.grid(row=1, column=0)

death_type = StringVar()
death_type_kill = Radiobutton_save(death_options, text='Kill Unit', takefocus=False, value='kill', variable=death_type, tracevar=death_type, settings='settings.txt', option='death_type')
death_type_kill.grid(row=0, column=0, sticky='W')
death_type_remove = Radiobutton_save(death_options, text='Remove Unit', takefocus=False, value='remove', variable=death_type, tracevar=death_type, settings='settings.txt', option='death_type')
death_type_remove.grid(row=1, column=0, sticky='W')

use_sound = IntVar()
use_sound.set(1)
use_sound_button = ttk.Checkbutton(misc_options, text='Add Sprite Audio', variable=use_sound, onvalue=1, offvalue=0)
use_sound_button.grid(row=2,column=0, sticky='W')



ob_number.trace('w', lambda *args, ob_number=ob_number: change_ob_number(ob_number, generate_btn))

def generate_triggers(text_display, obstacle, ob_number, loc_dict, trigger_player, force_name, DC, death, comment_config, timing, sound_dict, sound_flag):
    triggers = ''
    for n in range(1, obstacle.num_counts + 1):
        units = []
        sprites = []
        recycle_locations = []
        recycle_explosions = {}
        walls = []
        locations = []
        
        for l in range(1, len(loc_dict) + 1):
            loc = loc_dict[l]
            try:
                for explosion in obstacle.explosions[n][loc]:
                    locations.append(loc.label)
                    if explosion[0].sprite:
                        sprites.append((loc.label, explosion[0].name, explosion[0].player))
                    else:
                        units.append((loc.label, explosion[0].name, explosion[0].player))
            except:
                pass
                
            try:
                recycle_locations.append(loc.label)
                recycle_explosions[loc.label] = {}
                recycle_explosions[loc.label]['ID'] = loc.ID
                recycle_explosions[loc.label]['start'] = (loc.x, loc.y)
                recycle_explosions[loc.label]['explosions'] = []
                for coord in sorted(obstacle.recycle_explosions[n][loc].keys(), key=lambda k: [k[1], k[0]]):
                    explosion = obstacle.recycle_explosions[n][loc][coord][0]
                    recycle_explosions[loc.label]['explosions'].append(((coord[0], coord[1]), (explosion[0].name, explosion[0].player, explosion[0].sprite)))
            except:
                pass
        
            try:
                wall = obstacle.walls[n][loc]
                name = wall[1].name
                player = wall[1].player
                walls.append((name, loc.label, player, wall[0]))
            except:
                pass
        d = obstacle.timing[n]
        sounds = []
        if sound_flag == 1:
            sound_count = n + 1
            if sound_count > obstacle.num_counts:
                sound_count = 1
            try:
                for loc in obstacle.explosions[sound_count].keys():
                    for explosion in obstacle.explosions[sound_count][loc]:
                        if explosion[0].sprite:
                            try:
                                sounds.append(sound_dict[explosion[0].name].get())
                            except:
                                pass
            except:
                pass
            try:
                for loc in obstacle.recycle_explosions[sound_count].keys():
                    for coord in obstacle.recycle_explosions[sound_count][loc].keys():
                        for explosion in obstacle.recycle_explosions[sound_count][loc][coord]:
                            if explosion[0].sprite:
                                try:
                                    sounds.append(sound_dict[explosion[0].name].get())
                                except:
                                    pass
            except:
                pass
        count = obgen.count_triggers(ob_num=ob_number,
            count_num=n,
            last_count=(n == obstacle.num_counts),
            locations_used = locations,
            recycle_locations_list = recycle_locations,
            recycle_explosions_list = recycle_explosions,
            trig_owner=trigger_player,
            force=force_name,
            death_counters=DC,
            death_type=death,
            comment_options=comment_config,
            timing_type=timing,
            unit_explosions=units,
            sprite_explosions=sprites,
            use_sound_flag = sound_flag,
            sound_effects=set(sounds),
            wall_actions=walls,
            delay=d)
        for trigger in count:
            triggers += trigger
    text_display.delete(1.0, END)
    text_display.insert(1.0, triggers)

generate_btn = ttk.Button(trig_controls, text='Generate triggers', takefocus=False,
    command=lambda: generate_triggers(trig_text_display, 
    OBSTACLE,
    int(ob_number.get()),
    locations_numerical,
    trigger_owner_player.get(),
    player_force.get(),
    [ob_DC.get(), count_DC.get(), frame_DC.get(), DC_units_player.get()],
    death_type.get(),
    [comment_ob.get(), comment_count.get(), comment_part.get()],
    timing_controls.mode,
    sound_menus_dict,
    use_sound.get()))
    
generate_btn.grid(row=0, column=4, ipady=10, sticky='N')

def press_obstacle_edit_btn(thisUI, otherUIs, d):
    arrange_UIs(thisUI, otherUIs)
    root.bind('<Configure>', lambda event: draw_grid(d, event))

obstacle_edit_btn = ttk.Button(trig_generator, text = 'Obstacle Editor', takefocus=False, command=lambda: press_obstacle_edit_btn([Editor], [[trig_generator]], gridsize))
obstacle_edit_btn.grid(row=2, column=0, sticky = 'WE')

root.bind('<Configure>', lambda event: draw_grid(gridsize, event))

root.mainloop()