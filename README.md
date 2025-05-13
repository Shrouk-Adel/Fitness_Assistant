# Fitness_Assistant


 ![banner](https://github.com/user-attachments/assets/bba3c40f-3653-4c86-b136-1f93b0e580ab)


Staying consistent with fitness routines is challenging,
especially for beginners. Gyms can be intimidating, and personal
trainers aren't always available.

The Fitness Assistant provides a conversational AI that helps
users choose exercises and find alternatives, making fitness more
manageable.


## Project overview

The Fitness Assistant is a RAG application designed to assist
users with their fitness routines.

The main use cases include:

1. Exercise Selection: Recommending exercises based on the type
of activity, targeted muscle groups, or available equipment.
2. Exercise Replacement: Replacing an exercise with suitable
alternatives.
3. Exercise Instructions: Providing guidance on how to perform a
specific exercise.
4. Conversational Interaction: Making it easy to get information
without sifting through manuals or websites.

## Dataset

The dataset used in this project contains information about
various exercises, including:

- **Exercise Name:** The name of the exercise (e.g., Push-Ups, Squats).
- **Type of Activity:** The general category of the exercise (e.g., Strength, Mobility, Cardio).
- **Type of Equipment:** The equipment needed for the exercise (e.g., Bodyweight, Dumbbells, Kettlebell).
- **Body Part:** The part of the body primarily targeted by the exercise (e.g., Upper Body, Core, Lower Body).
- **Type:** The movement type (e.g., Push, Pull, Hold, Stretch).
- **Muscle Groups Activated:** The specific muscles engaged during
the exercise (e.g., Pectorals, Triceps, Quadriceps).
- **Instructions:** Step-by-step guidance on how to perform the
exercise correctly.

The dataset was generated using ChatGPT and contains 207 records. It serves as the foundation for the Fitness Assistant's exercise recommendations and instructional support.

## System Architecture
The Fitness Assistant uses a RAG-based architecture that combines retrieval mechanisms with generative AI to provide accurate,
contextually relevant responses to user queries about fitness and exercises.

 ![Screenshot 2025-05-13 141030](https://github.com/user-attachments/assets/75a25932-4542-47aa-aaea-ba1da7757a81)

## Key Components
The Fitness Assistant consists of several interconnected components:

Component	Description	Implementation
- Flask API	Web interface for user interactions	```app.py```
- RAG Flow	Core logic for retrieving and generating responses	```fitness_assistant/rag_flow.py```
- Indexing System	Processes exercise data and creates searchable vector representations	```fitness_assistant/Indexing.py```
- Vector Store	Stores embeddings for semantic search (ChromaDB)	Managed by ```Indexing.py``` 
- LLM Services	External AI models for text generation	Groq Llama3:8b
- Evaluation System	Validates response quality (LLM-as-Judge)	```models/gemini-2.0-flash```
- Database	Stores conversation history and user feedback	```PostgreSQL```

## Technologies

- Python 3.12
- Docker and Docker Compose for containerization
- langchain
- chromadb
- Flask as the API interface (see [Background](#background) for more information on Flask)
- postgres
- Gemini as an LLM for Jude
- Groq lama3:8b as LLM for text generation

## Preparation

Since we use Gemini and Groq, you need to provide the API key:

```API Keys:
Google Gemini API key (required for evaluation)
Groq API key (used for LLM integration)
```
you need to install system requirments

```pip install req.txt```

## Running the application


### Database configuration

Before the application starts for the first time, the database
needs to be initialized.

First, run `postgres`:

```bash
docker-compose up postgres
```

Then run the [`db_prep.py`](fitness_assistant/db_prep.py) script:

```bash
cd fitness_assistant

export POSTGRES_HOST=localhost
python db_prep.py
```


### Running with Docker-Compose

The easiest way to run the application is with `docker-compose`:

```bash
docker-compose up
```

### Running locally

If you want to run the application locally,
start only postgres :

```bash
docker-compose up postgres 
```

If you previously started all applications with
`docker-compose up`, you need to stop the `app`:

```bash
docker-compose stop app
```

Now run the app on your host machine:

```bash
cd fitness_assistant

export POSTGRES_HOST=localhost
python app.py
```

### Running with Docker (without compose)

Sometimes you might want to run the application in
Docker without Docker Compose, e.g., for debugging purposes.

First, prepare the environment by running Docker Compose
as in the previous section.

Next, build the image:

```bash
docker build -t fitness-assistant .
```

And run it:

```bash
docker run -it --rm \
    --network="fitness-assistant_default" \
    --env-file=".env" \
    -e OPENAI_API_KEY=${OPENAI_API_KEY} \
    -e DATA_PATH="data/data.csv" \
    -p 5000:5000 \
    fitness-assistant
```


## Using the application

When the application is running, we can start using it.

### Using `requests`

When the application is running, you can use
[requests](https://requests.readthedocs.io/en/latest/)
to send questions—use [test.py](test.py) for testing it:

```bash
python test.py
```

It will pick a random question from the ground truth dataset
and send it to the app.

### CURL

You can also use `curl` for interacting with the API:

```bash
URL=http://localhost:5000
QUESTION="Is the Lat Pulldown considered a strength training activity, and if so, why?"
DATA='{
    "question": "'${QUESTION}'"
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${DATA}" \
    ${URL}/question
```

You will see something like the following in the response:

```json
{
    "answer": "Yes, the Lat Pulldown is considered a strength training activity. This classification is due to it targeting specific muscle groups, specifically the Latissimus Dorsi and Biceps, which are essential for building upper body strength. The exercise utilizes a machine, allowing for controlled resistance during the pulling action, which is a hallmark of strength training.",
    "conversation_id": "4e1cef04-bfd9-4a2c-9cdd-2771d8f70e4d",
    "question": "Is the Lat Pulldown considered a strength training activity, and if so, why?"
}
```

Sending feedback:

```bash
ID="4e1cef04-bfd9-4a2c-9cdd-2771d8f70e4d"
URL=http://localhost:5000
FEEDBACK_DATA='{
    "conversation_id": "'${ID}'",
    "feedback": 1
}'

curl -X POST \
    -H "Content-Type: application/json" \
    -d "${FEEDBACK_DATA}" \
    ${URL}/feedback
```

After sending it, you'll receive the acknowledgement:

```json
{
    "message": "Feedback received for conversation 4e1cef04-bfd9-4a2c-9cdd-2771d8f70e4d: 1"
}
```

## Code

The code for the application is in the [`fitness_assistant`](fitness_assistant/) folder:

- [`app.py`](fitness_assistant/app.py) - the Flask API, the main entrypoint to the application
- [`rag_flow.py`](fitness_assistant/rag_flow.py) - the main RAG logic for building the retrieving the data and building the prompt
- [`ingest.py`](fitness_assistant/ingest.py) - loading the data into the knowledge base
- [`Indexing.py`](fitness_assistant/Indexing.py) - vectorstore database and retriever
- [`db.py`](fitness_assistant/db.py) - the logic for logging the requests and responses to postgres
- [`db_prep.py`](fitness_assistant/db_prep.py) - the script for initializing the database

We also have some code in the project root directory:

- [`test.py`](test.py) - select a random question for testing

### Interface

We use Flask for serving the application as an API.

Refer to the ["Using the Application" section](#using-the-application)
for examples on how to interact with the application.

### Indexing

The Indexing script is in [`Indexing.py`](fitness_assistant/Indexing.py).

It's executed inside [`rag_flow.py`](fitness_assistant/rag_flow.py)
when we import it.

## Experiments

For experiments, we use Jupyter notebooks.
They are in the [`notebooks`](notebooks/) folder.

To start Jupyter, run:

```bash
cd notebooks
python jupyter notebook
```

We have the following notebooks:

- [`rag.ipynb`](notebooks/rag.ipynb): The RAG flow and evaluating the system.
- [`evaluation-data-generation.ipynb`](notebooks/evaluation-data-generation.ipynb): Generating the ground truth dataset for retrieval evaluation.

### RAG flow evaluation

We used the LLM-as-a-Judge metric to evaluate the quality
of our RAG flow.

For `models/gemini-2.0-flash`, in a sample with 100 records, we had:

- 73  `RELEVANT`
- 25  `PARTLY_RELEVANT`
- 2  `NON_RELEVANT`


## Background

Here we provide background on some tech not used in the
course and links for further reading.

### Flask

We use Flask for creating the API interface for our application.
It's a web application framework for Python: we can easily
create an endpoint for asking questions and use web clients
(like `curl` or `requests`) for communicating with it.

In our case, we can send questions to `http://localhost:5000/question`.

For more information, visit the [official Flask documentation](https://flask.palletsprojects.com/).


## Acknowledgements 

I thank the course participants for all your energy
and positive feedback as well as the course sponsors for
making it possible to run this course for free. 

I hope you enjoyed doing the course =)


 



 
