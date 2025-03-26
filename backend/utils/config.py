from enum import Enum
import os, platform
import configparser
from pydantic import BaseModel

config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(config_path)
# print(f"config.ini path is {config_path}")


def get_chromedriver_path_manual():
    """
    DIfferent OS have different ChromeDriver, we need to ensure the correct usage.
    For Linux, ChromeDriver needs a few extra packages. If they were not installed, error message will show (this is from a Docker container):

        Message: Service /root/.cache/selenium/chromedriver/linux64/131.0.6778.87/chromedriver unexpectedly exited. Status code was: 127


    """
    base_dir = os.path.abspath(os.getcwd())
    os_type = platform.system()

    if os_type == "Windows":
        chromedriver_path = os.path.join(base_dir, "windows_driver", "chromedriver.exe")
    elif os_type == "Linux":
        chromedriver_path = os.path.join(base_dir, "linux_driver", "chromedriver")
    else:
        raise Exception(f"Unsupported operating system: {os_type}")

    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"ChromeDriver not found at {chromedriver_path}")

    return chromedriver_path


graph_config = {
    "llm": {
        # note: scrapegraphAI only have a built-in list of models, if our model is not in that list, an exception will be raised, but the function can still run.
        "model": "ollama/moondream",
        "temperature": 1,
        "format": "json",  # Ollama needs the format to be specified explicitly
        "model_tokens": 2000,  #  depending on the model set context length
        "base_url": "http://localhost:11434",  # set ollama URL of the local host (YOU CAN CHANGE IT, if you have a different endpoint
    }
}


recipients = ["lingjun.zhou@nrcan-rncan.gc.ca"]  # "rae.payette@nrcan-rncan.gc.ca"


class Grant(BaseModel):
    #  JSON payload, because the endpoing is called from JS
    url: str
    date: str
    status: str
    recipient: str


class Ghub(Enum):
    GITHUB_TOKEN = str(config["github"]["GITHUB_TOKEN"])
    GITHUB_USERNAME = config["github"]["GITHUB_USERNAME"]
    REPO_NAME = <your-data-repo-name>


class AZ(Enum):
    # connection_string is a credential, we shouldn't have it explicitly stored in the code
    connection_string = ""
    # azure ONLY accepts lowercase letters and numbers for names
    container_name = "tracking4url"


class PARSER(Enum):
    SELENIUM = "selenium"
    BS4 = "bs4"
    # RQST = "requests"


# OpenSearch Instances conf
class nlpModels(Enum):
    ST_Model1 = "paraphrase-MiniLM-L6-v2"
    ST_Model2 = "all-MiniLM-L6-v2"
    ST_Model3 = "all-mpnet-base-v2"
    ST_Model4 = "all-MiniLM-L12-v2"
    ST_Model5 = "all-roberta-large-v1"
    ST_Model6 = "paraphrase-mpnet-base-v2"
    # run python -m spacy download en_core_web_md to download this model before using
    spaCy_Model1 = "en_core_web_md"
    spaCy_Model2 = "en_core_web_lg"
    spaCy_Model3 = "en_core_web_trf"


class DriverPath(Enum):
    CHROME_DRIVER = ""  # get_chromedriver_path_manual()


class WarningMessages(Enum):
    URLNotValid = "URL is NOT VALID!!"
    ContentNotValid = "CONTENT of URL is NOT VALID!"
    FirstTimeTracking = "FIRST TRACKING THIS URL! NO PREVIOUS CONTENT!"
    NoChanges = "NO CHANGES TO THE CONTENT!"
    OnlyOneVersion = "THERE IS NO PREVIOUS CHANGE!"
    SignificantChange = "SIGNIFICANT CHANGE!"
    TrivialChange = "TRIVIAL CHANGE!"


class ChangeMonitor(Enum):
    NameRegistryFile = "name_registry.txt"
    WebTrackingRepo = "webpage_tracking_repo"
    GRANTS_DB = "grants.csv"
    KEYWORDS = "keywords.txt"
    SCHEDULES = "schedules.txt"
    EmailsFile = "emails.txt"


class RemoteOrigin(Enum):
    # ONLY 1 value can be True here
    Github = True
    Azure = False


class AutoEmail(Enum):
    # the email acct where the verification email originates from
    BTAP_verification_host_email = "lingjun.l.zhou@gmail.com"
    # If you do not have a gmail apps password, create a new app with using generate password.
    # Check your apps and passwords https://myaccount.google.com/apppasswords
    BTAP_verification_host_email_password = config["gmail"]["GMAIL_PWD"]


# class RemoteOrigin:
#     """
#     RemoteOrigin.set("GitHub")
#     print(RemoteOrigin.get())  # {'GitHub': True, 'AZ': False, 'noRemote': False}
#     print(RemoteOrigin.current())  # 'GitHub'

#     RemoteOrigin.set("AZ")
#     print(RemoteOrigin.get())  # {'GitHub': False, 'AZ': True, 'noRemote': False}
#     print(RemoteOrigin.current())  # 'AZ'

#     try:
#         RemoteOrigin.set("InvalidKey")
#     except ValueError as e:
#         print(e)  # Invalid remote origin: InvalidKey
#     """

#     _state = {
#         "Github": False,
#         "Azure": False,
#         "NoRemote": False,
#     }

#     @classmethod
#     def set(cls, key):
#         if key not in cls._state:
#             raise ValueError(f"Invalid remote origin: {key}")
#         # Set the selected key to True and others to False
#         for k in cls._state:
#             cls._state[k] = k == key

#     @classmethod
#     def get(cls):
#         return cls._state

#     @classmethod
#     def current(cls):
#         # Return the currently active remote origin
#         for k, v in cls._state.items():
#             if v:
#                 return k
#         return None  # None if all are False
