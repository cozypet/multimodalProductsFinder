# multimodalProductsFinder
### Introduction
Smart Products Finder is an AI-powered application that uses Streamlit for the frontend, MongoDB for data storage, and OpenAI's large language models for analyzing images and text. It offers a user-friendly interface to upload product photos, extract product details using AI, and perform vector searches on a MongoDB database to find similar products.

### Features
##### Image Upload: Users can upload product images for analysis.
AI Analysis of Images: Leverages OpenAI's GPT-4 Vision model to analyze uploaded images and extract product details.
Text Embedding and Vector Search: Utilizes OpenAI's embedding model to convert text to embeddings, and performs vector searches in MongoDB to find similar products.
Streamlit Interface: Offers an easy-to-use web interface for interacting with the application.
### Requirements
Python 3.6 or later
Streamlit
OpenAI Python Library
Pymongo
MongoDB server access
Internet connection for API calls to OpenAI
### Setup
Environment Variables: Set MONGO_URI and OPENAI_API_KEY in your environment.
Install Dependencies: Run pip install -r requirements.txt (assuming a requirements.txt file with necessary libraries is present).
### Usage
Start the Application: 
```Run streamlit run [app_file_name].py```
Use the Interface: Navigate through the sidebar menu to upload images, extract product details, or perform a vector search.
### Functions
#### get_embedding(text, model): Gets the embedding for a given text using OpenAI's API.
#### connect_mongodb(): Connects to MongoDB and returns the collection.
#### find_similar_documents(embedding): Finds similar documents in MongoDB based on the provided embedding.
#### encode_image(image_bytes): Encodes the image to base64.
#### analyze_image(image_bytes, user_prompt): Analyzes the image with OpenAI's GPT-4 Vision model.
#### upload_photo(): Handles image uploads.
#### products_from_photo(): Extracts products from an uploaded photo.
#### show_products(): Displays products after a vector search.
### Disclaimer
The application requires a valid OpenAI API key and MongoDB URI.
The performance and accuracy of the AI model depend on the OpenAI's GPT-4 Vision model capabilities and the quality of data in MongoDB.
### Support
For issues, suggestions, or contributions, please open an issue or pull request on the project's GitHub repository.

### License
[License information, if applicable]
