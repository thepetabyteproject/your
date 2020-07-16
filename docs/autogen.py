import glob
import os
import shutil

from keras_autodoc import DocumentationGenerator

pages = {
    'your.md': ["your.Your",
                "your.Your.bandpass",
                "your.Your.get_data",
                "your.Your.dispersion_delay",
                "your.Header"],

    'candidate.md': ["your.candidate.Candidate",
                     "your.candidate.Candidate.save_h5",
                     "your.candidate.Candidate.dispersion_delay",
                     "your.candidate.Candidate.get_chunk",
                     "your.candidate.Candidate.dedisperse",
                     "your.candidate.Candidate.dedispersets",
                     "your.candidate.Candidate.dmtime",
                     "your.candidate.Candidate.get_snr",
                     "your.candidate.Candidate.optimize_dm",
                     "your.candidate.Candidate.decimate",
                     "your.candidate.Candidate.resize"],

    'psrdada.md': ['your.dada.DadaManager',
                   'your.dada.DadaManager.setup',
                   'your.dada.DadaManager.dump_header',
                   'your.dada.DadaManager.dump_data',
                   'your.dada.DadaManager.mark_filled',
                   'your.dada.DadaManager.eod',
                   'your.dada.DadaManager.teardown',
                   'your.dada.YourDada',
                   'your.dada.YourDada.setup',
                   'your.dada.YourDada.teardown',
                   'your.dada.YourDada.your_dada_header',
                   'your.dada.YourDada.to_dada'],

    'pysigproc.md': ['your.pysigproc.SigprocFile',
                     'your.pysigproc.SigprocFile.get_data',
                     'your.pysigproc.SigprocFile.unpack',
                     'your.pysigproc.SigprocFile.write_header',
                     'your.pysigproc.SigprocFile.append_spectra'],

    'utils/rfi.md': ["your.utils.rfi.savgol_filter",
                     "your.utils.rfi.spectral_kurtosis"],

    'utils/plotter.md': ["your.utils.plotter.figsize",
                         "your.utils.plotter.get_params",
                         "your.utils.plotter.plot_h5",
                         "your.utils.plotter.save_bandpass"],

    'utils/astro.md': ["your.utils.astro.dec2deg",
                       "your.utils.astro.ra2deg"],

    'utils/heimdall.md': ["your.utils.heimdall.HeimdallManager",
                          "your.utils.heimdall.HeimdallManager.run"],

    'utils/math.md': ["your.utils.math.closest_number",
                      "your.utils.math.primes",
                      "your.utils.math.closest_divisor",
                      "your.utils.math.find_gcd",
                      "your.utils.math.normalise",
                      "your.utils.math.smad_plotter"],

    'utils/gpu.md': ["your.utils.gpu.gpu_dedisperse",
                     "your.utils.gpu.gpu_dmt",
                     "your.utils.gpu.gpu_dedisp_and_dmt_crop",
                     "your.utils.gpu.get_gpu_memory_map"],

    'utils/misc.md': ["your.utils.misc.MyEncoder"]
}

doc_generator = DocumentationGenerator(pages)
doc_generator.generate('./sources')

shutil.copyfile('../README.md', 'sources/index.md')

os.system("mkdir -p sources/bin")

for bin_files in glob.glob("../bin/*py"):
    output_file = "sources/bin/" + os.path.basename(bin_files)[:-2] + 'md'
    os.system(f"argdown --tiny -o {output_file} {bin_files}")
