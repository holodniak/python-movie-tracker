from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    mongo_connection_string: str = Field(
        "mongodb://localhost:27017",
        title="MongoDB Connection String",
        description="MongoDB connection",
        env="MONGODB_CONNECTION_STRING",
    )
    mongo_database_name: str = Field(
        "movie_track_db",
        title="MongoDB Movies database name",
        description="Movies name Database",
        env="MONGODB_DATABASE_NAME",
    )
