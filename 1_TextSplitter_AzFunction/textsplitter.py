import logging
import PyPDF2
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import azure.functions as func

def main(myblob: func.InputStream):
    logging.info(f"Processing blob \nName: {myblob.name}\nBlob Size: {myblob.length} bytes")

    # Read the PDF file from the input blob
    pdf_reader = PyPDF2.PdfFileReader(myblob)
    num_pages = pdf_reader.numPages

    # Azure Blob Storage connection string and container names
    connection_string = os.getenv('AzureWebJobsStorage')
    output_container_name = 'output-container'

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Split the PDF into individual pages and upload to output container
    for i in range(num_pages):
        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.addPage(pdf_reader.getPage(i))

        output_filename = f'split_page_{i + 1}.pdf'
        output_blob_client = blob_service_client.get_blob_client(container=output_container_name, blob=output_filename)

        with open(output_filename, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)

        # Upload the split PDF to the output container
        with open(output_filename, 'rb') as data:
            output_blob_client.upload_blob(data, overwrite=True)

        # Remove the local file after uploading
        os.remove(output_filename)

    logging.info(f"PDF split into {num_pages} pages and uploaded to {output_container_name} container.")