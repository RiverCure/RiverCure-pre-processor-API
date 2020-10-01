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
    context_name = request.args.get('context_name')
    try:
        if request.method == 'POST':
            for key in request.files:
                request.files[key].save(f'{destination_folder}/{key}')

        os.system(f'''(cd simulation/gis && ./mesh && cd ../.. \
                    && cp simulation/mesh/vtk/meshQuality.vtk paraview_visualizer/data/{context_name}_mesh.vtk &)''')
    except Exception as e:
        print(f'Failed pre processing!\nException{e}')
        return 'Pre processing failed'

    return 'Pre processing started\n'

@app.route('/simulate/', methods=['POST'])
def simulate():
    frequency_destination_folder = 'simulation/output/output.cnt'
    sensor_data_destination_folder = 'simulation/boundary/gauges'
    context_name = request.args.get('context_name')

    # bnd are duplicated might be necessary to remove them
    try:
        if request.method == 'POST':
            for key in request.files:
                if key == 'frequency':
                    request.files[key].save(f'{frequency_destination_folder}')
                    pass
                else:
                    request.files[key].save(f'{sensor_data_destination_folder}/{key}')

    except Exception as e:
        print(f'Failed simulation!\nException{e}')
        return 'Simulation failed'

    return 'Simulation started\n'

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=ENVIRONMENT_DEBUG)