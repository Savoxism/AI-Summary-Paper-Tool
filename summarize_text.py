import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Configuration for the generative model
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 35,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the generative model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

# Prompt template for summarization
prompt = """
You are an experienced researcher who has been asked to summarize a research paper. The paper is about a certain topic, and you need to provide a summary of the key information. You must also cite some sentences if possible. The summary should be at least 500 words and at most 1000 words. The summary must contain the most necessary information and not any other irrelevant details. You must answer these questions:
1.Research Problem:
- What is the main objective of the study?
- What problem or question is the article trying to solve?
2.Hypothesis/Research Questions:
- What are the main hypotheses or research questions that the article poses?
3.Research Methods:
- What is the approach that the author used to solve the problem?
- What specific tools, data, and procedures were applied in the study?
4.Results:
- What are the important results obtained by the study?
- What specific data or information demonstrate those results?
5.Discussion & Analysis:
- What do the results mean in a broader context?
- What important conclusions does the author draw or provide?
6.Conclusion & Recommendations:
- What are the main conclusions of the paper?
- What are the recommendations for future research or practical applications?
7.Limitations:
- What are the limitations or unresolved issues in the study?
##Paper##
"""

def summarize_text(paper_text, title):
    try:
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message([prompt, paper_text])
        return response.text
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return f"Error during summarization: {str(e)}"