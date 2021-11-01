import os, subprocess, shutil
from flask import Flask, Response, request, send_from_directory
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def ping():
    return Response(status=200)

# Returns the processing status based on the mesh generation's log file
@app.route('/process-status/', methods=['GET'])
def get_pre_processor_status():
    organizationCode = request.args.get('organizationCode', False)
    contextCode = request.args.get('contextCode', False)
    if not organizationCode or not contextCode:
        return Response(status=400)

    log_file = f'logs/{organizationCode}/{contextCode}/mesh_log.txt'
    if not os.path.isfile(log_file):
        return Response(status=404)

    msg = ""
    with open(log_file, "r") as f_log:
        msg = f_log.read()
    
    return msg

# Initiates a mesh generation process
@app.route('/process/', methods=['POST'])
def run_pre_processor():
    requester_ip = os.environ['RIVERCURE_URL']
    organizationCode = request.args.get('organizationCode', False)
    contextCode = request.args.get('contextCode', False)
    if not organizationCode or not contextCode:
        return Response(status=400)

    destination_folder = f'{organizationCode}/{contextCode}_simulation/gis'
    print(f'Mesh generate request for context {contextCode} of organization {organizationCode}')

    log_file = f'logs/{organizationCode}/{contextCode}/mesh_log.txt'

    # If organization's/context's log folder doesnt exist, create
    if not os.path.exists(f'logs/{organizationCode}/{contextCode}'):
        os.makedirs(f'logs/{organizationCode}/{contextCode}')

    # Delete log file for this context if it already exists
    if os.path.exists(log_file):
        os.remove(log_file)

    try:
        shutil.copytree('simulation', f'{organizationCode}/{contextCode}_simulation', dirs_exist_ok=True)

        for key in request.files:
            if key == 'dtm.tif' or key == 'frictionCoef.tif':
                request.files[key].save(f'{destination_folder}/rasters/{key}')
            else:
                request.files[key].save(f'{destination_folder}/context_files/{key}')

        log_f = open(log_file, 'w')
        subprocess.Popen(f'''(cd {organizationCode}/{contextCode}_simulation/gis && ./mesh && cd ../../.. \
                && cp {organizationCode}/{contextCode}_simulation/mesh/vtk/meshQuality.vtk paraview_visualizer/data/{organizationCode}_{contextCode}_mesh.vtk \
                && curl {requester_ip}/contexts/mesh-status/{contextCode}/change?organization={organizationCode}\&status=True &)''', 
                stdout=log_f, stderr=log_f, shell=True)
        
    except Exception as e:
        print(f'Failed pre-processing!\nException{e}')
        return 'fail'

    return 'success'

@app.route('/simulate-status/', methods=['GET'])
def get_simulation_status():
    organizationCode = request.args.get('organizationCode', False)
    contextCode = request.args.get('contextCode', False)
    eventName = request.args.get('eventName', False)
    if not organizationCode or not contextCode or not eventName:
        return Response(status=400)
    
    # Remove whitespaces from event name
    eventName = eventName.replace(' ', '_')

    log_file = f'logs/{organizationCode}/{contextCode}/{eventName}_simulation_log.txt'
    if not os.path.isfile(log_file):
        return Response(status=404)

    cleanup = False
    msg = []
    with open(log_file, 'r') as f_log:
        lines = f_log.readlines()
        msg = lines[-100:]
        numberOfLines = len(lines)
        if numberOfLines > 10000:
            cleanup = True
    msg = "".join(msg)

    # Prevent file from oversizing
    if cleanup:
        open(log_file, 'w').close()
    
    return msg

@app.route('/simulate/', methods=['POST'])
def simulate():
    requester_ip = os.environ['RIVERCURE_URL']
    organizationCode = request.args.get('organizationCode', False)
    contextCode = request.args.get('contextCode', False)
    eventName = request.args.get('eventName', False)
    eventId = request.args.get('eventId', False)
    if not organizationCode or not contextCode or not eventName or not eventId:
        return Response(status=400)
        
    print(f'Simulation request for event {eventName}, of context {contextCode}, of organization {organizationCode}')

    # Remove whitespaces from event name
    eventName = eventName.replace(' ', '_')
    
    frequency_destination_folder   = f'{organizationCode}/{contextCode}_simulation/output/output.cnt'
    sensor_data_destination_folder = f'{organizationCode}/{contextCode}_simulation/boundary/gauges'
    time_destination_folder        = f'{organizationCode}/{contextCode}_simulation/control/time.cnt'
    boundary_destination_folder    = f'{organizationCode}/{contextCode}_simulation/boundary/boundary.cnt'
    
    log_file = f'logs/{organizationCode}/{contextCode}/{eventName}_simulation_log.txt'
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Creates folders if they dont exist
    os.makedirs(f'logs/{organizationCode}/{contextCode}', exist_ok=True)
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

        log_f = open(log_file, 'w')
        # curl {requester_ip}/contexts/simulation/results/handle/{event_id} used to be here but now is not needed. Only the VTK in output/maxima/ is.
        subprocess.Popen(f'''(cd {organizationCode}/{contextCode}_simulation && ./solver2D \
                            && curl {requester_ip}/contexts/event-status/{eventId}/change?status=True &)''', 
                            stdout=log_f, stderr=log_f, shell=True)
    except Exception as e:
        print(f'Failed simulation!\nException{e}')
        return 'fail'

    return 'success'

@app.route('/pre-processing/results/')
def preprocessing_results():
    organizationCode = request.args.get('organizationCode', False)
    contextCode = request.args.get('contextCode', False)
    if not organizationCode or not contextCode:
        return Response(status=400)

    path = os.path.join(app.root_path, f'{organizationCode}/{contextCode}_simulation/mesh/vtk/')
    return send_from_directory(path, 'meshQuality.vtk')

@app.route('/simulation/results/')
def simulation_results():
    organizationCode = request.args.get('organizationCode', False)
    contextCode = request.args.get('contextCode', False)
    if not organizationCode or not contextCode:
        return Response(status=400)

    path = os.path.join(app.root_path, f'{organizationCode}/{contextCode}_simulation/output/maxima/')
    # The name can vary, but always starts with 'maxi'. Assume only one file, the desired one, is in this folder
    try:
        file_name = os.listdir(path)[0]
        return send_from_directory(path, file_name)
    except: # usually this happens if the file doesnt exist in the folder
        return Response(status=404)

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=ENVIRONMENT_DEBUG)