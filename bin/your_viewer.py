from your import Your
from tkinter import *
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import ndimage
from scipy import misc
import numpy as np
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
        self.gulp_size = 100

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

    def nice_print(self, dic):
        
        for key, item in dic.items():
            print(f"{key : >27}:\t{item}")
        
    def get_header(self):
        
        dic = vars(self.yr.your_header)
        dic['tsamp'] = self.yr.your_header.tsamp
        dic['nchans'] = self.yr.your_header.nchans
        dic['foff'] = self.yr.your_header.foff
        dic['nspectra'] = self.yr.your_header.nspectra
        self.nice_print(dic)
            
    canvas=''
    def load_file(self, f):
        
#         file_name = filedialog.askopenfilename(filetypes = (("fits/fil files", "*.fil *.fits")
#                                                              ,("All files", "*.*") ))
        file_name = f
        self.master.title(file_name)
        self.yr = Your(file_name)
        gulp = self.yr.get_data(self.start_samp, self.gulp_size)         
        self.get_header()          
                  
        self.image = gulp #misc.imread(filename)
        self.image = ndimage.rotate(self.image, -90)
        fig, ax = plt.subplots(1,1,figsize=(10,7))
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('Frequency [MHz]')
        #axs = self.im.axes
        #ax.set_xlabel()
        ax.set_yticks(np.linspace(0,self.yr.your_header.nchans,8))
        #yticks = [str(int(j)) for j in np.linspace(self.yr.your_header.nchans, 0,8)]
        yticks = [str(int(j)) for j in np.linspace(self.yr.chan_freqs[0],self.yr.chan_freqs[-1],8)]
        ax.set_yticklabels(yticks)
        
        xticks =  np.linspace(self.start_samp,self.start_samp+self.gulp_size,8)
        ax.set_xticks(xticks)
        ax.set_xticklabels([f"{j:.2f}" for j in xticks*self.yr.tsamp])
        
        self.im = plt.imshow(self.image, aspect='auto') # later use a.set_data(new_data)
        #ax.set_xticklabels(np.linspace(0,self.yr.your_header.nchans-1,8))
        if self.canvas=='':
            self.im = plt.imshow(self.image, aspect='auto') # later use a.set_data(new_data)
            plt.colorbar(orientation='vertical')

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
        self.start_samp += self.gulp_size
        proposed_end = self.start_samp + self.gulp_size
        #distance_to_end = self.yr.your_header.nspectra - proposed_end
        if proposed_end > self.yr.your_header.nspectra:
            self.start_samp  = self.start_samp - (proposed_end - self.yr.your_header.nspectra)
            print('End of file.')
        gulp = self.yr.get_data(self.start_samp, self.gulp_size)
        
        self.image = gulp
        self.image = ndimage.rotate(self.image, -90)
        self.im.set_data(gulp)
        
        axs = self.im.axes
        xticks = axs.get_xticks()
        xtick_labels = (xticks + self.start_samp)*self.yr.tsamp
        axs.set_xticklabels([f"{j:.2f}" for j in xtick_labels])

        self.im.set_data(self.image)
        self.canvas.draw()    

    def prev_gulp(self):
        if (self.start_samp - self.gulp_size) >= 0:
            self.start_samp -= self.gulp_size
        gulp = self.yr.get_data(self.start_samp, self.gulp_size)
        self.image = gulp
        self.image = ndimage.rotate(self.image, -90)
        self.im.set_data(gulp)
        
        axs = self.im.axes
        xticks = axs.get_xticks()
        xtick_labels = (xticks + self.start_samp)*self.yr.tsamp
        axs.set_xticklabels([f"{j:.2f}" for j in xtick_labels])
        
        self.im.set_data(self.image)
        self.canvas.draw()    

    
# root window created. Here, that would be the only window, but
# you can later have windows within windows.
root = Tk()

root.geometry("1920x1080")

#creation of an instance
app = Paint(root)
f = '../tests/data/28.fil'
app.load_file(f)

#mainloop
root.mainloop()

