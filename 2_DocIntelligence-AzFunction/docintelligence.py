import logging
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient
import azure.functions as func

def main(myblob: func.InputStream):
    logging.info(f"Processing blob \nName: {myblob.name}\nBlob Size: {myblob.length} bytes")

    # Azure Blob Storage connection string and container names
    connection_string = os.getenv('AzureWebJobsStorage')
    output_container_name = 'output-container'
    output_blob_name = myblob.name.replace('.pdf', '.txt')

    # Azure Document Intelligence credentials
    endpoint = os.getenv('FORM_RECOGNIZER_ENDPOINT')
    key = os.getenv('FORM_RECOGNIZER_KEY')

    # Create a DocumentAnalysisClient
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Read the PDF file from the input blob
    pdf_content = myblob.read()

    # Analyze the PDF using Azure Document Intelligence
    poller = document_analysis_client.begin_analyze_document("prebuilt-document", pdf_content)
    result = poller.result()

    # Extract text from the analyzed document
    text_content = ""
    for page in result.pages:
        for line in page.lines:
            text_content += line.content + "\n"

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    output_blob_client = blob_service_client.get_blob_client(container=output_container_name, blob=output_blob_name)

    # Upload the extracted text to the output container
    output_blob_client.upload_blob(text_content, overwrite=True)

    logging.info(f"Extracted text from {myblob.name} and uploaded to {output_container_name} container as {output_blob_name}.")