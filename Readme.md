1. This is a working app, the backend itself already has a UI, but it's with Jinja2 templates by FastAPI. User just need to change the `/landing` endpoint's return type to template response and add in the correponding data, the app will run with `uvicorn app:app`. 
1. There are a few things you might have to create: a `config.ini` to hold your credentials

    ```
    [github]
    ; note that we shoud not add str quotation marks "" to the credentials
    GITHUB_TOKEN = <your-git-token>
    GITHUB_USERNAME = <you-git-username>

    [gmail]
    GMAIL_PWD= <your-gmail-token>
    ```

    this is used in `config.py` via
    ```
    class Ghub(Enum):
    GITHUB_TOKEN = str(config["github"]["GITHUB_TOKEN"])
    GITHUB_USERNAME = config["github"]["GITHUB_USERNAME"]
    REPO_NAME = <your-git-data-repo>
    ```