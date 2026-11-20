# Why CVAT exports run in the background

The first time I exported a dataset through CVAT's REST API, I expected one request and a zip file back. Instead I got an ID, and had to ask again until the file was ready. This page explains why it works that way, and what that means when you're writing code against it.

## Exports can take a long time

An export isn't just a database read. CVAT has to collect every annotation in the task and convert it to the format you asked for. If you ask for images too, it has to pack them into the zip as well. For my 11 images that took under a second. For a task with thousands of high-resolution frames, it can take minutes.

An HTTP request that stays open for minutes is fragile. Proxies and load balancers time out, connections drop, and the client has no way to know how far along things are. So CVAT treats an export as a background job:

```
you:  start this export        -->  CVAT queues a job and gives you an ID
you:  how's it going?          -->  queued / started / finished / failed
you:  give me the file         -->  the zip
```

The [REST API quickstart](rest-api-quickstart.md) walks through those three calls.

## The request ID describes the job

The ID CVAT gave me looked like this:

```
action=export&target=task&target_id=2781643&user_id=489865&format=COCO_1~0&subresource=annotations
```

It isn't a random string. It reads as a description of the job: an export of task 2781643's annotations in COCO 1.0, requested by one user. That's also why it looks like a query string and catches people out. It's one ID, and it goes into the status URL as it is.

## Results don't last forever

When my export finished, the status response included an `expiry_date` exactly 24 hours after `finished_date`. After that the file is gone and you start a new export. If a pipeline exports at night and downloads in the morning, that's fine. If it exports on Friday and downloads on Monday, it isn't.

## The SDK does the waiting for you

The Python SDK's `export_dataset()` makes these same calls. It starts the export, checks the status every few seconds (5 by default, set by `status_check_period`), raises an error if the job fails, and downloads the result when it's done. From the outside it looks like one blocking call.

That's the right trade-off for most scripts. Going to the REST API directly makes sense when you're not in Python, or when you want to start many exports at once and collect them later instead of waiting on each one.

## One default to watch

The SDK and the REST API disagree on images by default:

| | Includes images by default? |
| --- | --- |
| SDK `export_dataset(include_images=...)` | Yes |
| REST `save_images` parameter | No |

So the same export can come back as a few kilobytes from one route and hundreds of megabytes from the other. Set the option explicitly either way, and your code won't depend on which default you happened to remember.

## See also

- [Reference](reference.md) for every parameter and status value
- [Python SDK tutorial](sdk-coco-tutorial.md) for the end-to-end workflow in Python
