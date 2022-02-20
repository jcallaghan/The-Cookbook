from getopt import getopt
from github import Github
from datetime import datetime, timedelta
import os, json, uuid, re

context_dict = json.loads(os.getenv("CONTEXT_GITHUB"))
g = Github(context_dict["token"])
repo = context_dict["repository"]
repo = g.get_repo(repo)

commitMsgEmoji = "🧑🏼‍🍳 "
labelsToExcludeList = ["⚙ ::: ","Meal ::: "]

def main():

    markdownContent = mealLabels = labels = ""

    workflow_triggered_by_issue = context_dict["event"]["issue"]["number"]
    issue = repo.get_issue(number=workflow_triggered_by_issue)

    # //TODO recipe markdown must include N headings (ingredients, method) and N optional headings (notes, pictures, related). Could check that these exist before proceeding.

    if issue != "":

        print("Found issue #" + str(issue.number) + ".")
        print("Title: " + issue.title)
        print("Generating recipe markdown...")

        # Start building our markdown content.
        markdownContent = (f"---\n") 
        markdownContent = markdownContent + (f"title: " + issue.title + "\n") 
        markdownContent = markdownContent + (f"date: " + datetime.today().strftime('%Y-%m-%dT%H:%M:%S') + "\n")

        # Use regex to find any reference of serves in the body.
        serves = re.findall("Serves: [+-]?\d+", issue.body)
        if serves != "":
            markdownContent = markdownContent + (f"serves: " + serves[-0].replace("Serves: ","") + "\n") 

        # Use regex to find any reference of prep time in the body.
        prep_time = re.findall("Prep time: [+-]?\d+ \w+", issue.body)
        if prep_time != "":
            markdownContent = markdownContent + (f"prep_time: " + prep_time[-0].replace("Prep time: ","") + "\n") 

        # Use regex to find any reference of cook time in the body.
        cook_time = re.findall("Cook time: [+-]?\d+ \w+", issue.body)
        if cook_time != "":
            markdownContent = markdownContent + (f"cook_time: " + cook_time[-0].replace("Cook time: ","") + "\n") 

        # Use regex to find any reference of total time in the body.
        total_time = re.findall("Total time: [+-]?\d+ \w+", issue.body)
        if total_time != "":
            markdownContent = markdownContent + (f"total_time: " + total_time[-0].replace("Total time: ","") + "\n") 

        # Continue building our markdown content.
        markdownContent = markdownContent + (f"issue_id: " + str(issue.number) + "\n") 
        markdownContent = markdownContent + (f"issue_link: https://github.com/" + repo.full_name + "/issues/" + str(issue.number) + "\n") 
        markdownContent = markdownContent + (f"thumbnail: " + issue.title.replace(" ","-").lower() + ".jpg\n") 

        # Get any meal labels applied to the issue.
        mealLabelFound = False
        for label in issue.get_labels():
            if label.name.startswith("Meal :::"):
                mealLabelFound = True
                mealLabels = mealLabels + (f"- " + str(label.name).replace("Meal ::: ","") + "\n") 
    
        if mealLabelFound:
            markdownContent = markdownContent + (f"meal_type:\n") 
            markdownContent = markdownContent + mealLabels

        # Get the labels applied to the issue excluding those in our exclude list.
        labelFound = False
        for label in issue.get_labels():
            if not label.name.startswith(tuple(labelsToExcludeList)):
                labelFound = True
                labels = labels + (f"- " + str(label.name).replace(" ::: "," - ") + "\n") 
    
        if labelFound:
            markdownContent = markdownContent + (f"labels:\n") 
            markdownContent = markdownContent + labels
    
        # Continue building our markdown content.
        markdownContent = markdownContent + (f"---\n\n") 
        markdownContent = markdownContent + (f"# " + issue.title + "\n\n")
        markdownContent = markdownContent + (f"" + str(issue.body) + "\n") 

        # //TODO replace any issue numbers in the related section with the issue title, issue number and the link to the issue.
        
        # //TODO consider uploading any image.githubusercontent.com images to the images directory and then replace them with repo/images path.
        
        # Export the recipe to a markdown file in the repo.
        path = export_to_markdown(issue, markdownContent)

        # Update the issue comment with the link to the markdown file. 
        # issueContent = (f"https://github.com/" + repo.full_name + "/tree/main/" + path + "\n\n")
        # issueContent = issueContent + str(issue.body)
        
        # In order to add a label we need to get the existing labels otherwise they will be lost.
        issueLabels = []
        for label in issue.labels:
            issueLabels.append(label.name)

        # Add the published label to the list of labels.
        issueLabels.remove("⚙ Trigger Published")
        issueLabels.append("⚙ ::: Markdown Published ✅")

        # Update issue.
        issue.edit(labels=issueLabels,state='closed')
        #issue.edit(body=issueContent,labels=issueLabels)

    else:
        print("No issue found.")

def export_to_markdown(issue, content):
    
    # Combine the issue title with the path to where recipes are saved.
    exportFilePath = "recipes/" + issue.title.replace(" ","-").lower() + ".md"
    contents = ""
    
    # See if a file exists already.
    try:
        contents = repo.get_contents(exportFilePath, ref="main")
    except:
        print("File doesn't exist doesn't exist.")
    
    # Create or update the file accordingly.
    if contents == "":
        repo.create_file(exportFilePath, "🧑🏼‍🍳 " + issue.title + " created #" + str(issue.number), content, branch="main")
        print("File " + exportFilePath + " created by markdown publishing automation.")
    else:
        repo.update_file(exportFilePath, "🧑🏼‍🍳 " + issue.title + " updated #" + str(issue.number), content, contents.sha, branch="main")
        print("File " + exportFilePath + " updated by markdown publishing automation.")  

    return(exportFilePath)

if __name__ == '__main__':
    main()
