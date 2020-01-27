from flask import jsonify, Flask

app= Flask(__name__)

tasks= [
    {
        'id':1,
        'task': 'FIRST'
    },
    {
        'id':2,
        'task': 'SECOND'
    }
]

@app.route('/static/json',methods=['POST'])
def get_tasks():
    return jsonify({'tasks':tasks})

if(__name__=='__main__'):
    app.run(port=8001,debug=False)