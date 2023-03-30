from fastapi import APIRouter

from fastapi.encoders import jsonable_encoder
from fastapi.responses import UJSONResponse
from api.dto.movie import DetailResponse
from starlette.responses import JSONResponse


router = APIRouter(prefix="/api/v1/responses")


@router.get("/json", response_model=DetailResponse)
def hello_world():
    return JSONResponse(
        status_code=201,
        content=jsonable_encoder(DetailResponse(message=f"Hello World!")),
    )


@router.get("/ujson", response_model=DetailResponse)
def hello_world():
    return UJSONResponse(
        status_code=200,
        content=jsonable_encoder(DetailResponse(message=f"Hello World!")),
    )
