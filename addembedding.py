from pymongo import MongoClient
import openai
import os

# MongoDB and OPENAI setup 
MONGO_URI = os.environ["MONGO_URI"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

def connect_mongodb():
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["produit"]  # Replace with your database name
    collection = db["products"]  # Replace with your collection name
    return collection

def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def update_documents_with_embeddings():
    collection = connect_mongodb()

    # Iterate over all documents in the collection
    for document in collection.find():
        # Combine 'name' and 'subcategory' for embedding
        text_to_embed = f"{document.get('name', '')} {document.get('subcategory', '')}"
        embedding = get_embedding(text_to_embed)

        # Update the document with the new 'nameEmbeddings' field
        collection.update_one(
            {"_id": document['_id']},
            {"$set": {"nameEmbeddings": embedding}}
        )

if __name__ == "__main__":
    update_documents_with_embeddings()
