# Script to take normalized MC, data (nom/up/down) pileup histograms and create a correctionlib file to bypass the regular puWeight module
import os
import pickle
import argparse

import uproot
import hist
import numpy as np

parser = argparse.ArgumentParser(description="Create pileup reweighting files")
parser.add_argument("--input_mc", type=str, help="MC pileup file")
parser.add_argument("--input_data", type=str, help="Data pileup file")
parser.add_argument("--hname_mc", type=str, help="Histogram name for MC")
parser.add_argument("--hname_data", type=str, help="Histogram name for Data")
parser.add_argument("--outfile", type=str, help="Output file name for correction")
args = parser.parse_args()

f_mc = uproot.open(args.input_mc)
f_data = uproot.open(args.input_data)

h_mc = f_mc[args.hname_mc].to_hist()
h_data = f_data[args.hname_data].to_hist()
h_data_up = f_data[f"{args.hname_data}_plus"].to_hist()
h_data_down = f_data[f"{args.hname_data}_minus"].to_hist()

ntrueint_axis = hist.axis.Variable(h_mc.axes[0].edges, name="ntrueint", label="Number of interactions")
h_ratio = hist.Hist(ntrueint_axis, storage=hist.storage.Weight())
h_ratio_up = hist.Hist(ntrueint_axis, storage=hist.storage.Weight())
h_ratio_down = hist.Hist(ntrueint_axis, storage=hist.storage.Weight())

ratio = h_data.values()/h_mc.values()
ratio = np.nan_to_num(ratio, posinf=1.0, neginf=1.0)
h_ratio.view().value[:] = ratio

ratio_up = h_data_up.values()/h_mc.values()
ratio_up = np.nan_to_num(ratio_up, posinf=1.0, neginf=1.0)
h_ratio_up.view().value[:] = ratio_up

ratio_down = h_data_down.values()/h_mc.values()
ratio_down = np.nan_to_num(ratio_down, posinf=1.0, neginf=1.0)
h_ratio_down.view().value[:] = ratio_down

##### Correctionlib conversion #####
import correctionlib
import correctionlib.schemav2 as cs
import correctionlib.convert

#h_ratio.axes[0].name = "ntrueint"
#h_ratio_up.axes[0].name = "ntrueint"
#h_ratio_down.axes[0].name = "ntrueint"

h_ratio.name = "PUWeight_nominal"
h_ratio.label = "weight"

h_ratio_up.name = "PUWeight_up"
h_ratio_up.label = "weight"

h_ratio_down.name = "PUWeight_down"
h_ratio_down.label = "weight"

correction_nominal = correctionlib.convert.from_histogram(h_ratio)
correction_nominal.data.flow = "clamp"

correction_up = correctionlib.convert.from_histogram(h_ratio_up)
correction_up.data.flow = "clamp"

correction_down = correctionlib.convert.from_histogram(h_ratio_down)
correction_down.data.flow = "clamp"

pileup_correction = cs.Correction(
    name = "PUWeight",
    description = "nTrueInt reweighting",
    version = 1,
    inputs = [
        cs.Variable(name="ntrueint", type="real", description="Number of interactions in event"),
        cs.Variable(name="ValType", type="string", description="sf | systup | systdown"),
    ],
    output = cs.Variable(name="weight", type="real", description="Scale factor"),
    data = cs.Category(
        nodetype="category",
        input="ValType",
        content=[
            cs.CategoryItem(key="sf", value=correction_nominal.data),
            cs.CategoryItem(key="systup", value=correction_up.data),
            cs.CategoryItem(key="systdown", value=correction_down.data),
        ],
    ),
)

# Wrap around a correctionset
pileup_cset = cs.CorrectionSet(
    schema_version = 2,
    description = "PUWeight corrections",
    corrections = [pileup_correction],
)

json_text = pileup_cset.model_dump_json(exclude_unset=True, indent=2)

with open(args.outfile, "w") as fout:
    fout.write(json_text)