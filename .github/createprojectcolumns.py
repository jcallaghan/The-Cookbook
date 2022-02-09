from github import Github
from datetime import datetime, timedelta
import os
import json

columnsToIgnore = ["Meal Planner Queue"]    # Columns to ignore in the project
project_name = "Meal Planner"
timelinedaysahead = 10

def main():

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

    allcolumns = project.get_columns()

    try:
        lastcolumndate = datetime.strptime(allcolumns[allcolumns.totalCount-1].name,"%a %d-%b %Y")
    except:
        lastcolumndate = datetime.today()

    diffcolumnstocreate = lastcolumndate.date() - (datetime.today()).date()
    deltadays = timelinedaysahead - diffcolumnstocreate.days
                
    if deltadays > 0:
        print("\n Creating " + str(deltadays) + " new columns in the " + project.name + " project...")
    else:
        print("The " + project.name + " is up-to-date.")

    i = 1
    while i <= deltadays:
        td = timedelta(i)
        newcolumnname = (lastcolumndate + td).strftime("%a %d-%b %Y")
        print(" - " + newcolumnname)
        try:
            response = project.create_column(newcolumnname) #//TODO add try here to catch errors
        except:
            print("   ^ Error creating column.")
            
        i = i + 1

if __name__ == '__main__':
    main()
