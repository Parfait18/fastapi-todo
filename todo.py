import databases
import sqlalchemy
from typing import Union
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel


#SQLAlchemy specific code, as with any other app
DATABASE_URL = "sqlite:///./test.db"

#DATABASE_URL = "postgresql://user:passord@postgresserver/db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

todos = sqlalchemy.Table(
        "todos",
        metadata,
        sqlalchemy.Column("id",sqlalchemy.Integer,primary_key=True),
        sqlalchemy.Column("content",sqlalchemy.String),
        sqlalchemy.Column("slug",sqlalchemy.String),
        )
engine = sqlalchemy.create_engine(
        DATABASE_URL, connect_args =  {"check_same_thread": False }
)

metadata.create_all(engine)

#model Todo 
class Todo(BaseModel):
    title: str
    content: str
    slug: Union[str, None] = None


app = FastAPI()

#to connect to database
@app.on_event("startup")
async def startup():
    await database.connect()

#to disconnect to database
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/todos", response_model=List[Todo])
async def read_todos():
    query = todos.select()
    return await database.fetch_all(query)


@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    query = todos.select().where(todos.id == todo_id)
    return await database.fetch_all(query)

@app.post("/todos/", response_model = Todo)
async def add_todo(todo: Todo):
    query = todos.insert().values(title = todo.title,content = todo.content,slug = todo.slug)
    last_record_id = await database.execute(query)
    return {**todo.dict(),"id": last_record_id }

