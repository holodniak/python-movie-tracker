from functools import lru_cache
from http import HTTPStatus
import typing
import uuid
from fastapi import APIRouter, Body, Depends, Path, Query, Response
from api.dto.movie import (
    CreateMovieBody,
    DetailResponse,
    MovieCreatedResponse,
    MovieResponse,
    MovieUpdateBody,
)
from api.entities.movies import Movie
from api.repository.movie.abstractions import MovieRepository, RepositoryException
from api.repository.movie.movie import MongoMovieRepository
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


from api.settings import Settings


router = APIRouter(prefix="/api/v1/movie", tags=["movies"])


@lru_cache()
def settings():
    return Settings()


def movie_repository(settings: Settings = Depends(settings)):
    return MongoMovieRepository(
        connection_string=settings.mongo_connection_string,
        database=settings.mongo_database_name,
    )


@router.post("/", status_code=201, response_model=MovieCreatedResponse)
async def create_movie(
    movie: CreateMovieBody = Body(..., title="Movie", description="movie details"),
    repo: MovieRepository = Depends(movie_repository),
):
    repo = MongoMovieRepository()
    movie_id = str(uuid.uuid4())

    await repo.create(
        movie=Movie(
            movie_id=movie_id,
            title=movie.title,
            description=movie.description,
            release_year=movie.release_year,
            watched=movie.watched,
        )
    )
    return MovieCreatedResponse(movie_id=movie_id)


@router.get(
    "/{movie_id}",
    responses={
        200: {"model": MovieResponse},
        404: {"model": DetailResponse},
    },
)
async def get_movie_by_id(
    movie_id: str, repo: MovieRepository = Depends(movie_repository)
):
    movie = await repo.get_by_id(movie_id=movie_id)

    if movie is None:
        return DetailResponse(message=f"Movie with id {movie_id} not found")

    return MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        release_year=movie.release_year,
        watched=movie.watched,
    )


@router.get("/", response_model=typing.List[MovieResponse])
async def get_movie_by_title(
    title: str = Query(..., title="Title", description="The title Movie", min_length=3),
    repo: MovieRepository = Depends(movie_repository),
):
    movies = await repo.get_by_title(title)
    movies_return_value = []
    for movie in movies:
        movies_return_value.append(
            MovieResponse(
                id=movie.id,
                title=movie.title,
                description=movie.description,
                release_year=movie.release_year,
                watched=movie.watched,
            )
        )
    return movies_return_value


@router.patch(
    "/{movie_id}",
    responses={200: {"model": DetailResponse}, 404: {"model": DetailResponse}},
)
async def patch_update_movie(
    movie_id: str = Path(
        ..., title="Movie ID", description="The id of the movie to update"
    ),
    update_parameters: MovieUpdateBody = Body(
        ...,
        title="Update Body",
        description="Update movie",
    ),
    repo: MovieRepository = Depends(movie_repository),
):
    try:
        await repo.update(
            movie_id=movie_id,
            update_parameters=update_parameters.dict(
                exclude_unset=True, exclude_none=True
            ),
        )
        return DetailResponse(message="Movie updated.")
    except RepositoryException as e:
        return JSONResponse(
            status_code=400, content=jsonable_encoder(DetailResponse(message=str(e)))
        )


@router.delete("/{movie_id}", status_code=204)
async def delete_movie(
    movie_id: str = Path(
        ..., title="Movie ID", description="The id of the movie to update"
    ),
    repo: MovieRepository = Depends(movie_repository),
):
    await repo.delete(movie_id=movie_id)
    return Response(status_code=204)
