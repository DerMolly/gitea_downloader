"""
hold all requests to the gitea instance and some error handling
"""
from typing import Set, List
from urllib.parse import urljoin

from colorama import Fore, Style
import requests
from requests import Response
from requests.auth import HTTPBasicAuth

from util.config import Config, AuthMode
from util.issue import Issue, Comment
from util.repo import Repo

STATUS_CODE_OK = 200
STATUS_CODE_NO_AUTH = 403

API_URL = "/api/v1"  # API Base URL
VERSION_URL = API_URL + "/version"  # Version API URL
REPOS_URL = API_URL + "/repos/search?uid={uid}&page={page}&limit=50"  # Repos API URL
USER_ID_URL = API_URL + "/user"  # User ID API URL
ISSUE_URL = API_URL + "/repos/{repo}/issues?page={page}&state={state}"  # Issue API URL
COMMENT_URL = API_URL + "/repos/{repo}/issues/{index}/comments"  # Comment API URL


def get_user_id(config: Config) -> int:
    """
    get the user id of the user in the config from a gitea instance
    :param config: the config to be used
    :return: the user id
    """
    user_id = __general_request(config, USER_ID_URL)
    return user_id.json()['id']


def get_version(config: Config) -> str:
    """
    get the gitea instances version
    :param config: the config to be used
    :return: the gitea instance version
    """
    return __general_request(config, VERSION_URL, False).json()['version']


def get_repos(config: Config) -> Set[Repo]:
    """
    get all repos the user in the config owns or has worked on
    :param config: the config to be used
    :return: set of Repo objects
    """
    user_id: int = get_user_id(config)
    repos: Set[Repo] = set()
    page = 1
    while True:
        try:
            repos_result = __general_request(config,
                                             REPOS_URL.format(uid=user_id, page=page))
        except GiteaException:
            break

        if not repos_result.json()['data']:
            break

        page += 1

        for repo in repos_result.json()['data']:
            repos.add(Repo(name=repo['full_name'], url=repo['ssh_url']))

    return repos


def get_issues(config: Config, repo: Repo) -> List[Issue]:
    """
    get all issues of corresponding repo
    :param config: the config to be used
    :param repo: the repo to gather the issues from
    :return: list of Issue
    """
    issues: List[Issue] = []
    for state in ['open', 'closed']:
        page = 1
        while True:
            try:
                issues_result = __general_request(config, ISSUE_URL.format(repo=repo.name,
                                                                           page=page,
                                                                           state=state))
            except GiteaException:
                break

            if not issues_result.json():
                break

            page += 1

            if issues_result.status_code is STATUS_CODE_OK:
                for issue_json in issues_result.json():
                    issue = Issue(title=issue_json['title'],
                                  author=issue_json['user']['full_name'],
                                  body=issue_json['body'],
                                  state=issue_json['state'])
                    for label_json in issue_json['labels']:
                        issue.add_label(label_json['name'])
                    issue.comments = get_comments(config, repo, issue_json['number'])
                    issues.append(issue)

    return issues


def get_comments(config: Config, repo: Repo, index: int) -> List[Comment]:
    """
    get all comments of a specific issue
    :param config: config: the config to be used
    :param repo: the repo to gather the issues from
    :param index: the index of the issue to gather comments from
    :return: list of Comment
    """
    comments: List[Comment] = []

    try:
        comments_result = __general_request(config, COMMENT_URL.format(repo=repo.name,
                                                                       index=index))
        for comment_json in comments_result.json():
            comments.append(Comment(body=comment_json['body'],
                                    author=comment_json['user']['full_name']))
    except GiteaException:
        pass

    return comments


def __general_request(config: Config, url: str, use_auth: bool = True) -> Response:
    """
    common function to build requests from
    :param config: the config to be used
    :param url: the url to work with
    :return: the response
    """
    request = ""
    try:
        if not use_auth:
            request = requests.get(urljoin(config.url, url))
        else:
            if config.auth.mode == AuthMode.PASSWORD:
                request = requests.get(urljoin(config.url, url),
                                       auth=HTTPBasicAuth(username=config.auth.user,
                                                          password=config.auth.password))
            elif config.auth.mode == AuthMode.TOKEN:
                request = requests.get(urljoin(config.url, url),
                                       headers={'Authorization': 'token ' + config.auth.token})
            else:
                print("I should auth but I can't. Somethings seems wrong")
                print("Exiting...")
                exit(2)
    except Exception:
        raise GiteaException()

    if request.status_code is STATUS_CODE_NO_AUTH:
        print(Fore.RED
              + "Your login credentials are not right and/or"
                "you don't have sufficient access rights"
              + Style.RESET_ALL)
        exit(2)
    elif request.status_code is STATUS_CODE_OK:
        pass
    else:
        raise GiteaException()
    return request


class GiteaException(Exception):
    """
    An catch-all exception for problems with requests against gitea
    """
