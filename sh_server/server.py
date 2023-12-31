from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)

from firebase import firebase
fb = firebase.FirebaseApplication('https://dynamo-1697a-default-rtdb.firebaseio.com/', None)

from utils.evaluation import get_groups, get_questions, evaluate_test
from utils.teach import get_vids, get_qna
CORS(app,resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def hello_world():
    return 'Hello world!'

username = "Benson"

@app.route('/topic', methods =["GET","POST"])
def get_topic():
    # get the topic from the user
    # use this topic to generate the set of questions  
    try:
        data =  request.get_json()

        # print("avi")
        sub = get_groups(data['topic'])
        try:
            fb.post(username + "/" + data['topic'], {f'week_{x}': {"topics": p , "learnt": False} for x, p in enumerate(sub)})
            print("data recieved from client",data)
            return jsonify({"message":"topic recieved"})
        except Exception as e:
            return jsonify({'error':str(e)}),400
    except Exception as e:
        return jsonify({'error':str(e)}), 400

# get the set of questions
@app.route('/questions', methods=["GET"])
def send_questions():
    # send the questions to client
    data = fb.get(username, '')
    
    topic = list(data.keys())[0]
    hash = list(data[topic].keys())[0]
    weeks = data[topic][hash]
    subtopics = [data[topic][hash][week]['topics'] for week in weeks]
    
    print(subtopics)
    questions = get_questions(subtopics, x=1)
    flatten = lambda x: [item for sublist in x for item in sublist]

    return flatten(questions["questions"])

# sending the answer back
@app.route('/answers', methods=["GET","POST"])
def get_answers():
    # get the answers and do the evals
    # try:
        data =  request.get_json()
        print("data recieved from client",data)
        qa_pairs = data['qa_pairs']
        answers = data['answers']
        ans = evaluate_test(qa_pairs=qa_pairs, answer_truth=answers)
        print(ans)

        
        data = fb.get(username, '')
        topic = list(data.keys())[0]
        hash = list(data[topic].keys())[0]
        weeks = data[topic][hash]
        week_data = [data[topic][hash][week] for week in weeks]
        subtopics = [data[topic][hash][week]['topics'] for week in weeks]

        path ="/" + topic + "/" + hash + "/"

        res = [bool(ans[i] and ans[i + 1] and ans[i + 2]) for i in range(0, len(ans) - 2, 3)]

        for r, week in zip(res, weeks):
            fb.put(username, path + week + "/learnt", r)

        # Return ans
        return jsonify({"message":"topic recieved"})

    # except Exception as e:
    #     return jsonify({'error':str(e)}), 400
    

# eval report
@app.route("/report", methods=['GET'])
def send_report():
    # send the generated report back to client
    
    data = fb.get(username, '')
    topic = list(data.keys())[0]
    hash = list(data[topic].keys())[0]
    weeks = data[topic][hash]
    subtopics = [data[topic][hash][week]['topics'] for week in weeks if not data[topic][hash][week]['learnt']]
    print(subtopics)
    print(topic)
    print(weeks)
    return jsonify({'topics':subtopics}), 200

@app.route("/videos", methods=["GET"])
def send_videos():
    data = fb.get(username, '')
    topic = list(data.keys())[0]
    hash = list(data[topic].keys())[0]
    weeks = data[topic][hash]
    subtopics = [data[topic][hash][week]['topics'] for week in weeks if not data[topic][hash][week]['learnt']]
    print(subtopics[0])
    if type(subtopics[0]) == dict:
        subtopics = list(subtopics[0].values())
    vids = get_vids(subtopics[0])
    print(vids)
    response = jsonify(
        [{"id": x["id"], "link": x["link"], "title": x["title"]} for x in vids]
        )
    return response

@app.route("/practiceqa", methods=["GET","POST"])
def send_qa():
    data = fb.get(username, '')
    
    topic = list(data.keys())[0]
    hash = list(data[topic].keys())[0]
    weeks = data[topic][hash]
    print(weeks)
    print(data[topic][hash])
    subtopics = [data[topic][hash][week]['topics'] for week in weeks if not data[topic][hash][week]['learnt']]
    
    print(subtopics)
    questions = get_questions([subtopics[0]], x=10)
    return jsonify({
        'questions': questions
    })