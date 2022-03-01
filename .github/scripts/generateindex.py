from getopt import getopt
from github import Github
from datetime import datetime, timedelta
import os, json, uuid, re   

context_dict = json.loads(os.getenv("CONTEXT_GITHUB"))
g = Github(context_dict["token"])
repo = context_dict["repository"]
repo = g.get_repo(repo)

indexes = [
            {"Title": "All Recipes","Labels":"Published"},
            {"Title": "BBQ","Labels":"BBQ"},
            {"Title": "Pasta","Labels":"Pasta"},
            {"Title": "Soups","Labels":"Soup,Broth"}
        ]

# //TODO add baking, cocktails and drinks, pizza. These indexes currently have additional information I want to preserve and move elsewhere.

outputContent = ""

def main():
    
    # Generate index for each index defined above.
    for item in indexes:    
        indexName = item["Title"]
        searchList = item["Labels"]
        searchList = searchList.split(",")
        generate_index(indexName,searchList)

def generate_index(indexName,searchList):

    issuesList = []
    labelsList = []

    print("Generating index for " + indexName.lower() + "...\n")

    # Get all the labels in the repo.
    for label in repo.get_labels():
        # Add any labels that match our search list to a list.       
        if any(word in label.name for word in searchList):
            labelsList.append(label.name)

    # Add content to the markdown content block.
    outputContent = (f"# " + indexName + "\n\n")

    # Get issues for each of the labels we found.
    for label in labelsList:
        label = repo.get_label(label)
        # Get issues that are labelled with a label.
        issues = list(repo.get_issues(state="all", labels=[label]))
        for issue in issues:
            # Get each of the labels the issue has been labelled with.
            issueLabelsList = []
            for label in issue.get_labels():
                issueLabelsList.append(label.name)
            labelsText = ", ".join(issueLabelsList)
            # Add information about the issue to a list.
            issuesList.append({"number":issue.number,"title":issue.title,"labels":labelsText})

    # Add content to the markdown content block.
    outputContent = outputContent + (f"There are " + str(len(issuesList)) + " " + indexName.lower() + " recipes in the cookbook.\n\n")
    outputContent = outputContent + (f"| |Number|Recipe|Labels|\n")
    outputContent = outputContent + (f"|-|------|------|------|\n")

    indexString = ""
    
    # Make our list of issues unique.
    issuesListUnique = [dict(tuple) for tuple in {tuple(sorted(dict.items())) for dict in issuesList}]
    # Sort our list by the title of the issue.
    issuesListSorted = sorted(issuesListUnique, key=lambda d: d['title']) 
    for item in issuesListSorted:
        # Get the first character of the issue title.
        firstCharacter = item["title"][0]
        # If the first character of the issue title isn't the same as the previous one then we have a new section.
        if firstCharacter != indexString:
            print(firstCharacter.upper())
            # Add content to the markdown content block.
            outputContent = outputContent + (f"| " + firstCharacter.upper() + "||||\n")
        
        print(" - " + str(item["number"]) + " " + item["title"])

        # Add content to the markdown content block.
        outputContent = outputContent + (f"||")
        outputContent = outputContent + (f"[" + str(item["number"]) + "](" + repo.html_url + "/issues/" + str(item["number"]) + ")|")
        outputContent = outputContent + (f"[" + item["title"] + "](" + repo.html_url + "/blob/main/recipes/" + item["title"].replace(" ","-").lower() + ".md)|")
        outputContent = outputContent + (f"" + item["labels"].replace(", ","<br>") + "|")
        outputContent = outputContent + (f"\n")

        # Store the first character of the issue title for the next item.
        indexString = firstCharacter

    # Add content to the markdown content block.
    outputContent = outputContent + (f"\n_This index was automatically generated at " + datetime.today().strftime('%d-%m-%Y %H:%M:%S') + " using a custom Python script and GitHub Action._")

    # Export the markdown content to a file.
    export_to_markdown(indexName,outputContent)

def export_to_markdown(filename, content):
    
    # Combine the index name with the path to where these indexes are saved.
    exportFilePath = "index/" + filename.replace(" ","-").lower() + ".md"
    contents = ""
    
    # See if a file exists already.
    try:
        contents = repo.get_contents(exportFilePath, ref="main")
    except:
        print("\nFile doesn't exist doesn't exist.")
    
    # Create or update the file accordingly.
    if contents == "":
        repo.create_file(exportFilePath, "🧑🏼‍🍳 " + filename + " index created", content, branch="main")
        print("\nFile " + exportFilePath + " created by markdown index automation.")
    else:
        repo.update_file(exportFilePath, "🧑🏼‍🍳 " + filename + " index updated", content, contents.sha, branch="main")
        print("\nFile " + exportFilePath + " updated by markdown index automation.")  

    return(exportFilePath)

if __name__ == '__main__':
    main()
