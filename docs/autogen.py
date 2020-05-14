import shutil

from keras_autodoc import DocumentationGenerator

pages = {'your.md': ["your.Your"],
         'utils/rfi.md': ["your.utils.rfi.mask_finder",
                          "your.utils.rfi.get_sg_window",
                          "your.utils.rfi.spectral_kurtosis"]}

doc_generator = DocumentationGenerator(pages)
doc_generator.generate('./sources')

shutil.copyfile('../README.md', 'index.md')
