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

## Technologies

- Python 3.12
- Langchain
- chromadb
- ollama
- Flask as the API interface (see [Background](#background) for more information on Flask)
- Gemini as an LLM

## Preparation

Since we use Gemini, you need to provide the API key:

 ```
 api_key =os.getenv('gemini_api_key')
 ```

For dependency management, so you need to install it:

```bash
pip install -r req.txt
```

 
### Interface

We use Flask for serving the application as an API.


### Indexing

The Indexing script is in [`Indexing.py`](fitness_assistant/Indexing.py).

### Rag Flow
The rag_flow script is in [`rag)flow.py`](fitness_assistant/rag_flow.py).

## Experiments

For experiments, we use Jupyter notebooks.
They are in the [`notebooks`](notebooks/) folder

We have the following notebooks:

- [`rag.ipynb`](notebooks/rag-test.ipynb): The RAG flow and evaluating the system.
- [`evaluation-data-generation.ipynb`](notebooks/evaluation-data-generation.ipynb): Generating the ground truth dataset for retrieval evaluation.

 ### RAG flow evaluation

We used the LLM-as-a-Judge metric to evaluate the quality
of our RAG flow.

-we used Gemini 1.5 flash


### Mdels
- Embedding ```plutonioumguy/bge-m3```
- text generation ```models/gemini-2.0-flash-lite```
- LLM as a Judge ```models/gemini-1.5-flash```

### Flask

We use Flask for creating the API interface for our application.
It's a web application framework for Python: we can easily
create an endpoint for asking questions and use web clients
(like `curl` or `requests`) for communicating with it.

In our case, we can send questions to `http://localhost:5000/question`.

For more information, visit the [official Flask documentation](https://flask.palletsprojects.com/).



 
