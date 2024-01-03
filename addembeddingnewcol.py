from pymongo import MongoClient
from openai import OpenAI
import os

# MongoDB and OPENAI setup 
MONGO_URI = os.environ["MONGO_URI"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

def connect_mongodb():
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["produit"]  # Replace with your database name
    return db

def get_embedding(text):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def update_documents_with_embeddings():
    db = connect_mongodb()

    # Access the original collection
    original_collection = db["bijous"]
    print("connected")
    # Access or create the new collection
    new_collection = db["retailProducts"]
    print("connected new")

    # Iterate over all documents in the original collection
    for document in original_collection.find({"processed": {"$ne": True}}):
    #    print("connected")
    #for document in original_collection.find():
        # Combine 'name' and 'subcategory' for embedding
        text_to_embed = f"{document.get('name', '')} {document.get('subcategory', '')} {document.get('category', '')} {document.get('variation_0_color', '')}  "
        print(text_to_embed)
        embedding = get_embedding(text_to_embed)

        # Prepare the updated document
        updated_document = document.copy()
        updated_document['nameEmbeddings'] = embedding

        # Insert the updated document into the new collection
        new_collection.insert_one(updated_document)

        # Mark the document as processed in the original collection
        original_collection.update_one(
            {"_id": document['_id']},
            {"$set": {"processed": True}}
        )

if __name__ == "__main__":
    update_documents_with_embeddings()
