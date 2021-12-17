# CCNY_Database_Project

## Requirements 

- [Python](https://www.python.org/downloads/)
- Free Spotify account to access [developer tools](https://developer.spotify.com/dashboard/)
- [MySQL Workbench](https://dev.mysql.com/doc/workbench/en/wb-windows.html)

## Instructions to run on your computer

1. Set up python virtual environment: 
    
    Create environment: `python3 -m venv env`

    Activate environment:

    - on Windonws: `env\Scripts\activate`

    - on Mac: `env/bin/activate`

2. Install required packages: `pip install -r requirements.txt`

3. Run `project_schema.sql` in MySQL workbench to create database and tables.

4. In flask_app folder, create a `.env` file with the following variables:
    - SECRET_KEY = 

    Key of your choice 

    - DATABASE_HOST = 
    - DATABASE_USER = 
    - DATABASE_PASS = 
    - DATABASE_SCHEMA = csc336_project

    Your MySQL login credentials.

    - SPOTIFY_CLIENT_ID = 
    - SPOTIFY_CLIENT_SECRET = 

    Create an app in your Spotify developer dashboard and use the client id and client secret from that app.

5. In `ccny_database_project` folder run: `py run.py`