"""
Test script to send events to Inngest for RAG PDF processing
"""
import requests
import json

# Inngest Dev Server URL (default)
INNGEST_DEV_URL = "http://localhost:8288"

def send_pdf_event(pdf_path: str, source_id: str = None):
    """
    Send a PDF ingestion event to Inngest
    
    Args:
        pdf_path: Path to the PDF file
        source_id: Optional source identifier (defaults to pdf_path)
    """
    event_data = {
        "name": "rag/inngest_pdf",
        "data": {
            "pdf_path": pdf_path,
        }
    }
    
    if source_id:
        event_data["data"]["source_id"] = source_id
    
    # Send to Inngest Dev Server
    response = requests.post(
        f"{INNGEST_DEV_URL}/e/rag_app",
        json=event_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"✅ Event sent successfully!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Error sending event: {response.status_code}")
        print(f"Response: {response.text}")
    
    return response

if __name__ == "__main__":
    # Test with your PDF
    pdf_path = r"C:\\Users\\Saif Rafat\\Downloads\\linux_basic_commands_cheatsheet.pdf"
    
    print(f"Sending PDF ingestion event for: {pdf_path}")
    send_pdf_event(pdf_path)
