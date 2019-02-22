"""
holds all infos about Issues
"""
from collections import namedtuple
from enum import Enum
from typing import List


class Issue:
    """
    represents an Issue in gitea consisting of:
    - author
    - state (see State object)
    - title
    - body
    - labels
    - comments (see Comment object)
    """
    def __init__(self, author, title, body, state) -> None:
        self.author: str = author
        self.title: str = title
        self.body: str = body

        if state.strip() == "open":
            self.state: State = State.open
        elif state.strip() == "closed":
            self.state: State = State.closed
        else:
            self.state: State = State.unknown

        self.labels: List[str] = []
        self.comments: List[Comment] = []

    def add_label(self, label: str) -> None:
        """
        add a label to the list of labels
        :param label: the label to add
        :return: None
        """
        self.labels.append(label)

    def __repr__(self) -> str:
        return "{title} by {author}".format(title=self.title, author=self.author)

    def save_to_file(self) -> str:
        """
        convert this issue into an multiline string to write to a file
        :return: multiline string
        """
        labels = ""
        for label in self.labels:
            labels = labels + label + ","

        issue_str: str = "# {title}\nby {author}".format(title=self.title, author=self.author)

        if labels:
            issue_str += "\nLabels:{labels}".format(labels=labels)

        issue_str += "\n\n{body}".format(body=self.body)

        if self.comments:
            issue_str += "\n\nComments:\n"
        for comment in self.comments:
            issue_str += "{comment}\n".format(comment=comment)
        return issue_str


# hold an comment for easier management
Comment = namedtuple("Comment", ['author', 'body'])


class State(Enum):
    """
    the state of the issue
    """
    open = 1
    closed = 2
    unknown = 3
