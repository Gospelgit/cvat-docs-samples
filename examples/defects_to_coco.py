"""Turn a folder of defect images into a CVAT task, then export it as COCO.

Usage:
    export CVAT_ACCESS_TOKEN='<token>'
    python defects_to_coco.py create ./images --name "Metal AM defects"
    # annotate the task in the CVAT UI, then:
    python defects_to_coco.py export 12345 --out defects_coco.zip

Requires Python 3.11+ and `pip install cvat-sdk`.
"""

import argparse
import json
import os
import sys
import zipfile
from collections import Counter
from pathlib import Path

from cvat_sdk import make_client, models
from cvat_sdk.core.proxies.tasks import ResourceType
from cvat_sdk.core.proxies.types import Location

HOST = os.environ.get("CVAT_HOST", "https://app.cvat.ai")
LABELS = ["crack", "porosity"]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


def get_token() -> str:
    token = os.environ.get("CVAT_ACCESS_TOKEN")
    if not token:
        sys.exit("CVAT_ACCESS_TOKEN is not set. Create a token in CVAT under Profile > Security.")
    return token


def create_task(name: str, image_dir: Path) -> None:
    token = get_token()
    if not image_dir.is_dir():
        sys.exit(f"Folder not found: {image_dir}. Check the path, or cd into the folder that contains it.")
    images = sorted(p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
    if not images:
        sys.exit(f"No images found in {image_dir}")

    spec = models.TaskWriteRequest(
        name=name,
        labels=[models.PatchedLabelRequest(name=label, type="rectangle") for label in LABELS],
    )

    with make_client(HOST, access_token=token) as client:
        task = client.tasks.create_from_data(
            spec=spec,
            resources=images,
            resource_type=ResourceType.LOCAL,
        )

    print(f"Created task {task.id} with {len(images)} images.")
    print(f"Annotate it here: {HOST}/tasks/{task.id}")


def export_coco(task_id: int, out: Path) -> None:
    with make_client(HOST, access_token=get_token()) as client:
        task = client.tasks.retrieve(task_id)
        task.export_dataset("COCO 1.0", out, include_images=False, location=Location.LOCAL)

    print(f"Saved COCO annotations to {out}")
    summarize(out)


def summarize(zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        json_files = [n for n in zf.namelist() if n.startswith("annotations/") and n.endswith(".json")]
        if not json_files:
            sys.exit("No annotation JSON found in the export.")
        coco = json.loads(zf.read(json_files[0]))

    names = {c["id"]: c["name"] for c in coco["categories"]}
    counts = Counter(names[a["category_id"]] for a in coco["annotations"])

    print(f"{len(coco['images'])} images, {len(coco['annotations'])} boxes")
    for label in LABELS:
        print(f"  {label}: {counts.get(label, 0)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="create a task from a folder of images")
    p_create.add_argument("image_dir", type=Path)
    p_create.add_argument("--name", default="Metal AM defects")

    p_export = sub.add_parser("export", help="export a task as COCO 1.0")
    p_export.add_argument("task_id", type=int)
    p_export.add_argument("--out", type=Path, default=Path("defects_coco.zip"))

    args = parser.parse_args()
    if args.command == "create":
        create_task(args.name, args.image_dir)
    else:
        export_coco(args.task_id, args.out)


if __name__ == "__main__":
    main()
