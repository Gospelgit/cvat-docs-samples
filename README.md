# CVAT docs samples

Documentation samples for [CVAT](https://www.cvat.ai), written and tested by Gospel Bassey.

**Read them here:** https://gospelgit.github.io/cvat-docs-samples/

Organised with [Diátaxis](https://diataxis.fr/):

- Tutorial: [Python SDK tutorial](docs/sdk-coco-tutorial.md), turning a folder of defect images into a labeled CVAT task and a COCO export
- How-to guide: [REST API quickstart](docs/rest-api-quickstart.md), with token auth, paging and dataset export using `curl`
- Reference: [SDK, API and script reference](docs/reference.md)
- Explanation: [Why exports run in the background](docs/explanation-exports.md)

Both guides use the same small project, 11 metal 3D printing defect images labeled `crack` or `porosity`. All commands and code were run against CVAT Online in November 2026.

## What's in here

```
docs/                     the guides, in Markdown
examples/defects_to_coco.py   the script the SDK tutorial walks through
mkdocs.yml                site settings
.github/workflows/docs.yml    builds the site, checks links, publishes to GitHub Pages
```

## Build the site locally

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Then open http://127.0.0.1:8000.

Every push to `main` builds the site with `mkdocs build --strict`, checks the script compiles, checks all links, and publishes to GitHub Pages. Pull requests get the same checks without publishing.
