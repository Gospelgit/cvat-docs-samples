# CVAT docs samples

Two guides I wrote for [CVAT](https://www.cvat.ai), the open-source tool for labeling images and video for computer vision.

Both use the same small project: 11 photos of metal 3D printing defects, labeled as `crack` or `porosity` and exported as a COCO dataset. I ran every command and every line of code against CVAT Online in November 2026, and the outputs you see in the guides are from those runs.

## The guides

[**Python SDK tutorial**](sdk-coco-tutorial.md) goes from a folder of images to a labeled CVAT task, then exports it as COCO with one script. Start here if you work in Python.

[**REST API quickstart**](rest-api-quickstart.md) does the export with plain `curl`, and covers token auth and paging through results along the way. Use this one if you work in another language or want to see the raw HTTP calls.

## About these samples

I wrote these as writing samples for my application to CVAT's Technical Writer role. The source is on [GitHub](https://github.com/Gospelgit/cvat-docs-samples), and every change is built and link-checked automatically before it goes live.

Gospel Bassey · [LinkedIn](https://www.linkedin.com/in/gospel-bassey-31a225143)
