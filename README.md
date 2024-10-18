# NotebookScraper

## Decription

Made to scrap content from webiste & dump it to files.
The output file format is made to be compatible with `notebooklm`.
This is ideal to recursively scrap content from a documentation website
and use it in a notebooklm project.

## How to use it

Fill the `doc-scraper.toml` file :

- One section per site to scrap
- In each section:
  - Provide a list of css selectors that will be used to scrap the content
  - Provide a list of css selectore to target links that the scraper will follow

## TODO

- [ ] Remove `PDF` from the project name, dirs, files and code
- [ ] Debug the python venv in the devcontainer
- [ ] Add a console script and make sure the tool can be properly installed
- [ ] Improve logging confguration & add a bit of tui user experience
