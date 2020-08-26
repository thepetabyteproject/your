import glob
import os
import re
import shutil

from keras_autodoc import DocumentationGenerator
from mdutils.mdutils import MdUtils

pages = {
    "your.md": [
        "your.Your",
        "your.Your.bandpass",
        "your.Your.get_data",
        "your.Your.dispersion_delay",
        "your.Header",
    ],
    "candidate.md": [
        "your.candidate.Candidate",
        "your.candidate.Candidate.save_h5",
        "your.candidate.Candidate.dispersion_delay",
        "your.candidate.Candidate.get_chunk",
        "your.candidate.Candidate.dedisperse",
        "your.candidate.Candidate.dedispersets",
        "your.candidate.Candidate.dmtime",
        "your.candidate.Candidate.get_snr",
        "your.candidate.Candidate.optimize_dm",
        "your.candidate.Candidate.decimate",
        "your.candidate.Candidate.resize",
    ],
    "writer.md": ["your.writer.Writer.to_fil", "your.writer.Writer.to_fits"],
    "formats/psrdada.md": [
        "your.formats.dada.DadaManager",
        "your.formats.dada.DadaManager.setup",
        "your.formats.dada.DadaManager.dump_header",
        "your.formats.dada.DadaManager.dump_data",
        "your.formats.dada.DadaManager.mark_filled",
        "your.formats.dada.DadaManager.eod",
        "your.formats.dada.DadaManager.teardown",
        "your.formats.dada.YourDada",
        "your.formats.dada.YourDada.setup",
        "your.formats.dada.YourDada.teardown",
        "your.formats.dada.YourDada.your_dada_header",
        "your.formats.dada.YourDada.to_dada",
    ],
    "formats/pysigproc.md": [
        "your.formats.pysigproc.SigprocFile",
        "your.formats.pysigproc.SigprocFile.get_data",
        "your.formats.pysigproc.SigprocFile.unpack",
        "your.formats.pysigproc.SigprocFile.write_header",
        "your.formats.pysigproc.SigprocFile.append_spectra",
    ],
    "formats/psrfits.md": [
        "your.formats.psrfits.PsrfitsFile",
        "your.formats.psrfits.PsrfitsFile.read_subint",
        "your.formats.psrfits.PsrfitsFile.get_data",
        "your.formats.psrfits.SpectraInfo",
        "your.formats.psrfits.unpack_2bit",
        "your.formats.psrfits.unpack_2bit",
        "your.formats.psrfits.unpack_4bit",
    ],
    "formats/filwriter.md": [
        "your.formats.filwriter.make_sigproc_obj",
        "your.formats.filwriter.write_fil",
    ],
    "formats/fitswriter.md": [
        "your.formats.fitswriter.initialize_psrfits",
        "your.formats.fitswriter.ObsInfo",
    ],
    "utils/rfi.md": [
        "your.utils.rfi.savgol_filter",
        "your.utils.rfi.spectral_kurtosis",
    ],
    "utils/plotter.md": [
        "your.utils.plotter.figsize",
        "your.utils.plotter.get_params",
        "your.utils.plotter.plot_h5",
        "your.utils.plotter.save_bandpass",
    ],
    "utils/astro.md": ["your.utils.astro.dec2deg", "your.utils.astro.ra2deg"],
    "utils/heimdall.md": [
        "your.utils.heimdall.HeimdallManager",
        "your.utils.heimdall.HeimdallManager.run",
    ],
    "utils/math.md": [
        "your.utils.math.closest_number",
        "your.utils.math.primes",
        "your.utils.math.closest_divisor",
        "your.utils.math.find_gcd",
        "your.utils.math.normalise",
        "your.utils.math.smad_plotter",
    ],
    "utils/gpu.md": [
        "your.utils.gpu.gpu_dedisperse",
        "your.utils.gpu.gpu_dmt",
        "your.utils.gpu.gpu_dedisp_and_dmt_crop",
        "your.utils.gpu.get_gpu_memory_map",
    ],
    "utils/misc.md": [
        "your.utils.misc.crop",
        "your.utils.misc.pad_along_axis",
        "your.utils.misc.MyEncoder",
    ],
}

doc_generator = DocumentationGenerator(pages)
doc_generator.generate("./sources")

shutil.copyfile("../README.md", "sources/index.md")

os.mkdir("sources/ipynb")
for nb in glob.glob("../examples/*ipynb"):
    file_name = os.path.basename(nb)
    os.symlink(os.path.abspath(nb), "sources/ipynb/" + file_name)

os.mkdir("sources/bin")

os.system(f"cd sources/bin; argmark -f ../../../bin/*py; cd ../")

mdFile = MdUtils(file_name="sources/cli", title="Command Line Interface")
mdFile.new_header(level=1, title="Overview")
mdFile.new_paragraph("`Your` comes with a set of command line scripts.")

list_of_strings = ["Script", "Description"]

for files in glob.glob("sources/bin/*md"):
    with open(files, "r") as f:
        text = f.read()
    text = text.replace("\n", " ")
    description = re.search(r"Description(.*?)\#", text).group(1).lstrip().rstrip()
    file_name = files.split("/")[-1][:-3] + ".py"
    file_link = "bin/" + os.path.basename(files)
    link = f"[{file_name}]({file_link})"
    list_of_strings.extend([link, description])
mdFile.new_line()
mdFile.new_table(
    columns=2, rows=len(list_of_strings) // 2, text=list_of_strings, text_align="left"
)
mdFile.create_md_file()
