import tkinter as tk
from patterns import patterns

class CustomText(tk.Text):
    '''A text widget with a new method, highlight_pattern()

    example:

    text = CustomText()
    text.tag_configure("red", foreground="#ff0000")
    text.highlight_pattern("this should be red", "red")

    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    '''
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
            if index == "": break
            if count.get() == 0: break # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")


def find_neighbors(x,y,board):
    # Return a list of all of a cells neighbors
    try:
        left_upper = board[y-1][x-1]
    except: left_upper = False
    try:
        left_mid = board[y][x-1]
    except: left_mid = False
    try:
        left_lower = board[y+1][x-1]
    except: left_lower = False
    try:
        right_upper = board[y-1][x+1]
    except: right_upper = False
    try:
        right_mid = board[y][x+1]
    except: right_mid = False
    try:
        right_lower = board[y+1][x+1]
    except: right_lower = False
    try:
        lower = board[y+1][x]
    except: lower = False
    try:
        upper = board[y-1][x]
    except: upper = False

    #print([left_upper,left_mid,left_lower,upper,lower,right_upper,right_mid,right_lower])

    return [left_upper,left_mid,left_lower,upper,lower,right_upper,right_mid,right_lower]
    

def is_living(x,y,board):
    # Rules:
    # Any live cell with fewer than two live neighbours dies, as if by underpopulation.
    # Any live cell with two or three live neighbours lives on to the next generation.
    # Any live cell with more than three live neighbours dies, as if by overpopulation.
    # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
    neighbors = find_neighbors(x,y,board)
    is_alive = board[y][x]

    if is_alive and neighbors.count(True) > 3: return False
    # Any live cell with more than three live neighbours dies, as if by overpopulation.

    if is_alive and neighbors.count(True) < 2: return False
    # Any live cell with fewer than two live neighbours dies, as if by underpopulation.

    if is_alive and neighbors.count(True) in [2,3]: return True
    # Any live cell with two or three live neighbours lives on to the next generation.

    if is_alive == False and neighbors.count(True) == 3: return True
    # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

    else: return False 



def next_generation(board):
    # Get the status of all the cells, but dont change any until we have them all.
    new_board = []

    row_num = 0
    for row in board:
        new_row = []
        cell_num = 0
        for cell in row:
            new_row.append(is_living(cell_num,row_num,board))
            cell_num += 1
        new_board.append(new_row)
        row_num += 1
    return new_board

class MainWindow(tk.Frame):

    def __init__(self,master,board):
        super().__init__(master) # Yes, I know someone is like "use super()!" NO.
        self.master = master
        self.master.board = board
        self.master.title("Conway's Game of Life")
        self.init_window() # Create Widgets
        self.grid()
        

    def init_window(self): # Create the widgets
        self.update_button = tk.Button(self,text="Update",command=self.update_output)
        self.update_button.grid(row=0,column=0,sticky='ew')

        self.next_button = tk.Button(self,text="Next",command=self.next)
        self.next_button.grid(row=0,column=1,sticky='ew')

        ### warp
        self.warp_StringVar = tk.StringVar()
        self.warp_StringVar.set("")
        self.warp_button = tk.Button(self,text="Warp",command = self.warp)
        self.warp_button.grid(row=1,column=2)
        self.warp_label = tk.Label(self,text="Generations to Warp:")
        self.warp_label.grid(row=1,column=0)
        self.warp_entry = tk.Entry(self, textvariable=self.warp_StringVar)
        self.warp_entry.grid(row=1,column=1)
        ### end warp

        ### auto advance
        self.auto_StringVar = tk.StringVar()
        self.delay_StringVar = tk.StringVar()
        self.auto_StringVar.set("")
        self.delay_StringVar.set("100")
        
        self.auto_label = tk.Label(self,text="Generations to Auto-advance:")
        self.auto_label.grid(row=2,column=0)
        self.auto_entry = tk.Entry(self, textvariable=self.auto_StringVar)
        self.auto_entry.grid(row=2,column=1)

        self.auto_delay_label = tk.Label(self,text="Delay:")
        self.auto_delay_label.grid(row=2,column=2)
        self.auto_delay_entry = tk.Entry(self, textvariable=self.delay_StringVar)
        self.auto_delay_entry.grid(row=2,column=3)

        self.auto_button = tk.Button(self,text="Auto",command = self.auto)
        self.auto_button.grid(row=2,column=4)
        ### end auto advance


        self.edit_button = tk.Button(self,text="Edit",command=self.edit)
        self.edit_button.grid(row=0,column=2,sticky='ew')


        ### output box
        self.output_area = CustomText(self,width=60,height=20,wrap="none")
        self.output_area.tag_configure("dead",background="black",foreground="black")
        self.output_area.tag_configure("alive",background="black",foreground="yellow")
        self.vertical_bar = tk.Scrollbar(self,orient="vertical",command=self.output_area.yview)
        self.horizontal_bar = tk.Scrollbar(self,orient="horizontal",command=self.output_area.xview)

        self.output_area.configure(yscrollcommand=self.vertical_bar.set, xscrollcommand=self.horizontal_bar.set)

        self.output_area.grid(row=4,pady=10,padx=10,columnspan=8, sticky="nsew")
        self.vertical_bar.grid(row=4, column=8, sticky="ns")
        self.horizontal_bar.grid(row=5, column=0, columnspan=8, sticky="ew")
        ### end output box



        ### template loading
        self.load_template_label = tk.Label(self,text="Load Template:")
        self.load_template_label.grid(row=3,column=0)

        self.load_template_StringVar = tk.StringVar()
        self.load_template_StringVar.set("")


        self.load_template_menu = tk.OptionMenu(self,self.load_template_StringVar,*[*patterns])
        self.load_template_menu.grid(row=3,column=1)

        self.load_template_button = tk.Button(self,text="Load",command=self.load_template)
        self.load_template_button.grid(row=3,column=2)
        ### end template loading
        
    
    def load_template(self):
        new_board = []
        text = patterns[self.load_template_StringVar.get()]
        text = text.splitlines()
        for row in text:
            new_row = []
            for char in row:
                if char == "O": new_row.append(True)
                else: new_row.append(False)
            new_board.append(new_row)

        self.master.board = new_board
        self.update_output()

       
    def update_output(self):
        output = ''
        for row in self.master.board:
            for loc in row:
                if loc: output += "O"
                else: output += "#"
            output += "\n"

        
        vbar = self.vertical_bar.get()    # Need to get the curren scrollbar position
        hbar = self.horizontal_bar.get()  # so that when this is done the scrollbars remain
                                          # in the same place, otherwise, they reset.
 
        self.output_area.configure(state ='normal')
        self.output_area.delete("1.0",tk.END)
        self.output_area.insert(tk.INSERT, output)

        
        self.output_area.highlight_pattern("#","dead")
        self.output_area.highlight_pattern("O","alive")


        self.output_area.configure(state ='disabled')

        #self.output_area.yview_moveto(vbar[1])
        #self.output_area.xview_moveto(hbar[1]) #ACK NO DOESNT WORK https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/text-methods.html
        #print(hbar,vbar)
        




     
    def next(self):
        self.master.board = next_generation(self.master.board)
        self.update_output()
    
    def warp(self):
        for i in range(int(self.warp_StringVar.get())):
            self.master.board = next_generation(self.master.board)
        self.update_output()

    def auto(self):
        self.next()
        num = int(self.auto_StringVar.get())
        if num >= 0:
            self.auto_StringVar.set(str(num-1))
            self.master.after(int(self.delay_StringVar.get()), self.auto)
            


    def edit(self):
        output = ''
        for row in self.master.board:
            for loc in row:
                if loc: output += "O"
                else: output += "#"
            output += "\n"
        EditWindow(self.master, output)



class EditWindow(tk.Toplevel):
    def __init__(self, master, game):
        super().__init__(master = master) 
        self.title("Edit") 
        self.grid()
        self.game = game
        self.init_window() # Create Widgets
  
    
    def init_window(self):

        self.save_button = tk.Button(self, text="Save",command=self.save)
        self.save_button.grid(row=0)

        self.cancel_button = tk.Button(self, text="Cancel",command=self.destroy)
        self.cancel_button.grid(row=0,column=1)

        self.output_area = tk.Text(self,width=60,height=20,wrap="none")
        self.vertical_bar = tk.Scrollbar(self,orient="vertical",command=self.output_area.yview)
        self.horizontal_bar = tk.Scrollbar(self,orient="horizontal",command=self.output_area.xview)

        self.output_area.configure(yscrollcommand=self.vertical_bar.set, xscrollcommand=self.horizontal_bar.set)

        self.output_area.grid(row=1,pady=10,padx=10,columnspan=8, sticky="nsew")
        self.vertical_bar.grid(row=1, column=8, sticky="ns")
        self.horizontal_bar.grid(row=2, column=0, columnspan=8, sticky="ew")

        MainWindow.update_output(self)
        self.output_area.configure(state ='normal')
    
    def save(self):
        # Save the new board and exit this window
        new_board = []
        text = self.output_area.get("1.0",tk.END)
        text = text.splitlines()
        for row in text:
            new_row = []
            for char in row:
                if char == "O": new_row.append(True)
                else: new_row.append(False)
            new_board.append(new_row)

        self.master.board = new_board
        self.destroy()






if __name__ == "__main__": # as if it would never not be

    
    BOARD_WIDTH = 100
    BOARD_HEIGHT = 40


    row = []
    for i in range(BOARD_WIDTH):
        row.append(False)

    board = []
    for i in range(BOARD_HEIGHT):
        board.append(row)
    
    root = tk.Tk()
    root.geometry('')
    app = MainWindow(root,board)
    app.mainloop()



