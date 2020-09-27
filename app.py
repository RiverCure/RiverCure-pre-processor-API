import os, requests
from flask import Flask, Response, request

app = Flask(__name__)


@app.route('/')
def ping():
    status_code = Response(status=200)
    return status_code

@app.route('/process/', methods=['POST'])
def run_pre_processor():
    destination_folder = 'simulation/gis/context_files'

    try:
        if request.method == 'POST':
            for key in request.files:
                request.files[key].save(f'{destination_folder}/{key}')

        os.system(f'(cd simulation/gis && ./mesh && cd ../mesh/vtk && mv meshQuality.vtk coura_mesh.vtk &)')
    except Exception as e:
        print(f'Failed simulation!\nException{e}')
        return 'Simulation failed'

    return 'Simulation being processed\n'

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=ENVIRONMENT_DEBUG)