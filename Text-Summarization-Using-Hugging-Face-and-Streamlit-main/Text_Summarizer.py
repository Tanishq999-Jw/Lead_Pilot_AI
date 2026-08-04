import streamlit as st
from transformers import pipeline

# Load the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary(article):
    # Split the article into chunks (adjust chunk size as needed)
    chunk_size = 500
    chunks = [article[i:i + chunk_size] for i in range(0, len(article), chunk_size)]

    # Generate summary for each chunk
    summary_texts = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summary_texts.append(summary[0]['summary_text'])

    # Combine the summary texts from all chunks
    final_summary = " ".join(summary_texts)
    return final_summary

# Main Streamlit app
st.title("Text Summarizer App")

# Text input area for the article
article_input = st.text_area("Enter the article:")

# Button to generate and display the summary
if st.button("Generate Summary"):
    if article_input:
        summary_result = generate_summary(article_input)
        st.subheader("Summary:")
        st.write(summary_result)
    else:
        st.warning("Please enter an article to summarize.")
