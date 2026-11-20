CVAT docs samples: Sphinx edition
=================================

This is the reference page from my `CVAT docs samples
<https://gospelgit.github.io/cvat-docs-samples/>`_, rewritten in
reStructuredText and built with Sphinx. The main site uses MkDocs and
Markdown. I keep both so the same content can be compared across the two
toolchains.

The full set of pages follows `Diátaxis <https://diataxis.fr/>`_:

.. list-table::
   :header-rows: 1
   :widths: 20 50

   * - Type
     - Page
   * - Tutorial
     - `Build a COCO dataset with the Python SDK
       <https://gospelgit.github.io/cvat-docs-samples/sdk-coco-tutorial/>`_
   * - How-to guide
     - `Export a dataset with the REST API
       <https://gospelgit.github.io/cvat-docs-samples/rest-api-quickstart/>`_
   * - Reference
     - :doc:`reference` (this edition)
   * - Explanation
     - `Why exports run in the background
       <https://gospelgit.github.io/cvat-docs-samples/explanation-exports/>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents

   reference
