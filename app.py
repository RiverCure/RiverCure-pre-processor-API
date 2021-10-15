import os, requests, subprocess, zipfile
from flask import Flask, Response, request, send_file, send_from_directory
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


@app.route('/')
def ping():
    status_code = Response(status=200)
    return status_code

@app.route('/process-status/', methods=['GET'])
def get_pre_processor_status():
    context_name = request.args.get('context_name')
    log_file = f"logs/{context_name}_process_log.txt"
    if not os.path.isfile(log_file):
        return Response(status=404)

    msg = ""
    with open(log_file, "r") as f_log:
        msg = f_log.read()
    
    return msg

@app.route('/process/', methods=['POST'])
def run_pre_processor():
    # requester_ip = request.remote_addr
    requester_ip = os.environ['RIVERCURE_URL']
    context_name = request.args.get('context_name')
    destination_folder = f'{context_name}_simulation/gis/'
    print(context_name)
    log_file = f"logs/{context_name}_process_log.txt"
    if os.path.exists(log_file):
        os.remove(log_file)

    try:
        os.system(f'cp -r simulation {context_name}_simulation')

        for key in request.files:
            if key == 'dtm.tif' or key == 'frictionCoef.tif':
                request.files[key].save(f'{destination_folder}rasters/{key}')
            else:
                request.files[key].save(f'{destination_folder}context_files/{key}')

        log_f = open(log_file, "w")
        subprocess.Popen(f'''(cd {context_name}_simulation/gis && ./mesh && cd ../.. \
                && cp {context_name}_simulation/mesh/vtk/meshQuality.vtk paraview_visualizer/data/{context_name}_mesh.vtk \
                && curl {requester_ip}/contexts/mesh-status/{context_name}?status=True &)''', 
                stdout=log_f, stderr=log_f, shell=True)
        
    except Exception as e:
        print(f'Failed pre-processing!\nException{e}')
        return 'fail'

    return 'success'

@app.route('/simulate-status/', methods=['GET'])
def get_simulation_status():
    event_id = request.args.get('event_id')
    context_name = request.args.get('context_name')
    log_file = f"logs/{context_name}_simulate_{event_id}_log.txt"
    if not os.path.isfile(log_file):
        return Response(status=404)

    msg = []
    with open(log_file, "r") as f_log:
        msg = f_log.readlines()[-100:]
    msg = "".join(msg)
    
    return msg

@app.route('/simulate/', methods=['POST'])
def simulate():
    requester_ip = os.environ['RIVERCURE_URL']
    context_name = request.args.get('context_name')
    event_id = request.args.get('event_id')
    print(f'Simulation request for event {event_id} of context {context_name}')
    
    frequency_destination_folder = f'{context_name}_simulation/output/output.cnt'
    sensor_data_destination_folder = f'{context_name}_simulation/boundary/gauges'
    time_destination_folder = f'{context_name}_simulation/control/time.cnt'
    boundary_destination_folder = f'{context_name}_simulation/boundary/boundary.cnt'
    
    log_file = f"logs/{context_name}_simulate_{event_id}_log.txt"
    if os.path.exists(log_file):
        os.remove(log_file)
    # bnd are duplicated might be necessary to remove them
    try:
        if request.method == 'POST':
            for key in request.files:
                if key == 'frequency':
                    request.files[key].save(f'{frequency_destination_folder}')
                elif key == 'time':
                    request.files[key].save(f'{time_destination_folder}')
                elif key == 'boundaries':
                    request.files[key].save(f'{boundary_destination_folder}')
                else:
                    request.files[key].save(f'{sensor_data_destination_folder}/{key}')

        log_f = open(log_file, "w")
        # curl {requester_ip}/contexts/simulation/results/handle/{event_id} used to be here but now is not needed. Only the VTK in output/maxima/ is.
        subprocess.Popen(f'''(cd {context_name}_simulation && ./solver2D \
                            && curl {requester_ip}/contexts/event-status/{event_id}?status=True &)''', 
                            stdout=log_f, stderr=log_f, shell=True)
    except Exception as e:
        print(f'Failed simulation!\nException{e}')
        return 'fail'

    return 'success'

@app.route('/pre-processing/results/')
def preprocessing_results():
    context_name = request.args.get('context_name')
    path = os.path.join(app.root_path, f'{context_name}_simulation/mesh/vtk/')
    return send_from_directory(path, filename='meshQuality.vtk')

@app.route('/simulation/results/')
def simulation_results():
    context_name = request.args.get('context_name')
    path = os.path.join(app.root_path, f'{context_name}_simulation/output/maxima/')
    # The name can vary, but always starts with 'maxi'. Assume only one file, the desired one, is in this folder
    try:
        file_name = os.listdir(path)[0]
        return send_from_directory(path, filename=file_name)
    except: # usually this happens if the file doesnt exist in the folder
        return Response(status=404)

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=ENVIRONMENT_DEBUG)