import abc
import typing

from api.entities.movies import Movie


class RepositoryException(Exception):
    pass


class MovieRepository(abc.ABC):
    async def create(self, movie: Movie):
        raise NotImplementedError

    async def get_by_id(self, movie_id: str) -> typing.Optional[Movie]:
        raise NotImplementedError

    async def get_by_title(
        self, title: str, skip: int = 0, limit: int = 0
    ) -> typing.List[Movie]:
        raise NotImplementedError

    async def delete(self, movie_id: str):
        raise NotImplementedError

    async def update(self, movie_id: str, update_parameters: dict):
        raise NotImplementedError
