import pydantic

class RAGChunkAndSrc(pydantic.BaseModel):
    source_id: str = None  
    chunks:list[str]


class RAGUpsertResult(pydantic.BaseModel):
    ingested:int

class RAGSearchResult(pydantic.BaseModel):
    contexts:list[str]
    sources:list[str]

class RAGQueryResult(pydantic.BaseModel):
    answer:str
    sources:list[str]
    num_contexts: int
