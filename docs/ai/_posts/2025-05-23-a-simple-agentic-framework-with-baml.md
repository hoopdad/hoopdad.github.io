---
layout: post
title:  "A Simple Agentic Framework with BAML"
---

This article gives practical, simplified definitions of AI Agents, Agentic Models, and an example of an application that might be useful for DevOps issues.

## AI Agents

AI Agents and Agentic models are popular topics in the current maturing of AI. Large Language Models (LLMs) like ChatGPT have enormous capabilities to understand and analyze, which you know from interacting with ChatGPT. Think of agents as code libraries with pre-defined jobs, and some awareness of their context.

As an example of an AI Agent that is about improving conversations, imagine a Python program that flows like this.

- Using the conversation transcript, determine the tone of a conversation.
- Using the conversation transcript, fact consistency analyzer to determine if each person was consistent throughout the conversation.
- Using the conversation transcript, communication style profiler to determine if the person is speaking directly, with empathy, and with clear goals.
- Using outputs from the prior steps, suggest how the person can improve their communication skills.

We have to break this down into multiple steps for two reasons.

- The amount of data or processing can be too much for the LLM to process at once.
- We can refine the overall process as time goes on, and these discrete steps enable iterating in an Agile fashion.

To go a little deeper into our example, the "tone" component of the agent might flow like this.

- Input is a conversation transcript.
- The program sends that conversation with a prompt like, "Identify the tone of each of the conversation participants".
- The LLM returns a set of adjectives like "happy, friendly" for person 1 and "silly" for person 2. 

Practically speaking, this Python program becomes an agent when this chaining of steps brings value and some decision support. (Decision making and taking action is the next level! But hard to do in this example because we can't make the person take the recommendations.)

To make this an Agentic Model, you write a program that takes a single, common input and chains the 4 components together. The final request is a a consolidated view of the 3 different perspectives provided by the first AI outputs. Depending on how complex the components are you, you might introduce a Planning component that decides which components to string together.

## Components of a Simplified Agentic Model using BAML

All of these connected together comprise an Agent.

- An LLM model and related credentials.
- Functions defined using BAML and using the BAML code generator to create Python code.
- An orchestrator written in Python to chain the BAML events together as your custom solution needs, using standard Python language constructs.
- An interface to handle gathering inputs and sending outputs.

### Simple rules to make this easier

With planning up front, you would want to make this Agentic Model easy to use and re-use.

- Simplified inputs - consolidate inputs as much as possible, so that values aren't repeated in the call to your model.
- Simplified processing - standardize on structured content responses from the LLM so the orchestration easily allows combining results or passing results from one agent into the next.
- Standardized output - a structure output, as opposed to a variable length narrative makes your program directly usable without further processing.

A tool called BAML makes this come together, along with some native Python structures.

## AI Functions

Define a function in BAML. We define the data structure and a function containing the prompt, in a language that is similar to JavaScript with Jinja. Here's what that code looks like.

```javascript
class GHLogProblems {
  problem_summary string? @description(#"
    1. Identify repeated errors or warnings.
    2. Group by error message or failure point.
    4. Output top 3-5 most critical issues.
  "#)
}
function GetLogProblems(log_output: string) -> GHLogProblems {
  client "CustomGPT4o"
  prompt #"
    You are a log analysis agent. You are given logs from a GitHub Action pipeline run.

    1. Identify repeated errors or warnings.
    2. Group by error message or failure point.
    3. Suggest probable root causes or code areas to inspect.
    4. Output top 3-5 most critical issues.

    Log Excerpt:
    [START_LOG]
    Log Output: {{ log_output }}
    [END_LOG]
    {{ ctx.output_format }}
  "#
}
```

Define a configuration that defines how to connect to your LLM.

```javascript
client<llm> CustomGPT4o {
  provider openai
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
```

The final steps with BAML are to run `BAML-cli generate` and then reference the generated files from your main program.

## Orchestrating the Agents

Let's say you write the above agent and then several more to flesh out the many perspectives of DevOps workflow tuning. So, next you need code to run agents in series. Assume we have the above `GetLogRecommendation`as well as a similar `GetWorkflowProblems` that takes the workflow as input, and `GetDevOpsRecommendation` which takes the output from the first two as its input.

Our inputs:

- log: the contents of a log file from one run of a workflow, as a string
- workflow: the code for our DevOps pipeline, as a string

```python
import json
from BAML_client import b

def coordinate( log:str, workflow:str)->str:
    # get the summary of problems reported in the logs from the log recommendation AI function
    log_problem_JSON = b.GetLogProblems(log)
    log_problem_summary = log_problem_JSON.problem_summary if log_problem_JSON.problem_summary else None

    # get the summary of problems with the code in our workflow
    workflow_problem_JSON = b.GetWorkflowProblems(workflow)
    workflow_problem_summary = workflow_problem_summary.summary if workflow_problem_summary.summary else None

    # create the part of the prompt with the information from both problem summaries
    log_problems = "START LOG PROBLEM SUMMARY\n"
    log_problems += log_problem_summary
    log_problems += "END LOG PROBLEM SUMMARY\n"

    workflow_problems = "START WORKFLOW PROBLEM SUMMARY\n"
    workflow_problems += workflow_problem_summary
    workflow_problems += "END WORKFLOW PROBLEM SUMMARY\n"

    # Use the problem summaries together to call our AI function for DevOps. This returns a summary and recommendation.
    workflow_recommendation_JSON = b.GetWorkflowRecommendation(
      log_problem+workflow_problems
    )

    # build a response that we control
    response = json.dumps(workflow_recommendation_JSON, indent=2)

    return response

```

This output could be sent to a UI or output to a command-line, or it might feed into a bigger process.

## Interface to this Agentic Model

We can put a simple Flask service around this Agentic Model to make it accessible from your web user interface or a command-line tool that you would build.

```python
from flask import Flask,  Response
app = Flask(__name__)
@app.route("/workflow_analysis", methods=["GET"])
def workflow_analysis():
    # assumes reading info from a properly secured storage service
    log = read_file_as_string(request.args.get("log_file_name"))
    workflow = read_file_as_string(request.args.get("workflow_file_name"))
    response = coordinate(log,workflow)
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

## Conclusion

With a very small amount of code, the BAML library and standard Python constructs, along with our Open AI account, we can create an Agentic Model.

Some benefits of this simplified framework include:

- Prompts can be defined and refined easily.
- Agents can be changed independently. By separating out the BAML outputs into different files or reusable libraries, they can be developed and tested independently.
- Structured output from BAML allows for codified flows with predictable output structures.
- Additional agents can be added to enhance the results.

More abstraction can provide abilities to manage different versions of agents, different ways of calling agents, and different methods for aggregating outputs.

This is a great starting point that can be iterated on to make as powerful as you need.
