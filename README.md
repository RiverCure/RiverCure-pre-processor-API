# RiverCure-pre-processor-API
Flask python REST API application for integration with RiverCure Portal

## API endpoints
The REST API definiton is on app.py file

### GET
```host```/<br/>
### POST
```host```/process/?context_name={context_name_value}<br/>
```host```/simulate/?event_id={event_id_value}&context_name={context_name_value}<br/>
```host```/simulation/results/?event_id={event_id_value}&context_name={context_name_value}<br/>

#### GET /
Check if server is alive

#### POST /process/
Generate mesh for a given context

Parameters
 | Name | Type | Description |
 | ---- | ---- | ----------- |
 | context name | String | Name of the context in RiverCure Portal to which the geometries sent belong to<br/>It is sent on the url |
 | domain | Geojson file | Geojson file with definiton of the context domain<br/>It is sent in the body of the request |
 | refinements | Geojson file | Geojson file with definiton of the context refinements<br/>It is sent in the body of the request |
 | alignments | Geojson file | Geojson file with definiton of the context alignments<br/>It is sent in the body of the request |
 | boundaries | Geojson file | Geojson file with definiton of the context boundaries<br/>It is sent in the body of the request |
 | boundaries_points | Geojson file | Geojson file with definiton of the context boundaries points<br/>It is sent in the body of the request |


#### POST /simulate/
Execute a HiSTAV simulation for a given context event

Parameters
 | Name | Type | Description |
 | ---- | ---- | ----------- |
 | context name | String | Name of the context in RiverCure Portal to which the simulation belongs to<br/>It is sent on the url |
 | event id | Int | Context event identifier in RiverCure Portal to which the simulation belongs to<br/>It is sent on the url |
 | output | Text file | Text file with 2 lines containing values for the simulation<br/>It is sent in the body of the request with .cnt extension|
 | series | Text file | Collection of text files containing the time series for each sensor<br/>1 file per context sensor<br/>It is sent in the body of the request with .bnd extension|

#### POST /simulation/results/
Return the results for a given context event simulation

Parameters
 | Name | Type | Description |
 | ---- | ---- | ----------- |
 | context name | String | Name of the context in RiverCure Portal to which the simulation belongs to<br/>It is sent on the url |
 | event id | Int | Context event identifier in RiverCure Portal to which the simulation belongs to<br/>It is sent on the url |

## Install requirements.txt
Might be necessary to install GDAL like:
    pip install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"

## stavResults
Python script to transform maxima vtk into geotiff
Depends on the installation of the requirements.txt mentioned in the above section
e.g. 
```
python stavResults.py -i {maxima_input_filename}.vtk -o {output_filename}.tif
```

## hiStav and pre-processor
It is necessary to create a folder with the name simulation and the tree of histav
mesh and gmsh 4.0.7 executables should be added in the respective places

```
.
├── bed
│   ├── activeLayers
│   │   ├── bedLayers.sed
│   │   └── nodesFrictionCoef.sed
│   ├── bed.cnt
│   ├── fractionData
│   │   ├── fineSand.sed
│   │   ├── gravel.sed
│   │   └── silt.sed
│   └── gradCurves
│       ├── curve-1.sed
│       ├── curve-2.sed
│       └── curve-3.sed
├── boundary
│   ├── boundary.cnt
│   └── meshData
│       ├── boundaryDim.bnd
│       ├── boundaryIdx-0.bnd
│       ├── boundaryIdx-1.bnd
│       ├── boundaryIdx-2.bnd
│       ├── boundaryIdx-3.bnd
│       └── boundaryIdx-4.bnd
├── control
│   ├── hpc.cnt
│   ├── numerics.cnt
│   ├── physics.cnt
│   └── time.cnt
├── forcing
│   ├── forcing.cnt
│   └── gauges
│       ├── rainGauge-1.env
│       ├── rainGauge-2.env
│       └── rainGauge-3.env
├── gis
│   ├── PreProcessingSTAV.log
│   ├── gmsh
│   │   ├── generatedSTAVMesh.geo
│   │   ├── generatedSTAVMesh.mesh
│   │   └── gmsh                    <--------- gmsh 4.0.7 executable
│   ├── mesh                        <--------- executable to run the program
│   ├── rasters
│   ├── context_files
│   │   ├── alignments.geojson
│   │   ├── boundaries_points.geojson
│   │   ├── boundaries.geojson
│   │   ├── domain.geojson
│   │   ├── refinements.geojson
│   └── test.qgz
├── initial
│   └── initial.cnt
├── mesh
│   ├── elements.mesh
│   ├── info.mesh
│   ├── nodes.mesh
│   └── vtk
│       └── meshQuality.vtk
└── output
    ├── bed
    ├── forcing
    ├── hydrodynamics
    ├── lagrangian
    ├── maxima
    ├── numerics
    ├── output.cnt
    └── scalars
```