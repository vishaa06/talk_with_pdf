import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from dotenv import load_dotenv
import uuid
import os
import datetime
#from google import genai
from openai import OpenAI
from data_loader import load_and_chunk_pdf,embed_texts
from vector_db import QdrantStorage
from custom_types import RAGChunkAndSrc,RAGUpsertResult,RAGSearchResult,RAGQueryResult

load_dotenv()

#genai_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

storage = QdrantStorage()

inngest_client=inngest.Inngest(
    app_id="rag_app",
    is_production=False,
    logger=logging.getLogger("uvicorn"),
    serializer=inngest.PydanticSerializer()    
)

@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf")
)
async def rag_ingest_pdf(ctx:inngest.Context):
    def _load(ctx:inngest.Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id",pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks,source_id=source_id)
        

    def _upsert(data:RAGChunkAndSrc) -> RAGUpsertResult:
        #chunks=chunks_and_src.chunks
        #source_id=chunks_and_src.source_id
        #data = RAGChunkAndSrc(**chunks_and_src)
        chunks = data.chunks
        source_id = data.source_id
        vecs=embed_texts(chunks)
        ids=[str(uuid.uuid5(uuid.NAMESPACE_URL,f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads=[{"source":source_id,"text":chunks[i]} for i in range(len(chunks))]
        storage.upsert(ids,vecs,payloads)
        return RAGUpsertResult(ingested=len(chunks))


    chunks_and_src = await ctx.step.run("load-and-chunk",lambda: _load(ctx),output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunks_and_src),output_type=RAGUpsertResult)
    return ingested.model_dump()

@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
async def rag_query_pdf_ai(ctx:inngest.Context):
    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", 5))
    
    """def _search(question: str, top_k: int = 5) -> RAGSearchResult:
        query_vec = embed_texts([question])[0]

        found = storage.search(query_vec, top_k)

        return RAGSearchResult(
            contexts=found["contexts"],
            sources=found["sources"]
        )"""
    def _search_step() -> RAGSearchResult:
        # 1. Embed the question
        query_vec = embed_texts([question])[0]
        raw_results = storage.search(query_vec, top_k)

        # 2. Get results from Qdrant
        # This now returns: [{"content": "...", "source": "..."}, ...]

        # 3. Format for the RAGSearchResult Pydantic model
        return RAGSearchResult(
            contexts=[r["content"] for r in raw_results],
            sources=list(set([r["source"] for r in raw_results])) # unique sources
        ).model_dump()


    found_dict = await ctx.step.run("embed-and-search", _search_step)
    
    # 2. Re-hydrate into an object so .contexts and .sources work!
    found = RAGSearchResult(**found_dict)

    if not found.contexts:
        return {
            "answer": "Not found in document",
            "sources": [],
            "num_contexts": 0
        }

    context_block="\n\n".join(f"- {c}" for c in found.contexts)
    user_content=(
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer concisely using ONLY the provided context. If the answer is not present, say 'Not found in document'."
    )

    """def _generate_answer():
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_content
        )
        return response.text

    answer = await ctx.step.run("generate-answer", _generate_answer)
    return {
        "answer": answer,
        "sources": found.sources,
        "num_contexts": len(found.contexts)
    }"""

    def _generate_answer():
        response = openrouter_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "user", "content": user_content}
            ]
        )
        return response.choices[0].message.content

    answer = await ctx.step.run("generate-answer", _generate_answer)

    return {
        "answer": answer,
        "sources": found.sources,
        "num_contexts": len(found.contexts)
    }


"""@inngest_client.create_function(
    fn_id="RAG: Search",
    trigger=inngest.TriggerEvent(event="rag/search"),
    react={})
async def rag_search(ctx:inngest.Context):
    def _search(query_vector,top_k=5):
        return QdrantStorage().sreach(query_vector,top_k)
    
    q = await ctx.step.run("retrieve-docs", lambda: _search(ctx.event.data["query_vector"], top_k=ctx.event.data.get("top_k",5)), output_type=dict)

    return q  """  



app=FastAPI()
inngest.fast_api.serve(app,inngest_client,[rag_ingest_pdf, rag_query_pdf_ai])