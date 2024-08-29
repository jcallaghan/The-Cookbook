import requests
import os
import json
import re

GITHUB_API_URL = "https://api.github.com/graphql"
PROJECT_NAME = "Meal Planner"
COLUMNS_TO_IGNORE = ["Meal Planner Queue", "Pantry"]

def normalize_string(input_str):
    # Remove special characters and make the string lowercase
    return re.sub(r'[^a-zA-Z0-9 ]', '', input_str).strip().lower()

def run_query(query, headers):
    response = requests.post(GITHUB_API_URL, json={'query': query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}. Response: {response.text}")

def get_project_id(headers):
    query = '''
    query {
      viewer {
        projectsV2(first: 100) {
          nodes {
            id
            title
          }
        }
      }
    }
    '''
    result = run_query(query, headers)
    projects = result["data"]["viewer"]["projectsV2"]["nodes"]
    
    normalized_project_name = normalize_string(PROJECT_NAME)
    
    print("Projects found in the account:")
    for project in projects:
        normalized_title = normalize_string(project["title"])
        print(f" - {project['title']} (Normalized: {normalized_title}, ID: {project['id']})")
        if normalized_project_name in normalized_title:
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
    # Ensure the CONTEXT_GITHUB environment variable is set correctly
    context_json = os.getenv("CONTEXT_GITHUB")
    if not context_json:
        print("Error: CONTEXT_GITHUB environment variable is not set.")
        return
    
    context_dict = json.loads(context_json)
    token = context_dict.get("token")
    if not token:
        print("Error: GitHub token not found in CONTEXT_GITHUB.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}

    project_id = get_project_id(headers)
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
