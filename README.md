# Mongo Multimodal Smart Products Finder

My Smart Products Finder is an advanced AI-powered application designed to revolutionize your fashion and retail experience. With a sleek, user-friendly interface, this app provides detailed insights into fashion products, interactive recommendations, and up-to-date fashion data analysis.
Demo video: https://recordit.co/En1QRevYM5

## Features

- **AI-Powered Product Analysis**: Utilize state-of-the-art AI to gain detailed insights into various fashion products from just a photo.
- **Interactive Product Recommendations**: Receive instant, AI-driven product recommendations that align with your style and preferences.
- **Visual Product Uploads**: Easily upload product images and let the AI provide you with detailed analysis and descriptions.
- **Customizable Search Experience**: Tailor your search with filters to find exactly what you're looking for in the vast fashion landscape.
- **User-Friendly Interface**: Navigate through the app with ease, thanks to the intuitive layout and design.
- **Up-to-Date Fashion Data**: Stay informed with the latest fashion trends, prices, and popular styles.

## Getting Started

To get started with My Smart Products Finder, follow these instructions:

### Prerequisites

Ensure you have the following installed:
- Python 3.10 
- Pip package manager
- MongoDB
- OpenAI API key

### Installation

Clone the repository to your local machine:
```bash
git clone https://github.com/your-username/my-smart-products-finder.git
cd my-smart-products-finder
```

Install the required Python packages:
```
pip install -r requirements.txt
```

Set your environment variables for MONGO_URI and OPENAI_API_KEY:
```
export MONGO_URI="your_mongodb_uri"
export OPENAI_API_KEY="your_openai_api_key"
```

Run the Streamlit application:
```streamlit run app.py```

### Setup
Environment Variables: Set MONGO_URI and OPENAI_API_KEY in your environment.
Install Dependencies: Run pip install -r requirements.txt (assuming a requirements.txt file with necessary libraries is present).
### Usage
Start the Application: 
```Run streamlit run [app_file_name].py```
Use the Interface: Navigate through the sidebar menu to upload images, extract product details, or perform a vector search.
```http://localhost:8501/```

### Disclaimer
The application requires a valid OpenAI API key and MongoDB URI.
The performance and accuracy of the AI model depend on the OpenAI's GPT-4 Vision model capabilities and the quality of data in MongoDB.
### Support
For issues, suggestions, or contributions, please open an issue or pull request on the project's GitHub repository.

### License
[License information, if applicable]
