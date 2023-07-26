from flask import Flask, jsonify, request
import os
import fitz  # PyMuPDF
import io
from PIL import Image
import base64
app = Flask(__name__)


def extract_images_from_pdf(pdf_file):
    extracted_images = []

    # Iterate over PDF pages
    for page_index in range(len(pdf_file)):
        # Get the page itself
        page = pdf_file[page_index]
        # Get image list
        image_list = page.get_images(full=True)
        # Iterate over the images on the page
        for image_index, img in enumerate(image_list, start=1):
            # Get the XREF of the image
            xref = img[0]
            # Extract the image bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            # Get the image extension
            image_ext = base_image["ext"]
            # Load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert image_bytes to a base64-encoded string
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            extracted_images.append({
                "image_base64": image_base64,
                "image_ext": image_ext,
                "page": page_index + 1,
                "image_index": image_index
            })

    return extracted_images


# Routes
@app.route("/")
def home():
    return "PDF Image Extractor API"

# POST /get_pdf_images
@app.route("/get_pdf_images", methods=["POST"])
def get_images_from_pdf():
    # Check if there is a pdf file in the request
    if not request.files:
        return jsonify({"message": "No pdf file uploaded"}), 400
    # Get the pdf file from the request
    
    pdf_file = request.files["pdf_file"]

    if not pdf_file:
        return jsonify({"message": "No pdf file uploaded"}), 400

    # Check if the pdf file is one of the allowed types/extensions
    if pdf_file.filename.split(".")[-1] != "pdf":
        return jsonify({"message": "Invalid pdf file"}), 400
    
    # parse the pdf file with PyMuPDF
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    # Extract images
    extracted_images = extract_images_from_pdf(pdf_document)

    # Return the images
    return jsonify({"images": extracted_images}), 200




if __name__ == "__main__":
    app.run(debug=True)