from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.handlers import movie_v1


def my_startup_event_handler():
    print("Hello world!")


def my_shutdown_event_handler():
    print("Goodbye world!")


def create_app():
    app = FastAPI(docs_url="/")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.on_event("startup")(my_startup_event_handler)
    app.on_event("shutdown")(my_shutdown_event_handler)

    app.include_router(movie_v1.router)

    return app
