# FL24-CSE437S Semester Project by Mercy and Rylan

## Folder Structure
Top Directory, 'SemesterProject', is the **project folder/root directory**.
The virtual environment directory should be in the same directory with the project folder, and it should be ignored by GitHub as they are specific to developers' devices.
When we create a Django project by command line, say called 'SemesterProject', it will automatically create a sub directory with **the same name, which is called the main project folder (NOT the project folder/root directory, which is its parent dir)**. This main project folder should be on the same level with app folders. So I realized we were working on the wrong folder structure all time and created this new branch, moving all our previous work to it.

The correct folder structure looks like this:


## Features that will be added after the MVP production
Authentication: login/register success/ pop-up windows; login token validation; Forget your password feature; login form autocomplete
Homepage: Toggle light/dark themes; Webpage logo design;

Local museums place map: 
user should be able to adjust the search radius (50km max). When there's no available place in range, set up a reminder banner.

Local museums place list: some places might not have an official website. Currently, it always displays a ref link at the end of each place item. I'll add a conditional logic to that later; independent scrolling (from the map on the left);