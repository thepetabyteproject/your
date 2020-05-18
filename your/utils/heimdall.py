import logging
import os


class HeimdallManager:

    def __init__(self, dada_key=None, filename=None, verbosity=None, nsamps_gulp=262144, beam=None, baseline_length=2,
                 output_dir=None, dm=None, dm_tol=1.25, zap_chans=None, max_giant_rate=None, dm_nbits=32, gpu_id=None,
                 no_scrunching=False, rfi_tol=5, rfi_no_narrow=False, rfi_no_broad=False, boxcar_max=4096, fswap=None,
                 min_tscrunch_width=None):
        self.k = dada_key
        self.f = filename
        self.verbosity = verbosity
        self.nsamps_gulp = nsamps_gulp
        self.beam = beam
        self.baseline_length = baseline_length
        self.output_dir = output_dir
        self.dm = dm
        self.dm_tol = dm_tol
        self.zap_chans = zap_chans
        self.max_gaint_rate = max_giant_rate
        self.dm_nbits = dm_nbits
        self.gpu_id = gpu_id
        self.no_scrunching = no_scrunching
        self.rfi_tol = rfi_tol
        self.rfi_no_narrow = rfi_no_narrow
        self.rfi_no_broad = rfi_no_broad
        self.boxcar_max = boxcar_max
        self.fswap = fswap
        self.min_tscrunch_width = min_tscrunch_width

        if (self.k is None) and (self.f is None):
            raise IOError(f"Need either a dada key or a filterbank file to run")

    def run(self):
        cmd = 'heimdall '
        for attribute, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, list):
                    if attribute == 'zap_chans':
                        for chans in value:
                            cmd += ' -zap_chans '
                            cmd += str(chans) + ' '
                            cmd += str(chans)
                    else:
                        cmd += str(f' -{attribute} ')
                        cmd += ' '.join(map(str, value))
                elif attribute == 'verbosity':
                    if value in ['V', 'v', 'g', 'G']:
                        cmd += str(f' -{value} ')
                    else:
                        logging.warning(f"Allowed verbosity is v,V,g,G")
                        logging.warning(f"Using v for now!")
                        cmd += f" -v "
                elif attribute == 'no_scrunching' or attribute == 'rfi_no_narrow' or attribute == 'rfi_no_broad':
                    if value:
                        cmd += str(f' -{attribute}')
                else:
                    cmd += str(f' -{attribute} {value}')

        logging.info(f"Using cmd: \n{cmd}")
        os.system(cmd)
