# NotebookScraper

## Description

Made to scrape content from websites & dump it to files.
The output file format is made to be compatible with `notebooklm`.
This is ideal to recursively scrape content from a documentation website
and use it in a notebooklm project.

## How to use it

Fill the `doc-scraper.toml` file:

- One section per site to scrape
- In each section:
  - Provide a list of CSS selectors that will be used to scrape the content
  - Provide a list of CSS selectors to target links that the scraper will follow
A very simple example is provided in the `doc-scraper.toml.default` file.

Install the package in a virtual environment and source it, or via pipx.
Then run the following command:

```bash
scrap -c my-doc-scraper.toml -o ~/my/output/dir
```

## TODO

- [x] Remove `PDF` from the project name, dirs, files and code
- [x] Debug the python venv in the devcontainer
- [x] Add a console script and make sure the tool can be properly installed
