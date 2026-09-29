# pip install gradio
import gradio as gr
from summarizer import summarize

gr.Interface(
    fn=summarize,                                  # your function
    inputs=gr.Textbox(label="Website URL"),
    outputs=gr.Markdown(label="Summary"),
    title="🔎 AI Website Summarizer",
).launch(share=True)   # share=True → a public link you can post! 🎉