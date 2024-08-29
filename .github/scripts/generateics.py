
import requests
import os
import json

GITHUB_API_URL = "https://api.github.com/graphql"
PROJECT_NAME = "Meal Planner"
COLUMNS_TO_IGNORE = ["Meal Planner Queue", "Pantry"]

def run_query(query, headers):
    request = requests.post(GITHUB_API_URL, json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed with status code {request.status_code}. Response: {request.text}")

def get_project_id(headers, repo_name):
    query = f'''
    query {{
      repository(owner: "{repo_name.split('/')[0]}", name: "{repo_name.split('/')[1]}") {{
        projectsV2(first: 100) {{
          nodes {{
            id
            title
          }}
        }}
      }}
    }}
    '''
    result = run_query(query, headers)
    projects = result["data"]["repository"]["projectsV2"]["nodes"]
    
    print("Projects found in the repository:")
    for project in projects:
        print(f" - {project['title']}")
        if PROJECT_NAME.lower() in project["title"].lower():
            return project["id"]
    return None

def get_project_items(headers, project_id):
    query = f'''
    query {{
      node(id: "{project_id}") {{
        ... on ProjectV2 {{
          items(first: 100) {{
            nodes {{
              id
              title: fieldValueByName(name: "Title") {{
                ... on ProjectV2ItemFieldValueText {{
                  text
                }}
              }}
              status: fieldValueByName(name: "Status") {{
                ... on ProjectV2ItemFieldValueText {{
                  text
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    result = run_query(query, headers)
    return result["data"]["node"]["items"]["nodes"]

def main():
    context_dict = json.loads(os.getenv("CONTEXT_GITHUB"))
    token = context_dict["token"]
    repo = context_dict["repository"]

    headers = {"Authorization": f"Bearer {token}"}

    project_id = get_project_id(headers, repo)
    if not project_id:
        print(f"Project '{PROJECT_NAME}' not found.")
        return

    items = get_project_items(headers, project_id)
    for item in items:
        title = item['title']['text'] if item['title'] else "No Title"
        status = item['status']['text'] if item['status'] else "No Status"
        print(f"Item: {title} - Status: {status}")

if __name__ == "__main__":
    main()
