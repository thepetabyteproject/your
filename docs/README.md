# Your Documentation

The source for your documentation is in this directory.
Our documentation uses extended Markdown, as implemented by [MkDocs](http://mkdocs.org).

## Building the documentation

- Install requirements: `pip install -r requirements.txt`
- From the root directory, `cd` into the `docs/` folder and run:
    - `python autogen.py`
    - `mkdocs serve`    # Starts a local webserver:  [localhost:8000](http://localhost:8000)
    - `mkdocs build`    # Builds a static site in `site/` directory
    - `mkdocs gh-deploy` # To deploy the docs online
    