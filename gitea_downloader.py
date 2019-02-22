#!/usr/bin/env python3
"""
this programs downloads repos and issues from a gitea instance
"""
from argparse import ArgumentParser
import os
import shutil
import subprocess
from subprocess import CalledProcessError
from typing import List

from colorama import Fore, Style

from util.config import Config, DEFAULT_CONFIG_FILE, get_config
from util.gitea_request import get_version, get_repos, get_issues
from util.issue import Issue, State
from util.repo import Repo


def remove_exceptions(exceptions: List[str], repos: List[Repo], verbose: bool) -> List[Repo]:
    """
    removing exceptions from repos
    :param exceptions: the name of the repos to remove
    :param repos: the repos (see Repo)
    :param verbose: verbose output?
    :return: list of repos with exceptions removed
    """
    for exception in exceptions:
        for repo in repos:
            if repo.is_name(exception):
                if verbose:
                    print("removing " + str(repo) + " due to " + exception)
                repos.remove(repo)
    return repos


def create_folder(folder: str, verbose: bool) -> None:
    """
    create folder if it does not exist
    :param folder: the folder to check for and possible create it
    :param verbose: verbose output?
    :return:
    """
    if not os.path.exists(folder):
        if verbose:
            print(folder + " does not exists. Will create it")
        os.makedirs(folder)


def check_for_git() -> None:
    """
    if git is installed return
    else print error and exit
    :return: None
    """
    if shutil.which('git') is None:
        print(Fore.RED +
              "\nYou need to install git https://git-scm.com/downloads"
              + Style.RESET_ALL)
        print("Exiting...")
        exit(2)


def download_repo(folder: str, repo: Repo) -> None:
    """
    git clone the Repo
    :param folder: folder to save to
    :param repo: the repo to clone
    :return: None
    """
    print("working on " + repo.name + " ", end='')
    try:
        git = subprocess.Popen(['git', 'clone', repo.url, str(os.path.join(folder, repo.name))],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
        git.communicate()
    except CalledProcessError:
        print(Fore.RED + "✘" + Style.RESET_ALL)
        return
    print(Fore.GREEN + "✓" + Style.RESET_ALL)


def working_on_issues(config: Config, repo: Repo, args) -> None:
    """
    get issues for repo and then ask user to save them
    :param config: the config to be used
    :param repo: the repo for which issues are worked on
    :param args: the commandline parameter
    :return:
    """
    if args.verbose:
        print("saving issues to file")
    issues: List[Issue] = get_issues(config, repo)
    if args.always_ask:
        if ask("save issues for " + repo.name):
            save_issues(args.folder, repo, issues, args.verbose)
    else:
        save_issues(args.folder, repo, issues, args.verbose)


def save_issues(folder: str, repo: Repo, issues: List[Issue], verbose: bool)-> None:
    """
    save the Issue to file
    :param folder: folder to save to
    :param repo: the repo to save Issues from
    :param issues: the list of Issues
    :param verbose: verbose output?
    :return: None
    """
    for issue in issues:
        if issue.state is State.open:
            create_folder(str(os.path.join(folder, "issues/" + repo.name + "/open")), verbose)
        elif issue.state is State.closed:
            create_folder(str(os.path.join(folder, "issues/" + repo.name + "/closed")), verbose)
        elif issue.state is State.unknown:
            create_folder(str(os.path.join(folder, "issues/" + repo.name + "/unknown")), verbose)

        with open(
                str(os.path.join(folder,
                                 "issues/" + repo.name
                                 + "/" + issue.state.name
                                 + "/" + issue.title)),
                'w') as out:
            out.write(issue.save_to_file())


def ask(question: str) -> bool:
    """
    ask to user the question until given an answer then return the answer
    :param question: the question to ask the user
    :return: the users answer
    """
    while True:
        answer: str = input("Do you want to " + question + "? [Y/n]")
        # check if one viable answers
        if answer.lower() == "y"\
                or answer == ""\
                or answer.lower() == "n":
            # return True if y or empty or False if n
            return answer.lower() == "y" or answer == ""


def main() -> None:
    """
    the main function loop
    :return: None
    """
    parser = ArgumentParser(description='Download git repos from a gitea instance')
    parser.add_argument('--config', '-c',
                        help='config file',
                        default=DEFAULT_CONFIG_FILE)
    parser.add_argument('-v', "--verbose",
                        help='increase verbosity',
                        action='store_true',
                        default=False)
    parser.add_argument('--no-issues',
                        help="don't download issues",
                        action='store_true',
                        default=False)
    parser.add_argument('--always-ask', '-a',
                        help='ask about every action',
                        action='store_true',
                        default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--folder', '-f',
                       help='download git repos here',
                       default='backup/')
    group.add_argument('--list', '-l',
                       help='list repos only (no download)',
                       action='store_true',
                       default=False)

    args = parser.parse_args()

    config: Config = get_config(args.config)

    if args.verbose:
        config.print()
        print("detected gitea version " + str(get_version(config)))

    repos: List[Repo] = get_repos(config)

    repos = remove_exceptions(config.exceptions, repos, args.verbose)

    if args.list:
        # List Repos
        print("Repos:")
        for repo in repos:
            print("\t- " + repo.name)
    else:
        create_folder(args.folder, args.verbose)

        if args.verbose:
            print("downloading to " + args.folder)

        check_for_git()

        # clone each git repo
        for repo in repos:
            if args.always_ask:
                if ask("download " + repo.name):
                    download_repo(args.folder, repo)
                    continue
            else:
                download_repo(args.folder, repo)

            if not args.no_issues:
                working_on_issues(config, repo, args)


if __name__ == "__main__":
    main()
