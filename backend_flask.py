from flask import Flask
app = Flask(__name__) #flask object!

@app.route('/')
def index():
    return "herro!"

if __name__ == "__main__":
    app.run(debug = True)