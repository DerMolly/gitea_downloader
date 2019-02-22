"""
hold all infos about Repos
"""


class Repo:
    """
    represents an repo with:
        - name
        - url
    """

    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url

    def is_name(self, name: str) -> bool:
        """
        check if name equals the name of the repo
        :param name: the name to check
        :return: bool
        """
        return self.name is name

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other):
        return self.name == other.name and self.url == other.url

    def __hash__(self):
        return id(self)
