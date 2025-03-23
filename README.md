# AI News Scraper & Summarizer with Text-to-Speech

## **Introduction**

This project is a **learning-focused exploration** of AI-powered text processing, **news summarization**, and **Flask API handling** using **Hugging Face models** and **Gradio** for UI.


## Table of Content

1. [Key Features & Workflow](#Key-Features--Workflow)
2. [Objectives](#Objectives)
3. [Tech Stack Used](#Tech-Stack-Used)
4. [Approach & Explorations](#Approach--Explorations)
5. [Performance Analysis](#Performance-Analysis)
6. [Setup & Installation](#Setup--Installation)
7. [Future Enhancements](#Future-Enhancements)
8. [Need Help?](#Need-Help)


## **Key Features & Workflow:**

1. **Scrape News** → Fetch up to **10 news articles** (title and content) from Google News based on a company name.
2. **Summarization & Analysis** → Use **BART and Gemini API** to generate:
	- Summarization
    - Key insights and trends
    - Sentiment analysis
    - Positive & negative aspects
    - Comparative insights
3. **Text-to-Speech** → Convert summaries into **speech output** for accessibility.
4. **Flask API Integration** → A **Flask backend** was explored to handle user requests and return responses in JSON format.

News Article Processing Funnel
Web Scraping
Article Summarization
Display Summary
Insights Generation![image](https://github.com/user-attachments/assets/ab4b4d44-31a7-4a6f-81d0-187569105ac3)




While this is not a full **Retrieval-Augmented Generation (RAG) model**, it follows a similar **fetch-process-generate** workflow. This project helped me get started with:

- **Scraping & processing real-world data**
- **Using LLMs for text summarization & analysis**
- **Deploying AI applications with [Gradio](https://www.gradio.app/) for UI**
- **Exploring [Hugging Face](https://huggingface.co/) model hosting & inference**

This project serves as a foundational step toward building more advanced AI applications.


## **Objectives**

This project primarily focuses on **learning and exploration** of AI-powered text processing, summarization, and API handling using **Hugging Face models**, **Google News scraping**, and **Gradio UI**.

### Key Goals

1. **Scrape news articles from Google**
    - Use `BeautifulSoup` to extract article links while respecting publishers.
    - Identify and filter **static pages** (excluding JavaScript-heavy content).
    - Fetch and store up to **10 relevant articles** for further processing.

2. **Summarization using LLMs (BART & Gemini API)**
    - Use `facebook/bart-large-cnn` (efficient yet powerful) for summarization.
    - **Chunk large articles** into smaller parts, summarize each, and combine the results.
    - Optionally use **Gemini API** for high-quality, multi-faceted summaries.

3. **Text-to-Speech conversion (TTS)**
    - Convert summarized text to **speech output** using `gTTS` for accessibility.

4. **Insight Extraction & Sentiment Analysis**
    - Utilize **Gemini API** to analyze trends, positive/negative points, and comparisons.
    - Generate **actionable insights** from summarized content.

5. **Build an AI-powered UI using Gradio**
    - Leverage **Gradio** for an interactive frontend with minimal effort.
    - Quickly visualize input/output for AI models and refine results.

6. **Develop API routes with Flask**
    - Implement a **Flask backend** to process user requests.
	- Return **structured JSON responses** for seamless integration.

### Additional Learnings

- Understanding **Hugging Face model integration** for real-world AI applications.
- Exploring **Gemini API’s free-tier capabilities** for generative AI tasks.
- **Using LLMs & Flask together** to create an end-to-end AI pipeline.


## **Tech Stack Used**

This project integrates **AI models, web scraping, and Flask API development** with various libraries and tools.

### 1. AI & NLP Models
   - **Transformers (`transformers`)** – Used Hugging Face’s `facebook/bart-large-cnn` for **text summarization**.
   - **Gemini API (Gemini 2.0 Flash)** – Provides **deep insights, comparative analysis, and sentiment understanding**.
   - **TextBlob (`textblob`)** – Used for **initial sentiment analysis** of news titles and content.

### 2. Web Scraping & Data Processing
- **BeautifulSoup (`bs4`)** – Extracts **news links & content** from Google News while filtering JavaScript-heavy pages.
- **Requests (`requests`)** – Handles **HTTP requests** to fetch webpage content.

### 3. Text-to-Speech (TTS)
- **Google Text-to-Speech (`gtts`)** – Converts **summarized content** into **speech output**.

### 4. API Development & UI
- **Flask (`flask`)** – Used to create a **lightweight API** that processes and returns JSON responses.
- **Gradio (`gradio`)** – Provides an **interactive UI** to test and visualize AI-powered summaries.

### 5. Optional Tools
- **Postman** – Used for **API testing and debugging**.
- **Python Community Edition (IDE)** – Primary development environment.
- **Docker – Containerizes the application to ensure **portability and scalability**.


## **Approach & Explorations**  

### **How did I approach building the project?**  

The development process followed a structured, objective-driven workflow:  

1. **Scraping Data** – Extracted **news links** from Google News using **BeautifulSoup** while handling JavaScript-heavy pages.  
2. **Fetching Article Content** – Retrieved **titles and full content** from extracted URLs while ensuring minimal noise.  
3. **Summarization** – Processed the article content using **Hugging Face’s `facebook/bart-large-cnn` model** for extracting key points.  
4. **Sentiment & Insights** – Applied **TextBlob** for initial sentiment analysis and **Gemini API** for deeper insights and comparative analysis.  
5. **Text-to-Speech Conversion** – Used **gTTS** to generate **audio output** for summarized content.  


### **Challenges Faced & Solutions**  

- **Integrating Hugging Face Models Efficiently**  
  - The main challenge was dealing with **long articles exceeding token limits**.  
  - **Solution:** Split content into **smaller chunks**, then **tokenize and summarize** piece by piece before merging results.  

- **Handling Different Article Formats**  
  - Some articles had **incomplete or misleading metadata**, affecting content extraction.  
  - **Solution:** Applied **heuristic filtering** to remove unnecessary elements and improve extracted text quality. 

- **Model Selection & Exploration**
  - Tested models like **Deepseek, Mistral, Phi-2, Ollama, Falcon**, but found them **too resource-intensive**.
  - **Final Decision:** Chose `BART-Large-CNN` for its **efficiency & summarization quality**.

- **Resource Constraints**
  - **Challenge:** Running large Hugging Face models on **16GB RAM + GTX 1650**.
  - **Solution:** Used **model quantization & batch processing** to optimize performance.


### **Exploring Different Models Before Finalizing One**  

Before finalizing **BART-Large-CNN**, I explored various **open-source AI models**:  

1. **DeepSeek R1** – Too large and overqualified for the summarization task.  
2. **Mistral & Phi-2** – Powerful models but **resource-intensive and impractical** for lightweight summarization.  
3. **Ollama & Falcon** – Required additional **credentials and setup overhead**, making them less suitable.  

After testing, **BART-Large-CNN** was chosen for its **efficiency, lightweight processing, and high-quality summaries**. It was also well-suited to our content, allowing us to explore key concepts like **chunking and sliding window processing** for handling large text inputs effectively.


## **Performance Analysis**

| **Metric**                                                                                                                                          | **Value**                                                                              |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Scrapping and providing summary for each article with TTS (Hindi)                                                                                   | **30-50 sec/article** (Needs optimization)<br><sub>30-40 sec/article with Gemini</sub> |
| **Overview**<br><sub>Key Insights, Trends, Sentiment analysis, and Keywords</sub>                                                                   | *1-2 minutes**                                                                         |
| **Comparative Sentiment Analysis**<br><sub>Overall Sentiment Distribution, Key Positive Themes, Key Negative Themes, and Comparative Insights</sub> | **1-2 minutes**                                                                        |


## **Setup & Installation**  

Follow these steps to set up and run the project:  
### 0. Prerequisites
- Ensure **Python 3.12** (or later) is installed on your system.  

### 1. Clone the Repository

```sh
git clone https://github.com/Harsha0431/News-Scraper-Summarizer-Text-to-Speech.git
cd News-Scraper-Summarizer-Text-to-Speech
```

### 2. Navigate to the Server Directory

```sh
cd server
```

### 3. Create a `.env` File
Inside the `server` folder, create a `.env` file and add the following values:

```
GEMINI_AI_API_KEY = <YOUR-API-KEY>  # Required  

PERIODIC_CLEAN_TIME_SECS = <NUMBER>  # Periodic timer for thread restart (default: 7200)  

FLASK_PORT = <PORT>  # Port for Flask (default: 5000 or 7860 for Hugging Face API) 
```

### 4. Set Up a Virtual Environment

```sh
python -m venv venv
source venv/bin/activate   # On macOS/Linux  
venv\Scripts\activate      # On Windows  
```

### 5. Install Dependencies

```sh
pip install -r requirements.txt
```

### 6. Running the Project

#### Option 1: Run the Gradio UI

```sh
python app.py
```
This launches the **Gradio-powered interactive UI**.
#### Option 2: Run the Flask API

```sh
python api.py
```
This starts the **Flask backend API**.

>**_NOTE:_** Extracting and summarizing data **may take up to 1 minute per article**, depending on content length and API response time.


## **Future Enhancements**

### 1. Expanding News Sources
- We can enhance web scraping by leveraging **Google News search queries** to fetch more relevant news articles:

  >`https://www.google.com/search?q=company:"{company_name}"+news&tbm=nws&start={skip_value}`
   
- This allows us to **dynamically fetch articles** related to a specific company or topic.  

### 2. Improving Summarization & Insights
- Explore **faster and optimized NLP models** that can **summarize content more efficiently** without compromising quality.  
- Implement **real-time streaming summarization**, breaking down long articles into smaller sections for faster processing.  

### 3. Additional AI Features
- Implement **multi-document summarization** to compare different sources and provide a **more comprehensive summary**.  
- Incorporate **fact-checking mechanisms** to assess the credibility of extracted articles.  
- Add **topic classification** to categorize news articles based on relevance.  

### 4. Enhancing API & UI
- Improve the **Flask API response time** by caching summaries for frequently requested articles.  
- Expand **Gradio UI functionalities**, allowing users to interactively select articles and customize summary length.  


## **Need Help?**

I’d love to hear your suggestions and feedback! Your insights can help improve the project and make it more efficient.  

### **Here are some areas where I need guidance:**  

1. **Scraping More High-Quality Articles**  
   - What are the best strategies to extract **relevant, high-quality news articles** while avoiding irrelevant or duplicate content?  
   - Any recommendations for improving web scraping efficiency?  

2. **Speeding Up Summarization Models**  
   - Currently, using **BERT-based models**, summarization takes **30-50 seconds per article**.  
   - Are there any optimizations or alternative models that could **process summaries faster** without losing quality?  

3. **Running Larger Hugging Face Models on Limited Hardware**  
   - I have a **16GB RAM system** with an **NVIDIA GeForce GTX 1650** GPU.  
   - What are the best ways to **optimize inference speed** and **reduce memory usage** when running large NLP models?  

4. **Other Performance Enhancements**  
   - Are there any **parallel processing techniques** (like multiprocessing or async calls) that could **speed up API response time**?  
   - Any lightweight alternative models or **efficient fine-tuning approaches**?  

---

💡 **I’m eager to learn and improve!** If you have any suggestions or insights, I’d love to hear them. Your feedback will not only enhance this project but also help me grow along the way! 🚀

📬 **Let's Connect!**

💼 [LinkedIn](https://www.linkedin.com/in/harshapolamarasetty/)  
🌐 [Portfolio](https://meetharsha.netlify.app/)
📧 Email: harshapolamarasetty6174@gmail.com
