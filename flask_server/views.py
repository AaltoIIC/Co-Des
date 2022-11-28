from app import app
from flask_utils import forced_response_analysis as fra
from flask import request

@app.route('/analyze_assembly', methods=['GET', 'POST'])
def assembly_analysis():
    #Not implemented
    if request.method == 'GET':
        pass

    #Analyze assembly
    elif request.method == 'POST':
        request_json = request.json
        rpm_linspace_dict = {}
        rpm_linspace_dict["start"] = request_json["linspace"]["start"]
        rpm_linspace_dict["stop"] = request_json["linspace"]["stop"]
        rpm_linspace_dict["num"] = request_json["linspace"]["num"]
        component_urls_for_assembly = request_json["assembly_urls"]
        max_amplitude = fra.forced_response_analysis(component_urls_for_assembly, rpm_linspace_dict)
        return {"max_amplitude": max_amplitude}
