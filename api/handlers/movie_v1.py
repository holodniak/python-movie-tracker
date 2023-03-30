from collections import namedtuple
import dataclasses
from functools import lru_cache
import typing
import uuid
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Header,
    Path,
    Query,
    Response,
)
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
from fastapi.security import (
    HTTPBasicCredentials,
    HTTPBasic,
)

from api.settings import Settings

http_basic = HTTPBasic()


def basic_authentication(credentials: HTTPBasicCredentials = Depends(http_basic)):
    if credentials.username == "Pedro" and credentials.password == "basic":
        return
    raise HTTPException(status_code=401, detail="invalid_credentials")


router = APIRouter(
    prefix="/api/v1/movie",
    tags=["movies"],
    dependencies=[Depends(basic_authentication)],
)


@lru_cache()
def settings():
    return Settings()


def movie_repository(settings: Settings = Depends(settings)):
    return MongoMovieRepository(
        connection_string=settings.mongo_connection_string,
        database=settings.mongo_database_name,
    )


def pagination_params(
    skip: int = Query(0, title="Skip", description="The number of items to skip", ge=0),
    limit: int = Query(
        1000,
        title="Limit",
        description="The limit of number of items returned",
        le=1000,
    ),
):
    Pagination = namedtuple("Pagination", ["skip", "limit"])
    return Pagination(skip=skip, limit=limit)


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
    movie_id: str,
    repo: MovieRepository = Depends(movie_repository),
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
    pagination=Depends(pagination_params),
    repo: MovieRepository = Depends(movie_repository),
):
    movies = await repo.get_by_title(
        title, skip=pagination.skip, limit=pagination.limit
    )
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
