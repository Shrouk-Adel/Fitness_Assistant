import os
from dotenv import load_dotenv
load_dotenv() 

from langchain_community.document_loaders import CSVLoader
# embedding 
from langchain.embeddings import OllamaEmbeddings
# vector db 
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from operator import itemgetter 
from langchain_google_genai import ChatGoogleGenerativeAI



GOOGLE_API_KEY =os.getenv('Gemini_key')


#load data
file_path =r"..\Data\data.csv"
loader =CSVLoader(file_path)
fit_docs =loader.load()
print(fit_docs[0].page_content)

embeddings =OllamaEmbeddings(model ='plutonioumguy/bge-m3')
# vectore_store =Chroma.from_documents(
#     embedding=embeddings,
#     persist_directory='./chromadb',
#     documents =fit_docs
# )

# # 3. Save the vector store
# vectore_store.persist()


# loading chromadb from disk later
vectore_store = Chroma(
    embedding_function=embeddings,
    persist_directory='./chromadb'
)

retriver =vectore_store.as_retriever(search_kwargs={'k':5})

# rag from documents
query = "Which muscles do push-ups work?"
response = retriver.get_relevant_documents(query)
response

llm =ChatGoogleGenerativeAI(
    model ='models/gemini-2.0-flash-lite',
    temperature=0.4,
    google_api_key=GOOGLE_API_KEY 
)

prompt_template ='\n'.join([
    "you are a fitness instructor",
    "answer the question based on the given context about exercises",
    "use only the facts from the context,when answering the question",
    "reply with a structured way"
    "Question:{question}",
    "context:{context}"
])

prompt =ChatPromptTemplate.from_template(prompt_template)

# rag chain 
fitness_chain= (
    {"question":itemgetter('question'),
     "context":lambda x:retriver.invoke(x['question'])}
    |prompt
    |llm
)


response = fitness_chain.invoke({"question": "Which exercise targets the core muscles?"})
print(response.content)  

# LLM As Jude --(Rag Evaluation)

import pandas as pd
df_question =pd.read_csv('../Data/ground-truth-retrieval.csv')
df_question.head()

ground_truth =df_question.to_dict(orient='records')
ground_truth[0]

llm_Judge=ChatGoogleGenerativeAI(
    model ='models/gemini-1.5-flash',
    temperature=0.2,
    google_api_key=GOOGLE_API_KEY 
)

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

Judge_chain=(
    Judge_prompt
    |llm_Judge
)

first_recored =ground_truth[0]
answer_llm =fitness_chain.invoke({'question':first_recored['question']})
# print(answer_llm)
response =Judge_chain.invoke({
                'question':first_recored['question'],
                'answer_llm':answer_llm.content
                })

print(response.content)

first_recored =ground_truth[0]
answer_llm =fitness_chain.invoke({'question':first_recored['question']})
# print(answer_llm)
response =Judge_chain.invoke({
                'question':first_recored['question'],
                'answer_llm':answer_llm.content
                })

print(response.content)

df_sample = df_question.sample(n=50, random_state=1)

sample = df_sample.to_dict(orient='records')

from tqdm.auto import tqdm
import json
import time 

evaluations = []
for record in tqdm(sample):
    question = record['question']
    answer_llm = answer_llm =fitness_chain.invoke({'question':question}).content

    response =Judge_chain.invoke({
                'question':question,
                'answer_llm':answer_llm
                }).content
    print(response)
    time.sleep(2)
    evaluation = json.loads(response)
    evaluations.append((record, answer_llm, evaluation))


df_eval =pd.DataFrame(evaluations,columns=['record','answer','evaluation'])

df_eval['id'] = df_eval.record.apply(lambda d: d['id'])
df_eval['question'] = df_eval.record.apply(lambda d: d['question'])

df_eval['relevance'] = df_eval.evaluation.apply(lambda d: d['Relevance'])
df_eval['explanation'] = df_eval.evaluation.apply(lambda d: d['Explanation'])

del df_eval['record']
del df_eval['evaluation']


# save data
df_eval.to_csv('../data/rag-eval', index=False)
