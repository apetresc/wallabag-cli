"""
Settings and configuration for wallabag-cli.
"""
import json
import time
from collections import OrderedDict
from pathlib import Path

CONFIG_FILENAME = ".wallabag-cli"


class Configs():
    """
    Static struct for storing the global configs.
    """

    # wallabag server
    serverurl = ""
    username = ""
    password = ""

    # wallabag api oauth2
    client = ""
    secret = ""

    # oauth2 token
    access_token = ""
    expires = 0


def is_token_expired():
    """
    Returns if the last created oauth2 token is expired.
    """
    return Configs.expires - time.time() < 0


def set_config(name, value):
    """
    Sets a config value to a given value without checking validity.
    """
    if hasattr(Configs, name):
        setattr(Configs, name, value)


def get_config(name):
    """
    Get a config value or None as default. Use "api.get_token()" instead if you
    wish to get a valid oauth2 token.
    """
    return getattr(Configs, name, None)


def __configs2dictionary():
    """
    Converts the configuration values to a json serializable dictionary.

    Returns
    -------
    dictionary
        Dictionary with the configurations
    """

    wallabag_api = OrderedDict()
    wallabag_api_oauth2 = OrderedDict()
    wallabag_api_oauth2_token = OrderedDict()

    wallabag_api['serverurl'] = Configs.serverurl
    wallabag_api['username'] = Configs.username
    wallabag_api['password'] = Configs.password

    wallabag_api_oauth2['client'] = Configs.client
    wallabag_api_oauth2['secret'] = Configs.secret
    wallabag_api["oauth2"] = wallabag_api_oauth2

    wallabag_api_oauth2_token["access_token"] = Configs.access_token
    wallabag_api_oauth2_token["expires"] = Configs.expires
    wallabag_api["oauth2"]["token"] = wallabag_api_oauth2_token

    return {"wallabag_api": wallabag_api}


def __dicionary2config(configdict):
    for item in configdict:
        if isinstance(configdict[item], str) or isinstance(configdict[item], int) or \
                isinstance(configdict[item], float):
            set_config(item, configdict[item])
        elif isinstance(configdict[item], dict):
            __dicionary2config(configdict[item])


def exist(path=CONFIG_FILENAME):
    file = Path(path)
    return file.is_file()


def save(path=CONFIG_FILENAME):
    """
    Saves the config into a file.

    Parameters
    ----------
    path : string
        Optional non default config filename.

    Returns
    -------
    bool
        True if successful
    """
    try:
        with open(path, mode='w') as file:
            jsonsave = json.dumps(__configs2dictionary(), indent=4)
            file.write(jsonsave)

            file.close()
        return True
    except:
        return False


def load(path=CONFIG_FILENAME):
    """
    Loads the config into a dictionary.

    Parameters
    ----------
    path : string
        Optional non default config filename.

    Returns
    -------
    bool
        True if successfull. Otherwise the config will be filles with default values
    """
    if not exist(path):
        return False
    try:
        with open(path, mode='r') as file:
            filecontent = file.read()
            file.close()
        dic = json.loads(filecontent)
        __dicionary2config(dic['wallabag_api'])
        return True
    except json.decoder.JSONDecodeError:
        return False
    except PermissionError:
        return False


def load_or_create(path=CONFIG_FILENAME):
    success = False
    if not exist(path):
        success = save(path)
    else:
        success = load(path)
    if not success:
        print("Error: Could not load or create the config file.")
        print()
        exit(-1)