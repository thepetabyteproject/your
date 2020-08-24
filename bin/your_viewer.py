from your import Your
from tkinter import *
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import argparse
import logging
logger = logging.getLogger()
logging_format = '%(asctime)s - %(funcName)s -%(name)s - %(levelname)s - %(message)s'

# based on https://steemit.com/utopian-io/@hadif66/tutorial-embeding-scipy-matplotlib-with-tkinter-to-work-on-images-in-a-gui-framework

class Paint(Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None):

        # parameters that you want to send through the Frame class.
        Frame.__init__(self, master)

        #reference to the master widget, which is the tk window
        self.master = master

        #Creation of init_window
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
    def load_file(self, file_name='', start_samp=0, gulp_size=1024):
        self.start_samp = start_samp
        self.gulp_size = gulp_size
        if len(file_name) == 0: 
            file_name = filedialog.askopenfilename(filetypes = (("fits/fil files", "*.fil *.fits")
                                                                  ,("All files", "*.*") ))
        
        logging.info(f'Reading file {file_name}.')
        self.master.title(file_name)
        self.yr = Your(file_name)
        logging.info(f'Printing Header parameters')
        self.get_header()          
        self.data = self.read_data()
        gs = gridspec.GridSpec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4], wspace=0.02, hspace=0.03)
        ax1 = plt.subplot(gs[0, 0])
        ax2 = plt.subplot(gs[1, 0])
        ax3 = plt.subplot(gs[0, 1])
        ax4 = plt.subplot(gs[1, 1])
        ax3.axis('off')
        ax1.set_xticks([])
        ax4.set_yticks([])

        ax1.set_ylabel('Avg. Arb. Flux')
        ax4.set_xlabel('Avg. Arb. Flux')
        
        self.vmax = np.median(self.data) + 5*np.std(self.data)
        self.vmin = np.min(self.data)        
        self.im_ft = ax2.imshow(self.data, aspect='auto', vmin=self.vmin, vmax=self.vmax) # later use a.set_data(new_data)
        bandpass = np.mean(self.data, axis=1)
        self.im_bandpass, = ax4.plot(bandpass, np.linspace(self.yr.your_header.nchans, 0, len(bandpass)))
        ax4.set_ylim([-1, len(bandpass)+1])
        time_series = np.mean(self.data,axis=0)
        self.im_time,  = ax1.plot(time_series)
        ax1.set_xlim(-1, len(time_series+1))
        #ax.set_xticklabels(np.linspace(0,self.yr.your_header.nchans-1,8))
        
        #plt.colorbar(orientation='vertical', pad=0.01, aspect=30)
        plt.colorbar(self.im_ft, orientation='vertical', pad=0.01, aspect=30)
        
        ax = self.im_ft.axes
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('Frequency [MHz]')
        ax.set_yticks(np.linspace(0,self.yr.your_header.nchans,8))
        yticks = [str(int(j)) for j in np.linspace(self.yr.chan_freqs[0],self.yr.chan_freqs[-1],8)]
        ax.set_yticklabels(yticks)
        self.set_x_axis()        
        
        # a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(self.im_ft.figure, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def client_exit(self):
        exit()

    def next_gulp(self):
        self.start_samp += self.gulp_size
        proposed_end = self.start_samp + self.gulp_size
        #distance_to_end = self.yr.your_header.nspectra - proposed_end
        if proposed_end > self.yr.your_header.nspectra:
            self.start_samp  = self.start_samp - (proposed_end - self.yr.your_header.nspectra)
            print('End of file.')
            
        self.data = self.read_data()        
        self.set_x_axis()
        self.im_ft.set_data(self.data)
        self.im_bandpass.set_xdata(np.mean(self.data, axis=1))
        self.im_time.set_ydata(np.mean(self.data,axis=0))
        self.canvas.draw()    

    def prev_gulp(self):
        if (self.start_samp - self.gulp_size) >= 0:
            self.start_samp -= self.gulp_size
        
        self.data = self.read_data()        
        self.set_x_axis()        
        self.im.set_data(self.data)
        self.im_bandpass.set_xdata(np.mean(self.data, axis=1))
        self.im_time.set_ydata(np.mean(self.data, axis=0))
        self.canvas.draw()    
    
    def read_data(self):
        ts = self.start_samp*self.yr.your_header.tsamp
        te = (self.start_samp + self.gulp_size)*self.yr.your_header.tsamp
        logging.info(f'Displaying {self.gulp_size} samples from sample {self.start_samp} i.e {ts:.2f}-{te:.2f}s')
        data = self.yr.get_data(self.start_samp, self.gulp_size)
        return data.T

    def set_x_axis(self):
        ax = self.im_ft.axes
        xticks = ax.get_xticks()
        logging.debug(f'x-axis ticks are {xticks}')
        xtick_labels = (xticks + self.start_samp)*self.yr.tsamp
        logging.debug(f'Setting x-axis tick labels to {xtick_labels}')
        ax.set_xticklabels([f"{j:.2f}" for j in xtick_labels])

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='your_viewer.py',
                                     description="Read fits/fil file and show the data",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--files',
                        help='Fits or filterbank files to view.',
                        required=False, default='')
    parser.add_argument('-s', '--start',
                        help='Start index', type=int,
                        required=False, default=0)
    parser.add_argument('-g', '--gulp',
                        help='Gulp size', type=int,
                        required=False, default=3072)
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    values = parser.parse_args()
    
    if values.verbose:
        logging.basicConfig(level=logging.DEBUG, format=logging_format)
    else:
        logging.basicConfig(level=logging.INFO, format=logging_format)
        
    matplotlib_logger = logging.getLogger('matplotlib')
    matplotlib_logger.setLevel(logging.INFO)
    
    # root window created. Here, that would be the only window, but
    # you can later have windows within windows.
    root = Tk()
    root.geometry("1920x1080")
    #creation of an instance
    app = Paint(root)
    app.load_file(values.files, values.start, values.gulp)
    root.mainloop()
