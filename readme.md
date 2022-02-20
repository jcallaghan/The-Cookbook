[![made-with-Markdown](https://img.shields.io/badge/Made%20with-Markdown-1f425f.svg)](http://commonmark.org)
[![GitHub Issues](https://img.shields.io/github/issues/jcallaghan/The-Cookbook.svg)](https://github.com/jcallaghan/The-Cookbook/issues/)
[![Closed Issues](https://img.shields.io/github/issues-closed/jcallaghan/The-Cookbook?label=)](https://github.com/jcallaghan/The-Cookbook/issues/)
[![Commits](https://img.shields.io/github/last-commit/jcallaghan/The-Cookbook)](https://github.com/jcallaghan/The-Cookbook/commits/)
![](https://img.shields.io/github/commit-activity/m/jcallaghan/The-Cookbook?label=activity)

[![Project column management](https://github.com/jcallaghan/The-Cookbook/actions/workflows/projectcolumnmanagement.yml/badge.svg)](https://github.com/jcallaghan/The-Cookbook/actions/workflows/projectcolumnmanagement.yml) 
[![Export project to ICS file](https://github.com/jcallaghan/The-Cookbook/actions/workflows/generateicsfile.yml/badge.svg)](https://github.com/jcallaghan/The-Cookbook/actions/workflows/generateicsfile.yml) 
[![Generate shopping list markdown file](https://github.com/jcallaghan/The-Cookbook/actions/workflows/generateshoppinglist.yml/badge.svg)](https://github.com/jcallaghan/The-Cookbook/actions/workflows/generateshoppinglist.yml)
[![Publish recipe](https://github.com/jcallaghan/The-Cookbook/actions/workflows/publishrecipe.yml/badge.svg)](https://github.com/jcallaghan/The-Cookbook/actions/workflows/publishrecipe.yml)

# I'm not a chef. I'm a geek who loves to cook great food!
[TLDR] This is a plain text (well, markdown) archive of all my favourite food and drinks recipes. Enjoy!

- [📅 Meal Planner](../../projects/10)
- [🛒 Shopping List](/resources/ShoppingList.md)
- [🧑‍🍳 All Recipes (published)](/index/all-recipes.md)
- [🍞 Bread](/index/bread.md)
- [🍥 Baking](/index/baking.md)
- [🔥 BBQ](/index/bbq.md)
- [🍝 Pasta](/index/pasta.md)
- [🍕 Pizza](/index/pizza.md)
- [🍲 Soup](/index/soups.md)
- [🍸 Cocktails and Drinks](/index/cocktails-and-drinks.md)
- [🔪 Equipment](/resources/equipment.md)
- [📖 Recipe Books](/resources/recipe-books.md)

## 👨🏼‍🍳 Background
For years I have snipped and saved recipes I come across and use. I have old written recipes, attempts at recipe books, recipes saved in OneNote, recipes I've published on my blog, pictures of pages from recipe books and countless recipe books with page markers. Still, I've never created a single archive of my recipes, from the staple weeknight dishes to challenging dishes I test myself with when hosting dinner parties. The main challenge is being able to find, search and explore all my recipes really easily.

## 🧰 Why Github 
I have so many recipes. Using GitHub just like I would with code felt like an ideal way to store the recipes. The entire repo is public, so my recipes are easy to share. All my recipe research is available alongside the recipe in an issue. I can access all the recipes (GitHub issues) using the GitHub app on my phone or, more often than not, on my Surface Pro X. The bonus with using [GitHub Issues](/issues) is I can leverage the label feature to easily categorise my recipes. This helps a lot when doing my weekly meal plan, and for this, I use a [GitHub Project](/projects/10) to provide me with a kanban board where I add recipes to each day over the next week. Once I'm happy with a recipe I close the issue and have a GitHub Action create a recipe file for me. 

### Feature call-outs
- Quick access to recipes that are easily shareable
- Project plan for my meal plan - with great API access too
- Tags
- Automation
- Weekly diggest
- Markdown!

## 🤓 The geeky chef 

The goal is to not get caught up with the formatting of the recipes and instead write them in markdown. I do try to write them consistently and leverage GitHub templates to help with the boiler plate for this. The first comment is typically my recipe, and the subsequent comments are research, alternative recipes or pictures for inspiration. Each recipe snip or photo is credited (where possible - DM for attribution).

I wanted to learn more about GitHub and other aspects of managing a large repo, such as GitHub Actions. I also want to learn more about Jekyll and Github pages. This repo will provide me with such opportunities. 

I hope to integrate this repo with other services such as Search, my calendar and a Tablet PC in the kitchen. Another benefit to storing my recipes in this repo is that I can automate tasks through my Smart Home automation using Home Assistant. This, for example, simplifies meal planning and reminds me if I need to defrost ingredients from the freezer and helps when I  do my weekly online food shop order. 

## 💖 Made with love 

I'll keep you updated with how I progress with all the geeky stuff, but for now, enjoy my recipes and be [nosy at what I'm currently planning to cook this week](../../projects/10)!

### //TODO
- [ ] Recipes to primary label markdown pages (indexes or categorisation)
- [x] ~Recipe issue primary comment to markdown recipe file (publish markdown file when issue is closed)~
- [x] ~Automatically create project columns in the meal planner~
- [x] ~Publish issues to .ical file~
- [x] ~Generate shopping list from meal planner~
- [ ] Website front-end (search and sharing)
- [ ] Power BI 'esque statistics from project recipes (analytics)

### Bugs
- Cannot search for issue to add to project column. These are typically issues that have been in the project before. They would have been removed by removing the column from the project. After this the issues in these columns are no longer returned when performing an issue search via the adding cards option.
