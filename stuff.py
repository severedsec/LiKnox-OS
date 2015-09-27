__author__ = 'austin'


import tkinter as tk  # imports the module tkinter with the alias of tk
import tkinter.messagebox  # imports tkinter.messagebox specifically
import time  # imports a module used for calculating time

class Stuff:
    """
    these are comment quotes. when used under a class they create documentation for that class
    """

    def __init__(self):  # this is the init function. it creates the objects for the class and runs when the class is called.
        self.root = tk.Tk()  # instantiates the tk object which is a GUI window
        self.create_widgets(self.root)  # calls the create widgets function (remember this is all that runs on start. it has to call anything else)
        self.root.title('title stuff')  # set window title
        self.root.geometry("300x100")  # size of the main window
        self.root.mainloop()  # executes the main window loop

    def create_widgets(self, root):
        """
        Draws the main window and the majority of GUI widgets
        """

        # Menu bar
        self.the_menu_bar = tk.Menu(self.root)  # creates a menu bar and names it the_menu_bar
        self.root.config(menu=self.the_menu_bar)  # adds the_menu_bar to the screen
        self.top = self.root.winfo_toplevel()
        self.top.rowconfigure(5, weight=1)  # these modify the grid layout used to organize objects on the screen
        self.top.columnconfigure(4, weight=1)
        self.root.rowconfigure(5, weight=1)
        self.root.columnconfigure(4, weight=1)

        # File menu
        self.the_file_menu = tk.Menu(self.the_menu_bar, tearoff=0)  # creates the file button
        self.the_menu_bar.add_cascade(label="File", menu=self.the_file_menu)  # adds the file button to the_menu_bar
        self.the_file_menu.add_command(label="Exit", command=root.quit)  # assigns the command of exit to the file menu

        # Help menu
        self.the_about_menu = tk.Menu(self.the_menu_bar, tearoff=0)
        self.the_menu_bar.add_cascade(label="Help", menu=self.the_about_menu)
        self.the_about_menu.add_command(label="About", command=lambda: tk.messagebox.showinfo  # this causes a messagebox to appear with info
            ("About",
            """
            this is some sample code it adds two numbers together and shows the result
            """))
        # box that shows equation solution
        self.number_label = tk.Label(root, text="0")  # creates a box of text
        self.number_label.grid(row=0, column=2)  # places that box of text at position 0,2 this is top->down left->right
        # box allows entering the first number
        self.number_1_entry = tk.Entry(root, width=10, takefocus=True)  # creates a box for entering numbers
        self.number_1_entry.grid(row=0, column=0, sticky=tk.N)  # places that box at 0,0
        # box allows entering a second number
        self.number_2_entry = tk.Entry(root, width=10, takefocus=True)  # another entry box
        self.number_2_entry.grid(row=0, column=1, sticky=tk.N)
        # button causes math to happen
        self.run_button = tk.Button(root, text="add", command=self.do_math)  # creates a button which when pressed executes a function
        self.run_button.grid(row=0, column=3, sticky=tk.N)

    def do_math(self):
        start_time = time.time()  # assigns the current time to vairiable start_time
        a = float(self.number_1_entry.get())  # assigns the numbers entered into the boxes to variables
        b = int(self.number_2_entry.get())  # the float/int part converts to floating point or integer types
                # try 1.0 + 1 and then try 1 + 1.0 and check the error. ints can only be whole numbers
        c = a + b  # does math and assigns answer to c
        self.number_label.config(text=c)  # puts c as the text in the answer box
        self.root.update_idletasks()  # pushes the new text config to the screen
        end_time = time.time()  # assigns the current time to variable end_time
        print('it took {} seconds to solve this math problem'.format(end_time - start_time))  # good example of text formatting and timing stuff

def main():
    Stuff()  # this instantiates stuff

if __name__ == "__main__":
    main()  # this executes main which in turn executes stuff
