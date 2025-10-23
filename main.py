import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv
import os
import datetime
import uuid

from data_loader import load_and_split_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAGChunkAndSrc, RAGUpsertResult, RAGSearchResult, RAGQueryResult

load_dotenv()


inngest_client = inngest.Inngest(
    app_id = "rag_app",
    logger = logging.getLogger("uvicorn"),
    is_production = False,
    serializer = inngest.PydanticSerializer(),
)

@inngest_client.create_function(
    fn_id="RAG : Inngest PDF",
    trigger= inngest.TriggerEvent(event="rag/inngest_pdf"),
)
async def rag_inngest_pdf(ctx: inngest.Context):
        # Access event data correctly from ctx.event.data
        pdf_path = ctx.event.data.get("pdf_path")
        source_id = ctx.event.data.get("source_id", pdf_path)
        
        print(f"📄 Processing PDF: {pdf_path}")
        print(f"🔖 Source ID: {source_id}")
        
        def _load() -> RAGChunkAndSrc:
            chunks = load_and_split_pdf(pdf_path)
            print(f"✅ Loaded {len(chunks)} chunks")
            return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

        def _upsert(data: RAGChunkAndSrc) -> RAGUpsertResult:
            chunks = data.chunks
            source_id = data.source_id
            print(f"🔄 Creating embeddings for {len(chunks)} chunks...")
            vectors = embed_texts(chunks)
            print(f"✅ Created {len(vectors)} embeddings")
            
            ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
            payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
            
            print(f"💾 Storing vectors in Qdrant...")
            QdrantStorage().upsert(ids, vectors, payloads)
            print(f"✅ Successfully stored {len(chunks)} chunks")
            return RAGUpsertResult(ingested=len(chunks))

        # Execute steps sequentially with explicit output types for serialization
        chunks_and_src = await ctx.step.run(
            "load-and-chunk",
            _load,
            output_type=RAGChunkAndSrc,
        )
        ingested = await ctx.step.run(
            "embed-and-upsert",
            lambda: _upsert(chunks_and_src),
            output_type=RAGUpsertResult,
        )

        result = {"ingested": ingested.ingested}
        print(f"🎉 Completed! Result: {result}")
        return result
        
@inngest_client.create_function(
    fn_id="RAG : Query PDF",
    trigger= inngest.TriggerEvent(event="rag/query_pdf"),
)
async def rag_query_pdf(ctx: inngest.Context):
    # Retrieve-only query using free Sentence Transformers embeddings (no LLM)
    question = ctx.event.data.get("question")
    top_k = int(ctx.event.data.get("top_k", 5))

    def _embed_query() -> list[float]:
        return embed_texts([question])[0]

    def _search(query_vector) -> RAGSearchResult:
        store = QdrantStorage()
        contexts, sources = store.search(query_vector=query_vector, top_k=top_k)
        # Ensure JSON-serializable types
        return RAGSearchResult(contexts=contexts, sources=sorted(list(sources)))

    query_vector = await ctx.step.run("embed-query", _embed_query)
    found = await ctx.step.run("vector-search", lambda: _search(query_vector), output_type=RAGSearchResult)

    def _compose_answer() -> RAGQueryResult:
        if found.contexts:
            # Simple extractive answer: return the top matching chunk
            best = found.contexts[0]
            # Trim overly long chunks in the answer for readability
            answer = best if len(best) <= 1024 else best[:1024] + "…"
        else:
            answer = "No relevant context found. Try rephrasing your question."
        return RAGQueryResult(answer=answer, sources=found.sources, num_contexts=len(found.contexts))

    result = await ctx.step.run("compose-answer", _compose_answer, output_type=RAGQueryResult)
    return result.model_dump()

app = FastAPI()
inngest.fast_api.serve(app, inngest_client, [rag_inngest_pdf, rag_query_pdf])