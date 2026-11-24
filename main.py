from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from typing import Literal


app = FastAPI()


engine = create_engine('sqlite:///./animes.db')

class Base(DeclarativeBase):
    pass

class AnimeDB(Base):
    __tablename__ = 'animes'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    status: Mapped[str]

class AnimeEntrada(BaseModel):
    nome: str
    status: Literal['assistindo', 'finalizado', 'pausado']

class Anime(BaseModel):
    id: int 
    nome: str
    status: str

Base.metadata.create_all(engine)

def buscar_anime_ou_404(anime_id: int, session: Session):
    anime = session.get(AnimeDB, anime_id)
    if anime is None:
        raise HTTPException(status_code=404, detail='Anime não encontrado')
    return anime


@app.post('/animes', response_model=Anime)
async def adicionar_anime(anime: AnimeEntrada):
    novo = AnimeDB(nome=anime.nome, status=anime.status)
    with Session(engine) as session:
        session.add(novo)
        session.commit()
        session.refresh(novo)
    return novo

@app.get('/animes', response_model=list[Anime])
async def listar_animes():
    with Session(engine) as session:
        animes = session.query(AnimeDB).all()
    return animes

@app.get('/animes/{anime_id}', response_model=Anime)
async def buscar_anime(anime_id: int):
    with Session(engine) as session:
        anime = buscar_anime_ou_404(anime_id, session)
    return anime

@app.delete('/animes/{anime_id}')
async def deletar_anime(anime_id: int):
    with Session(engine) as session:
        anime = buscar_anime_ou_404(anime_id, session)
        session.delete(anime)
        session.commit()
    return {'mensagem': 'Anime deletado com sucesso'}

@app.put('/animes/{anime_id}', response_model=Anime)
async def atualizar_anime(anime_id: int, dados: AnimeEntrada):
    with Session(engine) as session:
        anime = buscar_anime_ou_404(anime_id, session)
        anime.nome = dados.nome
        anime.status = dados.status
        session.commit()
        session.refresh(anime)
    return anime

