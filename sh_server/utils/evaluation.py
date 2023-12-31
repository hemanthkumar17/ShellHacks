from typing import List
import openai
from openai import ChatCompletion
from .api_keys import OPENAPI_KEY

# import torch
import json
# from sentence_transformers import util
import numpy as np

openai.api_key = OPENAPI_KEY
def get_questions(subtopics: List[List], x=3):
    questions = {"questions": []}
    for topic in subtopics:
        prompt = """
        Follow my instructions precisely. Everytime you receive an input list in the format:
        [
        "Introduction to Programming",
        "Programming languages and paradigms",
        "Setting up the development environment",
        ]
        Write """ + str(x) + """ questions to test the understanding of a student who has learned these. Give the output in the format:
        {"questions":
        [
            {"question": "What is programming?", "answer": "Programming is the process of writing instructions for a computer to execute."},
            {"question": "What are programming languages?", "answer": "Programming languages are formal languages used to communicate instructions to a computer."},
            {"question": "Why is setting up the development environment important?", "answer": "Setting up the development environment ensures that all necessary software and tools are installed and configured for programming."}
        ]
        }
        """
        while True:
            try:
                results = ChatCompletion.create(model="gpt-3.5-turbo", messages=[
                    {"role": "user", "content": prompt},
                    {"role": "user", "content": str(topic)}
                ])
                questions["questions"].append(json.loads(results["choices"][0]["message"]["content"])["questions"])
            except:
                continue
            else:
                break

    return questions

def compare(question, answer, answer_truth):
    res = []
    for q, a, at in zip(question, answer, answer_truth):
        print(q)
        print(a)
        print(at)
        qe = openai.Embedding.create(input = [q], model="text-embedding-ada-002")['data'][0]['embedding']
        ae = openai.Embedding.create(input = [a], model="text-embedding-ada-002")['data'][0]['embedding']
        ate = openai.Embedding.create(input = [at], model="text-embedding-ada-002")['data'][0]['embedding']
        cos_sim = lambda a, b: np.dot(a, b) / np.linalg.norm(a) / np.linalg.norm(b) 
        res.append((cos_sim(ae, qe) + cos_sim(ae, ate)).flatten() / 2)
        print(res)
    print(res)
    return [r >= 0.9 for r in res]

def evaluate_test(qa_pairs, answer_truth):
    """Evaluates a list(list(questions)) to give a list(list(answers)) and list(list(answer_truth))
    The first dimension defines the different subtopics (weeks in our case), and second dimension being the list of questions
    Args:
        qa_pairs ("questions": List({"question": "answer"})): Questions and answersthat ChatGPT generated
        answer_truth (List(List(String))): Answer Given by the user

    Returns:
        _type_: _description_
    """
    questions = [x["question"] for x in qa_pairs]
    answers = [x["answer"] for x in qa_pairs]
    res = []
    # print(questions)
    # print(answers)

    # for i, j, k in zip(questions, answers, answer_truth):
    #     res.append([compare(i, j, k)])
    res = compare(questions, answers, answer_truth)
    print(res)
    return res


def get_course_list_api(topic = "Programming"):
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", 
         "content": """Write a concise course plan about an introduction course to \"""" + topic + """}\" for students who are either starting to learn it or have covered a few topics in it. 
         Write a list of all subtopics that will be taught each week. Remove all the course recap, projects, assignments, and quizzes from the course. 
         Take a deep breath and think about this step by step. Now give me a list of sub-topics to include for teaching them. Give the answer in JSON format, {{week: topics}}"""}
    ]
    )
  return response

def get_groups(topic = "Programming"):
    
  groups=[]
  response=get_course_list_api(topic)
  response=response["choices"][0]["message"]["content"]
  response = response.replace("\\", "").replace("\n", "")
  response=json.loads(response)

  for i in response:
     groups.append(response[i])

  return groups