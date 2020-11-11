# RiverCure-pre-processor-API
Flask python REST API application for integration with RiverCure Portal

## API endpoints
The REST API definiton is on app.py file

### GET
```host```/
### POST
```host```/process/?event_id={event_id_value}&context_name={context_name_value}
```host```/simulate/?event_id={event_id_value}&context_name={context_name_value}
```host```/simulation/results/?event_id={event_id_value}&context_name={context_name_value}

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