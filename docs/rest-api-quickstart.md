# CVAT REST API quickstart with cURL

The Python SDK covers most of what I need in CVAT. But sometimes you're working in another language, or you just want to see the actual HTTP calls going back and forth. This guide starts with logging in and listing tasks, then spends most of its time on exporting a dataset, which is the part with the most moving pieces.

Everything here is plain `curl`, so it should translate easily to whatever HTTP library you use.

It takes about 15 minutes.

## Before you start

You need a CVAT Online account and a Personal Access Token. If you don't have a token yet, create one under **Profile > Security**. The [SDK tutorial](sdk-coco-tutorial.md#step-1-get-an-access-token) walks through it.

You'll also want a task with some annotations on it. I'm using task `2781643` from the SDK tutorial, so swap in your own ID.

`curl` comes with macOS and Linux, and with Windows 10 onwards.

> **Windows users:** PowerShell has a `curl` command, but it's really `Invoke-WebRequest` under another name, and it doesn't take the same options. Type `curl.exe` instead, like the PowerShell examples below.

Put your token and the server address in variables, so you don't have to paste them into every command:

```bash
# macOS / Linux
export CVAT_ACCESS_TOKEN='<your-token>'
export CVAT_HOST='https://app.cvat.ai'
```

```powershell
# Windows PowerShell
$env:CVAT_ACCESS_TOKEN = "<your-token>"
$env:CVAT_HOST = "https://app.cvat.ai"
```

## Step 1: Log in with your token

There's no separate login call when you use a token. You send it with every request, in an `Authorization` header with `Bearer` in front:

```
Authorization: Bearer <your-token>
```

To check it works, ask the API who you are:

```bash
curl -s -H "Authorization: Bearer $CVAT_ACCESS_TOKEN" "$CVAT_HOST/api/users/self"
```

```powershell
curl.exe -s -H "Authorization: Bearer $env:CVAT_ACCESS_TOKEN" "$env:CVAT_HOST/api/users/self"
```

You get your user record back as JSON. Mine, trimmed down:

```json
{
  "url": "https://app.cvat.ai/api/users/489865",
  "id": 489865,
  "username": "gospel0",
  "groups": ["user"],
  "is_active": true,
  ...
}
```

If you get a `401` or "Authentication credentials were not provided", jump to [Troubleshooting](#troubleshooting).

### Read-only or read/write?

When you create a token, you pick whether it can change data. A read-only token is enough for steps 1 and 2, but not for step 3, because starting an export creates a job on the server. I'd use read-only tokens for dashboards and reports, and read/write ones for scripts that actually create or export things.

## Step 2: List your tasks, page by page

`GET /api/tasks` gives you your tasks. CVAT doesn't send a long list all at once. It splits it into pages, and you choose the page with two query parameters:

| Parameter | What it does |
| --- | --- |
| `page` | Which page to return, starting at 1 |
| `page_size` | How many items per page |

Here's the first page, two tasks at a time, newest first:

```bash
curl -s -H "Authorization: Bearer $CVAT_ACCESS_TOKEN" \
  "$CVAT_HOST/api/tasks?page=1&page_size=2&sort=-id"
```

```powershell
curl.exe -s -H "Authorization: Bearer $env:CVAT_ACCESS_TOKEN" "$env:CVAT_HOST/api/tasks?page=1&page_size=2&sort=-id"
```

Every list response comes back with the same four fields:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2781643,
      "name": "Metal AM defects",
      "size": 11,
      "status": "annotation",
      "jobs": { "count": 1, "completed": 0, ... },
      ...
    }
  ]
}
```

I only have one task, so it all fits on page 1 and `next` is `null`. With more tasks than `page_size`, `next` holds the full URL of page 2, something like `https://app.cvat.ai/api/tasks?page=2&page_size=2&sort=-id`.

| Field | Meaning |
| --- | --- |
| `count` | Total number of matching items across all pages |
| `results` | The items on this page |
| `next` | Full URL of the next page, or `null` on the last page |
| `previous` | Full URL of the previous page, or `null` on the first page |

If you want everything, keep following `next` until it comes back `null`. Don't work out page numbers yourself. If someone adds a task while you're paging, the numbers shift, but `next` stays right.

### Search and sort

Two more parameters are worth knowing:

- `search` looks for text in task names and other fields: `?search=defects`
- `sort` orders the results by a field, and a `-` in front flips it: `?sort=-id` is newest first, `?sort=name` is A to Z.

You can mix them: `?search=defects&sort=-id&page_size=10`.

## Step 3: Export a dataset

Big tasks can take a while to export, so CVAT does it in the background. You don't get the file back straight away. Instead you go back and forth with the server:

```
POST  /api/tasks/{id}/dataset/export   -->  you get a request ID (rq_id)
GET   /api/requests/{rq_id}            -->  repeat until status is "finished"
GET   result_url                       -->  download the zip
```

### 3a. Start the export

```bash
curl -s -X POST -H "Authorization: Bearer $CVAT_ACCESS_TOKEN" \
  "$CVAT_HOST/api/tasks/2781643/dataset/export?format=COCO%201.0&save_images=false"
```

```powershell
curl.exe -s -X POST -H "Authorization: Bearer $env:CVAT_ACCESS_TOKEN" "$env:CVAT_HOST/api/tasks/2781643/dataset/export?format=COCO%201.0&save_images=false"
```

A couple of things in that URL:

- `COCO%201.0` is just `COCO 1.0` with the space written as `%20`. A plain space breaks the URL.
- `save_images=false` exports the annotations only. Set it to `true` if you want the images in the zip too.

CVAT replies with a request ID:

```json
{ "rq_id": "action=export&target=task&target_id=2781643&user_id=489865&format=COCO_1~0&subresource=annotations" }
```

Copy the `rq_id` value, since you need it next.

It looks like a query string, but it's all one ID. Paste the whole thing into the next URL as it is, and keep the URL in quotes so your shell doesn't split it at the `&` signs.

### 3b. Check the status

```bash
curl -s -H "Authorization: Bearer $CVAT_ACCESS_TOKEN" "$CVAT_HOST/api/requests/<rq_id>"
```

```powershell
curl.exe -s -H "Authorization: Bearer $env:CVAT_ACCESS_TOKEN" "$env:CVAT_HOST/api/requests/<rq_id>"
```

The `status` field goes through these values:

| Status | Meaning |
| --- | --- |
| `queued` | Waiting for a worker |
| `started` | Export in progress. `progress` shows how far along |
| `finished` | Done. `result_url` holds the download link |
| `failed` | Something went wrong. `message` says what |

Check again every few seconds until it says `finished`. Mine:

```json
{
  "status": "finished",
  "message": "",
  "operation": { "type": "export:annotations", "task_id": 2781643, "format": "COCO 1.0", ... },
  "created_date": "2026-11-20T16:19:55.708737Z",
  "finished_date": "2026-11-20T16:19:56.158486Z",
  "expiry_date": "2026-11-21T16:19:56.158486Z",
  "result_url": "https://app.cvat.ai/api/tasks/2781643/dataset/download?rq_id=action%3Dexport%26target%3Dtask%26target_id%3D2781643...",
  ...
}
```

My export was small, so it finished in under a second and I saw `finished` on the first check.

Look at `expiry_date` too. The file is only kept for 24 hours after it's ready. After that, you start a new export.

### 3c. Download the file

The download link needs your token as well. Use `-o` to save it to a file and `-L` to follow any redirect:

```bash
curl -L -H "Authorization: Bearer $CVAT_ACCESS_TOKEN" -o defects_coco.zip "<result_url>"
```

```powershell
curl.exe -L -H "Authorization: Bearer $env:CVAT_ACCESS_TOKEN" -o defects_coco.zip "<result_url>"
```

Paste `result_url` exactly as CVAT gave it to you, with the `%3D` and `%26` bits left alone. curl shows a progress table while it downloads:

```
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100   4019 100   4019   0      0   4077      0                              0
```

My annotations-only export for 11 images came to about 4 KB. With `save_images=true` it'll be a lot bigger.

Open `defects_coco.zip` and your COCO annotations are in the `annotations` folder. It's the same file the SDK's `export_dataset()` gives you, because the SDK makes these exact calls behind the scenes.

## Troubleshooting

| What you see | Likely cause | Fix |
| --- | --- | --- |
| `401` or "credentials were not provided" | Missing `Bearer ` prefix, or the token variable is empty | Check the header, and run `echo $CVAT_ACCESS_TOKEN` (PowerShell: `echo $env:CVAT_ACCESS_TOKEN`) |
| PowerShell error mentioning `Invoke-WebRequest` or `-H` | You typed `curl` instead of `curl.exe` | Use `curl.exe` |
| `403` when starting an export | Your token is read-only | Create a read/write token |
| Format not found, or a `400` on export | Space in `COCO 1.0` not encoded, or the name is misspelled | Use `format=COCO%201.0` |
| Shell error, or only part of the URL gets sent | URL not in quotes, so the shell treats `&` as a command separator | Put the whole URL in double quotes |
| Status stays `queued` for minutes | The server is busy | Wait and check again. Large tasks take longer |
| Status is `failed` | Export error on the server | Read the `message` field in the status response |
| Downloaded file is tiny or won't open | You saved an error page instead of the zip | Run 3c again without `-o` to read the error |

## Next steps

If you'd rather work in Python, the [SDK tutorial](sdk-coco-tutorial.md) does the same export in one function call and turns it into a defect-detection dataset.

To explore every endpoint, open `<cvat_host>/api/swagger` on your server. It's an interactive API reference where you can try calls right in the browser.
