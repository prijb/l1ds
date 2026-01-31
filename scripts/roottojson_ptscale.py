# Script to convert the ROOT pT scale histograms to a json
import numpy as np

from copy import deepcopy as copy
from analysis_tools.utils import import_root
ROOT = import_root()

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("--input", type=str, required=True, help="Input ROOT file")
parser.add_argument("--output", type=str, default="data/NUM_Data_DEN_MC_jet_pt_scale.json", help="Output JSON file")
args = parser.parse_args()

input_file = args.input
output_file = args.output
json_desc = output_file.split("/")[-1].split(".json")[0]

d = {
    "schema_version": 2,
    "corrections": [
        {
            "name": f"{json_desc}",
            "description": f"{json_desc}",
            "version": 1,
            "inputs": [
                {
                    "name": "Jet_eta",
                    "type": "real",
                    "description": "Jet eta"
                },
                {
                    "name": "Jet_pt",
                    "type": "real",
                    "description": "Jet pt"
                },
                {
                    "name": "ValType",
                    "type": "string",
                    "description": "sf or systup or systdown (currently 'sf' is nominal, and 'systup' and 'systdown' are up/down variations with total stat+syst uncertainties"
                }
            ],
            "output": {
                "name": "weight",
                "type": "real",
                "description": "Output scale factor (nominal) or uncertainty"
            },
            "data": {
                "nodetype": "binning",
                "input": "Jet_eta",
                "edges": [
                    -float("inf"), 
                    -3.0,
                    -2.5,
                    -2.0,
                    -1.3,
                    -0.5,
                    0.0,
                    0.5,
                    1.3,
                    2.0,
                    2.5,
                    3.0,
                    float("inf")
                ],
                "content": [],
                "flow": "error"
            }
        }
    ]
}

d_pt = {
    "nodetype": "binning",
    "input": "Jet_pt",
    "edges": [float("0")] + (np.arange(20, 452, 2, dtype=float).tolist()) + [float("inf")],
    "content": [],
    "flow": "error"
}

d_syst = {
    "nodetype": "category",
    "input": "ValType",
    "content": [
        {
            "key": "sf",
            "value": 0
        },
        {
            "key": "systup",
            "value": 0
        },
        {
            "key": "systdown",
            "value": 0
        }
    ]
}

tf = ROOT.TFile(args.input)
histo_nominal = tf.Get("h_scale_nominal")
histo_up = tf.Get("h_scale_up")
histo_down = tf.Get("h_scale_down")

n_pt_bins = len(d_pt["edges"]) - 1
n_pt_bins_hist = histo_nominal.GetNbinsY()
n_eta_bins = len(d["corrections"][0]["data"]["edges"]) - 1

for ib in range(len(d["corrections"][0]["data"]["edges"]) - 1):
    new_d_pt = copy(d_pt)
    #ibpt = 0
    for ibpt in range(len(new_d_pt["edges"]) - 1):
        new_d_syst = copy(d_syst)
        # Set for infinite eta bins
        if ((ib == 0) | (ib == (n_eta_bins - 1))):
            print(f"Filling eta bin with inf edge with 1 +- 0 for (ib={ib}, ibpt={ibpt})")
            content = 1.
            error = 0.
            new_d_syst["content"][0]["value"] = content
            new_d_syst["content"][1]["value"] = content + error
            new_d_syst["content"][2]["value"] = content - error
        else:
            if (ibpt == 0):
                print(f"Filling underflow bin with 1.0 +- 0.0 for (ib={ib}, ibpt={ibpt})")
                content = 1.0
                error = 0.0
                new_d_syst["content"][0]["value"] = content
                new_d_syst["content"][1]["value"] = content + error
                new_d_syst["content"][2]["value"] = content - error
            elif (ibpt == n_pt_bins -1):
                print(f"Filling overflow bin with {histo_nominal.GetBinContent(ib, ibpt -1)} +- 0.1 for (ib={ib}, ibpt={ibpt})")
                content = histo_nominal.GetBinContent(ib, ibpt -1)
                error = 0.1
                new_d_syst["content"][0]["value"] = content
                new_d_syst["content"][1]["value"] = content + error
                new_d_syst["content"][2]["value"] = content - error
            else:
                #print(f"Filling eta bin {ib} and pt bin {ibpt} with histogram bin contents ({ib + 1}, {ibpt + 1})")
                content_nominal = histo_nominal.GetBinContent(ib, ibpt)
                content_up = histo_up.GetBinContent(ib, ibpt)
                content_down = histo_down.GetBinContent(ib, ibpt)
                new_d_syst["content"][0]["value"] = content_nominal
                new_d_syst["content"][1]["value"] = content_up
                new_d_syst["content"][2]["value"] = content_down
        
        new_d_pt["content"].append(new_d_syst)
    d["corrections"][0]["data"]["content"].append(new_d_pt)

import json
with open(args.output, "w+") as fout:
    json.dump(d, fout, indent=4)

            
