from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    print('Hello World!')
    return ('hello world!')

if __name__ == "__main__":
    app.run()

@app.route('/user')
def user():
    return ('user')
