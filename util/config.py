"""
holds all config concerned classes
"""
import configparser
import json
import os
from enum import Enum
from typing import List
from urllib.parse import urlparse


class Config:
    """
    represents an config consisting of
        - url (of the gitea instance)
        - exception (list of exceptions)
        - auth
    """

    def __init__(self) -> None:
        self.url: str = urlparse("http://localhost").geturl()
        self.exceptions: List[str] = []
        self.auth: Auth = Auth()

    def load_config(self, config_name: str) -> None:
        """
        load config from file
        :param config_name: the name of the file to load from
        :return: None
        """
        config = configparser.ConfigParser()
        config.read(config_name)

        self.url = urlparse(config.get("gitea", "url")).geturl()
        exceptions = config.get("repos", "exception")
        if exceptions:
            self.exceptions = json.loads(exceptions)
        else:
            self.exceptions = []
        self.auth.load(config)

    def save_config(self, config_name: str) -> None:
        """
        save the config to a file
        :param config_name: the name of the config file to save to
        :return: None
        """
        if not os.path.isfile(config_name):
            # Create the configuration file as it doesn't exist yet
            config_file = open(config_name, 'w')

            # Add content to the file
            config = configparser.ConfigParser()
            config.add_section('gitea')
            config.set('gitea', 'url', self.url)
            config.add_section('repos')
            config.set('repos', 'exceptions', json.dumps(self.exceptions))
            config.add_section('auth')
            config.set('auth', 'user', self.auth.user)
            if self.auth.mode == AuthMode.PASSWORD:
                config.set('auth', 'password', self.auth.password)
            elif self.auth.mode == AuthMode.Token:
                config.set('auth', 'token', self.auth.token)
            config.write(config_file)
            config_file.close()

    def print(self) -> None:
        """
        print the config
        :return: None
        """
        print("Config:")
        print("url: %s" % self.url)
        print("exceptions:")
        for exception in self.exceptions:
            print("\t- '%s'" % exception)
        print("auth:")
        self.auth.print()


class Auth:
    """
    holds the auth information
    """

    def __init__(self) -> None:
        self.mode: AuthMode = AuthMode.PASSWORD  #
        self.user: str = "test"  #
        self.password: str = "sicher123"
        self.token: str = ""

    def load(self, config: configparser.ConfigParser) -> None:
        """
        load auth from file
        :param config: the file to load the config from
        :return: None
        """
        self.user = config.get("auth", "user")
        try:
            self.token = config.get("auth", "token")
            self.mode = AuthMode.TOKEN
        except configparser.NoOptionError:
            pass

        try:
            self.password = config.get("auth", "password")
            self.mode = AuthMode.PASSWORD
        except configparser.NoOptionError:
            pass

    def print(self) -> None:
        """
        print the auth
        :return: None
        """
        if self.mode is AuthMode.TOKEN:
            print("\tuser: %s" % self.user)
            print("\ttoken: %s" % self.token)
        else:
            print("\tuser: %s" % self.user)
            print("\tpassword: %s" % self.password)


class AuthMode(Enum):
    """
    how we want to auth
    """
    TOKEN = 1
    PASSWORD = 2


DEFAULT_CONFIG_FILE = "config.ini"


def get_config(config_name: str) -> Config:
    """
    get config from disk
    or if the file is not found get the default file
    or if this also not found get a default config
    :param config_name: the name of the file to load the config from
    :return: a Config for the program
    """
    # create a default config
    config: Config = Config()
    # check if config exists
    if not os.path.isfile(config_name):
        if config_name is not DEFAULT_CONFIG_FILE:
            print("config file not found. trying to use default config file")
        # check if default config exists
        if not os.path.isfile(DEFAULT_CONFIG_FILE):
            # it does not
            print("default config file not found. I will create it")
            config.save_config(config_name)
            print("Exiting...")
            exit(2)
        else:
            # load default config
            config.load_config(DEFAULT_CONFIG_FILE)
    else:
        # load config file
        config.load_config(config_name)

    return config
