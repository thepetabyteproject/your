#!/usr/bin/env python3
"""
Takes Dynamic Spectra (Frequency-Time data) from filterbank/fits files,
and displays in a GUI.

Shows time series above spectra and bandpass to the right.

It also reports some basic statistics of the data.

Key Binds:
    Left Arrow: Move the previous gulp

    Right Arrow: Move the the next gulp
"""

import argparse
import logging
import os
from tkinter import BOTH, TOP, Button, Frame, Menu, Tk, filedialog

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from rich import box
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from your import Your
from your.utils.astro import calc_dispersion_delays, dedisperse
from your.utils.math import bandpass_fitter
from your.utils.misc import YourArgparseFormatter

# based on
# https://steemit.com/utopian-io/@hadif66/tutorial-embeding-scipy-matplotlib-with-tkinter-to-work-on-images-in-a-gui-framework


class Paint(Frame):
    """
    Class for plotting object
    """

    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None, dm=0):
        # parameters that you want to send through the Frame class.
        Frame.__init__(self, master)

        # reference to the master widget, which is the tk window
        self.master = master

        # Bind left and right keys to move data chunk
        self.master.bind("<Left>", lambda event: self.prev_gulp())
        self.master.bind("<Right>", lambda event: self.next_gulp())

        self.dm = dm
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

        # save figure
        self.prev = Button(self)
        self.prev["text"] = "Save Fig"
        self.prev["command"] = self.save_figure
        self.prev.grid(row=0, column=1)

        # move image back to previous gulp of data
        self.prev = Button(self)
        self.prev["text"] = "Prevous Gulp"
        self.prev["command"] = self.prev_gulp
        self.prev.grid(row=0, column=2)

        # move image forward to next gulp of data
        self.next = Button(self)
        self.next["text"] = "Next Gulp"
        self.next["command"] = self.next_gulp
        self.next.grid(row=0, column=3)

    def table_print(self, dic):
        """
        Prints out data using rich.Table

        Inputs:
        dic --  dictionary containing data file meta data to be printed
        """

        console = Console()
        table = Table(show_header=True, header_style="bold red", box=box.DOUBLE_EDGE)
        table.add_column("Parameter", justify="right")
        table.add_column("Value")
        for key, item in dic.items():
            table.add_row(key, f"{item}")
        console.print(table)

    def get_header(self):
        """
        Gets meta data from data file and give the data
        to nice_print() to print to user
        """
        dic = vars(self.your_obj.your_header)
        dic["tsamp"] = self.your_obj.your_header.tsamp
        dic["nchans"] = self.your_obj.your_header.nchans
        dic["foff"] = self.your_obj.your_header.foff
        dic["nspectra"] = self.your_obj.your_header.nspectra
        self.table_print(dic)

    def load_file(
        self,
        file_name=[""],
        start_samp=0,
        gulp_size=4096,
        chan_std=False,
        bandpass_subtract=False,
    ):
        """
        Loads data from a file:

        Inputs:
        file_name -- name or list of files to load,
                     if none given user must use gui to give file
        start_samp -- sample number where to start show the file,
                      defaults to the beginning of the file
        gulp_size -- amount of data to show at a given time

        bandpass_subtract -- subtract a polynomial fit of the bandpass
        """
        self.start_samp = start_samp
        self.gulp_size = gulp_size
        self.chan_std = chan_std

        if file_name == [""]:
            file_name = filedialog.askopenfilename(
                filetypes=(("fits/fil files", "*.fil *.fits"), ("All files", "*.*"))
            )

        logging.info(f"Reading file {file_name}.")
        self.your_obj = Your(file_name)
        self.master.title(self.your_obj.your_header.basename)
        if bandpass_subtract:
            iinfo = np.iinfo(self.your_obj.your_header.dtype)
            self.min = iinfo.min
            self.max = iinfo.max
            self.subtract = True
        else:
            self.subtract = False

        logging.info("Printing Header parameters")
        self.get_header()
        if self.dm != 0:
            self.dispersion_delays = calc_dispersion_delays(
                self.dm, self.your_obj.chan_freqs
            )
            max_delay = np.max(np.abs(self.dispersion_delays))
            if max_delay > self.gulp_size * self.your_obj.your_header.native_tsamp:
                logging.warning(
                    f"Maximum dispersion delay for DM ({self.dm}) ="
                    f" {max_delay:.2f}s is greater than the input gulp size "
                    f"{self.gulp_size * self.your_obj.your_header.native_tsamp}"
                    f"s. Pulses may not be dedispersed completely."
                )
                logging.warning(
                    f"Use gulp size of "
                    f"{int(max_delay // self.your_obj.your_header.native_tsamp):0d}"
                    f" to dedisperse completely."
                )
        self.read_data()

        # create three plots,
        # for ax1=time_series, ax2=dynamic spectra, ax4=bandpass
        gs = gridspec.GridSpec(
            2, 2, width_ratios=[4, 1], height_ratios=[1, 4], wspace=0.02, hspace=0.03
        )
        ax1 = plt.subplot(gs[0, 0])
        ax2 = plt.subplot(gs[1, 0])
        ax3 = plt.subplot(gs[0, 1])
        ax4 = plt.subplot(gs[1, 1])
        ax3.axis("off")
        ax1.set_xticks([])
        ax4.set_yticks([])

        # get the min and max image values so that
        # we can see the typical values well
        median = np.median(self.data)
        std = np.std(self.data)
        self.vmax = min(np.max(self.data), median + 4 * std)
        self.vmin = max(np.min(self.data), median - 4 * std)
        self.im_ft = ax2.imshow(
            self.data, aspect="auto", vmin=self.vmin, vmax=self.vmax
        )

        # make bandpass
        bp_std = np.std(self.data, axis=1)
        bp_y = np.linspace(self.your_obj.your_header.nchans, 0, len(self.bandpass))
        (self.im_bandpass,) = ax4.plot(self.bandpass, bp_y, label="Bandpass")
        if self.chan_std:
            self.im_bp_fill = ax4.fill_betweenx(
                x1=self.bandpass - bp_std,
                x2=self.bandpass + bp_std,
                y=bp_y,
                interpolate=False,
                alpha=0.25,
                color="r",
                label="1 STD",
            )
            ax4.legend()
        ax4.set_ylim([-1, len(self.bandpass) + 1])
        ax4.set_xlabel("Avg. Arb. Flux")

        # make time series
        ax4.set_xlabel("Avg. Arb. Flux")
        (self.im_time,) = ax1.plot(self.time_series)
        ax1.set_xlim(-1, len(self.time_series + 1))
        ax1.set_ylabel("Avg. Arb. Flux")

        plt.colorbar(self.im_ft, orientation="vertical", pad=0.01, aspect=30)

        ax = self.im_ft.axes
        ax.set_xlabel("Time [sec]")
        ax.set_ylabel("Frequency [MHz]")
        ax.set_yticks(np.linspace(0, self.your_obj.your_header.nchans, 8))
        yticks = [
            str(int(j))
            for j in np.linspace(
                self.your_obj.chan_freqs[0], self.your_obj.chan_freqs[-1], 8
            )
        ]
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
            self.start_samp = self.start_samp - (
                proposed_end - self.your_obj.your_header.nspectra
            )
            logging.info("End of file.")
        self.update_plot()

    def prev_gulp(self):
        """
        Movies the images to the previous gulp of data
        """
        # check if new start samp is in the file
        if (self.start_samp - self.gulp_size) >= 0:
            self.start_samp -= self.gulp_size
        self.update_plot()

    def update_plot(self):
        """
        Redraws the plots when something is changed
        """
        self.read_data()
        self.set_x_axis()
        self.im_ft.set_data(self.data)
        self.im_bandpass.set_xdata(self.bandpass)
        if self.chan_std:
            self.fill_bp()
        self.im_bandpass.axes.relim()
        self.im_bandpass.axes.autoscale(axis="x")
        self.im_time.set_ydata(np.mean(self.data, axis=0))
        self.im_time.axes.relim()
        self.im_time.axes.autoscale(axis="y")
        self.canvas.draw()

    def fill_bp(self):
        """
        Adds each channel's standard deviations to bandpass plot
        """
        self.im_bp_fill.remove()
        bp_std = np.std(self.data, axis=1)
        bp_y = self.im_bandpass.get_ydata()
        self.im_bp_fill = self.im_bandpass.axes.fill_betweenx(
            x1=self.bandpass - bp_std,
            x2=self.bandpass + bp_std,
            y=bp_y,
            interpolate=False,
            alpha=0.25,
            color="r",
        )

    def read_data(self):
        """
        Read data from the psr search data file
        Returns:
        data -- a 2D array of frequency time plots
        """
        ts = self.start_samp * self.your_obj.your_header.tsamp
        te = (self.start_samp + self.gulp_size) * self.your_obj.your_header.tsamp
        self.data = self.your_obj.get_data(self.start_samp, self.gulp_size).T
        if self.dm != 0:
            logging.info(f"Dedispersing data at DM: {self.dm}")
            self.data = dedisperse(
                self.data.copy(),
                self.dm,
                self.your_obj.native_tsamp,
                delays=self.dispersion_delays,
            )
        if self.subtract:
            bandpass = bandpass_fitter(np.median(self.data, axis=1))
            # fit data to median bandpass
            np.clip(bandpass, self.min, self.max, out=bandpass)
            # make sure the fit is numerically possable
            self.data = self.data - bandpass[:, None]

            # attempt to return the correct data type,
            # most values are close to zero
            # add get clipped, causeing dynamic range problems
            # diff = np.clip(self.data - bandpass[:, None], self.min, self.max)
            # self.data = diff #diff.astype(self.your_obj.your_header.dtype)

        self.bandpass = np.mean(self.data, axis=1)
        self.time_series = np.mean(self.data, axis=0)
        logging.info(
            f"Displaying {self.gulp_size} samples from sample "
            f"{self.start_samp} i.e {ts:.2f}-{te:.2f}s - gulp mean: "
            f"{np.mean(self.data):.3f}, std: {np.std(self.data):.3f}"
        )

    def set_x_axis(self):
        """
        sets x axis labels in the correct location
        """
        ax = self.im_ft.axes
        xticks = ax.get_xticks()
        logging.debug(f"x-axis ticks are {xticks}")
        xtick_labels = (xticks + self.start_samp) * self.your_obj.your_header.tsamp
        logging.debug(f"Setting x-axis tick labels to {xtick_labels}")
        ax.set_xticklabels([f"{j:.2f}" for j in xtick_labels])

    def save_figure(self):
        """
        Saves the canvas image
        """
        img_name = (
            os.path.splitext(os.path.basename(self.your_obj.your_header.filename))[0]
            + f"_samp_{self.start_samp}_{self.start_samp + self.gulp_size}.png"
        )
        logging.info(f"Saving figure: {img_name}")
        self.im_ft.figure.savefig(img_name, dpi=300)
        logging.info(f"Saved figure: {img_name}")


if __name__ == "__main__":
    logger = logging.getLogger()
    logging_format = (
        "%(asctime)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s"
    )

    parser = argparse.ArgumentParser(
        prog="your_viewer.py",
        description="Read psrfits/filterbank files and show the data",
        formatter_class=YourArgparseFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "-f",
        "--files",
        help="Fits or filterbank files to view.",
        required=False,
        default=[""],
        nargs="+",
    )
    parser.add_argument(
        "-s", "--start", help="Start index", type=float, required=False, default=0
    )
    parser.add_argument(
        "-g", "--gulp", help="Gulp size", type=int, required=False, default=4096
    )
    parser.add_argument(
        "-e",
        "--chan_std",
        help="Show 1 standard deviation per channel in bandpass",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--display",
        help="Display size for the plot",
        type=int,
        nargs=2,
        required=False,
        metavar=("width", "height"),
        default=[1024, 640],
    )
    parser.add_argument(
        "-dm",
        "--dm",
        help="DM to dedisperse the data",
        type=float,
        required=False,
        default=0,
    )
    parser.add_argument(
        "-subtract",
        "--bandpass_subtract",
        help="subtract a polynomial fitted bandpass",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    values = parser.parse_args()

    if values.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format=logging_format,
            handlers=[RichHandler(rich_tracebacks=True)],
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format=logging_format,
            handlers=[RichHandler(rich_tracebacks=True)],
        )

    matplotlib_logger = logging.getLogger("matplotlib")
    matplotlib_logger.setLevel(logging.INFO)

    # root window created.
    root = Tk()
    root.geometry(f"{values.display[0]}x{values.display[1]}")
    # creation of an instance
    app = Paint(root, dm=values.dm)
    app.load_file(
        values.files,
        values.start,
        values.gulp,
        values.chan_std,
        values.bandpass_subtract,
    )  # load file with user params
    root.mainloop()
