# CCNY_Database_Project

This project can be used to track your albums that you have collected in the form of physical media. It uses Spotify data via the Spotipy library to search albums. MySQL and Flask are used for the backend.

## Requirements 

- [Python](https://www.python.org/downloads/)
- Free Spotify account to access [developer tools](https://developer.spotify.com/dashboard/)
- [MySQL Workbench](https://dev.mysql.com/doc/workbench/en/wb-windows.html)

## Instructions to run on your computer

1. Set up python virtual environment: 
    
    Create environment: 
    ```bash
    python3 -m venv env
    ```

    Activate environment:

    - on Windonws: 
        ```bash
        env\scripts\activate
        ```

    - on Mac: 
        ```bash
        env/bin/activate
        ```

2. Install required packages: 
    ```bash
    pip install -r requirements.txt
    ```

3. Run `project_schema.sql` in MySQL workbench to create database and tables.

4. In `flask_app` folder, create a `.env` file with the following variables:
    
    Key of your choice 
    ```sh
    SECRET_KEY =
    ``` 

    Your MySQL login credentials. `DATABASE_HOST` is most likely localhost and `DATABASE_USER` is most likely root.
    ```sh
    DATABASE_HOST = 
    DATABASE_USER = 
    DATABASE_PASS = 
    DATABASE_SCHEMA = csc336_project
    ```
    
    Create an app in your Spotify developer dashboard and use the client id and client secret from that app.
    ```sh
    SPOTIFY_CLIENT_ID = 
    SPOTIFY_CLIENT_SECRET = 
    ```

    
5. In `ccny_database_project` folder run: 
    ```bash
    py run.py
    ```