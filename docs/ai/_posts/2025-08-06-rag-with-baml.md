---
layout: post
title:  "Retrieval Augmented Generation (RAG) with BAML and PostgreSQL"
---

Leverage the increased reliability and lower maintenance of BAML in a solution that takes advantage of PostgreSQL's add-on capabilities for RAG solutions!

The full source code for this solution is at [https://github.com/hoopdad/rag_in_python_postgresql/](https://github.com/hoopdad/rag_in_python_postgresql/)

## Why RAG

RAG is a solution that allows for faster, smaller interactions with a Large Language Model (LLM). It takes advantage of re-use strategies and vector math. By letting your AI service define for you where in it's multi-dimensional sphere of data that your question fits, you can find the closest data that answers that question.

If you run many prompts against the same source, it's worth converting your data to vectors, a process called embedding, and saving them to a database for retrieval later. If you are going to ask more than 1 question about a certain document, this is probably going to reduce your cost. By focusing the prompts on a subset of focused data, you are sending less data to your AI service and asking it to do less work, translating to fewer tokens of data exchanged and lower cost. It also means a lot less processing time for the AI service.

The scenario used in this proof of concept is asking an LLM to determine a failure cause for a workflow log file. This is the output from a series of steps. It is a mix of random bits of information about the process, results from steps within that process, and a collection of warnings and possibly errors. While it will have a single pass/fail decision at the end, more resolution on the reasons behind it, but not too much narrative, will help a team understand failures and prioritize fixes.

Note: lengthy log files often need to be consumed as a single document to get the full context. This scenario seems to work because it asks AI about any failures found; sections with anything like a failure are sent to the LLM without needing to know the entire sequential flow.

## Why BAML

Previous posts in this blog about BAML covered some of the benefits of BAML, summarized here.

- A Domain Specific Language (DSL) for writing and executing prompts
- Guaranteed structured input and output for scaling agentic models and many contributors
- Separation of Prompts from the framework code that runs them
- Resiliency with built-in features like retry policies
- Ability to communicate with API's from many AI vendors, running in the cloud, on-premises, or locally

This is a key piece of a framework that allows scaling up and reusing prompts. Using the DSL lets a person focus on the Prmopt itself, separating system programming with prompt development.

## Layers of this Solution

### Database

For proof of concept purposes, I installed PostgreSQL and configured pgvector in a Docker image. See [docker-compose.yml](https://github.com/hoopdad/rag_in_python_postgresql/blob/main/docker-compose.yml) and [run-db.sh](https://github.com/hoopdad/rag_in_python_postgresql/blob/main/run-db.sh)

pgvector is our plug-in library for PostgreSQL that enables vector math, specifically cosine similarity. This is that math that tells how close two vectors are; closer vectors in LLM's mean relevant data in RL. It comes with some task-specific language constructs such as "<=>" which you might not see elsewhere in PostgreSQL.

See the queries in [embeddings_persistence_postgres.py](https://github.com/hoopdad/rag_in_python_postgresql/blob/main/embeddings_persistence_postgres.py)

### Database Layer

The file [embeddings_persistence_postgres.py](https://github.com/hoopdad/rag_in_python_postgresql/blob/main/embeddings_persistence_postgres.py) wraps our communications with our database. It includes functions as follows.

- _ensure_table is called internally and sets up our database.
- save_embeddings saves the chunks of our log file to the database. Those chunks are determined by our python code. We don't save the whole log file as one chunk because that would defeat the efficiency gains.
- embeddings_exist checks if we already saved embeddings for this file. This is how we gain efficiencies in re-running prompts against the same log file.
- cosine_similarity sends a database query that uses our vectorized question to find the most relevant log chunks.
- load_embeddings will retrieve the vectors, in cases where one might want to do the cosine similarity math on their python client. It is not used in this POC.

### Prompt Layer

This is BAML. You can see how it's used in the `query_logs` function in [embed_on_postgres.py](https://github.com/hoopdad/rag_in_python_postgresql/blob/main/embed_on_postgres.py). We don't have to write a lot of code for this!

#### Calling the Client

All we need to do to call the BAML client is to set up a dictionary and then pass that into our generated function. This is in `query_logs` in [embed_on_postgres.py](https://github.com/hoopdad/rag_in_python_postgresql/blob/main/embed_on_postgres.py)

```py
    prompt_input: WorkflowAnalysisDetails = WorkflowAnalysisDetails(
        logs=chunks, question=question
    )
    response: workflow_completion_status = (
        workflow_completion_client.DetermineWorkflowCompletionStatus(input=prompt_input)
    )
```

#### Defining the prompt

Check out [workflow_completion.baml](https://github.com/hoopdad/rag_in_python_postgresql/blob/main/baml_src/workflow_completion.baml) to see how we define our prompt.

Then see how we define the connection to our AI Service in [clients.baml](https://github.com/hoopdad/rag_in_python_postgresql/blob/main/baml_src/clients.baml). Note the use of an Azure Open AI service, my Open AI instance that is hosted on Azure, along with the retry policy. Retry is so important in cloud design that it is built into the BAML framework.

Once we edit the baml files, we run `baml-cli generate` to generate our python code.

#### Putting it all together

These are the steps that we handled in this proof of concept. 

- Create our database instance, running in our local Docker
- Create our table if it doesn't exist
- Check for our log file in our RAG database
- If it's not already there, break it into chunks, vectorize ("embed") each chunk, and save all of that to the database
- Embed our question
- Ask the database to give us the log chunks most relevant to the question
- Send the question and log chunks through BAML to the LLM
- Output our response

## Conclusion

This proof of concept was successful for a number of key goals.

It proved that PostgreSQL has a competent engine for doing advanced AI work, RAG. This is a versatile, low-cost database that can be run in any cloud, in a data center, or on your laptop.

It proved that BAML can remain not just a player in the single prompt, in the multi-prompt chaining, and agentic models, but also in RAG. It features a for loop that makes including lists of document chunks, for one, but we covered many other benefits as well.

It also proved that RAG can be implemented quickly without too many moving parts.

There are certainly opportunities to improve on the scalability and resiliency of this RAG platform. For example, document and model versions and dates could be included as metadata that would enhance the relevance of pre-saved embeddings. Line numbers for document chunks could be included for easier reference. And actually it should be developed as a service that can run on a server somewhere, not under my desk. Most importantly, however, this is a great foundation to iterate on.
