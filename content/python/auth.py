# Copyright: 2024 Ibrahem Mouhamad

import abc

import logging
logger = logging.getLogger('my_logger')

logging.basicConfig()

class Auth(abc.ABC):
    """
    Base class of all authentication methods.
    """
    @property
    @abc.abstractmethod
    def token_type(self) -> str:
        """
        The type of the auth token, e.g. Bearer or Basic.

        :return: token type

        """
    @property
    @abc.abstractmethod
    def token(self) -> str:
        """
        The auth token as used in the HTTP Authorization header.

        :return: token

        """
    def authentication(self, headers: dict) -> None:
        """
        Add authorization to the headers.
        """
        headers["Authorization"] = f"{self.token_type} {self.token}"


class Token(Auth):
    """
    This class is used to authenticate with a single constant token.
    """

    def __init__(self, token: str):
        assert isinstance(token, str)
        assert len(token) > 0
        self._token = token

    @property
    def token_type(self) -> str:
        return "token"

    @property
    def token(self) -> str:
        return self._token
