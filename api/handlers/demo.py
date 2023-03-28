from fastapi import APIRouter, Body, HTTPException, Path, Query
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


from api.responses.detail import DetailResponse


router = APIRouter(prefix="/api/v1/demo")


class NameIn(BaseModel):
    name: str
    prefix: str = "Mr"


@router.get("/", response_model=DetailResponse)
def hello_world():
    return DetailResponse(message="Hello World!")


@router.get("/hello", response_model=DetailResponse)
def send_data_query(name: str = Query(..., title="Name", description="The Name")):
    return DetailResponse(message=f"Hello {name}")


@router.post("/hello/name", response_model=DetailResponse)
def send_data_body(
    name: NameIn = Body(..., title="Body", description="The body of send data.")
):
    return DetailResponse(message=f"Hello {name.prefix} {name.name}")


@router.post("/hello/{name}", response_model=DetailResponse)
def send_data_path(name: str = Path(..., title="Name")):
    return DetailResponse(message=f"Hello {name}")


@router.delete("/delete", response_model=DetailResponse)
def delete_data():
    return DetailResponse(message="Data Deleted")


@router.delete(
    "/delete/{name}",
    response_model=DetailResponse,
    responses={404: {"model": DetailResponse}},
)
def delete_data(name: str):
    if name == "admin":
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder(DetailResponse("cannot delete data for admin")),
        )
    return DetailResponse(message=f"Data deleted for {name}")


@router.delete(
    "/error",
    response_model=DetailResponse,
    responses={404: {"model": DetailResponse}},
)
def get_error_htpp():
    raise HTTPException(404, detail="This endpoint always fails.")
