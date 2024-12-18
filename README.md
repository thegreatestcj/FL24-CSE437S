# FL24-CSE437S Semester Project by Rylan Tang

12/18/24: I re-push this semester project to my own GitHub profile.

## Folder Structure
Top Directory, 'SemesterProject', is the **project folder/root directory**.
The virtual environment directory should be in the same directory with the project folder, and it should be ignored by GitHub as they are specific to developers' devices.
When we create a Django project by command line, say called 'SemesterProject', it will automatically create a sub directory with **the same name, which is called the main project folder (NOT the project folder/root directory, which is its parent dir)**. This main project folder should be on the same level with app folders. So I realized we were working on the wrong folder structure all time and created this new branch, moving all our previous work to it.


## Features that will be added after the MVP production
Authentication: 

login/register success/ pop-up windows (make it more user-friendly); login token validation; Forget your password feature; login form autocomplete; replace traditional FBV with CBV with REST framework APIViews; **CSRF token**.

Homepage: Toggle light/dark themes; Webpage logo design;

Local museums place map: 

user should be able to adjust the search radius (50km max). When there's no available place in range, set up a reminder banner.

May use different graphics for museums and galleries after MVP production.

**IMPORTANT ASYNC HANDLING: the event-view and place-view buttons will trigger event and place markers on the map, but these two functions require the map and places parameters. We need to make sure that the buttons will work only if the map and nearby places are successfully loaded.**

Local museums place list: 

**Make the Places/Events buttons fixed on the top w/ independent scrolling on the side bar.**
some places might not have an official website. Currently, it always displays a ref link at the end of each place item. I'll add a conditional logic to that later; independent scrolling (from the map on the left);

Nearby event list:

We might add an event list item detail page to show up after user clicks an item in the event list.

## Features that will be added after the Beta Production
All expectations above for the Beta ver completed.
See the updated Kanban PR in GitHub Projects


