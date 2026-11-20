# Reference: SDK calls, API endpoints and script options

Everything the two guides on this site use, in one place. Values were checked against `cvat-sdk` 2.83.0 and CVAT Online in November 2026.

## Environment variables

| Variable | Read by | Meaning |
| --- | --- | --- |
| `CVAT_ACCESS_TOKEN` | CVAT SDK, `cvat-cli`, `defects_to_coco.py` | Personal Access Token. Create one under **Profile > Security** |
| `PASS` | CVAT SDK and `cvat-cli`, when `--auth USER` is given without a password | Password for the deprecated password sign-in |
| `CVAT_HOST` | `defects_to_coco.py` only | Server URL. Default: `https://app.cvat.ai` |

## Python SDK

Install with `pip install cvat-sdk`. Requires Python 3.11 or newer.

### `make_client`

```python
make_client(host, *, port=None, credentials=None, access_token=None) -> Client
```

| Parameter | Type | Description |
| --- | --- | --- |
| `host` | `str` | Server URL, for example `https://app.cvat.ai` |
| `port` | `int` | Optional. Server port |
| `credentials` | `tuple[str, str]` | Optional. Username and password |
| `access_token` | `str` | Optional. Personal Access Token |

Use it as a context manager: `with make_client(...) as client:`.

### `client.users.retrieve_current_user`

```python
client.users.retrieve_current_user()
```

Returns the signed-in user. Useful as a token check.

### `client.tasks.create_from_data`

```python
client.tasks.create_from_data(spec, resources, *, resource_type=ResourceType.LOCAL,
                              data_params=None, annotation_path="",
                              annotation_format="CVAT XML 1.1",
                              status_check_period=None, pbar=None) -> Task
```

| Parameter | Description |
| --- | --- |
| `spec` | A `models.TaskWriteRequest` with `name` and `labels` |
| `resources` | List of file paths or URLs |
| `resource_type` | `ResourceType.LOCAL` (default), `ResourceType.REMOTE` or `ResourceType.SHARE` |
| `data_params` | Optional. Extra data settings, as a dict |
| `annotation_path` | Optional. Annotations file to import after upload |
| `annotation_format` | Format of `annotation_path`. Default: `"CVAT XML 1.1"` |
| `status_check_period` | Seconds between upload status checks. Default: 5, from the client config |

Waits until the server finishes processing the upload, then returns the task.

### Label types

Pass one of these as `type` in `models.PatchedLabelRequest(name=..., type=...)`:

`rectangle`, `polygon`, `polyline`, `points`, `ellipse`, `cuboid`, `mask`, `tag`, `any`

Leaving `type` out allows any shape.

### `client.tasks.retrieve`

```python
client.tasks.retrieve(task_id) -> Task
```

### `Task.export_dataset`

```python
task.export_dataset(format_name, filename, *, include_images=True, location=None,
                    cloud_storage_id=None, status_check_period=None, pbar=None) -> Path | None
```

| Parameter | Description |
| --- | --- |
| `format_name` | Export format, matched exactly. For example `"COCO 1.0"` |
| `filename` | Where to save the zip |
| `include_images` | Put images in the zip. **Default: `True`** |
| `location` | `Location.LOCAL` (`"local"`) or `Location.CLOUD_STORAGE` (`"cloud_storage"`). Import from `cvat_sdk.core.proxies.types` |
| `cloud_storage_id` | Required when `location` is cloud storage |
| `status_check_period` | Seconds between status checks. Default: 5 |

## REST API

Every request needs the header `Authorization: Bearer <token>`.

| Method and path | Purpose |
| --- | --- |
| `GET /api/users/self` | The signed-in user |
| `GET /api/tasks` | List tasks, one page at a time |
| `POST /api/tasks/{id}/dataset/export` | Start a dataset export. Returns `rq_id` |
| `GET /api/requests/{rq_id}` | Status of a background request |
| `GET <result_url>` | Download a finished export. Needs the same header |

### `GET /api/tasks` query parameters

| Parameter | Description |
| --- | --- |
| `page` | Page number, starting at 1 |
| `page_size` | Results per page |
| `search` | Search term. Searches `assignee`, `name`, `owner`, `project_name`, `subset` and `tracker_link` |
| `sort` | Field to order by. Prefix with `-` for descending. Fields include `id`, `name`, `created_date`, `updated_date` and `status` |
| `filter` | JSON Logic filter for complex queries |
| `name`, `owner`, `status` | Exact-match filters on that field |

### List response

| Field | Description |
| --- | --- |
| `count` | Total matching items across all pages |
| `next` | URL of the next page, or `null` |
| `previous` | URL of the previous page, or `null` |
| `results` | Items on this page |

### `POST /api/tasks/{id}/dataset/export` query parameters

| Parameter | Description |
| --- | --- |
| `format` | Required. Export format, URL-encoded. For example `COCO%201.0` |
| `save_images` | Include images. **Default: `false`** |
| `filename` | Optional. Name for the exported file |
| `location` | Optional. Where to save the result |
| `cloud_storage_id` | Optional. Target cloud storage |

### Request object

Returned by `GET /api/requests/{rq_id}`.

| Field | Description |
| --- | --- |
| `status` | `queued`, `started`, `finished` or `failed` |
| `progress` | Progress of a started request |
| `message` | Error details when `status` is `failed` |
| `result_url` | Download link, once finished |
| `created_date`, `started_date`, `finished_date` | Timestamps |
| `expiry_date` | When the result is deleted. 24 hours after `finished_date` in testing |

## `defects_to_coco.py`

```
python defects_to_coco.py create IMAGE_DIR [--name NAME]
python defects_to_coco.py export TASK_ID [--out PATH]
```

| Command | Option | Default |
| --- | --- | --- |
| `create` | `IMAGE_DIR`: folder of `.jpg`, `.jpeg`, `.png` or `.bmp` files | Required |
| `create` | `--name`: task name | `Metal AM defects` |
| `export` | `TASK_ID`: task to export | Required |
| `export` | `--out`: path for the zip | `defects_coco.zip` |

Labels are fixed in the script as `crack` and `porosity`, both rectangles.
