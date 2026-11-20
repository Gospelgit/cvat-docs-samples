Reference: SDK calls, API endpoints and script options
======================================================

Everything the CVAT docs samples use, in one place. Values were checked
against ``cvat-sdk`` 2.83.0 and CVAT Online in November 2026.

.. contents:: On this page
   :local:
   :depth: 1

Environment variables
---------------------

.. list-table::
   :header-rows: 1
   :widths: 20 35 45

   * - Variable
     - Read by
     - Meaning
   * - ``CVAT_ACCESS_TOKEN``
     - CVAT SDK, ``cvat-cli``, ``defects_to_coco.py``
     - Personal Access Token. Create one under :guilabel:`Profile > Security`.
   * - ``PASS``
     - CVAT SDK and ``cvat-cli``, when ``--auth USER`` is given without a
       password
     - Password for the deprecated password sign-in.
   * - ``CVAT_HOST``
     - ``defects_to_coco.py`` only
     - Server URL. Default: ``https://app.cvat.ai``.

Python SDK
----------

Install with ``pip install cvat-sdk``. Requires Python 3.11 or newer.

.. py:function:: make_client(host, *, port=None, credentials=None, access_token=None)

   Create a client connected to a CVAT server. Use it as a context manager:
   ``with make_client(...) as client:``.

   :param str host: Server URL, for example ``https://app.cvat.ai``.
   :param int port: Optional. Server port.
   :param credentials: Optional. Username and password.
   :type credentials: tuple[str, str]
   :param str access_token: Optional. Personal Access Token.
   :returns: A connected client.
   :rtype: Client

.. py:method:: client.users.retrieve_current_user()

   Return the signed-in user. Useful as a quick check that a token works.

.. py:method:: client.tasks.create_from_data(spec, resources, *, resource_type=ResourceType.LOCAL, data_params=None, annotation_path="", annotation_format="CVAT XML 1.1", status_check_period=None, pbar=None)

   Create a task and upload its data. Waits until the server has finished
   processing the upload, then returns the task.

   :param spec: Task name and labels.
   :type spec: models.TaskWriteRequest
   :param resources: File paths or URLs to upload.
   :param resource_type: ``ResourceType.LOCAL`` (default),
      ``ResourceType.REMOTE`` or ``ResourceType.SHARE``.
   :param dict data_params: Optional. Extra data settings.
   :param str annotation_path: Optional. Annotations file to import after
      upload.
   :param str annotation_format: Format of ``annotation_path``. Default:
      ``"CVAT XML 1.1"``.
   :param status_check_period: Seconds between status checks. Default: 5,
      from the client config.
   :returns: The new task.
   :rtype: Task

.. py:method:: client.tasks.retrieve(task_id)

   Return the task with the given ID.

   :param int task_id: Task ID.
   :rtype: Task

.. py:method:: Task.export_dataset(format_name, filename, *, include_images=True, location=None, cloud_storage_id=None, status_check_period=None, pbar=None)

   Export the task as a dataset and download it. Starts the export on the
   server, checks its status until it finishes, then saves the result.

   :param str format_name: Export format, matched exactly. For example
      ``"COCO 1.0"``.
   :param filename: Where to save the zip.
   :param bool include_images: Put images in the zip. **Default: True.**
   :param location: ``Location.LOCAL`` (``"local"``) or
      ``Location.CLOUD_STORAGE`` (``"cloud_storage"``). Import from
      ``cvat_sdk.core.proxies.types``.
   :param int cloud_storage_id: Required when ``location`` is cloud storage.
   :param status_check_period: Seconds between status checks. Default: 5.

.. note::

   The SDK includes images by default, but the REST API's ``save_images``
   parameter defaults to ``false``. Set the option explicitly on either route.

Label types
~~~~~~~~~~~

Pass one of these as ``type`` in
``models.PatchedLabelRequest(name=..., type=...)``:

``rectangle``, ``polygon``, ``polyline``, ``points``, ``ellipse``,
``cuboid``, ``mask``, ``tag``, ``any``

Leaving ``type`` out allows any shape.

REST API
--------

Every request needs the header ``Authorization: Bearer <token>``.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Method and path
     - Purpose
   * - ``GET /api/users/self``
     - The signed-in user.
   * - ``GET /api/tasks``
     - List tasks, one page at a time.
   * - ``POST /api/tasks/{id}/dataset/export``
     - Start a dataset export. Returns ``rq_id``.
   * - ``GET /api/requests/{rq_id}``
     - Status of a background request.
   * - ``GET <result_url>``
     - Download a finished export. Needs the same header.

``GET /api/tasks`` query parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Parameter
     - Description
   * - ``page``
     - Page number, starting at 1.
   * - ``page_size``
     - Results per page.
   * - ``search``
     - Search term. Searches ``assignee``, ``name``, ``owner``,
       ``project_name``, ``subset`` and ``tracker_link``.
   * - ``sort``
     - Field to order by. Prefix with ``-`` for descending. Fields include
       ``id``, ``name``, ``created_date``, ``updated_date`` and ``status``.
   * - ``filter``
     - JSON Logic filter for complex queries.
   * - ``name``, ``owner``, ``status``
     - Exact-match filters on that field.

List response
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Field
     - Description
   * - ``count``
     - Total matching items across all pages.
   * - ``next``
     - URL of the next page, or ``null``.
   * - ``previous``
     - URL of the previous page, or ``null``.
   * - ``results``
     - Items on this page.

``POST /api/tasks/{id}/dataset/export`` query parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Parameter
     - Description
   * - ``format``
     - Required. Export format, URL-encoded. For example ``COCO%201.0``.
   * - ``save_images``
     - Include images. **Default: false.**
   * - ``filename``
     - Optional. Name for the exported file.
   * - ``location``
     - Optional. Where to save the result.
   * - ``cloud_storage_id``
     - Optional. Target cloud storage.

Request object
~~~~~~~~~~~~~~

Returned by ``GET /api/requests/{rq_id}``.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Description
   * - ``status``
     - ``queued``, ``started``, ``finished`` or ``failed``.
   * - ``progress``
     - Progress of a started request.
   * - ``message``
     - Error details when ``status`` is ``failed``.
   * - ``result_url``
     - Download link, once finished.
   * - ``created_date``, ``started_date``, ``finished_date``
     - Timestamps.
   * - ``expiry_date``
     - When the result is deleted. 24 hours after ``finished_date`` in
       testing.

``defects_to_coco.py``
----------------------

.. code-block:: text

   python defects_to_coco.py create IMAGE_DIR [--name NAME]
   python defects_to_coco.py export TASK_ID [--out PATH]

.. list-table::
   :header-rows: 1
   :widths: 15 55 30

   * - Command
     - Option
     - Default
   * - ``create``
     - ``IMAGE_DIR``: folder of ``.jpg``, ``.jpeg``, ``.png`` or ``.bmp``
       files
     - Required
   * - ``create``
     - ``--name``: task name
     - ``Metal AM defects``
   * - ``export``
     - ``TASK_ID``: task to export
     - Required
   * - ``export``
     - ``--out``: path for the zip
     - ``defects_coco.zip``

Labels are fixed in the script as ``crack`` and ``porosity``, both
rectangles.
