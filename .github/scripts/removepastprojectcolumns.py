from github import Github
from datetime import datetime, timedelta
import os
import json

columnsToIgnore = ["Meal Planner Queue"]    # Columns to ignore in the project
project_name = "Meal Planner"

def main():

    columnsFound = False    # This is updated if columns are found and removed. Allows for message at end if still false.
    
    context_dict = json.loads(os.getenv("CONTEXT_GITHUB"))
    g = Github(context_dict["token"])
    repo = context_dict["repository"]
    repo = g.get_repo(repo)
     
    project = ""    
    for repoProject in repo.get_projects():
        if project_name.lower() in (repoProject.name).lower():
            project = repoProject
            print("Found project: " + project.name + " (" + str(repoProject.id) + ")")

    if project == "": print("Project " + project_name.lower() + " not found. Check project name is correct and exists in repository."); quit();

    for column in project.get_columns():
        if not column.name in columnsToIgnore:
            if datetime.strptime(column.name,"%a %d-%b %Y").date() < (datetime.today()).date():    # We need to convert the column name to a date and check if it is in the past.
                print("Removing column " + column.name + "...")
                columnsFound = True
                for card in column.get_cards():
                    card.delete()
                column.delete()

    if not columnsFound:
        print("No past columns were found or removed.")

if __name__ == '__main__':
    main()
