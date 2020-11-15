import json
import requests
import scaleapi

from PIL import Image
from io import BytesIO

api_key = "live_74275b9b2b8b44d8ad156db03d2008ed"
proj_name = "Traffic Sign Detection"
task_size = "100"

client = scaleapi.ScaleClient(api_key)

tasklist = client.tasks(
    project = proj_name,
    limit = task_size
)

'''
For each task:
1. Ignore accepted/rejected tasks
2. If the task has an issue, add it to the resulting list, otherwise ignore it
3. Return the results as a JSON
'''

aggregated_task_data = []
for task in tasklist:
    # Check to see if it has been accepted/rejected
    if hasattr(task, "customer_review_status"):
        if task.customer_review_status == "rejected" or task.customer_review_status == "accepted":
            continue
    # Set score: Low. Failing a check escalates at least one tier: Low (L), Med (M), High (H).
    initial_score = "Low"
    task_id = task.task_id
    task_data = {
        "task_id": task_id,
        "score": initial_score,
        "aggregated_annotation_data": []
    }
    # Read image, get width and height
    attachment = task.params["attachment"]
    response = requests.get(attachment)
    image = Image.open(BytesIO(response.content))
    width, height = image.size
    area = width * height

    annotations = task.response["annotations"]
    for annotation in annotations:
        annotation_data = {
            "uuid": annotation["uuid"],
            "score": initial_score,
            "issues": []
        }
        # Check 1 (M/H): Overlapping annotations must have at least one annotation occlusion % fit this formula: floor(overlapping area / annotation area)
        # TODO
        # Check 2 (H): Annotations with >0% truncation must touch an edge of the image
        if annotation["attributes"]["truncation"] != "0%":
            if (annotation["left"] > width / 50 and annotation["left"] + annotation["width"] < width 
                    and annotation["top"] > height / 50 and annotation["top"] + annotation["height"] < height):
                annotation_data["score"] = "High"
                annotation_data["issues"].append("Truncation")
        # Check 3 (H): Annotations with non_visible_face label must have not_applicable background color
        if annotation["label"] == "non_visible_face":
            if annotation["attributes"]["background_color"] != "not_applicable":
                annotation_data["score"] = "High"
                annotation_data["issues"].append("Non_visible_face background color must be not_applicable")
        # Check 4 (M): Annotation width, height, or area are within certain sizes (adjustable)
        if annotation["width"] < 5 or annotation["height"] < 5:
            annotation_data["score"] = "High"
            annotation_data["issues"].append("Width/Height <5px")
        if annotation["width"] * annotation["height"] > area * 0.05:
            annotation_data["score"] = "High"
            annotation_data["issues"].append("Annotation > 5%")
        elif annotation["width"] * annotation["height"] > area * 0.03:
            if annotation_data["score"] == "Low":
                annotation_data["score"] = "Med"
            annotation_data["issues"].append("Annotation > 3%")
        # Add annotation data to list, update task severity to highest severity in list
        if annotation_data["score"] != "Low":
            task_data["aggregated_annotation_data"].append(annotation_data)
            # Update task severity if it is lower than annotation severity
            if annotation_data["score"] == "High" and task_data["score"] != "High":
                task_data["score"] = "High"
            elif task_data["score"] == "Low":
                task_data["score"] = "Med"
    if task_data["score"] != "Low":
        aggregated_task_data.append(task_data)

with open('traffic_sign_detection_issues.json', 'w') as json_file:
    json.dump(aggregated_task_data, json_file)