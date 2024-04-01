from fastapi import HTTPException,Depends,FastAPI,Body,Path,Query, Request
from fastapi.responses import HTMLResponse,JSONResponse
from typing import Coroutine, Optional,List#tipos
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel,Field #modelos de datos
from jwt_manager import create_token,validate_token
from fastapi.security import HTTPBearer

from models.movie import Movie as MovieModel
from config.database import Session,engine,Base

app = FastAPI()
app.title = "Mi aplicacion con FastAPI"
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
   async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data["email"] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="credenciales son invalidas")


class User(BaseModel):
    email:str
    password:str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5,max_length=15)
    overview: str = Field(min_length=15,max_length=50)
    year: int = Field(le=2022)
    rating: float = Field(ge=1,le=10)
    category: str = Field(min_length=5,max_length=15)

    class Config:
        json_schema_extra = {
            "example": 
            [
                {
                    "id": 1,
                    "title": "Mi pelicula",
                    "overview": "Descripcion",
                    "year": 2022,
                    "rating": 9.8,
                    "category": "Acción"
                }
            ]
        }

class CreateMovieRes(Base):
    Message: str

@app.get("/",tags=["Home"])
def message():
    return HTMLResponse("<h1>hola halan marcelo</h1>")

#generado tokens
@app.post("/login",tags=["auth"])
def login(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.model_dump())
        return JSONResponse(status_code= 200,content=token)

movies = [
    {
        "id":1,
        "title":"avatar",
        "overview":"es una pelicula aburrida",
        "year":2009,
        "rating":7.8,
        "category":"Accion"
    },
    {
        "id":2,
        "title":"avatar",
        "overview":"es una pelicula aburrida",
        "year":2009,
        "rating":7.8,
        "category":"Aventura"
    }
]


@app.get("/movies",tags=["movies"],response_model=List[Movie],status_code=200,dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    return JSONResponse(status_code= 200, content=movies)

#en ruta parametros
@app.get("/movies/{id}",tags=["movies"],response_model=Movie)
def get_movie(id: int = Path(ge=1, le=2000)) -> Movie :
    for item in movies:
        if item["id"] == id:
            return JSONResponse(content=item)
    return JSONResponse(status_code=404,content=[])

#parametros query
@app.get("/movies/", tags=["Query"],response_model=List[Movie])
def get_movies_by_category(category: str = Query(min_length=5,max_length=15)) -> List[Movie]:
    movies_by_category = []
    for movie in movies:
        if(movie["category"] == category):
            movies_by_category.append(movie)
    return JSONResponse(content = movies_by_category)

#crear
@app.post('/movies',tags=['movies'],response_model=CreateMovieRes, status_code= 201)
def create_movie(movie: Movie) -> dict:    
    db = Session()
    new_movie = MovieModel(**movie.model_dump_json())
    db.add(new_movie)
    db.commit()
    db.refresh(db)
    #movies.append(movie)
    return JSONResponse(status_code = 201 ,content=)
#modificar y borrar

#put
@app.put('/movies/{id}',tags=['movies'],response_model=dict, status_code=200)
def update_movie(id: int,movie: Movie ) -> dict:    
    for item in movies:
        if item["id"] == id:
            item["title"] = movie.title,
            item["overview"] = movie.overview,
            item["year"] = movie.year,
            item["rating"] = movie.rating,
            item["category"] = movie.category
            return JSONResponse(status_code= 200, content={"message":"Se ha modificado la pelicula"})

#delete
@app.delete('/movies/{id}',tags=['movies'],response_model=dict, status_code=200)
def delete_movies(id: int) -> dict:
    for item in movies:
        if item["id"] == id:
            movies.remove(item)
            return JSONResponse(status_code= 200, content = {"message":"Se ha eliminado la pelicula"})
        
#pydantic
#Validaciones de parámetros con Pydantic
#JSONResponse
#Codigos de estado HTTP en FastAPI
#Autenticación en FastAPI
#Generando tokens con PyJWT
#middlewere
#Conexión con bases de datos en FastAPI