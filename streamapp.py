import streamlit as st
import openai
from pymongo import MongoClient
import os
import base64
import requests


# MongoDB and OPENAI setup 
MONGO_URI = os.environ["MONGO_URI"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Function to get the embedding for a given text using OpenAI's API.
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']

# Connect to the MongoDB server and return the collection.
def connect_mongodb():
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["produit"]
    collection = db["products"]
    return collection

# Function to find similar documents in MongoDB based on the provided embedding.
def find_similar_documents(embedding):
    collection = connect_mongodb()
    documents = list(collection.aggregate([
        {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": embedding,
            "numCandidates": 10,
            "limit": 10,
            "filter": {"document_type": "child"}
            }
        },
        {"$project": {"_id": 0, "name": 1, "subcategory" :1, "model" :1, "id":1 }}
    ]))
    return documents

# Function to encode the image to base64
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# Function to analyze the image with OpenAI's GPT-4 Vision model
def analyze_image(image_bytes, user_prompt):
    # Convert the image to a base64 string
    base64_image = encode_image(image_bytes)

    # OpenAI API Key - Ensure to replace "YOUR_OPENAI_API_KEY" with your actual API key
    api_key = OPENAI_API_KEY
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt  # User's prompt replacing the static question
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    # Send a post request to the OpenAI API
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(response)
    # Return the JSON response from the API
    return response.json()


# Function to handle image uploads

def upload_photo():
    st.header("Upload your product photo")
    uploaded_image = st.file_uploader("Select photo and upload", type=['jpg', 'png'])
    if uploaded_image is not None:
        # To read the file as bytes:
        bytes_data = uploaded_image.getvalue()
        # Save the uploaded image to the session state
        st.session_state['uploaded_image'] = bytes_data
        # To convert to a format that Streamlit can use to display the image:
        st.image(bytes_data, caption='Uploaded photo', use_column_width=True)


# Function to handle the chatbot interaction and product extraction
def products_from_photo():
    st.header("Extract products from your photo")
    user_input = st.text_area("Ask the AI to extract outfit details:", "You are a helpful AI assistant, extract outfit from photo, each product in JSON format, with a detailed description.")
    
    # Retrieve the uploaded image from the session state
    bytes_data = st.session_state.get('uploaded_image', None)
   
    if bytes_data:
        st.write("Image is present.")
        st.image(bytes_data, caption='Uploaded Outfit', use_column_width=True)
    else:
        st.write("No image has been uploaded yet.")
    if st.button("Extract"):
        if bytes_data is not None and user_input:
            # Call the analyze_image function with the image bytes and user's prompt
            result = analyze_image(bytes_data, user_input)
            # Process the result and extract the outfit elements descriptions
            # The result processing will depend on the structure of the response
            st.write(result)  # Placeholder to display the raw result





# Function to display the products after vector search
def show_products():
    st.header("Show products from vector search")
    # Assuming 'vector_search_results' contains the product details from the vector search
    vector_search_results = []
    if st.button("Run vector search"):
        # Here you would run the vector search in MongoDB and store the results in 'vector_search_results'
        pass
    for product in vector_search_results:
        st.subheader(product.get("name", "Product Name"))
        st.image(product.get("image", ""), caption=product.get("name", "Product Name"))
        st.write(product.get("description", "Product Description"))

# Main app structure
def main():
    st.sidebar.title("My Smart Products Finder")
    menu = ["Upload Photo", "Products from Photo", "Show Products"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Upload Photo":
        upload_photo()
    elif choice == "Products from Photo":
        products_from_photo()
    elif choice == "Show Products":
        show_products()

if __name__ == "__main__":
    main()
