from github import Github
from datetime import datetime, timedelta
import os
import json
import uuid

columnsToIgnore = ["Meal Planner Queue", "Pantry"]  # Columns to ignore in the project
project_name = "Meal Planner 📅"

def main():
    cardsfound = hasrecipes = False
    commitmsgemoji = "🧑🏼‍🍳 "
    icsfilepath = "resources/MealPlanner.ics"
    icsevents = icsevent = project = contents = ""

    # Ensure you have the context set correctly in the environment
    context_dict = json.loads(os.getenv("CONTEXT_GITHUB"))
    g = Github(context_dict["token"])
    repo = context_dict["repository"]
    repo = g.get_repo(repo)

    for repoProject in repo.get_projects():
        if project_name.lower() in (repoProject.name).lower():
            project = repoProject
            print("Found project: " + project.name + " (" + str(repoProject.id) + ")")

    if project == "":
        print(f"Project {project_name.lower()} not found. Check project name is correct and exists in repository.")
        quit()

    for column in project.get_columns():
        if column.name not in columnsToIgnore:
            recipes = []
            recipesdetail = []
            hasrecipes = False
            cardsfound = True
            for card in column.get_cards():
                if card.note:
                    recipetitle = card.note
                    recipemore = "Note: " + card.note
                    hasrecipes = True
                else:
                    issue = repo.get_issue(int(card.content_url.split('/')[-1]))
                    recipetitle = issue.title + " #" + str(issue.number)
                    recipemore = issue.title + " #" + str(issue.number) + " - " + issue.html_url
                    hasrecipes = True

                recipes.append(recipetitle)
                recipesdetail.append(recipemore)

            if hasrecipes:
                icseventtitle = ", ".join(recipes[:-1]) + " and " + recipes[-1] if len(recipes) > 1 else recipes[0]
                icseventbody = "\n".join(recipesdetail)

                print("- " + icseventtitle)

                icstodaydate = datetime.today().strftime("%Y%m%dT%H%M%S")
                icseventdate = datetime.strptime(column.name, "%a %d-%b %Y").strftime("%Y%m%d")

                icsevent = (f"BEGIN:VEVENT\n"
                            f"UID:{uuid.uuid4()}\n"
                            f"DTSTAMP:{icstodaydate}\n"
                            f"DTSTART:{icseventdate}T180000\n"
                            f"DTEND:{icseventdate}T200000\n"
                            f"SUMMARY:{icseventtitle} for dinner\n"
                            f"DESCRIPTION:{icseventbody}\n"
                            f"SEQUENCE:0\n"
                            f"LOCATION:\n"
                            f"TRANSP:TRANSPARENT\n"
                            f"END:VEVENT\n")

                icsevents += icsevent

    if icsevent and cardsfound:
        icsfilecontent = (f"BEGIN:VCALENDAR\n"
                          f"PRODID://James Callaghan\n"
                          f"VERSION:2.0\n"
                          f"X-WR-CALNAME:Meal Planner\n"
                          f"REFRESH-INTERVAL;VALUE=DURATION:P30M\n"
                          f"BEGIN:VTIMEZONE\n"
                          f"TZID:Europe/London\n"
                          f"BEGIN:DAYLIGHT\n"
                          f"TZOFFSETFROM:+0000\n"
                          f"TZOFFSETTO:+0100\n"
                          f"TZNAME:BST\n"
                          f"DTSTART:19700329T010000\n"
                          f"RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU\n"
                          f"END:DAYLIGHT\n"
                          f"BEGIN:STANDARD\n"
                          f"TZOFFSETFROM:+0100\n"
                          f"TZOFFSETTO:+0000\n"
                          f"TZNAME:GMT\n"
                          f"DTSTART:19701025T020000\n"
                          f"RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU\n"
                          f"END:STANDARD\n"
                          f"END:VTIMEZONE\n"
                          f"{icsevents}"
                          f"END:VCALENDAR")

        try:
            contents = repo.get_contents(icsfilepath, ref="main")
        except:
            print("ICS file doesn't exist.")
        
        if not contents:
            repo.create_file(icsfilepath, commitmsgemoji + "Created " + icsfilepath, icsfilecontent, branch="main")
            print(icsfilepath + " created.")
        else:
            repo.update_file(icsfilepath, commitmsgemoji + "Updated " + icsfilepath, icsfilecontent, contents.sha, branch="main")
            print(icsfilepath + " updated.")           

    if not cardsfound:
        print("No cards were found to generate an ICS file.")

if __name__ == '__main__':
    main()
