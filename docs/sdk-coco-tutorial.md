# Turning defect images into a COCO dataset with the CVAT Python SDK

I wanted a quick way to get a folder of metal 3D printing defect images into CVAT, label them, and pull the labels back out as COCO so I could train on them. Clicking through the web UI is fine for a handful of images. Past that, I'd rather script it. This is how I did it with the CVAT Python SDK.

It took me about 20 minutes, not counting the time spent drawing boxes.

## What you'll end up with

```
folder of images --> CVAT task (labels: crack, porosity) --> annotate in UI --> COCO 1.0 zip
```

The script has two commands. `create` uploads your images and sets up the labels. `export` pulls the finished annotations back down and counts the boxes per label, which is a handy check before you train anything.

## Before you start

You'll need Python 3.11 or newer, since the SDK doesn't support older versions. You also need a free [CVAT Online](https://app.cvat.ai) account, though a self-hosted server works too.

For images, any `.jpg` or `.png` files will do. I used 11 photos of surface defects from metal 3D printing.

Install the SDK:

```bash
pip install cvat-sdk
```

## Step 1: Get an access token

You can log in with your username and password, but I'd go with a Personal Access Token instead. If it ever leaks, you revoke the token and your password stays safe. It also keeps credentials out of your code.

1. In CVAT, go to **Profile > Security**.
2. Create a token and copy it straight away. CVAT only shows it once.
3. Save it as an environment variable:

```bash
# macOS / Linux
export CVAT_ACCESS_TOKEN='<your-token>'
```

```powershell
# Windows PowerShell
$env:CVAT_ACCESS_TOKEN = "<your-token>"
```

On a self-hosted server, set `CVAT_HOST` as well, for example `export CVAT_HOST='http://localhost:8080'`. If you don't set it, the script uses `https://app.cvat.ai`.

## Step 2: Connect to CVAT

Every SDK session starts with `make_client`. I use it in a `with` block so the connection closes when I'm done. Printing your username is the easiest way to check the token actually works:

```python
import os
from cvat_sdk import make_client

with make_client("https://app.cvat.ai", access_token=os.environ["CVAT_ACCESS_TOKEN"]) as client:
    user = client.users.retrieve_current_user()
    print(f"Logged in as {user.username}")
```

## Step 3: Create a task with labels

In CVAT, a task is your images plus the labels people can draw with. You define both and pass them to `create_from_data`:

```python
from pathlib import Path
from cvat_sdk import models
from cvat_sdk.core.proxies.tasks import ResourceType

images = sorted(Path("images").glob("*.jpg"))

spec = models.TaskWriteRequest(
    name="Metal AM defects",
    labels=[
        models.PatchedLabelRequest(name="crack", type="rectangle"),
        models.PatchedLabelRequest(name="porosity", type="rectangle"),
    ],
)

task = client.tasks.create_from_data(
    spec=spec,
    resources=images,
    resource_type=ResourceType.LOCAL,
)
print(f"Created task {task.id}")
```

Some notes on this:

- `type="rectangle"` means bounding boxes only. For segmentation, use `"polygon"` or `"mask"`. If you leave `type` out, any shape is allowed.
- `ResourceType.LOCAL` uploads from your own machine. CVAT can also pull images from URLs or cloud storage.
- `create_from_data` waits until CVAT has finished processing the upload, so you can use `task.id` right away.

To run the full script instead, first `cd` into the folder that holds the script and your `images` folder. `./images` is read relative to wherever your terminal is, and that caught me out the first time.

```bash
cd path/to/your/project        # Windows: cd C:\Users\<you>\project
python defects_to_coco.py create ./images --name "Metal AM defects"
```

Here's what I got:

```
Created task 2781643 with 11 images.
Annotate it here: https://app.cvat.ai/tasks/2781643
```

## Step 4: Draw the boxes

Open the link the script printed, click into the job and draw your boxes. Remember to save, because unsaved boxes won't show up in the export.

You can't really script this part, since you don't have labels yet. If you already have a model, the auto-annotation API can do a first pass for you. There's more on that in [Next steps](#next-steps).

## Step 5: Export as COCO

Get the task by its ID and call `export_dataset`:

```python
from cvat_sdk.core.proxies.types import Location

task = client.tasks.retrieve(2781643)  # your task ID from step 3
task.export_dataset(
    "COCO 1.0",
    "defects_coco.zip",
    include_images=False,
    location=Location.LOCAL,
)
```

`include_images` is `True` by default, so the zip gets every image unless you say otherwise. I already had the images on my machine, so I turned it off. Leave it on if you're sending the dataset to someone who doesn't have them.

The format name has to match CVAT's list exactly, version number included. `"COCO 1.0"` works, but `"COCO"` on its own won't.

With the script:

```bash
python defects_to_coco.py export 2781643 --out defects_coco.zip
```

## Step 6: Check what you exported

I like to look inside the zip before training on it. The script opens it, reads the COCO JSON and counts the boxes per label:

```python
import json, zipfile
from collections import Counter

with zipfile.ZipFile("defects_coco.zip") as zf:
    name = next(n for n in zf.namelist() if n.startswith("annotations/") and n.endswith(".json"))
    coco = json.loads(zf.read(name))

names = {c["id"]: c["name"] for c in coco["categories"]}
print(Counter(names[a["category_id"]] for a in coco["annotations"]))
```

My run:

```
Saved COCO annotations to defects_coco.zip
11 images, 11 boxes
  crack: 4
  porosity: 7
```

If a label shows zero boxes, it's usually spelled differently in the task, or the job never got saved.

## Troubleshooting

| What you see | Likely cause | Fix |
| --- | --- | --- |
| `401 Unauthorized` | Token missing, mistyped or revoked | Check `echo $CVAT_ACCESS_TOKEN`, or create a new token |
| `CVAT_ACCESS_TOKEN is not set` | Variable set in a different terminal | Set it in the same terminal you run the script from |
| `Folder not found: images` | Terminal is in a different folder from your images | `cd` into the folder that contains `images`, or pass the full path |
| Export fails with an unknown format | Format name doesn't match exactly | Use `"COCO 1.0"`, version included |
| `SyntaxError` or install fails | Python older than 3.11 | Run `python --version` and upgrade |
| Zip is huge | `include_images` left at its default | Pass `include_images=False` |

## Next steps

- If you train in PyTorch, you can skip the export step entirely. Install `cvat-sdk[pytorch]` and `cvat_sdk.pytorch` will load the task as a PyTorch `Dataset`.
- If you already have a model, the auto-annotation API (`cvat_sdk.auto_annotation`) can pre-label a task, so you only fix its mistakes instead of drawing every box.

The full script is in [`examples/defects_to_coco.py`](https://github.com/Gospelgit/cvat-docs-samples/blob/main/examples/defects_to_coco.py).
