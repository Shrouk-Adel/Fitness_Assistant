from langchain.prompts import ChatPromptTemplate
from operator import itemgetter 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableParallel
import Indexing
import os
from dotenv import load_dotenv
load_dotenv() 


retriver =Indexing.retriever()
GOOGLE_API_KEY =os.getenv('Gemini_key')

def model():
    llm =ChatGoogleGenerativeAI(
        model ='models/gemini-2.0-flash-lite',
        temperature=0.4,
        google_api_key=GOOGLE_API_KEY 
    )
    return llm

def prompt_fun():
    prompt_template ='\n'.join([
        "you are a fitness instructor",
        "answer the question based on the given context about exercises",
        "use only the facts from the context,when answering the question",
        "reply with a structured way"
        "Question:{question}",
        "context:{context}"
    ])

    prompt =ChatPromptTemplate.from_template(prompt_template)

    return prompt

def rag(query):
    """
    Process a question through the RAG pipeline and return the answer.
    """
    try:
        if not query:
            return "Error: No question provided"

        # Define the input processing step
        inputs = RunnableParallel(
            question=itemgetter('question'),
            context=lambda x: retriver.invoke(x['question'])
        )

        # Define the RAG chain
        fitness_chain = (
            inputs
            | prompt_fun()
            | model()
        )

        response = fitness_chain.invoke({"question": query}).content
        return response
    except Exception as e:
        return f"Error processing question: {str(e)}"