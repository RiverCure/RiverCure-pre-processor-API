import os
from flask import Flask, Response

app = Flask(__name__)


@app.route('/')
def ping():
    status_code = Response(status=200)
    return status_code

@app.route('/process/')
def run_pre_processor():
    os.system('./mesh && \\n')
    app.logger.warning('User requested a simulation\n')
    return 'Processed\n'

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=ENVIRONMENT_DEBUG)