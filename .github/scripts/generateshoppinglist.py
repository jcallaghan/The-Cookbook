from getopt import getopt
from github import Github
from datetime import datetime, timedelta
import os, json, uuid, re

columnsToIgnoreList = ["Meal Planner Queue"]    # Columns to ignore in the project
excludeLinesList = ["http","![image]","[","ingredientsShoppingListDict","#"]
markdownIngredientLinesList = ["* ","- "]
measuresList = ["tsp","tbsp","g","kg","ml","l","cup","lb","oz"]

pantryMisc = ["butter","water","chicken stock","garlic cloves"]
pantryBaking = ["baking soda","baking powder","caster sugar","cornflour","corn flour","plain flour","self-raising flour","self raising flour","flour","light brown sugar"]
pantryHerbsSpicesList = ["seasoning","sea salt","salt","black pepper","white pepper","bay leaf","curry powder","cumin","dried basil","dried oregano","fennel seeds","cloves","green cardamon","star anise","mustard seeds","garam masala","turmeric powder","turmeric","crushed chillies","smoked paprika","garlic powder","chipotle chilli flakes","sesame seeds","shichimi powder"]
pantrySaucesList = ["worcestershire sauce","soy sauce","light soy sauce","tomato purée","tomato puree","tomatoes","béchamel sauce","bechamel sauce"]
pantryVinegarsOilsList = ["sesame oil","vegetable oil","sunflower oil","cooking oil","coconut oil","olive oil"]
pantryIngredientsList = pantryMisc + pantryBaking + pantryHerbsSpicesList + pantrySaucesList + pantryVinegarsOilsList

pantryingredientsShoppingListDictUsedList = []

commitMsgEmoji = "🧑🏼‍🍳 "
exportFilePath = "resources/ShoppingList.md"

context_dict = json.loads(os.getenv("CONTEXT_GITHUB"))
g = Github(context_dict["token"])
repo = context_dict["repository"]
repo = g.get_repo(repo)

project_name = "Meal Planner"

notesList = []
columnsList = []
ingredientsShoppingListDict = {}
mealPlannerDict = {}

def get_shopping_list_from_meal_planner(project):
    
    # Loop through our project columns.
    for column in project.get_columns():
        # Ignore any columns in our ignore list.
        if not column.name in columnsToIgnoreList:
            columnsList.append(column.name)
            # Lopp through each card in the column.
            for card in column.get_cards():
                # Catch any notesList.
                if card.note != None:
                    # Save the note to our notesList list.
                    notesList.append(card.note)
                else:
                    # Get the issue number from the cards content url by removing the url up to the issue number.
                    issue = repo.get_issue(int((card.content_url).replace("https://api.github.com/repos/" + repo.full_name + "/issues/","")))
                    # Get the ingredientsShoppingListDict for this issue.
                    get_ingredients_from_issue(issue)   # //TODO see if the ingredientsShoppingListDict can be returned by this function.
                    # Save the issue to our meal planner dictionary and save other issue attributes as child dictionaries.
                    mealPlannerDict[issue.number] = {'date':column.name,'number':issue.number,'title':issue.title,'body':issue.body,'ingredientsShoppingListDict':''}

def pluralise_ingredient(ingredient):
    # //TODO Consider replacing with function # https://www.codespeedy.com/program-that-pluralize-a-given-word-in-python/
    # When I looked at this I didn't think it would work - I think I read it with chilli/chillies in mind.    

    ingredient = re.sub(r"\bonion\b","onions",ingredient.lower())
    ingredient = re.sub(r"\bclove\b","cloves",ingredient.lower())
    ingredient = re.sub(r"\bcarrot\b","carrots",ingredient.lower())
    ingredient = re.sub(r"\bpepper\b","peppers",ingredient.lower())
    ingredient = re.sub(r"\bchilli\b","chillies",ingredient.lower())
    ingredient = re.sub(r"\banchovy\b","anchovies",ingredient.lower())
    ingredient = re.sub(r"\bshallot\b","shallots",ingredient.lower())
    ingredient = re.sub(r"\bsalt and pepper to taste\b","seasoning",ingredient.lower())
    ingredient = re.sub(r"\bsalt and peppers to taste\b","seasoning",ingredient.lower())
    ingredient = re.sub(r"\bsalt and peppers\b","seasoning",ingredient.lower())
    ingredient = re.sub(r"\begg\b","eggs",ingredient.lower())
    return ingredient

def get_ingredients_from_issue(issue):

    issueBody = issue.body      
    headingType = ""
    findInHeading = "ingredients"       
    
    # Loop through each line in the issue body.
    for line in issueBody.split("\n"):
        # Check to see if line matches the heading we are looking for.
        if findInHeading in line.lower() and headingType == "":
            # We can now determine the markdown heading type/level used.
            headingType = line.lower().partition(" " + findInHeading)[0].lstrip()

    # Proceed if the heading was found.
    if headingType != "":

        # Split the issue body by the heading type/level we found above.
        issueBodyHeadings = issueBody.split(headingType.strip() + " ",1)

        # Loop through each of the headings we split.
        for heading in issueBodyHeadings:

            # Loop through each of the lines in the heading block.
            for line in heading.splitlines():

                # Reset the variables we need for every ingredient we expect.
                ingredientLine = measurement = ingredient = measurementJoin = ""

                # If the line starts with our heading then ignore the line.
                if line.strip().lower().startswith(headingType.strip() + " "):
                    break
                else:
                    # Check to see if the ingredient line matches one that we'd typically expect from markdown text (not blank, not link, starts with a list character)
                    if not line.strip().lower().startswith(tuple(excludeLinesList)) and line.strip() != "" and line.strip().lower().startswith(tuple(markdownIngredientLinesList)): 

                        # Remove any markdown lists by doing a blank replace on them when we find them.
                        ingredientLine = line 
                        for item in markdownIngredientLinesList:
                            ingredientLine = ingredientLine.replace(item,"")

                        # Check if the ingredient item starts with a number, if so we know we have a quantity or measure of an ingredient.
                        if ingredientLine[:1].isnumeric():  

                            # Lets use our measures list to identify if the quantity or measure is a measurement we expect such as tbsp or lb.
                            for measure in measuresList:        

                                # We assume no measurement until we find one.
                                measurement = ""                                    
                                # To avoid our measurements clashing with words like l in farfalle we pad the measurement with spaces either side as we'd expect to find it 2 tbsp butter.
                                # //TODO we should add the leading and trailing spaces in the measures list as we would expect them.
                                measure = " " + measure + " "                       
                               
                                # Check each of our measurements to see if it is in the ingredient line. 
                                if measure.lower() in ingredientLine.lower():      
                                    # If we find one we break out of the our measurements as we found the one we were looking for.
                                    measurement = measure.strip()                   
                                    break
                            
                            # Check we have a measurement.
                            if measurement != "":
                                # Split the ingredient from the measurement.
                                ingredient = str(ingredientLine.split(",")[-0]).split(measurement)[-1].strip()
                                # Split the measurement from the ingredient.
                                measurement = ingredientLine.split(measurement)[-0].strip() + " " + measurement.strip()
                            else:
                                # As we're looking for measurements with spaces either side it misses 50g or 100ml. 
                                # This splits based on the assumption the measure is the first word before the first space.
                                # If we find our ingredient includes an application such as seasoning, to taste then we remove it.
                                ingredient = str(ingredientLine.split(",")[-0].strip()).split(ingredientLine.split(" ")[-0].strip())[-1].strip()
                                # As we're looking for measurements with spaces either side it misses 50g or 100ml. 
                                # This splits based on the assumption the measure is the first word before the first space.
                                measurement = ingredientLine.split(" ")[-0].strip()

                        else:
                            # Our ingredient had no measure specified so we assume it is a wholeel ingredient like fresh parsley or seasoning.
                            # If we find our ingredient includes an application such as seasoning, to taste then we remove it.
                            ingredient = ingredientLine.split(",")[-0].strip()
                            measurement = ""

                # Check to see if we have saved the ingredient to our list already.
                if ingredient.lower() in ingredientsShoppingListDict:
                    # Check if the ingredient in the list has a measurement.
                    if ingredientsShoppingListDict[ingredient.lower()] != "" and measurement != "":
                        # Concatenate the saved measurement with our new measurement.
                        measurementJoin = ingredientsShoppingListDict[ingredient.lower()] + " + " + measurement
                    else:
                        # If the ingredient in the list has no measure then we just add our measurement.
                        measurementJoin = measurement
                    # Update the measure needed for ingredient in our list.
                    ingredientsShoppingListDict[ingredient.lower()] = measurementJoin
                else:
                    # Catch singular ingredients and replace them with their plural.
                    ingredient = pluralise_ingredient(ingredient)

                    # Check if the ingredient is in our pantry ingredient list.
                    if ingredient.lower().strip() in pantryIngredientsList:
                        # If it is then we assume we have it already.
                        # We add it to a seperate list to verify the pantry ingredients we have assumed are in stock.
                        pantryingredientsShoppingListDictUsedList.append(ingredient.lower().strip().capitalize())
                    else:
                        # Don't add an empty ingredient to ingredient list.
                        if ingredient != "":
                            # Add a new ingredient to our list along with the measurement required.
                            ingredientsShoppingListDict[ingredient.lower()] = measurement

def main():

    markdowncontent = ""

    # Find our meal planner project.
    for repoProject in repo.get_projects():
        if project_name.lower() in (repoProject.name).lower():
            project = repoProject
            print("Found project: " + project.name + " (" + str(repoProject.id) + ")")

    if project == "": print("Project " + project_name.lower() + " not found. Check project name is correct and exists in repository."); quit();
    
    get_shopping_list_from_meal_planner(project)

    print("\nSHOPPING LIST\n")
    markdowncontent = markdowncontent + (f"# Shopping List\n\n")

    print("Generated: " + datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
    markdowncontent = markdowncontent + (f"" + columnsList[-0] + " - " + columnsList[-1])
    markdowncontent = markdowncontent + (f"\n\nThis shopping list has been automatically generated with the ingredients from the recipes found in the meal planner project.\n")

    if len(mealPlannerDict) == 0: print("No recipes found in meal planner."); quit()

    print("\nMEAL PLANNER:")
    # Add heading to the markdown content block.
    markdowncontent = markdowncontent + (f"\n## 📅 Meal Planner\n\n") 
    markdowncontent = markdowncontent + (f"|📅 Date| 🍽️ Meal|\n")
    markdowncontent = markdowncontent + (f"|----|----|\n")

    date = ""
    for key, value in mealPlannerDict.items():
        if str(value["date"]) == date:
            print(" - " + str(value["title"]) + " #" + str(value["number"]))
            # Add meal to markdown content block.
            markdowncontent = markdowncontent + (f"||[" + str(value["title"]) + " #" + str(value["number"]) + "](https://github.com/" + repo.full_name + "/issues/" + str(value["number"]) + ")|\n")
        else:
            print("" + str(value["date"]))
            print(" - " + str(value["title"]) + " #" + str(value["number"]))
            # Add each meal to markdown content block.
            markdowncontent = markdowncontent + (f"|" + str(value["date"]) + "|[" + str(value["title"]) + " #" + str(value["number"]) + "](https://github.com/" + repo.full_name + "/issues/" + str(value["number"]) + ")|\n")
        date = value["date"]

    if len(ingredientsShoppingListDict) > 0:
        print("\nSHOPPING LIST: ")
        # Add heading to the markdown content block.
        markdowncontent = markdowncontent + (f"\n## 🛒 Shopping List\n\n") 
        markdowncontent = markdowncontent + (f"| 🍌 Ingredient| ⚖️ Measurement|\n")
        markdowncontent = markdowncontent + (f"|----------|-----------|\n")

        for key, value in sorted(ingredientsShoppingListDict.items()):

            if len(value) > 0:
                measurement = "" + value.strip()
            else:
                measurement = ""
            # This just lists the ingredient and the measure.
            print(" - " + key.capitalize() + measurement) 

            # Add each ingredient to markdown content block.
            #markdowncontent = markdowncontent + (f"1. [" + key.capitalize() + measurement + "](https://www.sainsburys.co.uk/gol-ui/SearchResults/" + key.capitalize().replace(" ","%20") + ")\n")
            markdowncontent = markdowncontent + (f"|[" + key.capitalize() + "](https://www.sainsburys.co.uk/gol-ui/SearchResults/" + key.capitalize().replace(" ","%20") + ")|" + measurement + "|\n")
        
    if len(notesList) > 0:

        print("\n NOTES:")
        # Add heading to the markdown content block.
        markdowncontent = markdowncontent + (f"\n## 🗒️ Notes\n\n") 

        for note in notesList:
            # Output any notesList to the console.
            print(" - " + note) 
            # Add the notesList to the markdown content block.
            markdowncontent = markdowncontent + (f"1. " + note + "\n")

    # Output the ingredientsShoppingListDict held list to a sorted list.
    pantryingredientsShoppingListDictUsed = list(map(str, sorted(set(pantryingredientsShoppingListDictUsedList))))

    # Check we have used pantry ingredientsShoppingListDict.
    if len(pantryingredientsShoppingListDictUsed) > 0:  
        if len(pantryingredientsShoppingListDictUsed) == 1: 
            # Just output the single pantry ingredient used.
            pantryingredientsShoppingListDictUsed = ", ".join(pantryingredientsShoppingListDictUsed) 
        if len(pantryingredientsShoppingListDictUsed) > 1:
            # Join al the pantry ingredientsShoppingListDict used and join the last one with an and to form a sentence.
            pantryingredientsShoppingListDictUsed = ", ".join(pantryingredientsShoppingListDictUsed[:-1]) + " and " + pantryingredientsShoppingListDictUsed[-1] + "." 

        # Output the pantry ingredientsShoppingListDict used to the console.
        print("\nPANTRY:\n" + pantryingredientsShoppingListDictUsed + "\n")  
        # This adds the pantry items to a markdown content block.
        markdowncontent = markdowncontent + (f"\n## 🏪 Pantry Ingredients\n\nThe following items have not been added to the shopping list as they are like in the pantry already.\n\n" + pantryingredientsShoppingListDictUsed + "\n")   
        markdowncontent = markdowncontent + (f"\n\n_This shopping list was generated at " + datetime.today().strftime('%d-%m-%Y %H:%M:%S') + "._")

    export_to_markdown(markdowncontent)

def export_to_markdown(content):

    contents = ""
    try:
        contents = repo.get_contents(exportFilePath, ref="main")
    except:
        print("File doesn't exist doesn't exist.")
    
    if contents == "":
        repo.create_file(exportFilePath, commitMsgEmoji + "Created " + exportFilePath, content, branch="main")
        print("File " + exportFilePath + " created.")
    else:
        repo.update_file(exportFilePath, commitMsgEmoji + "Updated " + exportFilePath, content, contents.sha, branch="main")
        print("File " + exportFilePath + " updated.")      

    print()

if __name__ == '__main__':
    main()
