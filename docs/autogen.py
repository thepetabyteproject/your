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

    'utils/rfi.md': ["your.utils.rfi.savgol_filter",
                     "your.utils.rfi.spectral_kurtosis"],

    'utils/plotter.md': ["your.utils.plotter.figsize",
                         "your.utils.plotter.get_params",
                         "your.utils.plotter.plot_h5"],

    'utils/astro.md': ["your.utils.astro.dec2deg",
                       "your.utils.astro.ra2deg"],

    'utils/heimdall.md': ["your.utils.heimdall.HeimdallManager",
                          "your.utils.heimdall.HeimdallManager.run"],

    'utils/math.md': ["your.utils.math.closest_number",
                      "your.utils.math.primes",
                      "your.utils.math.closest_divisor",
                      "your.utils.math.find_gcd",
                      "your.utils.math.normalise"]
}

doc_generator = DocumentationGenerator(pages)
doc_generator.generate('./sources')

shutil.copyfile('../README.md', 'sources/index.md')
