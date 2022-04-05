import units
import obgen
import math
import tkinter as tk
import ttkwidgets
from ttkwidgets.autocomplete import AutocompleteCombobox as acc
from tkinter.scrolledtext import ScrolledText
from tkinter import *
from tkinter import ttk, StringVar
from PIL import Image, ImageTk

#the main window
root = tk.Tk()
root.title('Obstacle Studio')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

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
Editor.rowconfigure(0, weight=10)
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

#the display on which terrain, locations, and explosions can be placed
display = tk.Canvas(Editor, bg="black")
display['borderwidth'] = 2
display['relief'] = 'groove'
display.grid(column=0, row=0, sticky='NESW')

#creates the various image layers the display needs
display.create_image(0, 0, anchor='nw', tag='terrain', image=transparent_pixel)
display.create_image(0, 0, anchor='nw', tag='location', image=transparent_pixel)
display.create_image(0, 0, anchor='nw', tag='wall', image=transparent_pixel)
display.create_image(0, 0, anchor='nw', tag='explosion', image=transparent_pixel)
display.create_image(0, 0, anchor='nw', tag='highlight', image=transparent_pixel)
display.create_image(0, 0, anchor='nw', tag='grid', image=transparent_pixel)
display.create_image(0, 0, anchor='nw', tag='locationMouseover', image=transparent_pixel)
display.create_image(0, 0, anchor='nw', tag='locationExtras', image=transparent_pixel)

def mouseover_display(event):
    display.focus_set()
    
display.bind('<Enter>', mouseover_display)

#recreates a layer on the display in case it's deleted
def recreate_layer(layer):
    if len(display.find_withtag(layer)) == 0:
        display.create_image(0, 0, anchor='nw', tag=layer, image=transparent_pixel)

#reorders the layers on the display
def organize_layers():
    display.tag_raise('locationExtras')
    display.tag_lower('grid', 'locationExtras')
    display.tag_lower('locationMouseover', 'grid')
    display.tag_lower('highlight', 'locationMouseover')
    display.tag_lower('explosion', 'highlight')
    display.tag_lower('wall', 'explosion')
    display.tag_lower('location', 'wall')
    display.tag_lower('terrain', 'location')
    
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

#redraws the grid if the window is resized
#def redraw_grid(event, d):
    #draw_grid(d.num)

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
    organize_layers()

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
def press_Terrain_btn(thisUI, otherUIs, hotkey_widgets, unhotkey_widgets, mode_btn, other_mode_btns, canvas, tool, d, w, h, tile_choice, loc_dictionary, event=None):
    highlight_atCursor(d, w, h, 1, None)
    tool.replace(1)
    canvas.bind('<Motion>', lambda event: highlight_atCursor(d, w, h, 1, event))
    d.replace(32)
    canvas.bind('<Button-1>', lambda event: place_terrain(canvas, tile_choice, w, h, event))
    canvas.bind('<B1-Motion>', lambda event: place_terrain(canvas, tile_choice, w, h, event))
    canvas.bind('<Button-3>', lambda event: delete_terrain(canvas, w, h, event))
    canvas.bind('<B3-Motion>', lambda event: delete_terrain(canvas, w, h, event))
    canvas.unbind('<ButtonRelease-1>')
    hide_locations(loc_dictionary)
    hide_obstacle()
    arrange_UIs(thisUI, otherUIs)
    unbind_hotkeys(unhotkey_widgets)
    rebind_hotkeys(hotkey_widgets)
    for btn in other_mode_btns:
        btn.config(state='normal')
    mode_btn.config(state='disabled')
    
def press_Location_btn(thisUI, otherUIs, hotkey_widgets, unhotkey_widgets, mode_btn, other_mode_btns, canvas, tool, gridsize_choice, d, w, h, loc_dictionary, event=None):
    highlight_atCursor(d, w, h, 2, None)
    tool.replace(2)
    d.replace(gridsize_choice)
    canvas.bind('<Motion>', lambda event: highlight_atCursor(d, w, h, 2, event))
    canvas.bind('<ButtonRelease-1>', lambda event: place_location(d, w, h, loc_dictionary, event))
    canvas.bind('<Button-3>', delete_location)
    canvas.bind('<B1-Motion>', lambda event: move_location(d, w, h, loc_dictionary, event))
    canvas.unbind('<B3-Motion>')
    canvas.unbind('<Button-1>')
    show_locations(loc_dictionary)
    hide_obstacle()
    arrange_UIs(thisUI, otherUIs)
    unbind_hotkeys(unhotkey_widgets)
    rebind_hotkeys(hotkey_widgets)
    for btn in other_mode_btns:
        btn.config(state='normal')
    mode_btn.config(state='disabled')


def press_Obstacle_btn(thisUI, otherUIs, hotkey_widgets, unhotkey_widgets, mode_btn, other_mode_btns, canvas, tool, d, w, h, loc_dictionary, ob, count_display, wall_menu, wall_player, event=None):
    tool.replace(3)
    canvas.delete('highlight')
    recreate_layer('highlight')
    canvas.bind('<Motion>', lambda event: highlight_atCursor(d, w, h, 3, event))
    canvas.bind('<Button-1>', lambda event: place_explosion(event, ob))
    canvas.bind('<Button-3>', lambda event: delete_explosion(event, ob))
    canvas.bind('<KeyRelease-w>', lambda event: place_wall(event, ob, wall_menu, wall_player, loc_dictionary))
    canvas.bind('<KeyRelease-r>', lambda event: remove_wall(event, ob, loc_dictionary))
    canvas.unbind('<ButtonRelease-1>')
    canvas.unbind('<B1-Motion>')
    canvas.unbind('<B3-Motion>')
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
                        
Terrain_btn.config(command=lambda: press_Terrain_btn(Terrain_UI, [Location_UI, Obstacle_UI], Terrain_hotkeys, [Location_hotkeys, Obstacle_hotkeys], Terrain_btn, [Location_btn, Obstacle_btn], display, selected_tool, gridsize, W, H, selected_tile, locations_numerical))
Terrain_btn.cmd(lambda event: press_Terrain_btn(Terrain_UI, [Location_UI, Obstacle_UI], Terrain_hotkeys, [Location_hotkeys, Obstacle_hotkeys], Terrain_btn, [Location_btn, Obstacle_btn], display, selected_tool, gridsize, W, H, selected_tile, locations_numerical, event))
Terrain_btn.keybind()
Terrain_btn_tip = tooltip(root, Terrain_btn, '(Alt+T)', (20,10))
Terrain_btn.grid(row=0, column=0)

Location_btn.config(command=lambda: press_Location_btn(Location_UI, [Terrain_UI, Obstacle_UI], Location_hotkeys,  [Terrain_hotkeys, Obstacle_hotkeys], Location_btn, [Terrain_btn, Obstacle_btn], display, selected_tool, int(gridsize_changed.get()), gridsize, W, H, locations_numerical))
Location_btn.cmd(lambda event: press_Location_btn(Location_UI, [Terrain_UI, Obstacle_UI], Location_hotkeys, [Terrain_hotkeys, Obstacle_hotkeys], Location_btn, [Terrain_btn, Obstacle_btn], display, selected_tool, int(gridsize_changed.get()), gridsize, W, H, locations_numerical, event))
Location_btn.keybind()
Location_btn_tip = tooltip(root, Location_btn, '(Alt+L)', (20,10))
Location_btn.grid(row=1, column=0)

Obstacle_btn.config(command=lambda: press_Obstacle_btn(Obstacle_UI, [Terrain_UI, Location_UI], Obstacle_hotkeys, [Terrain_hotkeys, Location_hotkeys], Obstacle_btn, [Location_btn, Terrain_btn], display, selected_tool, gridsize, W, H, locations_numerical, OBSTACLE, count_display, wall_units_menu, selected_wall_player))
Obstacle_btn.cmd(lambda event: press_Obstacle_btn(Obstacle_UI, [Terrain_UI, Location_UI], Obstacle_hotkeys, [Terrain_hotkeys, Location_hotkeys], Obstacle_btn, [Location_btn, Terrain_btn], display, selected_tool, gridsize, W, H, locations_numerical, OBSTACLE, count_display, wall_units_menu, selected_wall_player, event))
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

delete_terrain_btn = hotkey_ttkBtn(toolkit, window=root, hotkey='<BackSpace>', text='Delete all terrain', takefocus=False, callback=lambda event: delete_all_terrain(display, terrain, event), command=lambda: delete_all_terrain(display, terrain))
delete_terrain_tip = tooltip(root, delete_terrain_btn, '(BackSpace)', (20, 10))
delete_terrain_btn.grid(row=1, column=0)

terrain = {} #hashes coordinates (x,y) to the terrain tile whose top left corner is at (x,y)

#places terrain tiles in the highlighted region when the left mouse button is pressed
def place_terrain(canvas, tile_choice, w, h, event):
    width = w.num
    height = h.num
    if tile_choice.num >= 0:
        for i in range(0,width):
            for j in range(0,height):
                (a,b) = (snap(32, width, height)[0] + 32*i, snap(32, width, height)[1] + 32*j)
                try:
                    canvas.delete(terrain[(a,b)])
                    del terrain[(a,b)]
                except:
                    pass
                T = canvas.create_image(a, b, anchor='nw', tag='terrain', image=tileimages[tile_choice.num])
                terrain[(a,b)] = T
    highlight_atCursor(data_number(32), w, h, 1, None)
    canvas.tag_lower('terrain', 'location')

#deletes terrain tiles in the highlighted region when the right mouse button is pressed
def delete_all_terrain(canvas, tileMap, event=None):
    for tile in list(tileMap.keys()):
        canvas.delete(tileMap[tile])
        del tileMap[tile]

def delete_terrain(canvas, w, h, event):
    width = w.num
    height = h.num
    highlight_atCursor(data_number(32), w, h, 1, None)
    for i in range(0, width):
        for j in range(0, height):
            (a,b) = (snap(32, width, height)[0] + 32*i, snap(32, width, height)[1] + 32*j)
            try:
                canvas.delete(terrain[(a,b)])
                del terrain[(a,b)]
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
loc_count = 0 #tracks the number of locations currently placed


def delete_all_locations(loc_dict, number, event=None):
    while number > 0:
        loc_dict[number].delete()
        number -= 1
        
def rename_locations(rename_locations):
    for i in range(1, loc_count + 1):
        locations_numerical[i].write_name()
        
def resize_grid(d, gridsize_changed):
    new_d = int(gridsize_changed.get())
    d.replace(new_d)
    draw_grid(d, event=None)

#Location Mode UI
location_naming_options = ttk.LabelFrame(toolkit, text='Naming convention:')
location_naming_options.grid(row=0, column=0, sticky = 'NW')

location_prefix = StringVar()
location_prefix.trace('w', lambda name, index, mode, location_prefix=location_prefix: rename_locations(location_prefix))
location_prefix_entry = ttk.Entry(location_naming_options, textvariable=location_prefix)
location_prefix_entry.grid(row=0, column=0)

naming_convention = StringVar()
naming_convention.trace('w', lambda name, index, mode, naming_convention=naming_convention: rename_locations(naming_convention))
naming_conventions = ('Numeric (no leading 0\'s)', 'Numeric (leading 0\'s)', 'Alphabetic (A,B,C,...)')
naming_conventions_menu = ttk.OptionMenu(location_naming_options, naming_convention, naming_conventions[0], naming_conventions[0], naming_conventions[1], naming_conventions[2])
naming_conventions_menu.grid(row=1, column=0)

delete_locations_btn = hotkey_ttkBtn(toolkit, text='Delete all locations', takefocus=False, window=root, hotkey='<BackSpace>', callback=lambda event: delete_all_locations(locations_numerical, loc_count, event), command=lambda: delete_all_locations(locations_numerical, loc_count))
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
        self.borders.append(display.create_line((self.x, self.y), (self.x + 32*self.width, self.y), tag='locationExtras', fill='#20ff26'))
        self.borders.append(display.create_line((self.x + 32*self.width, self.y), (self.x + 32*self.width, self.y + 32*self.height), tag='locationExtras', fill='#20ff26'))
        self.borders.append(display.create_line((self.x, self.y + 32*self.height), (self.x + 32*self.width, self.y + 32*self.height), tag='locationExtras', fill='#20ff26'))
        self.borders.append(display.create_line((self.x, self.y), (self.x, self.y + 32*self.height), tag='locationExtras', fill='#20ff26'))
        self.top = self.borders[0]
        self.right = self.borders[1]
        self.bottom = self.borders[2]
        self.left = self.borders[3]
        
        self.highlighted = False
        self.motion = False
        
        self.explosions = {}
        self.walls = {}
        
    def write_name(self):
        try:
            display.delete(self.name)
        except:
            pass
        numbering = ''
        if naming_convention.get() == naming_conventions[0]:
            numbering = str(self.number)
        elif naming_convention.get() == naming_conventions[1]:
            numbering = '0'*(len(str(loc_count)) - len(str(self.number))) + str(self.number)
        elif naming_convention.get() == naming_conventions[2]:
            alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            if loc_count <= 26:
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
        if self.x < x < self.x + 32*self.width and self.y < y < self.y + 32*self.height:
            return True;
        else:
            return False
            
    def mouseover_highlight(self):
        if not self.highlighted:
            self.highlighted = True
            try:
                display.delete(self.overlay)
            except:
                pass
            self.mouseover_overlay = display.create_image(self.x, self.y, anchor='nw', tag='locationMouseover', image=location_mouseover_overlays[(self.width,self.height)])
            organize_layers()
            
    def unmouseover(self):
        if self.highlighted:
            self.highlighted = False
            try:
                display.delete(self.mouseover_overlay)
            except:
                pass
            self.overlay = display.create_image(self.x, self.y, anchor='nw', tag='location', image=location_overlays[(self.width,self.height)])
            organize_layers()
            
    def delete(self):
        global loc_count, locations_numerical
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
        del locations_numerical[self.number]
        for i in range(self.number + 1, loc_count + 1):
            loc = locations_numerical[i]
            loc.number -= 1
            loc.write_name()
            locations_numerical[loc.number] = loc
        loc_count -= 1
        
    def delete_onClick(self):
        if mouseover(self):
            self.delete()
            
    def move(self, d):
        x = snap(d, self.width, self.height)[0]
        y = snap(d, self.width, self.height)[1]
        self.motion = True
        display.delete('highlight')
        display.coords(self.mouseover_overlay, x, y)
        display.coords(self.name, x + 2, y + 2)
        display.coords(self.top, x, y, x + 32*self.width, y)
        display.coords(self.right, x + 32*self.width, y, x + 32*self.width, y + 32*self.height)
        display.coords(self.bottom, x, y + 32*self.height, x + 32*self.width, y + 32*self.height)
        display.coords(self.left, x, y, x, y + 32*self.height)
        for count in self.explosions.keys():
            for explosion in self.explosions[count]:
                display.coords(explosion[1], x + 16*self.width, y + 16*self.width)
        self.x = x
        self.y = y
        self.topleft_corner = (x,y)
        recreate_layer('highlight')
        organize_layers()
            
    def place_explosion(self, explosion, count):
        self.explosions[count] = self.explosions.get(count, []) + [(explosion, display.create_image(self.x + 16*self.width, self.y + 16*self.height, anchor='center', tag='explosion', image=explosion.img))]
        organize_layers()
        
    def delete_explosion(self, count):
        display.delete(self.explosions[count][-1][1])
        self.explosions[count].pop(-1)
        if self.explosions[count] == []:
            del self.explosions[count]
            
    def edit_wall(self, wall, count, action):
        if action == 'c':
            img = display.create_image(self.x + 16*self.width, self.y + 16*self.height, anchor='center', tag='wall', image=wall.img)
        if action == 'r':
            img = 0
        self.walls[count] = (wall, img, action)
        organize_layers()
        
    def delete_wall(self, count):
        display.delete(self.walls[count][-1][1])
        self.walls[count].pop(-1)
        if self.walls[count] == []:
            del self.walls[count]
            
    def search_walls(self, count, num_counts):
        i = count
        wall = False
        while i > 0:
            try:
                if self.walls[i][2] == 'c':
                    wall = self.walls[i]
                    break
            except:
                pass
            i -= 1
        if i > 0:
            flag = True
            for j in range(i+1, count+1):
                try:
                    if self.walls[j][2] == 'r':
                        display.itemconfigure(wall[1], state='hidden')
                        flag = False
                        break
                except:
                    pass
            if flag:
                display.itemconfigure(wall[1], state='normal')
        else:
            i = count + 1
            while i <= num_counts:
                try:
                    if self.walls[i][2] == 'c':
                        wall = self.walls[i]
                        break
                except:
                    pass
                i += 1
            if i <= num_counts:
                flag = True
                for j in range(1, count):
                    try:
                        if self.walls[j][2] == 'r':
                            display.itemconfigure(wall[1], state='hidden')
                            flag = False
                            break
                    except:
                        pass
                if flag:
                    display.itemconfigure(wall[1], state='normal')
            
def move_location(d, w, h, loc_dictionary, event):
    highlight_atCursor(d, w, h, 2, event=None)
    n = loc_count
    while n > 0:
        loc = loc_dictionary[n]
        if loc.highlighted:
            break
        else:
            n -= 1
    if n > 0:
        loc.move(d.num)
            
def show_locations(dictionary):
    for loc in dictionary.values():
        for item in (loc.top, loc.right, loc.bottom, loc.left, loc.name, loc.overlay, loc.mouseover_overlay):
            display.itemconfigure(item, state='normal') 
        try:
            display.itemconfigure(loc.overlay, state='normal')
        except:
            pass
        try:
            display.itemconfigure(loc.mouseover_overlay, state='normal')
        except:
            pass
            
def hide_locations(dictionary):
    for loc in dictionary.values():
        for item in (loc.top, loc.right, loc.bottom, loc.left, loc.name, loc.overlay, loc.mouseover_overlay):
            display.itemconfigure(item, state='hidden')
        try:
            display.itemconfigure(loc.overlay, state='hidden')
        except:
            pass
        try:
            display.itemconfigure(loc.mouseover_overlay, state='hidden')
        except:
            pass


#highlights (in green) the top location underneath the mouse cursor           
def highlight_location(dictionary, number):
    num = -1
    for n in range(1, number + 1):
        loc = dictionary[n]
        try:
            if loc.motion:
                num = loc.number
            else:
                loc.unmouseover()
        except:
            pass
    for n in reversed(range(1, number + 1)):
        loc = dictionary[n]
        if loc.mouseover() and num in (-1, loc.number):
            loc.mouseover_highlight()
            break
            
def open_text_window(string):
    text_window = tk.Toplevel(root)
    message = ttk.Label(text_window, text=string)
    message.pack()

#places a location of size w*h tiles at the highlighted region when the left mouse button is clicked
def place_location(d, w, h, loc_dict, event):

    #checks if the user is currently moving a location. if so, a new location will not be placed
    flag = False
    for n in loc_dict.keys():
        if loc_dict[n].motion:
            flag = True
            
    if not flag:
        width = w.num
        height = h.num
        global loc_count
        x = snap(d.num, width, height)[0]
        y = snap(d.num, width, height)[1]
        if loc_count < 255 and ((x,y),(width,height)):
            loc_count += 1
            loc = Location((x,y), (width, height), loc_count)
            loc.write_name()
            locations_numerical[loc_count] = loc
            
            #renames the locations after placing the 10th or 100th location if using the leading 0's convention
            if naming_convention.get() == naming_conventions[1] and loc_count in (10,100):
                rename_locations('')
            
            #renames the locations after placing the 27th location if using the alphabetic convention
            if naming_convention.get() == naming_conventions[2] and loc_count == 27:
                rename_locations('')
            
            elif loc_count == 255:
                open_text_window('You have reached the 255 location limit.')
                
    for n in loc_dict.keys():
        loc_dict[n].motion = False
    highlight_atCursor(d, w, h, 2, None)
    display.tag_lower('location', 'explosion')
                    
def delete_location(event):
    global loc_count, locations_numerical
    for n in reversed(range(1, loc_count + 1)):
        if locations_numerical[n].mouseover():
            locations_numerical[n].delete()
            #renames the locations after placing the 10th or 100th location if using the leading 0's convention
            if naming_convention.get() == naming_conventions[1] and loc_count in (9,999):
                rename_locations('')
            
            #renames the locations after placing the 27th location if using the alphabetic convention
            if naming_convention.get() == naming_conventions[2] and loc_count == 26:
                rename_locations('')
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
wall_controls.grid(row=0, column=0, sticky='N')
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
        
class Obstacle:
    def __init__(self, canvas, count_display, timing_UI):
        self.walls = {}
        self.locs = {1: []}
        self.timing = {1: 1}
        self.num_counts = 1
        self.count = 1
        self.canvas = canvas
        self.count_display = count_display
        self.timing_UI = timing_UI
       
    def hide_count(self):
        try:
            for loc in self.locs[self.count]:
                for explosion in loc.explosions[self.count]:
                    display.itemconfigure(explosion[1], state='hidden')
        except:
            pass
        
    def show_count(self, delay):
        try:
            for loc in self.locs[self.count]:
                for explosion in loc.explosions[self.count]:
                    self.canvas.itemconfigure(explosion[1], state='normal')
        except:
            pass
        self.timing_UI.set_delay(self, delay)
        self.count_display.configure(text='Count #' + str(self.count))
        try:
            for item in self.walls[self.count]:
                item[0].search_walls(self.count, self.num_counts)
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
            
def place_wall(event, ob, wall_menu, player, loc_dict):
    n = loc_count
    while n > 0:
        loc = loc_dict[n]
        if loc.highlighted:
            name = wall_menu.get()
            if name != '':
                ob.walls[ob.count] = ob.walls.get(ob.count, []) + [(loc, 'c')]
                wall = Wall(name, player.get())
                loc.edit_wall(wall, ob.count, 'c')
            break
        else:
            n -= 1
                
def remove_wall(event, ob, loc_dict):
    n = loc_count
    while n > 0:
        loc = loc_dict[n]
        if loc.highlighted:
            flag = False
            for i in range(1, ob.count):
                try:
                    for item in ob.walls[i]:
                        L = item[0]
                        if L == loc:
                            if item[1] == 'c':
                                wall = L.walls[i][0]
                                flag = True
                            else:
                                flag = False
                except:
                    pass
            if flag:
                ob.walls[ob.count] = ob.walls.get(ob.count, []) + [(loc, 'r')]
                loc.edit_wall(wall, ob.count, 'r')
                loc.search_walls(ob.count, ob.num_counts)
            break
        else:
            n -= 1

def place_explosion(event, ob):
    n = loc_count
    while n > 0:
        loc = locations_numerical[n]
        if loc.highlighted:
            for menu in explosion_menus:
                name = menu.menu.get()
                if name != '':
                    if name == 'Spider Mine':
                        name = 'Vulture ' + name
                    elif name != 'Infested Terran':
                        name = menu.prefix + name
                    explosion = Explosion(name, selected_player.get(), menu.sprite)
                    flag = False
                    try:
                        for EXPLOSION in loc.explosions[ob.count]:
                            if EXPLOSION[0].name == explosion.name:
                                flag = True
                                print(2)
                    except:
                        pass
                    if not flag:
                        loc.place_explosion(explosion, ob.count)
                        flag = False
                        try:
                            if loc in ob.locs[ob.count]:
                                flag = True
                        except:
                            pass
                        if not flag:
                            ob.locs[ob.count] = ob.locs.get(ob.count, []) + [loc]
                        ob.timing[ob.count] = current_delay.get()
            break
        else:
            n -= 1
            
def delete_explosion(event, ob):
    n = loc_count
    while n > 0:
        loc = locations_numerical[n]
        if loc.highlighted:
            try:
                loc.delete_explosion(ob.count)
                if ob.count not in loc.explosions.keys():
                    ob.locs[ob.count].remove(loc)
            except:
                pass
            break
        else:
            n -= 1

def hide_obstacle():
    display.itemconfigure('explosion', state='hidden')
    
def show_obstacle(canvas, ob):
    for loc in ob.locs[ob.count]:
        for explosion in loc.explosions[ob.count]:
            canvas.itemconfigure(explosion[1], state='normal')
            

explosion_selection = ttk.LabelFrame(toolkit, text='Explosions:')
explosion_selection.grid(row=0, column=1)

selected_unit = {}
image_index = 0


class explosion_menu(ttk.LabelFrame):
    def choose():
        global selected_unit
        if self.selection.get() != '':
            selected_unit = self.prefix + self.selection.get()
        
    def __init__(self, *args, options=[], prefix='', sprite=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = options
        self.prefix = prefix
        self.sprite = sprite
        self.selection = StringVar()
        self.menu = acc(self, textvariable=self.selection, completevalues = self.options)
        self.menu.grid(row=0, column=0)
        
def reset_unit_selections(variables):
    for var in variables:
        if var.get() != '':
            var.set('')

unit_selection = ttk.LabelFrame(explosion_selection, text='Units:')
unit_selection.grid(row=0,column=0, sticky='N')

terran_unit_selection = explosion_menu(unit_selection, options=terran_units, prefix='Terran ', text='Terran')
terran_unit_selection.grid(row=0, column=0)

zerg_unit_selection = explosion_menu(unit_selection, options=zerg_units, prefix='Zerg ', text='Zerg')
zerg_unit_selection.grid(row=1, column=0)

protoss_unit_selection = explosion_menu(unit_selection, options=protoss_units, prefix='Protoss ', text='Protoss')
protoss_unit_selection.grid(row=2, column=0)

other_unit_selection = explosion_menu(unit_selection, options=other_units, text='Other')
other_unit_selection.grid(row=3, column=0)


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

spell_sprite_selection = explosion_menu(sprite_selection, options=spell_sprites, sprite=True, text='Spells')
spell_sprite_selection.grid(row=0, column=0)

attack_sprite_selection = explosion_menu(sprite_selection, options=attack_sprites, sprite=True, text='Attacks')
attack_sprite_selection.grid(row=1, column=0)

unit_sprite_selection = explosion_menu(sprite_selection, options=unit_sprites, sprite=True, text='Units')
unit_sprite_selection.grid(row=2, column=0)

other_sprite_selection = explosion_menu(sprite_selection, options=other_sprites, sprite=True, text='Other')
other_sprite_selection.grid(row=3, column=0)


explosion_menus = [terran_unit_selection, zerg_unit_selection, protoss_unit_selection, other_unit_selection, spell_sprite_selection, attack_sprite_selection, unit_sprite_selection, other_sprite_selection]


def reset_selections(menus, i, j):
    for index in range(i,j+1):
        menus[index].selection.set('')

unit_reset_btn = ttk.Button(unit_selection, text='Reset', command=lambda: reset_selections(explosion_menus, 0, 3))
unit_reset_btn.grid(row=4, column=0)

sprite_reset_btn = ttk.Button(sprite_selection, text='Reset', command=lambda: reset_selections(explosion_menus, 4, 7))
sprite_reset_btn.grid(row=4, column=0)


player_options = ttk.LabelFrame(explosion_selection, text='Player:')
player_options.grid(row=1, column=0, columnspan=2, sticky='N')

selected_player = StringVar()
player_number_menu = acc_save(player_options, completevalues=players, textvariable=selected_player, tracevar=selected_player, settings='settings.txt', option='explosion_player')
selected_player.trace('w', lambda *args, selected_player=selected_player: player_number_menu.save())
player_number_menu.grid(row=0, column=0)



obstacle_controls = ttk.Frame(toolkit, style='gray.TFrame')
obstacle_controls.grid(row=0, column=2, sticky='N')


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
        #window.bind(hotkey, self.press)
        
    def next_count(self):
        new_count = {'_': 1, '-': max(1, self.ob.count - 1), ']': self.ob.count, '=': self.ob.count + 1, '+': self.ob.num_counts, '[': max(1,min(self.ob.count, self.ob.num_counts - 1))}
        return new_count[self.hotkey]
    
    def press(self, event=None):
        self.ob.hide_count()
        if self.hotkey == ']':
            for num in self.loc_dict.keys():
                loc = self.loc_dict[num]
                loc.explosions = dict_shift(loc.explosions, self.ob.count, self.ob.num_counts, None)
            self.ob.locs = dict_shift(self.ob.locs, self.ob.count, self.ob.num_counts, [])
            self.ob.timing = dict_shift(self.ob.timing, self.ob.count, self.ob.num_counts, self.delay)
        if self.hotkey == '[':
            self.ob.locs = dict_delete(self.ob.locs, self.ob.count, self.ob.num_counts)
            self.ob.timing = dict_delete(self.ob.timing, self.ob.count, self.ob.num_counts)
            for num in self.loc_dict.keys():
                loc = self.loc_dict[num]
                loc.explosions = dict_delete(loc.explosions, self.ob.count, self.ob.num_counts)
        self.ob.count = self.next_count()
        flag = False
        if self.ob.count <= self.ob.num_counts:
            flag = True
        if self.hotkey == ']' or self.ob.count > self.ob.num_counts:
            self.ob.num_counts += 1
        elif self.hotkey == '[':
            self.ob.num_counts = max(1, self.ob.num_counts - 1)
        if flag:
            self.delay = self.ob.timing[self.ob.count]
        self.ob.show_count(self.delay)

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

first_count_btn = count_btn(count_controls, win=root, key='_', cb=None, ob=OBSTACLE, delay=timing_controls.delay.get(), loc_dict=locations_numerical, tooltip_text='First Count (_)', text='<<', width=3)
first_count_btn.cmd(first_count_btn.press)
first_count_btn.grid(row=1, column=0)

prev_count_btn = count_btn(count_controls, win=root, key='-', cb=None, ob=OBSTACLE, delay=timing_controls.delay.get(), loc_dict=locations_numerical, tooltip_text='Previous Count (-)', text='<', width=3)
prev_count_btn.cmd(prev_count_btn.press)
prev_count_btn.grid(row=1, column=1)

insert_count_btn = count_btn(count_controls, win=root, key=']', cb=None, ob=OBSTACLE, delay=timing_controls.delay.get(), loc_dict=locations_numerical, tooltip_text='Insert Count (])', text='*', width=2)
insert_count_btn.cmd(insert_count_btn.press)
insert_count_btn.grid(row=1, column=2)

next_count_btn = count_btn(count_controls, win=root, key='=', cb=None, ob=OBSTACLE, delay=timing_controls.delay.get(), loc_dict=locations_numerical, tooltip_text='Next Count (=)', text='>', width=3)
next_count_btn.cmd(next_count_btn.press)
next_count_btn.grid(row=1, column=3)

last_count_btn = count_btn(count_controls, win=root, key='+', cb=None, ob=OBSTACLE, delay=timing_controls.delay.get(), loc_dict=locations_numerical, tooltip_text='Last Count (+)', text='>>', width=3)
last_count_btn.cmd(last_count_btn.press)
last_count_btn.grid(row=1, column=4)

play_btn = ttk.Button(count_controls, text='Play', width=4) #button to animate the counts in sequence
play_btn.grid(row=2, column=2)

delete_count_btn = count_btn(count_controls, win=root, key='[', cb=None, ob=OBSTACLE, delay=timing_controls.delay.get(),loc_dict=locations_numerical, tooltip_text='Delete Count ([)', text='Delete', width=6)
delete_count_btn.cmd(delete_count_btn.press)
delete_count_btn.grid(row=2, column=3, columnspan = 2)
###################################################################################################################################################################################################################################################

Obstacle_UI = []
Obstacle_UI.append(explosion_selection)
Obstacle_UI.append(obstacle_controls)
Obstacle_UI.append(wall_controls)
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





ob_number.trace('w', lambda *args, ob_number=ob_number: change_ob_number(ob_number, generate_btn))

def generate_triggers(text_display, obstacle, ob_number, trigger_player, force_name, DC, death, comment_config, timing):
    triggers = ''
    for n in range(1, obstacle.num_counts + 1):
        units = []
        sprites = []
        walls = []
        for loc in obstacle.locs[n]:
            for explosion in loc.explosions[n]:
                if explosion[0].sprite:
                    sprites.append((loc.label, explosion[0].name, explosion[0].player))
                else:
                    units.append((loc.label, explosion[0].name, explosion[0].player))
        try:
            for wall in obstacle.walls[n]:
                name = wall[0].walls[n][0].name
                player = wall[0].walls[n][0].player
                loc = wall[0].label
                walls.append((name, loc, player, wall[1]))
        except:
            pass
        d = obstacle.timing[n]
        count = obgen.count_triggers(ob_num=ob_number, count_num=n, last_count=(n == obstacle.num_counts), trig_owner=trigger_player, force=force_name, death_counters=DC, death_type=death, comment_options=comment_config, timing_type=timing, unit_explosions=units, sprite_explosions=sprites, wall_actions=walls, delay=d)
        for trigger in count:
            triggers += trigger
    text_display.delete(1.0, END)
    text_display.insert(1.0, triggers)

generate_btn = ttk.Button(trig_controls, text='Generate triggers', takefocus=False, command=lambda: generate_triggers(trig_text_display, 
    OBSTACLE,
    int(ob_number.get()),
    trigger_owner_player.get(),
    player_force.get(),
    [ob_DC.get(), count_DC.get(), frame_DC.get(), DC_units_player.get()],
    death_type.get(),
    [comment_ob.get(), comment_count.get(), comment_part.get()],
    timing_controls.mode))
    
generate_btn.grid(row=0, column=4, ipady=10, sticky='N')

def press_obstacle_edit_btn(thisUI, otherUIs, d):
    arrange_UIs(thisUI, otherUIs)
    root.bind('<Configure>', lambda event: draw_grid(d, event))

obstacle_edit_btn = ttk.Button(trig_generator, text = 'Obstacle Editor', takefocus=False, command=lambda: press_obstacle_edit_btn([Editor], [[trig_generator]], gridsize))
obstacle_edit_btn.grid(row=2, column=0, sticky = 'WE')

root.bind('<Configure>', lambda event: draw_grid(gridsize, event))

root.mainloop()