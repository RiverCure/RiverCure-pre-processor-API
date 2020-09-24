import os, requests
from flask import Flask, Response

app = Flask(__name__)


@app.route('/')
def ping():
    status_code = Response(status=200)
    return status_code

@app.route('/process/<string:context_id>')
def run_pre_processor(context_id):
    # Request and download files
    url = f'http://localhost:8000/contexts/download/{context_id}'
    downloaded_folder = 'download_context.zip'
    destination_folder = 'simulation/context_files'
    req = requests.get(url)
    open(downloaded_folder, 'wb').write(req.content)
    os.system(f'''rm {destination_folder}/* ; \
                unzip {downloaded_folder} -d {destination_folder} && rm -R {downloaded_folder} && \
                (cd {destination_folder} && rename \'s/Coura_*//\' *) && \
                (cd simulation && ./mesh &)''')

    return 'Files downloaded\n'

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=ENVIRONMENT_DEBUG)