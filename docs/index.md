# CVAT docs samples

Documentation I wrote for [CVAT](https://www.cvat.ai), the open-source tool for labeling images and video for computer vision.

Both use the same small project: 11 photos of metal 3D printing defects, labeled as `crack` or `porosity` and exported as a COCO dataset. I ran every command and every line of code against CVAT Online in November 2026, and the outputs you see in the guides are from those runs.

## How this site is organised

The pages follow [Diátaxis](https://diataxis.fr/), which splits documentation by what the reader needs at that moment:

| Type | Page | Read it when |
| --- | --- | --- |
| Tutorial | [Build a COCO dataset with the Python SDK](sdk-coco-tutorial.md) | You're new to CVAT and want a working result end to end |
| How-to guide | [Export a dataset with the REST API](rest-api-quickstart.md) | You know what you want and need the steps, in any language |
| Reference | [SDK, API and script reference](reference.md) | You need an exact parameter, default or status value |
| Explanation | [Why exports run in the background](explanation-exports.md) | You want to understand how exports work before building on them |

Keeping these apart means each page can do one job well. The tutorial doesn't stop to list every parameter, and the reference doesn't try to teach.

## About these samples

I wrote these as writing samples for my application to CVAT's Technical Writer role. The source is on [GitHub](https://github.com/Gospelgit/cvat-docs-samples), and every change is built and link-checked automatically before it goes live.

Gospel Bassey · [LinkedIn](https://www.linkedin.com/in/gospel-bassey-31a225143)
