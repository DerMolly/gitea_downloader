# Gitea Downloader
![pylint Score](https://mperlet.github.io/pybadge/badges/10.00.svg)

This tool downloads all contributed repos of an user on a gitea instance and the issues of these repos.

## Requirements

- `python3.3` or higher (I think)
- `git`
- `pip`

## Installation

It is recommended to use a [venv](https://docs.python.org/3/library/venv.html) or similar.

install the dependencies:

`pip install -r requirements.txt`

## Auth

You can either use your username and password to authenticate yourself against gitea or your username and an api token.

If both are given the password will be used.

You can get an API Token under this link [https://your-gitea-instance/user/settings/applications](https://your-gitea-instance/user/settings/applications).

## Usage

`[molly@linuxbox]$ ./gitea_downloader.py`

```
usage: gitea_downloader.py [-h] [--config CONFIG] [-v] [--no-issues]
                           [--always-ask] [--folder FOLDER | --list]

Download git repos from a gitea instance

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        config file
  -v, --verbose         increase verbosity
  --no-issues           don't download issues
  --always-ask, -a      ask about every action
  --folder FOLDER, -f FOLDER
                        download git repos here
  --list, -l            list repos only (no download)
```

## Config

The config file (which is assumed to be config.ini, but you can specify something else with `--config`) should look similar to this:

Please note that the inclusion of both password and token are neither required nor really a good idea.

```
[gitea]
;url of your gitea instance
url = https://localhost

[repos]
;comma separted list of repos to ignore (json-style)
exception = []

[auth]
;your username
user = test
;your password
password = test123
;your token
token = xxxxxxx
```