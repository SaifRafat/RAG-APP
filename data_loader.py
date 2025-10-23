from openai import OpenAI
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

EMBED_MODEL = "text-embedding-3-large"
EMBED_DIM = 3072

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)
def load_and_split_pdf(file_path: str):
    docs = PDFReader().load_data(file_path=file_path)
    texts = [d.text for d in docs if getattr(d, 'text', None)]
    chunks = []
    for text in texts:
        chunks.extend(splitter.split_text(text))
    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:

    response = client.embeddings.create(
            input=texts,
            model=EMBED_MODEL
        )
    return [data.embedding for data in response.data]