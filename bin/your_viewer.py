from your import Your
from tkinter import *
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import ndimage
from scipy import misc
from matplotlib.figure import Figure

#based on https://steemit.com/utopian-io/@hadif66/tutorial-embeding-scipy-matplotlib-with-tkinter-to-work-on-images-in-a-gui-framework

class Paint(Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None):

        # parameters that you want to send through the Frame class.
        Frame.__init__(self, master)

        #reference to the master widget, which is the tk window
        self.master = master

        #with that, we want to then run init_window, which doesn't yet exist
        self.init_paint()

    #Creation of init_window
    def init_paint(self):

        # changing the title of our master widget
        self.master.title("your_viewer")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH)#, expand=1)
        self.create_widgets()
        # creating a menu instance
        menu = Menu(self.master)
        self.master.config(menu=menu)

        # create the file object)
        file = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        file.add_command(label="Exit", command=self.client_exit)

        #added "file" to our menu
        menu.add_cascade(label="File", menu=file)
        self.start_samp = 0 
        self.gulp = 4096

    def create_widgets(self):
            self.browse = Button(self)
            self.browse["text"] = "Browse file"
            self.browse["command"] = self.load_file
            self.browse.grid(row=0, column=0)

            self.next = Button(self)
            self.next["text"] = "Next Gulp"
            self.next["command"] = self.next_gulp
            self.next.grid(row=0, column=1)
            
            self.prev = Button(self)
            self.prev["text"] = "Prevous Gulp"
            self.prev["command"] = self.prev_gulp
            self.prev.grid(row=0, column=3)


    canvas=''
    def load_file(self):
        print("In load file")
        file_name = filedialog.askopenfilename(filetypes = (("fits/fil files", "*.fil *.fits")
                                                             ,("All files", "*.*") ))

        self.yr = Your(file_name)
        gulp = self.yr.get_data(self.start_samp, self.gulp)         
                  
                  
        self.image = gulp #misc.imread(filename)
        self.image = ndimage.rotate(self.image, -90)
        #print(type(misc.imread(filename)))
        fig = plt.figure(figsize=(10,7))
        plt.xlabel('Sample')
        plt.ylabel('Channel')
        if self.canvas=='':
            self.im = plt.imshow(self.image, aspect='auto') # later use a.set_data(new_data)
            plt.colorbar(orientation='vertical')
            axs = plt.gca()
            #axs.set_xticklabels([])
            #axs.set_yticklabels([])

            # a tk.DrawingArea
            self.canvas = FigureCanvasTkAgg(fig, master=root)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        else:
            self.im.set_data(self.image)
            self.canvas.draw()

    def client_exit(self):
        exit()

    def next_gulp(self):
        print("In next gulp")
        self.start_samp += self.gulp
        gulp = self.yr.get_data(self.start_samp, self.gulp)
        self.image = gulp
        self.image = ndimage.rotate(self.image, -90)
        self.im.set_data(gulp)
        
        self.im.set_data(self.image)
        self.canvas.draw()    

    def prev_gulp(self):
        print("In next gulp")
        self.start_samp -= self.gulp
        gulp = self.yr.get_data(self.start_samp, self.gulp)
        self.image = gulp
        self.image = ndimage.rotate(self.image, -90)
        self.im.set_data(gulp)
        
        self.im.set_data(self.image)
        self.canvas.draw()    
        
# root window created. Here, that would be the only window, but
# you can later have windows within windows.
root = Tk()

root.geometry("1920x1080")

#creation of an instance
app = Paint(root)


#mainloop
root.mainloop()
