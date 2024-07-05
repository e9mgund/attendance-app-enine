# ATTENDANCE MANAGEMENT SYSTEM IN DJANGO

## Overview

This is an attendance management system implemented as a learning assignment to practice Django. This app utilizes Python and Django as the backend and HTML,CSS,Javascript and Bootstrap for the front end.

### Prerequisites

Before you begin, ensure you have the following installed:

- Python (3.6 or higher)
- Django (3.x recommended)

## Installation
1. Locate to the Directory in which you want to clone this repo.
2. Open terminal by,
    + In Linux systems : By pressing `Ctrl` + `Alt` + `T` keys.
    + In Windows systems : Right mouse click and choose option ***Open in terminal***.
3. Inside terminal Type and run :
```
git clone https://github.com/e9mgund/attendance-app-enine.git
```
4. Run ```cd attendance-app-enine``` to go inside the repository.
5. Update the submodules with ```git submodule update --init```.

6. Ensure that you have created a Virtual Environment , if not then ,
    + In Linux Systems : Run `/usr/bin/python3 -m venv env_name` statement into the Terminal.
    + In Windows Systems : You have to install a python module named ***virtualenv***. To install it run the statement `pip install virtualenv` in terminal. Now run `virtualenv env_name` .
7. Ensure that you have activated the virtual environment, if not then,
    + In Linux Systems : Run `source env_name/bin/activate` .
    + In Windows Systems : Run `env_name\Scripts\activate` .

8. Upgrade pip, `pip install --upgrade pip` .
9. Install all the neccesary requirements by `pip install -r requirements/dev.txt`
10. migrate the databse using `python3 manage.py migrate`.
11. Use the script below in the terminal of your editor to create users, first use `python3 manage.py shell`.Then run the script,
```
from apps.attendance.models import Employee
from django.contrib.auth.models import Userfor i in range(1,25):
     username="Employee"+str(i)
     a = User.objects.create(username=username,password="abcd@1234",email=username+"@email.com")
```
12. migrate the databse using `python3 manage.py makemigrations` and `python3 manage.py migrate`.
13. Create a superuser to access the admin panel with `python manage.py createsuperuser`.
14. Start the server with:
    + In Linux Systems : Run `python3 manage.py runserver` .
    + In Windows Systems : Run `py manage.py runserver` .
15. Set up a username, email and password. Go to a new tab, copy the base url and add a "admin/" endpoint to it.The url will look something like this `http:127.0.0.1:8000/admin/`.
16. Login to the admin panel using the credentials you created, Add employees and status inside the admin panel.
17. After creating a user, go to the app with the `http:127.0.0.1:8000/attendance/`.
18. Login with any user credentials.
