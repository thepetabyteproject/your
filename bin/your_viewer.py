import argparse
import logging
import os
from tkinter import *
from tkinter import filedialog

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from your import Your


# based on https://steemit.com/utopian-io/@hadif66/tutorial-embeding-scipy-matplotlib-with-tkinter-to-work-on-images-in-a-gui-framework

class Paint(Frame):
    """
    Class for plotting object
    """

    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None):

        # parameters that you want to send through the Frame class.
        Frame.__init__(self, master)

        # reference to the master widget, which is the tk window
        self.master = master

        # Creation of init_window
        # set widget title
        self.master.title("your_viewer")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH)  # , expand=1)
        self.create_widgets()
        # creating a menu instance
        menu = Menu(self.master)
        self.master.config(menu=menu)

        # create the file object)
        file = Menu(menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        file.add_command(label="Exit", command=self.client_exit)

        # added "file" to our menu
        menu.add_cascade(label="File", menu=file)

    def create_widgets(self):
        """
        Create all the user buttons
        """
        # which file to load
        self.browse = Button(self)
        self.browse["text"] = "Browse file"
        self.browse["command"] = self.load_file
        self.browse.grid(row=0, column=0)

        # move image foward to next gulp of data
        self.next = Button(self)
        self.next["text"] = "Next Gulp"
        self.next["command"] = self.next_gulp
        self.next.grid(row=0, column=1)

        # move image back to previous gulp of data
        self.prev = Button(self)
        self.prev["text"] = "Prevous Gulp"
        self.prev["command"] = self.prev_gulp
        self.prev.grid(row=0, column=3)

        # save figure
        self.prev = Button(self)
        self.prev["text"] = "Save Fig"
        self.prev["command"] = self.save_figure
        self.prev.grid(row=0, column=4)

    def nice_print(self, dic):
        """
        Prints out data files into in a nice to view way

        Inputs:
        dic --  dictionary containing data file meta data to be printed
        """
        for key, item in dic.items():
            print(f"{key : >27}:\t{item}")

    def get_header(self):
        """
        Gets meta data from data file and give the data to nice_print() to print to user
        """
        dic = vars(self.your_obj.your_header)
        dic['tsamp'] = self.your_obj.your_header.tsamp
        dic['nchans'] = self.your_obj.your_header.nchans
        dic['foff'] = self.your_obj.your_header.foff
        dic['nspectra'] = self.your_obj.your_header.nspectra
        self.nice_print(dic)

    def load_file(self, file_name=[''], start_samp=0, gulp_size=1024, chan_std=False):
        """
        Loads data from a file:

        Inputs:
        file_name -- name or list of files to load, if none given user must use gui to give file
        start_samp -- sample number where to start show the file, defaults to the beginning of the file
        gulp_size -- amount of data to show at a given time
        """
        self.start_samp = start_samp
        self.gulp_size = gulp_size
        self.chan_std = chan_std

        if len(file_name) == 0:
            file_name = filedialog.askopenfilename(filetypes=(("fits/fil files", "*.fil *.fits")
                                                              , ("All files", "*.*")))
        self.file_name = file_name

        logging.info(f'Reading file {file_name}.')
        self.your_obj = Your(file_name)
        self.master.title(self.your_obj.your_header.basename)
        logging.info(f'Printing Header parameters')
        self.get_header()
        self.read_data()

        # create three plots, for ax1=time_series, ax2=dynamic spectra, ax4=bandpass
        self.gs = gridspec.GridSpec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4], wspace=0.02, hspace=0.03)
        ax1 = plt.subplot(self.gs[0, 0])
        ax2 = plt.subplot(self.gs[1, 0])
        ax3 = plt.subplot(self.gs[0, 1])
        ax4 = plt.subplot(self.gs[1, 1])
        ax3.axis('off')
        ax1.set_xticks([])
        ax4.set_yticks([])

        # get the min and max image values to that we can see the typical values well
        self.vmax = min(np.max(self.data), np.median(self.data) + 5 * np.std(self.data))
        self.vmin = max(np.min(self.data), np.median(self.data) - 5 * np.std(self.data))
        self.im_ft = ax2.imshow(self.data, aspect='auto', vmin=self.vmin, vmax=self.vmax)

        # make bandpass
        bp_std = np.std(self.data, axis=1)
        bp_y = np.linspace(self.your_obj.your_header.nchans, 0, len(self.bandpass))
        self.im_bandpass, = ax4.plot(self.bandpass, bp_y, label='Bandpass')
        if self.chan_std:
            self.im_bp_fill = ax4.fill_betweenx(x1=self.bandpass - bp_std, x2=self.bandpass + bp_std, y=bp_y,
                                                interpolate=False, alpha=0.25, color='r', label='1 STD')
            ax4.legend()
        ax4.set_ylim([-1, len(self.bandpass) + 1])
        ax4.set_xlabel('Avg. Arb. Flux')

        # make time series
        ax4.set_xlabel('Avg. Arb. Flux')
        self.im_time, = ax1.plot(self.time_series)
        ax1.set_xlim(-1, len(self.time_series + 1))
        ax1.set_ylabel('Avg. Arb. Flux')

        plt.colorbar(self.im_ft, orientation='vertical', pad=0.01, aspect=30)

        ax = self.im_ft.axes
        ax.set_xlabel('Time [sec]')
        ax.set_ylabel('Frequency [MHz]')
        ax.set_yticks(np.linspace(0, self.your_obj.your_header.nchans, 8))
        yticks = [str(int(j)) for j in np.linspace(self.your_obj.chan_freqs[0], self.your_obj.chan_freqs[-1], 8)]
        ax.set_yticklabels(yticks)
        self.set_x_axis()

        # a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(self.im_ft.figure, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def client_exit(self):
        """
        exits the plotter
        """
        exit()

    def next_gulp(self):
        """
        Moves the images to the next gulp of data
        """
        self.start_samp += self.gulp_size
        # check if there is a enough data to fill plt
        proposed_end = self.start_samp + self.gulp_size
        if proposed_end > self.your_obj.your_header.nspectra:
            self.start_samp = self.start_samp - (proposed_end - self.your_obj.your_header.nspectra)
            logging.info('End of file.')
        self.update_plot()

    def prev_gulp(self):
        """
        Movies the images to the prevous gulp of data
        """
        # check if new start samp is in the file
        if (self.start_samp - self.gulp_size) >= 0:
            self.start_samp -= self.gulp_size
        self.update_plot()

    def update_plot(self):
        self.read_data()
        self.set_x_axis()
        self.im_ft.set_data(self.data)
        self.im_bandpass.set_xdata(self.bandpass)
        if self.chan_std:
            self.fill_bp()
        self.im_bandpass.axes.set_xlim(np.min(self.bandpass) * 0.97, np.max(self.bandpass) * 1.03)
        self.im_time.set_ydata(np.mean(self.data, axis=0))
        self.im_time.axes.set_ylim(np.min(self.time_series) * 0.97, np.max(self.time_series) * 1.03)
        self.canvas.draw()

    def fill_bp(self):
        self.im_bp_fill.remove()
        bp_std = np.std(self.data, axis=1)
        bp_y = self.im_bandpass.get_ydata()
        self.im_bp_fill = self.im_bandpass.axes.fill_betweenx(x1=self.bandpass - bp_std, x2=self.bandpass + bp_std,
                                                              y=bp_y, interpolate=False, alpha=0.25, color='r')

    def read_data(self):
        """
        Read data from the psr seach data file
        Returns:
        data -- a 2D array of frequency time plts
        """
        ts = self.start_samp * self.your_obj.your_header.tsamp
        te = (self.start_samp + self.gulp_size) * self.your_obj.your_header.tsamp
        self.data = self.your_obj.get_data(self.start_samp, self.gulp_size).T
        self.bandpass = np.mean(self.data, axis=1)
        self.time_series = np.mean(self.data, axis=0)
        logging.info(
            f'Displaying {self.gulp_size} samples from sample {self.start_samp} i.e {ts:.2f}-{te:.2f}s - gulp mean: '
            f'{np.mean(self.data):.3f}, std: {np.std(self.data):.3f}')

    def set_x_axis(self):
        """
        sets x axis labels in the correct location
        """
        ax = self.im_ft.axes
        xticks = ax.get_xticks()
        logging.debug(f'x-axis ticks are {xticks}')
        xtick_labels = (xticks + self.start_samp) * self.your_obj.your_header.tsamp
        logging.debug(f'Setting x-axis tick labels to {xtick_labels}')
        ax.set_xticklabels([f"{j:.2f}" for j in xtick_labels])

    def save_figure(self):
        """
        Saves the canvas image
        """
        img_name = os.path.splitext(os.path.basename(self.file_name))[
                       0] + f'_samp_{self.start_samp}_{self.start_samp + self.gulp_size}.png'
        logging.info(f'Saving figure: {img_name}')
        self.im_ft.figure.savefig(img_name, dpi=300)
        logging.info(f'Saved figure: {img_name}')


if __name__ == '__main__':
    logger = logging.getLogger()
    logging_format = '%(asctime)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s'

    parser = argparse.ArgumentParser(prog='your_viewer.py',
                                     description="Read fits/fil file and show the data",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--files',
                        help='Fits or filterbank files to view.',
                        required=False, default=[''], nargs='+')
    parser.add_argument('-s', '--start',
                        help='Start index', type=int,
                        required=False, default=0)
    parser.add_argument('-g', '--gulp',
                        help='Gulp size', type=int,
                        required=False, default=3072)
    parser.add_argument('-e', '--chan_std',
                        help='Show 1 standard devation per channel in bandpass',
                        required=False, default=False, action='store_true')
    parser.add_argument('-v', '--verbose', help='Be verbose', action='store_true')
    values = parser.parse_args()

    if values.verbose:
        logging.basicConfig(level=logging.DEBUG, format=logging_format)
    else:
        logging.basicConfig(level=logging.INFO, format=logging_format)

    matplotlib_logger = logging.getLogger('matplotlib')
    matplotlib_logger.setLevel(logging.INFO)

    # root window created.
    root = Tk()
    root.geometry("1920x1080")
    # creation of an instance
    app = Paint(root)
    app.load_file(values.files, values.start, values.gulp, values.chan_std)  # load file with user params
    root.mainloop()
