"""
Convert Filterbank files to PSRFITS file

Original Source: https://github.com/rwharton/fil2psrfits
"""

import logging

import astropy.coordinates as coord
import astropy.time as time
import numpy as np
from astropy.io import fits

logger = logging.getLogger(__name__)
import json


class ObsInfo(object):
    """
    Class to setup observation info for psrfits header

    """

    def __init__(self):
        self.file_date = self.format_date(time.Time.now().isot)
        self.observer = "Human"
        self.proj_id = "Awesome_Project"
        self.obs_date = ""
        self.fcenter = 0.0
        self.bw = 0.0
        self.nchan = 0
        self.src_name = ""
        self.ra_str = "00:00:00"
        self.dec_str = "+00:00:00"
        self.bmaj_deg = 0.0
        self.bmin_deg = 0.0
        self.bpa_deg = 0.0
        self.scan_len = 0
        self.stt_imjd = 0
        self.stt_smjd = 0
        self.stt_offs = 0.0
        self.stt_lst = 0.0

        self.dt = 0.0
        self.nbits = 16
        self.nsuboffs = 0.0
        self.chan_bw = 0.0
        self.nsblk = 0

        self.telescope = 'VLA'
        self.ant_x = -1601185.63
        self.ant_y = -5041978.15
        self.ant_z = 3554876.43
        self.longitude = self.calc_longitude()

    def calc_longitude(self):
        cc = coord.EarthLocation.from_geocentric(self.ant_x,
                                                 self.ant_y,
                                                 self.ant_z,
                                                 unit='m')
        longitude = cc.lon.deg
        return longitude

    def fill_from_mjd(self, mjd):
        stt_imjd = int(mjd)
        stt_smjd = int((mjd - stt_imjd) * 24 * 3600)
        stt_offs = ((mjd - stt_imjd) * 24 * 3600.0) - stt_smjd
        self.stt_imjd = stt_imjd
        self.stt_smjd = stt_smjd
        self.stt_offs = stt_offs
        self.obs_date = self.format_date(time.Time(mjd, format='mjd').isot)

    def fill_freq_info(self, fcenter, nchan, chan_bw):
        self.fcenter = fcenter
        self.bw = nchan * chan_bw
        self.nchan = nchan
        self.chan_bw = chan_bw

    def fill_source_info(self, src_name, ra_str, dec_str):
        self.src_name = src_name
        self.ra_str = ra_str
        self.dec_str = dec_str

    def fill_beam_info(self, bmaj_deg, bmin_deg, bpa_deg):
        self.bmaj_deg = bmaj_deg
        self.bmin_deg = bmin_deg
        self.bpa_deg = bpa_deg

    def fill_data_info(self, dt, nbits):
        self.dt = dt
        self.nbits = nbits

    def calc_start_lst(self, mjd):
        self.stt_lst = self.calc_lst(mjd, self.longitude)

    def calc_lst(self, mjd, longitude):
        gfac0 = 6.697374558
        gfac1 = 0.06570982441908
        gfac2 = 1.00273790935
        gfac3 = 0.000026
        mjd0 = 51544.5  # MJD at 2000 Jan 01 12h
        H = (mjd - int(mjd)) * 24  # Hours since previous 0h
        D = mjd - mjd0  # Days since MJD0
        D0 = int(mjd) - mjd0  # Days between MJD0 and prev 0h
        T = D / 36525.0  # Number of centuries since MJD0
        gmst = gfac0 + gfac1 * D0 + gfac2 * H + gfac3 * T ** 2.0
        lst = ((gmst + longitude / 15.0) % 24.0) * 3600.0
        return lst

    def format_date(self, date_str):
        # Strip out the decimal seconds
        out_str = date_str.split('.')[0]
        return out_str

    def fill_primary_header(self):
        p_hdr = fits.Header()
        p_hdr["HDRVER"] = ('3.4             ', "Header version                               ")
        p_hdr["FITSTYPE"] = ('PSRFITS', "FITS definition for pulsar data files        ")
        p_hdr["DATE"] = (self.file_date, "File creation date (YYYY-MM-DDThh:mm:ss UTC) ")
        p_hdr["OBSERVER"] = (self.observer, "Observer name(s)                             ")
        p_hdr["PROJID"] = (self.proj_id, "Project name                                 ")
        p_hdr["TELESCOP"] = (self.telescope, "Telescope name                               ")
        p_hdr["ANT_X"] = (self.ant_x, "[m] Antenna ITRF X-coordinate (D)            ")
        p_hdr["ANT_Y"] = (self.ant_y, "[m] Antenna ITRF Y-coordinate (D)            ")
        p_hdr["ANT_Z"] = (self.ant_z, "[m] Antenna ITRF Z-coordinate (D)            ")
        p_hdr["FRONTEND"] = ('                ', "Rx and feed ID                               ")
        p_hdr["NRCVR"] = (1, "Number of receiver polarisation channels     ")
        p_hdr["FD_POLN"] = ('CIRC', "LIN or CIRC                                  ")
        p_hdr["FD_HAND"] = (-1, "+/- 1. +1 is LIN:A=X,B=Y, CIRC:A=L,B=R (I)   ")
        p_hdr["FD_SANG"] = (45.0, "[deg] FA of E vect for equal sigma in A&B (E)  ")
        p_hdr["FD_XYPH"] = (0.0, "[deg] Phase of A^* B for injected cal (E)    ")
        p_hdr["BACKEND"] = ('YUPPI', "Backend ID                                   ")
        p_hdr["BECONFIG"] = ('N/A', "Backend configuration file name              ")
        p_hdr["BE_PHASE"] = (-1, "0/+1/-1 BE cross-phase:0 unknown,+/-1 std/rev")
        p_hdr["BE_DCC"] = (0, "0/1 BE downconversion conjugation corrected  ")
        p_hdr["BE_DELAY"] = (0.0, "[s] Backend propn delay from digitiser input ")
        p_hdr["TCYCLE"] = (0.0, "[s] On-line cycle time (D)                   ")
        p_hdr["OBS_MODE"] = ('SEARCH', "(PSR, CAL, SEARCH)                           ")
        p_hdr["DATE-OBS"] = (self.obs_date, "Date of observation (YYYY-MM-DDThh:mm:ss UTC)")
        p_hdr["OBSFREQ"] = (self.fcenter, "[MHz] Centre frequency for observation       ")
        p_hdr["OBSBW"] = (self.bw, "[MHz] Bandwidth for observation              ")
        p_hdr["OBSNCHAN"] = (self.nchan, "Number of frequency channels (original)      ")
        p_hdr["CHAN_DM"] = (0.0, "DM used to de-disperse each channel (pc/cm^3)")
        p_hdr["SRC_NAME"] = (self.src_name, "Source or scan ID                            ")
        p_hdr["COORD_MD"] = ('J2000', "Coordinate mode (J2000, GAL, ECLIP, etc.)    ")
        p_hdr["EQUINOX"] = (2000.0, "Equinox of coords (e.g. 2000.0)              ")
        p_hdr["RA"] = (self.ra_str, "Right ascension (hh:mm:ss.ssss)              ")
        p_hdr["DEC"] = (self.dec_str, "Declination (-dd:mm:ss.sss)                  ")
        p_hdr["BMAJ"] = (self.bmaj_deg, "[deg] Beam major axis length                 ")
        p_hdr["BMIN"] = (self.bmin_deg, "[deg] Beam minor axis length                 ")
        p_hdr["BPA"] = (self.bpa_deg, "[deg] Beam position angle                    ")
        p_hdr["STT_CRD1"] = (self.ra_str, "Start coord 1 (hh:mm:ss.sss or ddd.ddd)      ")
        p_hdr["STT_CRD2"] = (self.dec_str, "Start coord 2 (-dd:mm:ss.sss or -dd.ddd)     ")
        p_hdr["TRK_MODE"] = ('TRACK', "Track mode (TRACK, SCANGC, SCANLAT)          ")
        p_hdr["STP_CRD1"] = (self.ra_str, "Stop coord 1 (hh:mm:ss.sss or ddd.ddd)       ")
        p_hdr["STP_CRD2"] = (self.dec_str, "Stop coord 2 (-dd:mm:ss.sss or -dd.ddd)      ")
        p_hdr["SCANLEN"] = (self.scan_len, "[s] Requested scan length (E)                ")
        p_hdr["FD_MODE"] = ('FA', "Feed track mode - FA, CPA, SPA, TPA          ")
        p_hdr["FA_REQ"] = (0.0, "[deg] Feed/Posn angle requested (E)          ")
        p_hdr["CAL_MODE"] = ('OFF', "Cal mode (OFF, SYNC, EXT1, EXT2)             ")
        p_hdr["CAL_FREQ"] = (0.0, "[Hz] Cal modulation frequency (E)            ")
        p_hdr["CAL_DCYC"] = (0.0, "Cal duty cycle (E)                           ")
        p_hdr["CAL_PHS"] = (0.0, "Cal phase (wrt start time) (E)               ")
        p_hdr["STT_IMJD"] = (self.stt_imjd, "Start MJD (UTC days) (J - long integer)      ")
        p_hdr["STT_SMJD"] = (self.stt_smjd, "[s] Start time (sec past UTC 00h) (J)        ")
        p_hdr["STT_OFFS"] = (self.stt_offs, "[s] Start time offset (D)                    ")
        p_hdr["STT_LST"] = (self.stt_lst, "[s] Start LST (D)                            ")
        return p_hdr

    def fill_table_header(self):
        t_hdr = fits.Header()
        t_hdr["INT_TYPE"] = ('TIME', "Time axis (TIME, BINPHSPERI, BINLNGASC, etc)   ")
        t_hdr["INT_UNIT"] = ('SEC', "Unit of time axis (SEC, PHS (0-1), DEG)        ")
        t_hdr["SCALE"] = ('FluxDen', "Intensity units (FluxDen/RefFlux/Jansky)       ")
        t_hdr["NPOL"] = (1, "Nr of polarisations                            ")
        t_hdr["POL_TYPE"] = ('AA+BB', "Polarisation identifier (e.g., AABBCRCI, AA+BB)")
        t_hdr["TBIN"] = (self.dt, "[s] Time per bin or sample                     ")
        t_hdr["NBIN"] = (1, "Nr of bins (PSR/CAL mode; else 1)              ")
        t_hdr["NBIN_PRD"] = (0, "Nr of bins/pulse period (for gated data)       ")
        t_hdr["PHS_OFFS"] = (0.0, "Phase offset of bin 0 for gated data           ")
        t_hdr["NBITS"] = (self.nbits, "Nr of bits/datum (SEARCH mode 'X' data, else 1)")
        t_hdr["NSUBOFFS"] = (self.nsuboffs, "Subint offset (Contiguous SEARCH-mode files)   ")
        t_hdr["NCHAN"] = (self.nchan, "Number of channels/sub-bands in this file      ")
        t_hdr["CHAN_BW"] = (self.chan_bw, "[MHz] Channel/sub-band width                   ")
        t_hdr["NCHNOFFS"] = (0, "Channel/sub-band offset for split files        ")
        t_hdr["NSBLK"] = (self.nsblk, "Samples/row (SEARCH mode, else 1)              ")
        return t_hdr


def initialize_psrfits(outfile, your_object, npsub=-1, nstart=None, nsamp=None, chan_freqs=None):
    """
    Set up a PSRFITS file with everything set up EXCEPT
    the DATA.

    Args:

        outfile: path to the output fits file to write to

        your_object: your object with the input Filterbank file

        npsub: number of spectra in a subint

        nstart: start sample to read from (for the input file)

        nsamp: number of spectra to read

        chan_freqs: array with frequencies of all the channels

    """

    # Obs Specific Metadata
    # Time Info
    nbits = your_object.your_header.nbits
    mjd = your_object.your_header.tstart
    tsamp = your_object.your_header.tsamp  # seconds

    if nsamp:
        nsamps = nsamp
    else:
        nsamps = your_object.your_header.nspectra

    if nstart:
        mjd += nstart * tsamp / (24 * 60 * 60)
        if nstart + nsamps > your_object.your_header.nspectra:
            logging.warning('Data requested exceeds the length of file. Reading data till end of file.')
            nsamps = your_object.your_header.nspectra - nstart

    # Frequency Info (All freqs in MHz)
    if not chan_freqs.all():
        chan_freqs = your_object.chan_freqs
    nchans = len(chan_freqs)
    fch1 = chan_freqs[0]
    foff = your_object.your_header.foff

    freqs = fch1 + np.arange(nchans) * foff
    fcenter = fch1 + nchans * foff / 2

    nifs = your_object.your_header.npol
    # Source Info
    src_name = your_object.your_header.source_name

    from astropy.coordinates import SkyCoord

    if your_object.your_header.ra_deg and your_object.your_header.dec_deg:
        ra = your_object.your_header.ra_deg
        dec = your_object.your_header.dec_deg
    else:
        ra = 0
        dec = 0

    loc = SkyCoord(ra, dec, unit='deg')
    ra_hms = loc.ra.hms
    dec_dms = loc.dec.dms

    ra_str = f'{int(ra_hms[0]):02d}:{np.abs(int(ra_hms[1])):02d}:{np.abs(ra_hms[2]):07.4f}'
    dec_str = f'{int(dec_dms[0]):02d}:{np.abs(int(dec_dms[1])):02d}:{np.abs(dec_dms[2]):07.4f}'

    # Beam Info
    beam_info = np.array([0.0, 0.0, 0.0])
    bmaj_deg = beam_info[0] / 3600.0
    bmin_deg = beam_info[1] / 3600.0
    bpa_deg = beam_info[2]

    # Fill in the ObsInfo class
    d = ObsInfo()
    d.fill_from_mjd(mjd)
    d.fill_freq_info(fcenter, nchans, foff)
    d.fill_source_info(src_name, ra_str, dec_str)
    d.fill_beam_info(bmaj_deg, bmin_deg, bpa_deg)
    d.fill_data_info(tsamp, nbits)
    d.calc_start_lst(mjd)

    logging.info('ObsInfo updated with relevant parameters')

    # Determine subint size for PSRFITS table
    if npsub > 0:
        n_per_subint = npsub
    else:
        n_per_subint = int(1.0 / tsamp)

    n_subints = int(nsamps / n_per_subint)
    if nsamps % n_per_subint:
        n_subints += 1

    tstart = 0.0
    t_subint = n_per_subint * tsamp
    d.nsblk = n_per_subint
    d.scan_len = t_subint * n_subints

    tsubint = np.ones(n_subints, dtype=np.float64) * t_subint
    offs_sub = (np.arange(n_subints) + 0.5) * t_subint + tstart

    logger.info(
        f'Setting the following info to be written in {outfile} \n {json.dumps(vars(d), indent=4, sort_keys=True)}')

    # Fill in the headers
    phdr = d.fill_primary_header()
    thdr = d.fill_table_header()
    fits_data = fits.HDUList()
    data = np.array([], dtype=your_object.your_header.dtype)

    # Prepare arrays for columns
    lst_sub = np.array([d.calc_lst(mjd + tsub / (24. * 3600.0), d.longitude) for tsub in offs_sub], dtype=np.float64)
    ra_deg, dec_deg = your_object.your_header.ra_deg, your_object.your_header.dec_deg
    l_deg, b_deg = your_object.your_header.gl, your_object.your_header.gb
    ra_sub = np.ones(n_subints, dtype=np.float64) * ra_deg
    dec_sub = np.ones(n_subints, dtype=np.float64) * dec_deg
    glon_sub = np.ones(n_subints, dtype=np.float64) * l_deg
    glat_sub = np.ones(n_subints, dtype=np.float64) * b_deg
    fd_ang = np.zeros(n_subints, dtype=np.float32)
    pos_ang = np.zeros(n_subints, dtype=np.float32)
    par_ang = np.zeros(n_subints, dtype=np.float32)
    tel_az = np.zeros(n_subints, dtype=np.float32)
    tel_zen = np.zeros(n_subints, dtype=np.float32)
    dat_freq = np.vstack([freqs] * n_subints).astype(np.float32)

    dat_wts = np.ones((n_subints, nchans), dtype=your_object.your_header.dtype)
    dat_offs = np.zeros((n_subints, nchans), dtype=your_object.your_header.dtype)
    dat_scl = np.ones((n_subints, nchans), dtype=your_object.your_header.dtype)

    # https://het.as.utexas.edu/HET/Software/Astropy-1.0/_modules/astropy/io/fits/column.html
    # mapping from TFORM data type to numpy data type (code)
    # L: Logical (Boolean)
    # B: Unsigned Byte
    # I: 16-bit Integer
    # J: 32-bit Integer
    # K: 64-bit Integer
    # E: Single-precision Floating Point
    # D: Double-precision Floating Point
    # C: Single-precision Complex
    # M: Double-precision Complex
    # A: Character

    dtype = your_object.your_header.dtype
    if dtype == np.uint8:
        data_format = 'B'
    elif dtype == np.uint16:
        data_format = 'I'
    elif dtype == np.uint32:
        data_format = 'J'
    elif dtype == np.uint64:
        data_format = 'K'
    elif dtype == np.float32:
        data_format = 'E'
    elif dtype == np.float64:
        data_format = 'D'
    else:
        data_format = 'E'

    # Make the columns
    tbl_columns = [
        fits.Column(name="TSUBINT", format='1D', unit='s', array=tsubint),
        fits.Column(name="OFFS_SUB", format='1D', unit='s', array=offs_sub),
        fits.Column(name="LST_SUB", format='1D', unit='s', array=lst_sub),
        fits.Column(name="RA_SUB", format='1D', unit='deg', array=ra_sub),
        fits.Column(name="DEC_SUB", format='1D', unit='deg', array=dec_sub),
        fits.Column(name="GLON_SUB", format='1D', unit='deg', array=glon_sub),
        fits.Column(name="GLAT_SUB", format='1D', unit='deg', array=glat_sub),
        fits.Column(name="FD_ANG", format='1E', unit='deg', array=fd_ang),
        fits.Column(name="POS_ANG", format='1E', unit='deg', array=pos_ang),
        fits.Column(name="PAR_ANG", format='1E', unit='deg', array=par_ang),
        fits.Column(name="TEL_AZ", format='1E', unit='deg', array=tel_az),
        fits.Column(name="TEL_ZEN", format='1E', unit='deg', array=tel_zen),
        fits.Column(name="DAT_FREQ", format=f'{nchans}E', unit='MHz', array=dat_freq),
        fits.Column(name="DAT_WTS", format=f'{nchans}E', array=dat_wts),
        fits.Column(name="DAT_OFFS", format=f'{nchans}E', array=dat_offs),
        fits.Column(name="DAT_SCL", format=f'{nchans}E', array=dat_scl),
        fits.Column(name="DATA", format=str(nifs * nchans * n_per_subint) + data_format,
                    dim=f'({nchans}, {nifs}, {n_per_subint})', array=data),
    ]

    # Add the columns to the table
    logging.info("Building the PSRFITS table")
    table_hdu = fits.BinTableHDU(fits.FITS_rec.from_columns(tbl_columns),
                                 name="subint", header=thdr)

    # Add primary header
    primary_hdu = fits.PrimaryHDU(header=phdr)

    # Add hdus to FITS file and write
    logging.info(f'Writing PSRFITS table to file: {outfile}')
    fits_data.append(primary_hdu)
    fits_data.append(table_hdu)
    fits_data.writeto(outfile, overwrite=True)
    logging.info(f'Header information written in {outfile}')
    return
