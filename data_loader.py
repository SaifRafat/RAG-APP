from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384 

print(f"🔄 Loading embedding model: {EMBED_MODEL}...")
_embedding_model = SentenceTransformer(EMBED_MODEL)
print(f"✅ Model loaded! Embedding dimension: {EMBED_DIM}")

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_split_pdf(file_path: str):
    """Load and split PDF into chunks"""
    docs = PDFReader().load_data(file=file_path)
    texts = [d.text for d in docs if getattr(d, 'text', None)]
    chunks = []
    for text in texts:
        chunks.extend(splitter.split_text(text))
    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed texts using local Sentence Transformers model (FREE)
    No OpenAI API key or credits needed!
    """
    embeddings = _embedding_model.encode(
        texts, 
        show_progress_bar=True,
        convert_to_numpy=True
    )
    return embeddings.tolist()