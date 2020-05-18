import shutil

from keras_autodoc import DocumentationGenerator

pages = {
    'your.md': ["your.Your"],

    'utils/rfi.md': ["your.utils.rfi.savgol_filter",
                     "your.utils.rfi.spectral_kurtosis"],

    'utils/plotter.md': ["your.utils.plotter.figsize",
                         "your.utils.plotter.get_params",
                         "your.utils.plotter.plot_h5"],
    'utils/astro.md': ["your.utils.astro.dec2deg",
                       "your.utils.astro.ra2deg"]

         }

doc_generator = DocumentationGenerator(pages)
doc_generator.generate('./sources')

shutil.copyfile('../README.md', 'index.md')