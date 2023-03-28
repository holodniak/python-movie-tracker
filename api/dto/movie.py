from pydantic import BaseModel, validator


class CreateMovieBody(BaseModel):
    title: str
    description: str
    release_year: int
    watched: bool = False

    @validator("title")
    def title_length_gt_three(cls, v):
        if len(v) < 4:
            raise ValueError("Title's length must be greater than 3 caracters.")
        return v

    @validator("description")
    def description_length_gt_three(cls, v):
        if len(v) < 4:
            raise ValueError("Descripton's length must be greater than 3 caracters.")
        return v

    @validator("release_year")
    def release_year_gt_1900(cls, v):
        if v < 1900:
            raise ValueError("release_year's must be greater than 1900.")
        return v
