class Movie:
    def __init__(
        self,
        *,
        movie_id: str,
        title: str,
        description: str,
        release_year: int,
        watched: bool = False
    ):
        if id is None:
            raise ValueError("Movie id is required")
        self._id = movie_id
        self._title = title
        self._description = description
        self._release_year = release_year
        self._watched = watched

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def release_year(self) -> int:
        return self._release_year

    @property
    def watched(self) -> bool:
        return self._watched
