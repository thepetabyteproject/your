#!/usr/bin/env python3
import logging
import os

from your.psrfits import PsrfitsFile
from your.pysigproc import SigprocFile

logger = logging.getLogger(__name__)

class Your(PsrfitsFile, SigprocFile):
    def __init__(self, file):
        self.your_file = file
        if isinstance(self.your_file, str):
            ext = os.path.splitext(self.your_file)[1]
            if ext == ".fits" or ext == ".sf":
                PsrfitsFile.__init__(self, psrfitslist=[self.your_file])
                self.isfits = True
                self.isfil = False
            elif ext == ".fil":
                SigprocFile.__init__(self, fp=self.your_file)
                self.isfits = False
                self.isfil = True
            else:
                raise TypeError('Filetype not supported')
        elif isinstance(self.your_file, list):
            if len(self.your_file) == 1 and os.path.splitext(*self.your_file)[1] == ".fil":
                for filterbank_file in self.your_file:
                    SigprocFile.__init__(self, fp=filterbank_file)
                    logger.debug(f'Reading filterbank file {filterbank_file}')
                    self.isfits = False
                    self.isfil = True
            else:
                for f in self.your_file:
                    ext = os.path.splitext(f)[1]
                    if ext == ".fits" or ext == ".sf" or ext == ".fil":
                        pass
                    else:
                        raise TypeError("Can only work with list of fits file or filterbanks")
                self.your_file.sort()
                PsrfitsFile.__init__(self, psrfitslist=self.your_file)
                logger.debug(f'Reading the following fits files: {self.your_file}')
                self.isfits = True
                self.isfil = False
    
    @property
    def nspectra(self):
        if self.isfil:
            return SigprocFile.nspectra(self)
        else:
            return PsrfitsFile.nspectra(self)
        
    def get_data(self, nstart, nsamp):
        if self.isfil:
            return SigprocFile.get_data(self, nstart, nsamp)
        else:
            return PsrfitsFile.get_data(self, nstart, nsamp)


    def __repr__(self):
        if isinstance(self.your_file, list):
            s = "\n".join(map(str, self.your_file))
        else:
            s = self.your_file
        return f"Using Files:\n{s}"
