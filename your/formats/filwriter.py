import logging

from your.formats.pysigproc import SigprocFile

logger = logging.getLogger(__name__)


def sigproc_object_from_writer(your_writer):
    """

    Convert a `your_writer` object to Sigproc object for writing

    Args:
        your_writer: `your_writer` object

    Returns:
        sigproc object

    """
    logger.debug(f"Generating Sigproc object")
    fil_obj = SigprocFile()
    fil_obj.rawdatafile = your_writer.outname
    fil_obj.source_name = your_writer.your_object.your_header.source_name

    fil_obj.machine_id = 0  # use "Fake" for now
    fil_obj.barycentric = 0  # by default the data isn't barycentered
    fil_obj.pulsarcentric = 0
    fil_obj.telescope_id = 6  # use only GBT for now
    fil_obj.data_type = 0

    fil_obj.nchans = your_writer.nchans
    fil_obj.foff = your_writer.your_object.your_header.foff
    fil_obj.fch1 = your_writer.chan_freqs[0]
    fil_obj.nbeams = 1
    fil_obj.ibeam = 0
    fil_obj.nbits = your_writer.your_object.your_header.nbits
    fil_obj.tsamp = your_writer.your_object.your_header.tsamp

    fil_obj.tstart = your_writer.tstart

    fil_obj.nifs = 1  # Only use Intensity values

    if (
        your_writer.your_object.your_header.ra_deg
        and your_writer.your_object.your_header.dec_deg
    ):
        ra = your_writer.your_object.your_header.ra_deg
        dec = your_writer.your_object.your_header.dec_deg
    else:
        ra = 0
        dec = 0

    from astropy.coordinates import SkyCoord
    import numpy as np

    loc = SkyCoord(ra, dec, unit="deg")
    ra_hms = loc.ra.hms
    dec_dms = loc.dec.dms

    fil_obj.src_raj = float(
        f"{int(ra_hms[0]):02d}{np.abs(int(ra_hms[1])):02d}{np.abs(ra_hms[2]):07.4f}"
    )
    fil_obj.src_dej = float(
        f"{int(dec_dms[0]):02d}{np.abs(int(dec_dms[1])):02d}{np.abs(dec_dms[2]):07.4f}"
    )

    fil_obj.az_start = -1
    fil_obj.za_start = -1
    return fil_obj


def make_sigproc_object(
    rawdatafile: str,
    source_name: str,
    nchans: int,
    foff: float,
    fch1: float,
    tsamp: float,
    tstart: float,
    src_raj: float = 112233.44,
    src_dej: float = 112233.44,
    machine_id: int = 0,
    nbeams: int = 0,
    ibeam: int = 0,
    nbits: int = 8,
    nifs: int = 1,
    barycentric: int = 0,
    pulsarcentric: int = 0,
    telescope_id: int = 6,
    data_type: int = 0,
    az_start: float = -1,
    za_start: float = -1,
):
    """
    Create a Sigprocfile from scratch.

    Args:
        rawdatafile (str): Raw file name
        source_name (str): Source Name
        nchans (int): Number of channels
        foff (float): Channel Bandwidth (MHz)
        fch1 (float): Frequncy of first channel (MHz)
        tsamp (float): Sampling interval (seconds)
        tstart (float): MJD of the start sample
        src_raj (float): RA of the source in format HHMMSS.SS
        src_dej (float): Dec of source in format DDMMSS.SS
        machine_id (int): Machine ID
        nbeams (int): Number of beams in the rcvr
        ibeam (int): Beam number
        nbits (int): Number of bits
        nifs (int): Number of IFs
        barycentric (int): 0 for not barycentered data, 1 otherwise.
        pulsarcentric (int): 0 for not pulsarcentered data, 1 otherwise.
        telescope_id (int): Telescope ID
        data_type (int): Data Type
        az_start (float): Azimuth Angle start
        za_start (float):  Zenith Angle start

    Returns:
        sigproc object

    """
    logger.debug(f"Generating Sigproc object")

    fil_obj = SigprocFile()
    fil_obj.rawdatafile = rawdatafile
    fil_obj.source_name = source_name

    fil_obj.machine_id = machine_id
    fil_obj.barycentric = barycentric
    fil_obj.pulsarcentric = pulsarcentric
    fil_obj.telescope_id = telescope_id
    fil_obj.data_type = data_type

    fil_obj.nchans = nchans
    fil_obj.foff = foff
    fil_obj.fch1 = fch1
    fil_obj.nbeams = nbeams
    fil_obj.ibeam = ibeam
    fil_obj.nbits = nbits
    fil_obj.tsamp = tsamp

    fil_obj.tstart = tstart
    fil_obj.nifs = nifs

    fil_obj.src_raj = src_raj
    fil_obj.src_dej = src_dej

    fil_obj.az_start = az_start
    fil_obj.za_start = za_start

    return fil_obj
