"""
Simple test script for RAG functionality
Tests PDF loading, embedding, and vector storage
"""
from data_loader import load_and_split_pdf, embed_texts
from vector_db import QdrantStorage
import uuid

def test_pdf_ingestion(pdf_path: str):
    """Test the complete RAG pipeline"""
    print(f"📄 Loading PDF: {pdf_path}")
    
    # Step 1: Load and split PDF
    try:
        chunks = load_and_split_pdf(pdf_path)
        print(f"✅ Loaded {len(chunks)} chunks from PDF")
        print(f"First chunk preview: {chunks[0][:100]}...")
    except Exception as e:
        print(f"❌ Error loading PDF: {e}")
        return
    
    # Step 2: Create embeddings
    try:
        print(f"\n🔄 Creating embeddings for {len(chunks)} chunks...")
        vectors = embed_texts(chunks)
        print(f"✅ Created {len(vectors)} embeddings (dimension: {len(vectors[0])})")
    except Exception as e:
        print(f"❌ Error creating embeddings: {e}")
        return
    
    # Step 3: Store in Qdrant
    try:
        print(f"\n💾 Storing vectors in Qdrant...")
        source_id = pdf_path
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
        
        db = QdrantStorage()
        db.upsert(ids, vectors, payloads)
        print(f"✅ Successfully stored {len(chunks)} chunks in Qdrant")
    except Exception as e:
        print(f"❌ Error storing in Qdrant: {e}")
        return
    
    # Step 4: Test search
    try:
        print(f"\n🔍 Testing search functionality...")
        query = "What is the main topic of this document?"
        query_vector = embed_texts([query])[0]
        
        contexts, sources = db.search(query_vector, top_k=3)
        print(f"✅ Search returned {len(contexts)} results")
        print(f"Sources: {sources}")
        if contexts:
            print(f"Top result preview: {contexts[0][:200]}...")
    except Exception as e:
        print(f"❌ Error during search: {e}")
        return
    
    print("\n✅ All tests passed successfully!")

if __name__ == "__main__":
    import sys
    import os
    
    # Check if PDF path is provided as argument
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Default test path
        pdf_path = r"C:\\Users\\Saif Rafat\\Downloads\\linux_basic_commands_cheatsheet.pdf"
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        print(f"\nUsage: python test_rag.py <path_to_pdf>")
        print(f"Example: python test_rag.py 'C:\\path\\to\\your\\file.pdf'")
        sys.exit(1)
    
    test_pdf_ingestion(pdf_path)
