from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(__name__)

# import routes
from views.calls import bp as calls
from views.transcribe import bp as transcribe

app.register_blueprint(calls)
app.register_blueprint(transcribe)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

if __name__ == '__main__':
    app.run()