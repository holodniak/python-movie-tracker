import typing

import motor.motor_asyncio
from api.entities.movies import Movie
from api.repository.movie.abstractions import MovieRepository, RepositoryException


class MemoryMovieRepository(MovieRepository):
    def __init__(self):
        self._storage = {}

    async def create(self, movie: Movie):
        self._storage[movie.id] = movie

    async def get_by_id(self, movie_id: str) -> typing.Optional[Movie]:
        return self._storage.get(movie_id)

    async def get_by_title(self, title: str) -> typing.List[Movie]:
        return_value = []
        for _, value in self._storage.items():
            if title == value.title:
                return_value.append(value)
            return return_value

    async def update(self, movie_id: str, update_params: dict):
        movie = self._storage.get(movie_id)
        if movie is None:
            raise RepositoryException(f"movie: {movie_id} not found")
        for key, value in update_params.items():
            if key == "id":
                raise RepositoryException(f"can't update movie id.")
            # Check that update_parameters are fields from Movie entity.
            if hasattr(movie, key):
                # Update the Movie entity.
                setattr(movie, key, value)

    async def delete(self, movie_id: str):
        self._storage.pop(movie_id, None)


class MongoMovieRepository(MovieRepository):
    def __init__(
        self,
        connection_string: str = "mongodb://localhost:27017",
        database: str = "movie_track_db",
    ):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
        self._database = self._client[database]
        self._movies = self._database["movies"]

    async def create(self, movie: Movie):
        await self._movies.insert_one(
            {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "release_year": movie.release_year,
                "watched": movie.watched,
            }
        )

    async def get_by_id(self, movie_id: str) -> typing.Optional[Movie]:
        document = await self._movies.find_one(
            {
                "id": movie_id,
            }
        )
        if document:
            return Movie(
                movie_id=document.get("id"),
                title=document.get("title"),
                description=document.get("description"),
                release_year=document.get("release_year"),
                watched=document.get("watched"),
            )
        return None

    async def get_by_title(self, title: str) -> typing.List[Movie]:
        return_value: typing.List[Movie] = []
        documents_cursor = self._movies.find({"title": title})
        async for document in documents_cursor:
            return_value.append(
                Movie(
                    movie_id=document.get("id"),
                    title=document.get("title"),
                    description=document.get("description"),
                    release_year=document.get("release_year"),
                    watched=document.get("watched"),
                )
            )
        return return_value

    async def update(self, movie_id: str, update_parameters: dict):
        if "id" in update_parameters.keys():
            raise RepositoryException("can't updated movie id")
        result = await self._movies.update_one(
            {"id": movie_id}, {"$set": update_parameters}
        )
        if result.modified_count == 0:
            raise RepositoryException(f"movie: {movie_id} not found")

    async def delete(self, movie_id: str):
        await self._movies.delete_one({"id": movie_id})
