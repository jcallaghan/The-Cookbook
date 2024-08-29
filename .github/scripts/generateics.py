import os
import requests
from datetime import datetime
import json
import uuid
from github import Github

# Get the token from environment variables
token = os.getenv("GITHUB_TOKEN")
if not token:
    print("GitHub token not found. Please set it in the .env file or as an environment variable.")
    exit(1)

# Initialize GitHub object
g = Github(token)

columnsToIgnore = ["Queue", "Pantry"]  # Columns to ignore in the project
project_name = "Meal Planner"

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%a %d-%b %Y")
        return True
    except ValueError:
        return False

def main():
    cardsfound = hasrecipes = False
    commitmsgemoji = "🧑🏼‍🍳 "
    icsfilepath = os.getenv("ICS_PATH", "resources/MealPlanner.ics")
    icsevents = icsevent = project = contents = ""

    # Define the GraphQL query to get the project
    query = """
    {
      viewer {
        projectsV2(first: 10) {
          nodes {
            id
            title
            url
            items(first: 100) {
              nodes {
                content {
                  ... on Issue {
                    title
                    number
                    url
                  }
                  ... on DraftIssue {
                    title
                  }
                }
                fieldValues(first: 10) {
                  nodes {
                    ... on ProjectV2ItemFieldTextValue {
                      text
                    }
                    ... on ProjectV2ItemFieldSingleSelectValue {
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    # Set the headers for the request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Make the request to the GitHub GraphQL API
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query},
        headers=headers
    )

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        projects = data['data']['viewer']['projectsV2']['nodes']
        
        # Debugging output: print the names of the projects retrieved
        print("Projects retrieved from GitHub:")
        for proj in projects:
            print(f" - {proj['title']} ({proj['id']})")
        
        for proj in projects:
            if project_name.lower() in proj['title'].lower():
                project = proj
                print(f"Found project: {proj['title']} ({proj['id']})")

        if not project:
            print(f"Project {project_name.lower()} not found. Check project name is correct and exists in repository.")
            return

        for item in project['items']['nodes']:
            print(f"Processing item: {item}")
            ignore_item = False
            for field in item['fieldValues']['nodes']:
                field_text = field.get('text') or field.get('name')
                if field_text:
                    field_text = field_text.strip()
                    if field_text in columnsToIgnore:
                        print(f"Ignoring item due to field: {field_text}")
                        ignore_item = True
                        break
            if ignore_item:
                continue

            for field in item['fieldValues']['nodes']:
                field_text = field.get('text') or field.get('name')
                if field_text:
                    field_text = field_text.strip()
                    if is_valid_date(field_text):
                        recipes = []
                        recipesdetail = []
                        hasrecipes = False
                        cardsfound = True
                        content = item['content']
                        if 'title' in content:
                            recipetitle = content['title']
                            recipemore = f"Note: {content['title']}"
                            hasrecipes = True
                        if 'number' in content:
                            recipetitle = f"{content['title']} #{content['number']}"
                            recipemore = f"{content['title']} #{content['number']} - {content['url']}"
                            hasrecipes = True

                        recipes.append(recipetitle)
                        recipesdetail.append(recipemore)

                        if hasrecipes:
                            recipesjoin = list(map(str, recipes))

                            if len(recipesjoin) == 1:
                                icseventtitle = ", ".join(recipesjoin)
                            if len(recipesjoin) > 1:
                                icseventtitle = ", ".join(recipesjoin[:-1])
                                icseventtitle = icseventtitle + " and " + recipesjoin[-1]

                            recipesdetailjoin = list(map(str, recipesdetail))
                            icseventbody = "\n".join(recipesdetailjoin)

                            print("- " + icseventtitle)

                            icstodaydate = datetime.today().strftime("%Y%m%dT%H%M%S")
                            icseventdate = datetime.strptime(field_text, "%a %d-%b %Y").strftime("%Y%m%d")

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

                            icsevents = icsevents + icsevent

        if icsevent != "" and cardsfound:
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

            if contents == "":
                repo.create_file(icsfilepath, commitmsgemoji + "Created " + icsfilepath, icsfilecontent, branch="main")
                print(icsfilepath + " created.")
            else:
                repo.update_file(icsfilepath, commitmsgemoji + "Updated " + icsfilepath, icsfilecontent, contents.sha, branch="main")
                print(icsfilepath + " updated.")

        if not cardsfound:
            print("No cards were found to generate an ICS file.")
    else:
        print(f"Query failed to run by returning code of {response.status_code}. {response.text}")

if __name__ == '__main__':
    main()
