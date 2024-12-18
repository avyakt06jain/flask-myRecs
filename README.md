# Flask Web Application (myRecs)

## Table of Contents
1. [Description](#description)
2. [Directories](#directories)
3. [What Each `.py` File Does](#what-each-py-file-does)
4. [Main Code](#main-code)
5. [Contributions](#contributions)
6. [License](#license)

## Description
**myRecs** is a simple Flask web application that allows users to manage and store records. The application features user authentication (login/logout), a homepage to view records, and a page for adding new records. It organizes different functionalities into separate modules using Flask Blueprints for better structure and scalability. 
With **myRecs**, users can:
- Log in to access the records
- View a list of stored records
- Add new records to the list
- Log out and clear session data
  
The application is designed to be easily deployable and customizable, providing a good foundation for a variety of web applications requiring record management.


## Directories
The project consists of the following directories and files:
- **main.py**: The entry point of the application
- **homepg.py**: Contains the home page blueprint
- **lgn.py**: Contains the login blueprint
- **recs.py**: Contains the records blueprint and the logic for adding/viewing records
- **addingrecs.py**: Contains the blueprint for adding records
- **lgout.py**: Contains the logout blueprint
- **data.py**: Stores the list of records in memory
- **templates/**: Directory for HTML templates used in the application (homepg.html, login.html, recs.html, addingrecs.html)

## What Each `.py` File Does
1. **main.py**: 
   - Initializes the Flask app and registers all blueprints (`homepg`, `lgn`, `recs`, `lgout`, `addingrecs`).
   - Also contains the secret key for sessions and runs the app.
2. **homepg.py**: 
   - Contains the blueprint for the homepage of the web application. This blueprint renders the home page when the user accesses the root route.
3. **lgn.py**: 
   - Contains the blueprint for the login page. It processes the login form and renders the login page.
4. **recs.py**: 
   - Handles the records page, where the user can add and view records. It also manages session data for the logged-in user and interacts with the `data.py` module to store records.
5. **addingrecs.py**: 
   - Provides functionality for the page where users can add new records. It renders the add records form.
6. **lgout.py**: 
   - Contains the logic to log out the user, clearing the session and redirecting the user to the home page.
7. **data.py**: 
   - Stores the records in memory as a list (`records_list`). It provides the data for the records page and allows new records to be added.

## Main Code
The main code of the application is located in the **main.py** file. This file initializes the Flask application, registers the blueprints for different routes, and runs the app.

## Contributions
Contributions to this project are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to your forked repository (`git push origin feature-branch`).
5. Open a pull request on the original repository.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
