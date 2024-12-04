import streamlit as st
import openai
from openai import OpenAI
from pymongo import MongoClient
import os
import base64
import requests
import json


# MongoDB and OPENAI setup 
MONGO_URI = os.environ["MONGO_URI"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Function to get the embedding for a given text using OpenAI's API.
def get_embedding(text):
    client = OpenAI()
    response = client.embeddings.create(
    input=text,
    model="text-embedding-ada-002"
    )
    return response.data[0].embedding

# Connect to the MongoDB server and return the collection.
def connect_mongodb():
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["produit"]
    collection = db["retailProducts"]
    return collection

# Function to find similar documents in MongoDB based on the provided embedding.
def find_similar_documents(embedding):
    collection = connect_mongodb()
    documents = list(collection.aggregate([
        {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "nameEmbeddings",
            "queryVector": embedding,
            "numCandidates": 10,
            "limit": 1
            }
        },
        {"$project": {"_id": 0, "name": 1, "subcategory" :1, "model" :1, "id":1 , "variation_0_image":1, "raw_price":1}}
    ]))
    print(documents)
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
        "model": "gpt-4o",
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

    response_js = response.json() 

    # Extract the content from the first choice
    content = response_js.get('choices', [{}])[0].get('message', {}).get('content', '')
    

    # Ensure the response is OK
    if response.status_code == 200:
        try:
            response_js = response.json()

            # Extracting the content
            content = response_js.get('choices', [{}])[0].get('message', {}).get('content', '')

            # Find the start and end of the JSON object
            json_start_index = content.find('{')
            json_end_index = content.rfind('}')

            if json_start_index != -1 and json_end_index != -1:
                # Extract only the valid JSON part
                content = content[json_start_index:json_end_index+1]

            # Debugging: Print the content
            print("Content received:", content)

            if content:
                # Parsing the content as JSON
                content_dict = json.loads(content)
                product_list = content_dict.get('product_list', {})
                st.session_state['product_list'] = product_list
                if not isinstance(product_list, dict):
                    print("product_list is not a dictionary.")
                    return {}
                return product_list
            else:
                print("No content received in the response.")
                return {}

        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
            return {}

    else:
        print(f"Failed API request with status code: {response.status_code}")
        return {}



# Function to handle image uploads

def upload_photo():
    st.header("Upload your product photo")
    # Create columns
    uploaded_image = st.file_uploader("Select photo and upload", type=['jpg', 'png'])
    col1, col2, col3 = st.columns([1, 2, 1]) # Adjust the ratio as needed
    with col1:
        # Empty column for spacing
        st.write("")

    with col2:
        # The actual file uploader
        
        if uploaded_image is not None:
            # To read the file as bytes:
            bytes_data = uploaded_image.getvalue()
            # Save the uploaded image to the session state
            st.session_state['uploaded_image'] = bytes_data
            # To convert to a format that Streamlit can use to display the image:
            st.image(bytes_data, caption='Uploaded photo', use_column_width=True)
    with col3:
        # Empty column for spacing
        st.write("")

# Function to handle the chatbot interaction and product extraction
def products_from_photo():
    st.header("Extract products from your photo")
    
    user_prompt = ("You are a helpful AI assistant, extracting outfit products from the photo, each product in a separate JSON format, "
                   "with a simple description and color in French. "
                   "You should follow strictly the format but not the content: "
                   "```{\"product_list\": {\"{category of product}\": \"{product descriptions}\", \"{category of product}\": "
                   "\"{product descriptions}\", \"{category of product}\": \"{product descriptions}\", "
                   "\"{category of product}\": \"{product descriptions}\"}```")
    user_input = st.text_area("Ask the AI to extract outfit details:", user_prompt, height=200)

    # Retrieve the uploaded image from the session state
    bytes_data = st.session_state.get('uploaded_image', None)
    
    if bytes_data:
        st.write("Image is present.")
        col1, col2, col3 = st.columns([1, 2, 1]) # Adjust the ratio as needed
        with col1:
            # Empty column for spacing
            st.write("")

        with col2:
            # The actual file uploader
            
            st.image(bytes_data, caption='Uploaded Outfit', use_column_width=True)
        with col3:
            # Empty column for spacing
            st.write("")
   
    else:
        st.write("No image has been uploaded yet.")
    if st.button("Extract"):
        if bytes_data is not None and user_input:
            # Call the analyze_image function with the image bytes and user's prompt
            result = analyze_image(bytes_data, user_input)
            # Process the result and extract the outfit elements descriptions
            # The result processing will depend on the structure of the response
            st.write(result)  # Placeholder to display the raw result


def product_Recommandation(product_list):
    # Initialize an empty list for the search results
    search_results = []

    # Check if product_list is valid
    if not isinstance(product_list, dict):
        print("Invalid product list. Expected a dictionary.")
        return search_results

    # Iterate over the products in the list
    for key, value in product_list.items():
        result = f"{key}: {value}\n"
        print(result)
        product_embedding = get_embedding(result)
        print(f"Searching for: {key}: {value}")
        documents = find_similar_documents(product_embedding)

        # Add the found documents to the search results
        search_results.extend(documents)

    # Return the list of found documents
    return search_results




# Function to display the products after vector search

def show_products1():
    st.header("Show products from vector search")

    # Check if 'product_list' is available in the session state
    if 'product_list' in st.session_state:
        product_list = st.session_state['product_list']

        # Call the product_Recommandation function
        vector_search_results = product_Recommandation(product_list)

        # Check if the result is not None and is iterable
        if vector_search_results:
            for product in vector_search_results:
                st.subheader(product.get("name", "Product Name"))
                st.image(product.get("image_url", ""), caption=product.get("name", "Product Name"))
                st.write(product.get("description", "Product Description"))
        else:
            st.write("No products found or no product list provided.")
    else:
        st.write("No product list found. Please analyze an image first.")

def show_products():
    st.header("Show Products from Vector Search")

    # Check if 'product_list' is available in the session state
    if 'product_list' in st.session_state and st.session_state['product_list']:
        product_list = st.session_state['product_list']

        # Assuming product_list is a dictionary
        if isinstance(product_list, dict):
            st.subheader("Current Product List:")

            # Temporary dictionary to store modifications
            modified_product_list = {}

            for category, description in product_list.items():
                st.text(f"Category: {category}")
                modified_description = st.text_area(f"Modify description for {category}", value=description)
                modified_product_list[category] = modified_description

            if st.button("Update and Search Similar Products"):
                # Update session state with modified product list
                st.session_state['product_list'] = modified_product_list

                # Call the product_Recommandation function with the updated product list
                vector_search_results = product_Recommandation(modified_product_list)

                # Display the search results
                if vector_search_results:
                    st.subheader("Search Results:")
                    st.subheader("Search Results:")
                    for product in vector_search_results:
                        product_name = product.get("name", "Unknown Product Name")
                        product_subcategory = product.get('subcategory', 'Unknown')
                        product_image_url = product.get("variation_0_image", "")

                        # Debugging: Print the image URL
                        print("Attempting to display image URL:", product_image_url)

                        st.write(product_name)
                        st.write(f"Subcategory: {product_subcategory}")

                        # Display the image if the URL is present
                        if product_image_url:
                            try:
                                col1, col2, col3 = st.columns([1, 2, 1]) # Adjust the ratio as needed
                                with col1:
                                    # Empty column for spacing
                                    st.write("")

                                with col2:
                                    # The actual file uploader
                                    st.image(product_image_url, caption=product_name, use_column_width=True)
                                with col3:
                                    # Empty column for spacing
                                    st.write("")
                                
                            except Exception as e:
                                st.error(f"Error displaying image: {e}")
                        else:
                            st.write("No image available for this product.")
                        #st.write(product.get("name", "Unknown Product Name"))
                        #st.write(f"Subcategory: {product.get('subcategory', 'Unknown')}")
                        #st.image(product.get("image_url", ""), caption=product.get("name", "Product Name"), use_column_width=True)
                else:
                    st.write("No similar products found.")
                

        else:
            st.error("The product list is not in the expected format. Please check the data source.")
    else:
        st.write("No product list found. Please analyze an image first.")


# Main app structure
def main1():
    st.sidebar.title("My Smart Products Finder")
    menu = ["Upload Photo", "Products from Photo", "Show Products"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Upload Photo":
        upload_photo()
    elif choice == "Products from Photo":
        products_from_photo()
    elif choice == "Show Products":
        show_products()
# Function to use icons
def load_fontawesome():
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        """, unsafe_allow_html=True)

def main():
    load_fontawesome()
    st.sidebar.title("Mongo Smart Products Finder")
    page = st.sidebar.radio("Select a Page", ["Homepage", "Upload", "Analysis","Products Search"])

    if page == "Homepage":
        st.title("Welcome to Mongo Smart Products Finder")
        st.markdown("""
            <style>
                .icon {
                    font-size: 22px; /* Icon size */
                    color: #2678EC; /* Icon color */
                }
                h1 {
                    color: #2678EC; /* Header color */
                    font-size: 40px; /* Header size */
                }
                .feature {
                    margin: 16px 0px;
                    font-size: 18px; /* Feature text size */
                }
                .feature-header {
                    font-weight: bold;
                    color: #2678EC; /* Feature header color */
                    display: block; /* Make the feature header block so icon and text are on the same line */
                    font-size: 20px; 
                }
                .st-bb {
                    border-bottom: 1px solid #2678EC;
                }
                .st-bb .st-eb {
                    border-bottom: none;
                }
            </style>
            """, unsafe_allow_html=True)

        # Feature section with icons
        features = {
            "fa-search": "AI-Powered Product Analysis: Dive into detailed insights with our advanced AI.",
            "fa-thumbs-up": "Interactive Product Recommendations: Get instant product recommendations.",
            "fa-camera": "Visual Product Uploads: Easily upload images for detailed AI analysis.",
            "fa-cogs": "Customizable Search Experience: Modify your search to find exactly what you want.",
            "fa-users": "User-Friendly Interface: Sleek, modern interface for easy navigation.",
            "fa-line-chart": "Up-to-Date Fashion Data: Stay on top of the latest trends and styles."
        }

        for icon, desc in features.items():
            st.markdown(f"""
                <div class="feature">
                    <i class="fa {icon} icon"></i>
                    <span class="feature-header">{desc.split(':')[0]}</span>
                    <span>{desc.split(':')[1]}</span>
                </div>
                """, unsafe_allow_html=True)

    elif page == "Upload":
        st.title("Upload the outfit you want to get")
        upload_photo()

    elif page == "Analysis":
        st.title("Product Analysis")
        st.write("Product analysis details will be shown here.")
        products_from_photo()
    
    elif page == "Products Search":
        st.title("Products Search in my favorite shop")
        st.write("Similar Products details will be shown here.")
        show_products()

if __name__ == "__main__":
    main()




