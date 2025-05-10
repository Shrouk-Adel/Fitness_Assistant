from langchain.prompts import ChatPromptTemplate
from operator import itemgetter 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableParallel
from langchain_groq import ChatGroq
import Indexing
import time 
from json_repair import repair_json
import json
import os
from dotenv import load_dotenv
load_dotenv() 

#________Define Api key_________
GEMINI_API_KEY =os.getenv('GEMINI_API_KEY')
GROQ_API_KEY= os.getenv('GROQ_API_KEY')

#________Retreiver_______-
retriver =Indexing.retriever()
# _________llm as a Judge_______
gemini_llm =ChatGoogleGenerativeAI(
    model ='models/gemini-2.0-flash',
    temperature=0.2,
    google_api_key=GEMINI_API_KEY 
)
# _______Rag llm_______
lama_llm =ChatGroq(
model ='llama3-8b-8192',
temperature=0.3,
groq_api_key =GROQ_API_KEY
)
# ______________Rag without evaluation_________
# prompts
prompt_template ='\n'.join([
    "you are a fitness instructor",
    "answer the question based on the given context about exercises",
    "use only the facts from the context,when answering the question",
    "reply with a structured way"
    "Question:{question}",
    "context:{context}"
])

prompt =ChatPromptTemplate.from_template(prompt_template)

def rag_without_eval(question):
    """
    Process a question through the RAG pipeline and return the answer.
    """
    try:
        if not question:
            return "Error: No question provided"

        # Define the input processing step
        inputs = RunnableParallel(
            question=itemgetter('question'),
            context=lambda x: retriver.invoke(x['question'])
        )

        # Define the RAG chain
        fitness_chain = (
            inputs
            | prompt
            | lama_llm
        )

        answer = fitness_chain.invoke({"question": question}).content

        return answer
    except Exception as e:
        return f"Error processing question: {str(e)}"


#____________evaluation___________

Judge_template = """
You are an expert evaluator for a RAG system.
Your task is to analyze the relevance of the generated answer to the given question.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

Question: {question}
Generated Answer: {answer_llm}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
"Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
"Explanation": "[Provide a brief explanation for your evaluation]"
}}
""".strip()

Judge_prompt =ChatPromptTemplate.from_template(Judge_template)


# ___________evaluation function_______
def evaluation_respons(question ,answer):
    Judge_chain=(
    Judge_prompt
    |gemini_llm
    )
    response =Judge_chain.invoke({
                'question':question,
                'answer_llm':answer
                }).content
    time.sleep(2)
    res_str =repair_json(response)
    evaluation = json.loads(res_str)

    return evaluation

# _________Rag with evalutaion of answer_________
def rag(question):
    answer =rag_without_eval(question)
    evaluation =evaluation_respons(question,answer)

    answer_data={
       "answer":answer,
       'relevance':evaluation.get('Relevance','unknown'),
       'relevance_explanation':evaluation.get('Explanation','no valiable explanation')
    }

    return answer_data
 