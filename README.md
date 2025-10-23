# RAG PDF Upload System

A Retrieval-Augmented Generation (RAG) system for uploading PDFs to a vector database using Qdrant.

## Features

- 📄 PDF document loading and chunking
- 🔢 **FREE** Text embedding using Sentence Transformers (no API key needed!)
- 💾 Vector storage in Qdrant
- 🔄 Workflow orchestration with Inngest
- 🚀 FastAPI integration

## Prerequisites

1. **Qdrant** running on `localhost:6333`
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

2. **Python 3.12+** installed

3. **No API Key Required!** - Uses free local embeddings

## Installation

```bash
uv sync
```

## Usage

### Option 1: Direct Testing (No Inngest)

Test the RAG pipeline directly:

```bash
uv run python test_rag.py <path_to_your_pdf>
```

Example:
```bash
uv run python test_rag.py "C:\Documents\sample.pdf"
```

### Option 2: Using Inngest (Full Workflow)

1. **Start the FastAPI server:**
   ```bash
   uv run uvicorn main:app --reload
   ```

2. **Start Inngest Dev Server:**
   ```bash
   npx inngest-cli@latest dev
   ```

3. **Send an event to trigger PDF ingestion:**
   ```bash
   # Install requests if needed
   uv add requests
   
   # Run the test script
   uv run python test_inngest.py
   ```

   Or send a custom event:
   ```python
   import requests
   
   requests.post(
       "http://localhost:8288/e/rag_app",
       json={
           "name": "rag/inngest_pdf",
           "data": {
               "pdf_path": "path/to/your/file.pdf",
               "source_id": "optional_source_identifier"
           }
       }
   )
   ```

## Project Structure

- `main.py` - FastAPI app with Inngest function
- `data_loader.py` - PDF loading and embedding logic
- `vector_db.py` - Qdrant storage operations
- `custom_types.py` - Pydantic models
- `test_rag.py` - Direct testing script
- `test_inngest.py` - Inngest event testing script

## How It Works

1. **Load & Chunk**: PDFs are loaded and split into chunks (1000 chars with 200 overlap)
2. **Embed**: Each chunk is converted to a 384-dimensional vector using **FREE** Sentence Transformers (all-MiniLM-L6-v2)
3. **Store**: Vectors are stored in Qdrant with metadata (source, text)
4. **Search**: Similar chunks can be retrieved using vector similarity

## Why Sentence Transformers?

✅ **Completely FREE** - No API keys or credits needed  
✅ **Runs Locally** - Your data never leaves your machine  
✅ **Fast** - Optimized for CPU/GPU  
✅ **Good Quality** - State-of-the-art embeddings  
✅ **No Rate Limits** - Process as many documents as you want

## Troubleshooting

- **"PDF file not found"**: Make sure the PDF path is correct and file exists
- **"Connection refused to Qdrant"**: Ensure Qdrant is running on port 6333
- **"RetryError"**: Usually indicates file path or parameter issues
- **Model downloading slowly**: First run downloads the embedding model (~80MB), subsequent runs are fast

## Recent Updates

- ✅ **Switched to FREE Sentence Transformers** - No OpenAI API needed!
- ✅ Fixed variable scope in `_upsert` function
- ✅ Fixed typo `inngested` → `ingested`
- ✅ Fixed `sources.app()` → `sources.add()` in vector_db
- ✅ Updated PDFReader parameter from `file_path` to `file`
- ✅ Updated embedding dimension from 3072 to 384
