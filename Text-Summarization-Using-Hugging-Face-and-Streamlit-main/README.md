# Text Summarizer App

This is a simple Streamlit web application that utilizes the Hugging Face Transformers library to perform text summarization using the BART (Bidirectional and Auto-Regressive Transformers) model.

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/mzaid295/Text-Summarization-Using-Hugging-Face-and-Streamlit.git
   
2. Install the required dependencies:
   
    ```bash
   pip install -r requirements.txt

3. Run the Streamlit app:
   
   ```bash
   streamlit run app.py


# Dependencies
**Streamlit:** The app framework for building interactive web applications.

**Transformers:** Hugging Face's library for working with state-of-the-art models in Natural Language Processing.

# How it Works
The app allows users to input an article in the provided text area. Upon clicking the "Generate Summary" button, the app divides the input article into chunks, processes each chunk independently for summarization, and then combines the individual summaries into a final summary. The summarization is performed using the Facebook BART-Large-CNN model.


## Text Summarizer App

![Text Summarizer App](https://github.com/mzaid295/Text-Summarization-Using-Hugging-Face-and-Streamlit/blob/f001581b3820e1afdcbec8ff831ec782cf8b87f2/Final%20Output.JPG)
