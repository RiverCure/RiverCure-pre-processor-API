import os, requests, subprocess, zipfile
from flask import Flask, Response, request, send_file
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


@app.route('/')
def ping():
    status_code = Response(status=200)
    return status_code

@app.route('/process/', methods=['POST'])
def run_pre_processor():
    requester_ip = request.remote_addr
    destination_folder = 'simulation/gis/'
    context_name = request.args.get('context_name')
    print(context_name)
    try:
        if request.method == 'POST':
            for key in request.files:
                if key == 'dtm.tif' or key == 'frictionCoef.tif':
                    request.files[key].save(f'{destination_folder}rasters/{key}')
                else:
                    request.files[key].save(f'{destination_folder}context_files/{key}')

        # os.system(f'''(cd simulation/gis && ./mesh && cd ../.. \
        #             && cp simulation/mesh/vtk/meshQuality.vtk paraview_visualizer/data/{context_name}_mesh.vtk &)''')

        subprocess.call(f'''(cd simulation/gis && ./mesh && cd ../.. \
                    && cp simulation/mesh/vtk/meshQuality.vtk paraview_visualizer/data/{context_name}_mesh.vtk \
                    && curl {requester_ip}/contexts/mesh-status/{context_name}?status=True &)''', shell=True)
        
        # payload = {'status': True}
        # requests.get(f'{rivercure_url}/contexts/mesh-status/{context_name}', params=payload)
    except Exception as e:
        print(f'Failed pre-processing!\nException{e}')
        return 'fail'

    return 'success'

@app.route('/simulate/', methods=['POST'])
def simulate():
    requester_ip = request.remote_addr
    frequency_destination_folder = 'simulation/output/output.cnt'
    sensor_data_destination_folder = 'simulation/boundary/gauges'
    context_name = request.args.get('context_name')
    event_id = request.args.get('event_id')
    print(event_id)
    # bnd are duplicated might be necessary to remove them
    try:
        if request.method == 'POST':
            for key in request.files:
                if key == 'frequency':
                    request.files[key].save(f'{frequency_destination_folder}')
                else:
                    request.files[key].save(f'{sensor_data_destination_folder}/{key}')

        subprocess.call(f'''(cd simulation && ./solver2D-OMP.dat \
                            && curl {requester_ip}/contexts/simulation/results/handle/{event_id} &)''', shell=True)
    except Exception as e:
        print(f'Failed simulation!\nException{e}')
        return 'fail'

    return 'success'

@app.route('/simulation/results/')
def simulation_results():
    #event id necessary in the future
    context_name = request.args.get('context_name')
    event_id = request.args.get('event_id')
    folder_name = f'{context_name}_event_{event_id}_results.zip'

    os.system(f'''rm -r *.zip ; rm -r results/* \
                ; vtk=$(cd simulation/output/maxima && ls | grep *.vtk) \
                && (cd simulation/output/rasters && python stavResults.py -i ../maxima/$vtk -o ../../../results/{context_name}_event_{event_id})''')
    # files = {
    #     'max_depth': open('out-Max_Depth.tif', 'rb'),
    #     'max_level': open('out-Max_Level.tif', 'rb'),
    #     'max_q': open('out-Max_Q.tif', 'rb'),
    #     'max_vel': open('out-Max_Vel.tif', 'rb')
    # }

    with zipfile.ZipFile(folder_name, 'w', compression = zipfile.ZIP_STORED) as zipfolder:

        for root,dirs, files in os.walk('results/'):
            for file in files:
                zipfolder.write('results/' + file)

    return send_file(folder_name,
            mimetype = 'zip',
            attachment_filename= folder_name,
            as_attachment = True)

    # return send_file('./out-Max_Depth.tif', attachment_filename='out-Max_Depth.tif')

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("DEBUG", False)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=ENVIRONMENT_DEBUG)