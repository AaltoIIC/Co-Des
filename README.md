# Co-Des framework
This repository includes scripts that implement the proof of concept of Co-Des framework.

The PoC uses openTorsion library to implement analysis service.

OpenTorsion examples: https://github.com/Aalto-Arotor/openTorsion/tree/main/opentorsion/examples

Digital Twin Documents for development are located in this Twinbase instance: https://juusoautiosalo.github.io/dev-twinbase-ddt/

## Install
Note: Python 3.9 or 3.10 is required

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

## Run

### Analysis server
Open new terminal or command window and navigate to flask_server folder.

Start analysis server by running:
Linux:
```sh
python3 app.py
```

Windows:
```sh
python app.py
```

### Find optimal design
Now that analysis server is running, the optimal design finder script can be executed. Go to the root folder and run:

Linux:
```sh
python3 python find_optimal_design_threaded.py
```

Windows:
```sh
python find_optimal_design_threaded.py
```

## Other files

`measurements` folder contains scripts for running performance measurements.

## Authors

Riku Ala-Laurinaho, Juuso Autiosalo, Sampo Laine, Urho Hakonen, and Raine Viitala.
