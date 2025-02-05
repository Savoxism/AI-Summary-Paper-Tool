import os
import google.generativeai as genai 
from dotenv import load_dotenv

load_dotenv()

# GOOGLE_API_KEY=AIzaSyCVQM4930V4nLP8h7TF2IG9QrKr7zhFHPw
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 35,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

prompt = """
Read the article carefully and summarize it with the following key information and return it in markdown format and in Vietnamese but keep the title in English:
1.Research Problem:
- What is the main objective of the study?
- What problem or question is the article trying to solve?

2.Hypothesis/Research Questions:
- What are the main hypotheses or research questions that the article poses?

3.Research Methods:
- What is the approach that the author used to solve the problem?
- What specific tools, data and procedures were applied in the study?

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

def summarize_text(paper_path, title, chat_history=None):
    try:
        # Upload the file to Google Generative AI
        paper_file = genai.upload_file(paper_path)
        
        # Start a chat session with the history
        chat_session = model.start_chat(history=chat_history or [])
        
        # Generate content using the prompt and uploaded file
        response = chat_session.send_message([prompt, paper_file])
        summary = response.text
        
        # Return the updated chat history and the summary
        return chat_session.history, summary
    except Exception as e:
        return [], f"Error during summarization: {str(e)}"