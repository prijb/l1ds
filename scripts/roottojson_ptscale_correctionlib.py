# Correctionlib version of roottojson_ptscale
# Testing generating correctionlib files
import numpy as np
import correctionlib
import correctionlib.schemav2 as cs
import correctionlib.convert
import rich
import gzip

# Uproot version
import uproot
import hist

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("--input", type=str, required=True, help="Input ROOT file")
parser.add_argument("--output", type=str, default="data/test/test.json", help="Output JSON file")
args = parser.parse_args()

input_file = args.input
output_file = args.output

tf = uproot.open(input_file)
histo_nominal = tf["h_scale_nominal"].to_hist()
histo_up = tf["h_scale_up"].to_hist()
histo_down = tf["h_scale_down"].to_hist()

# Rename the axes
histo_nominal.axes.name = ("Jet_eta", "Jet_pt")
histo_up.axes.name = ("Jet_eta", "Jet_pt")
histo_down.axes.name = ("Jet_eta", "Jet_pt")

scale_correction_nominal = correctionlib.convert.from_histogram(histo_nominal)
scale_correction_nominal.data.flow = "clamp"

scale_correction_up = correctionlib.convert.from_histogram(histo_up)
scale_correction_up.data.flow = "clamp"

scale_correction_down = correctionlib.convert.from_histogram(histo_down)
scale_correction_down.data.flow = "clamp"

# Note: The first two variables should be the same names as the variables in the three corrections which are the histogram axis names
scale_correction = cs.Correction(
    name = "L1JES",
    description = "Jet L1/Reco response factor",
    version = 1,
    inputs = [
        cs.Variable(name="Jet_eta", type="real", description="Jet eta"),
        cs.Variable(name="Jet_pt", type="real", description="Jet pt"),
        cs.Variable(name="ValType", type="string", description="sf | systup | systdown"),
    ],
    output = cs.Variable(name="weight", type="real", description="Scale factor"),
    data = cs.Category(
        nodetype="category",
        input="ValType",
        content=[
            cs.CategoryItem(key="sf", value=scale_correction_nominal.data),
            cs.CategoryItem(key="systup", value=scale_correction_up.data),
            cs.CategoryItem(key="systdown", value=scale_correction_down.data),
        ],
    ),
)

# Wrap around a correctionset
cset = cs.CorrectionSet(
    schema_version = 2,
    description = "L1 JES corrections",
    corrections = [scale_correction],
)

if hasattr(cset, "model_dump_json"):
    json_text = cset.model_dump_json(exclude_unset=True, indent=2)
else:
    json_text = cset.json(exclude_unset=True, indent=2)

with open(output_file, "w") as fout:
    fout.write(json_text)

