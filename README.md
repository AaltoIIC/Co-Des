# Co-Des framework
This repository includes scripts that implement the proof of concept of Co-Des framework.

The PoC uses openTorsion library to implement analysis service.

OpenTorsion examples: https://github.com/Aalto-Arotor/openTorsion/tree/main/opentorsion/examples

Digital Twin Documents for development are located in this Twinbase instance: https://juusoautiosalo.github.io/dev-twinbase-ddt/

## Repository structure

The repository structure is presented as a tree below. Next this structure is presented in more detail.

```sh
├── flask_server
│   ├── app.py
│   ├── config.py
│   ├── views.py
│   └── flask_utils 
│       ├── forced_response_analysis.py
│       └── openTorsion_converter.py
├── measurements
│   ├── analyze_results.py
│   ├── execution_times.pdf
│   ├── find_optimal_design_threaded_measurements.py
│   ├── measurements_combined.csv
│   ├── results.pdf
│   ├── results.txt
│   └── tests.py
├── ontologies
│   ├── ddt.md
│   ├── tors.md
│   └── twinschema.md
├── find_optimal_design_threaded.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

### **/flask_server**
This folder contains files necessary to run an example analysis server. This server implements a torsional vibration analysis of a given assembly using openTorsion library.
The server has only one endpoint /v1/opentorsion. The server specification in OpenAPI format can be find from: https://juusoautiosalo.github.io/dev-twinbase-ddt/16b5f878-e6a1-47fc-8b6a-bb168b29dfe8/openapi.yaml


#### **/flask_server/app.py**
App.py is part of default Flask file structure and defines the application. Run this file to run the server:
```sh
python3 app.py
```

#### **/flask_server/config.py**
Flask server configuration. Remember to change SECRET_KEY for production.

#### **/flask_server/views.py**
Contains the endpoints of the server and the associated operations. Currently, there is only one endpoint: /v1/opentorsion.
This endpoint takes as an input the components forming an assembly and the tested RPM range in a JSON format. The endpoint returns the maximum torsional vibration amplitude of the system.
An example input for the system is as follows:

{
  "assembly_urls": [
    "https://dtid.org/e85c46f4-bdc2-4e0e-acd2-6b0ae582072d",
    "https://dtid.org/1febe1f0-16ff-4245-8fb2-759c93b01808",
    "https://dtid.org/efa0d72f-994d-4ad4-9f16-f1565371a18d"
  ],
  "linspace": {
    "start": 0.1,
    "stop": 25,
    "num": 5000
  }
}
```
"assembly_urls" is a list of component DTID (Digital Twin IDentifiers, i.e., urls referencing to the corresponding digital twin document. For example, https://dtid.org/c8060ee0-8abe-4a25-a3b3-7f90ea55d616) that form an assembly.
"linspace" defines the RPMs the powertrain is tested. "num" specifies how many test points are formed between "start" and "stop" values.

The server returns the maximum torsional vibration for the system:
```sh
{
  "max_amplitude": 53123.235
}
```

#### **/flask_server/flask_utils**
This folder contains files that provide helper functions to run the torsional vibration analysis. These functions are called from views.py file.

#### **/flask_server/flask_utils/forced_response_analysis.py**
This script calculates the maximum torsional vibration amplitude for a system with a specific excitations and rpm range. Th script follows the [Forced response example](https://github.com/Aalto-Arotor/openTorsion/blob/main/opentorsion/examples/forced_response.py) from openTorsion library. This example was modified to be able to take varying excitation as an input. 

#### **/flask_server/flask_utils/openTorsion_converter.py**
This scripts takes a list of component DTIDs as an input and creates an openTorsion assembly from these components. The script fetches the component information from the Digital Twin Descriptions Documents of components stored in [Twinbase](https://github.com/twinbase/twinbase). These information include, for example, damping and excitation of components.


### **/measurements**
This folder contains all the files necessary to run performance measurements.


#### **/measurements/analyze_results.py**
This script takes two files as an input: execution times of analyzing assemblies (see: /measurements/measurements_combined.csv) and results of analyzing assemblies (see: /measurements/results.csv).
The script plots the execution times (see: /measurements/execution_times.pdf) and torsional vibration amplitudes (see: /measurements/results.pdf). In addition, it prints the exection times including min, max, median, average and mean absolute error.

#### **/measurements/execution_times.pdf**
Execution times plottes with Violin plot style.

#### **/measurements/find_optimal_design_threaded_measurements.py**
This is a modified version of the *find_optimal_design_threaded.py* in the root folder for the measurements. The modifications include functions to measure execution times and limiting the number of concurrent connections to the Flask server.

#### **/measurements/measurements_combined.csv**
Execution times of running *find_optimal_design_threaded_measurements.py* script with the given parameters.

#### **/measurements/results.csv**
Maximum torsional vibration of the tested assemblies.

#### **/measurements/results.pdf**
Plot of maximum torsional vibration of the tested assemblies.

#### **/measurements/tests.py**
This script is use to run performance measurements. First a DTID of a system design, i.e., Digital Design Template is given as input. Thereafter, user can either specify the list of components that script uses to find optimal component candidates or a DTID of a component catalog stored in Twinbase, for example, https://dtid.org/4802e224-b05d-45df-9b5e-35a8f23af79f.

### **ontologies**
This folder contains ontologies for digital twin documents.

#### **ontologies/ddt.md**
This file describes ontology for Digital Design Template.

#### **ontologies/tors.md**
This file describes ontology for torsional vibration analysis.

#### **ontologies/twinschema.md**
This file describes ontology for digital twins.

### **.gitignore**
File to desribe which files should be excluded from the repository.

### **find_optimal_design_threaded.py**
This script is used to find the optimal components for a system described in a Digital Design Template (for ex. https://dtid.org/2ef85647-aee2-40c5-bb5a-380c9563ed16) from a given list of components.

### **LICENSE**
This work uses MIT licence defined in this file.

### **requirements.txt**
Python libraries needed to run the Co-Des framework.



## Install
Note: The current version of the repository is tested with Python 3.11.4.

Clone source code
```sh
git clone git@github.com:AaltoIIC/digital-design-template.git
cd digital-design-template
```
Create and activate virtual environment (recommended)

Linux:
```sh
python3 -m venv env
source env/bin/activate
```
Windows:
```sh
python -m venv env
env\Scripts\activate
```

Install requirements

Linux:
```sh
pip3 install -r requirements.txt
```

Windows:
```sh
pip install -r requirements.txt
```

## Use of the framework

Next, it is presented how the Co-Des framework can be used to analyze selected components and how performance tests can be run.

### Analyzing components

Analyzing components requires first to start an analysis server, to which assemblies are sent to be analyzed. Thereafter, *find_optimal_design_threaded.py* script is run that analyzes all possible assemblies for the selected system design with a given set of components.

#### Start analysis server
Open new terminal or command window and navigate to flask_server folder.
```sh
cd flask_server
```

Start analysis server by running:
Linux:
```sh
python3 app.py
```

Windows:
```sh
python app.py
```

#### Analyze assemblies
Now that analysis server is running, the optimal design finder script can be executed. Go to the root folder and run:

Linux:
```sh
python3 python find_optimal_design_threaded.py
```

Windows:
```sh
python find_optimal_design_threaded.py
```

### Running measurements


## Authors

Riku Ala-Laurinaho, Juuso Autiosalo, Sampo Laine, Urho Hakonen, and Raine Viitala.
