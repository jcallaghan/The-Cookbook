from getopt import getopt
from tarfile import TarError
from github import Github
from datetime import datetime, timedelta
import os, json, uuid, re, requests

context_dict = json.loads(os.getenv("CONTEXT_GITHUB"))
g = Github(context_dict["token"])
repo = context_dict["repository"]
repo = g.get_repo(repo)

commitMsgEmoji = "🧑🏼‍🍳 "
labelsToExcludeList = ["⚙ ","Meal / "]

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
        markdownContent = markdownContent + (f"date: " + issue.created_at.strftime('%Y-%m-%dT%H:%M:%S') + "\n")

        # Use regex to find any reference of serves in the body.
        serves = re.findall("- Serves: [+-]?\d+", issue.body)
        if len(serves) > 0:
            markdownContent = markdownContent + (f"serves: " + serves[-0].replace("- Serves: ","") + "\n") 

        # Use regex to find any reference of prep time in the body.
        prep_time = re.findall("- Prep Time: [+-]?\d+ \w+", issue.body)
        if len(prep_time) > 0:
            markdownContent = markdownContent + (f"prep_time: " + prep_time[-0].replace("- Prep Time: ","") + "\n") 

        # Use regex to find any reference of cook time in the body.
        cook_time = re.findall("- Cook Time: [+-]?\d+ \w+", issue.body)
        if len(cook_time) > 0:
            markdownContent = markdownContent + (f"cook_time: " + cook_time[-0].replace("- Cook Time: ","") + "\n") 

        # Use regex to find any reference of total time in the body.
        total_time = re.findall("- Total Time: [+-]?\d+ \w+", issue.body)
        if len(total_time) > 0:
            markdownContent = markdownContent + (f"total_time: " + total_time[-0].replace("- Total Time: ","") + "\n") 

        # Continue building our markdown content.
        markdownContent = markdownContent + (f"issue_id: " + str(issue.number) + "\n") 
        markdownContent = markdownContent + (f"issue_link: https://github.com/" + repo.full_name + "/issues/" + str(issue.number) + "\n") 
        markdownContent = markdownContent + (f"thumbnail: " + issue.title.replace(" ","-").lower() + ".jpg\n") 

        # Get any meal labels applied to the issue.
        mealLabelFound = False
        for label in issue.get_labels():
            if label.name.startswith("Meal / "):
                mealLabelFound = True
                mealLabels = mealLabels + (f"- " + str(label.name).replace("Meal / ","") + "\n") 
    
        if mealLabelFound:
            markdownContent = markdownContent + (f"meal_type:\n") 
            markdownContent = markdownContent + mealLabels

        # Get the labels applied to the issue excluding those in our exclude list.
        # //TODO sort labels and remove emoji and parent label?
        labelFound = False
        for label in issue.get_labels():
            if not label.name.startswith(tuple(labelsToExcludeList)):
                labelFound = True
                labels = labels + (f"- " + str(label.name).replace(" / "," - ") + "\n") 
    
        if labelFound:
            markdownContent = markdownContent + (f"labels:\n") 
            markdownContent = markdownContent + labels
    
        # Continue building our markdown content.
        markdownContent = markdownContent + (f"---\n\n") 
        markdownContent = markdownContent + (f"# " + issue.title + "\n\n")

        # //TODO replace any issue numbers in the related section with the issue title, issue number and the link to the issue.
        
        # Store the body markdown so we can replace any image paths.
        newBody = str(issue.body)

        # Find any markdown image tags.
        images = re.findall("(?:!\[(.*?)\]\((.*?)\))", issue.body)

        i = 1
        # If images were found upload image to repo.
        if len(images) > 0:
            for image in images:
                print("Found image (" + str(i) + ") - " + image[1])
                # Upload image from URL.
                newImage = upload_image(issue,image[1],i)
                # Replace URL reference with repo path.
                newBody = newBody.replace(image[1],repo.html_url + "/blob/main/" + newImage)
                i = i + 1

        # Add the new body to the markdown content to export.
        markdownContent = markdownContent + (f"" + newBody + "\n") 
        
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
        try:
            issueLabels.remove("⚙ Trigger Publishing")
        except:
            print("Trigger publishing label missing.")

        issueLabels.append("⚙ Published")

        # Update issue.
        issue.edit(labels=issueLabels,state='closed')
        #issue.edit(body=issueContent,labels=issueLabels)
      
    else:
        print("No issue found.")

def export_to_markdown(issue, content):
        
    # Remove non-alphanumeric characters.
    pattern = "[^0-9a-zA-ZÀ-ÿ]+"
    cleanTitle = re.sub(pattern, "-", issue.title)
    if cleanTitle[-1] == "-":
        cleanTitle = "".join(cleanTitle.rsplit("-",1))

    # Combine the issue title with the path to where recipes are saved.    
    exportFilePath = "recipes/" + cleanTitle.lower() + ".md"
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

def upload_image(issue,sourceImageUrl,sequence):
        
    # Remove non-alphanumeric characters.
    pattern = "[^0-9a-zA-ZÀ-ÿ]+"
    cleanTitle = re.sub(pattern, "-", issue.title)
    if cleanTitle[-1] == "-":
        cleanTitle = "".join(cleanTitle.rsplit("-",1))

    # Combine the issue title with the path to where recipes are saved.    
    targetImagePath = "recipes/images/" + cleanTitle.lower() + "-" + str(sequence) + ".jpg"

    print(targetImagePath)
    contents = ""
    sha = ""

    # See if a file exists already.
    try:
        contents = repo.get_contents(targetImagePath, ref="main")
        sha = contents.sha
    except:
        print("File doesn't exist doesn't exist or is too large.")

    if sha == "":
        sha = get_blob_content(repo,"main",targetImagePath)
        try:
            sha = sha.sha
        except:
            print()

    try:
        r = requests.get(sourceImageUrl)
        sourceImageContent = r.content
    except:
        print("File couldn't be found.")

    # Create or update the file accordingly.
    if sha == None:
        repo.create_file(targetImagePath, "🧑🏼‍🍳 " + issue.title + " image created #" + str(issue.number), sourceImageContent, branch="main")
        print("File " + targetImagePath + " created by markdown publishing automation.")
    else:
        repo.update_file(targetImagePath, "🧑🏼‍🍳 " + issue.title + " image updated #" + str(issue.number), sourceImageContent, sha, branch="main")
        print("File " + targetImagePath + " updated by markdown publishing automation.")  

    return(targetImagePath)

def get_blob_content(repo, branch, path_name):
    # First get the branch reference.
    ref = repo.get_git_ref(f'heads/{branch}')
    # Then get the tree.
    tree = repo.get_git_tree(ref.object.sha, recursive='/' in path_name).tree
    # Look for path in tree.
    sha = [x.sha for x in tree if x.path == path_name]
    if not sha:
        # Not found.
        return None
    # We have SHA.
    return repo.get_git_blob(sha[0])

if __name__ == '__main__':
    main()
