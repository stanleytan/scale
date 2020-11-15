# Scale Traffic Light Assignment

## Summary
I was able to collect the data from Scale's API and implemented some basic checks listed below (severity scores are either Medium (Med) or High (High)):
1. **Annotations with 25% or higher truncation must have the box touching an edge.**
> This was slightly difficult to correctly implement since image size does not entirely match the image itself; I added a small margin for error (2%).
2. **Annotations with non_visible_face must have not_applicable background color.**
> Straightforward and easy to implement.
3. **Annotation width/height/area must be practical: width/height must be >=5px and area <5% image size.**
> Image size between 3-5% raises the severity score to Medium.

The script takes the live API (live_74275b9b2b8b44d8ad156db03d2008ed) and a limit size of 100, both of which can be changed. The output is a JSON file named traffic_sign_detection_issues.json. The JSON format is listed below:
```
[
  {
    "task_id": "helloworld",
    "score": "High",
    "aggregated_annotation_data": [
      {
        "uuid": "someid",
        "score": "High",
        "issues": [
          "Truncation"
        ]
      },
      {
        "uuid": "randomid",
        "score": "High",
        "issues": [
          "Annotation > 5%"
        ]
      }
    ]
  },
  {
    "task_id": "goodbyeworld",
    "score": "High",
    "aggregated_annotation_data": [
      {
        "uuid": "anotherid",
        "score": "High",
        "issues": [
          "Non_visible_face background color must be not_applicable"
        ]
      }
    ]
  }
]
```
## Future plans for additional checks:
1. **Overlapping annotations must have at least one annotation occlusion % fit this formula: floor(overlapping area / annotation area).**
> E.g. If the overlap between annotation A and annotation B is 30% of A and 60% of B, either A has 25% occlusion or B has 50% occlusion. This is fairly time-consuming to implement since it would have to iterate through every image overlap.
2. **Annotation background color should be the majority of the annotation box.**
> Check pixels and find color plurality through classifying each pixel as one of the background colors.
3. **Annotations encompassed entirely by other annotations cannot have an occlusion of 100%.**
> E.g. Traffic light in front of a giant freeway sign. There may be extreme edge cases where the traffic light is blocked by something in front of it, but at that point, the traffic sign shouldn't be labeled.
4. **Follow-up to #3, annotations should not have 100% occlusion or 100% truncation.**
> If an annotation is covered up by more than 87.5%, it may not be useful to the model since it's a guess at that point, but this is a controversial decision.
