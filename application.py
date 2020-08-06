import os
from flask import Flask, Response

app = Flask(__name__)


@app.route('/')
def ping():
    status_code = Response(status=200)
    return status_code

@app.route('/process/')
def run_pre_processor():
    os.system('./mesh && \n')
    app.logger.warning('User resquest a simlulation\n')
    return 'Processed\n'