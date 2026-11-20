# Sphinx configuration for the reStructuredText edition of the CVAT docs samples.

project = "CVAT docs samples (Sphinx edition)"
author = "Gospel Bassey"
copyright = "2026, Gospel Bassey"

extensions = []

html_theme = "furo"
html_title = "CVAT docs samples"
html_theme_options = {
    "source_repository": "https://github.com/Gospelgit/cvat-docs-samples/",
    "source_branch": "main",
    "source_directory": "sphinx/",
}

exclude_patterns = ["_build"]
