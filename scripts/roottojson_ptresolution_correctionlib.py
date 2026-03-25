# Generating correctionlib files for JER smearing
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

# Example: python3 scripts/roottojson_ptresolution_correctionlib.py --input_res data/resolution/prod_240326/resolution_WJet24NanoV15_fit.root --input_sf data/resolution/prod_240326/resolution_Muon24G_WJet24NanoV15_ratio_fit.root --output_res data/jec_240326/jet_pt_resolution_mc.json --output_sf data/jec_240326/jet_pt_resolution_sf_2024.json --output_smear data/jec_240326/jet_pt_resolution_smear_2024_norand.json --skiprand
parser = ArgumentParser()
parser.add_argument("--input_res", type=str, required=True, help="Input ROOT file for resolution")
parser.add_argument("--input_sf", type=str, required=True, help="Input ROOT file for smearing SF")
parser.add_argument("--output_res", type=str, default="data/test/test_res.json", help="Output JSON file for resolution")
parser.add_argument("--output_sf", type=str, default="data/test/test_sf.json", help="Output JSON file for resolution SF")
parser.add_argument("--output_smear", type=str, default="data/test/test_smear.json", help="Output JSON file for resolution smear")
parser.add_argument("--skiprand", action="store_true", help="Make a smear json that already accepts the random term")
args = parser.parse_args()

input_file_res = args.input_res
input_file_sf = args.input_sf
output_file_res = args.output_res
output_file_sf = args.output_sf
output_file_smear = args.output_smear

f_res = uproot.open(input_file_res)
f_sf = uproot.open(input_file_sf)

histo_res = f_res["h_resolution_nominal"].to_hist()

histo_sf_nominal = f_sf["h_resolution_nominal"].to_hist()
histo_sf_up = f_sf["h_resolution_up"].to_hist()
histo_sf_down = f_sf["h_resolution_down"].to_hist()

# Rename the axes
histo_res.axes.name = ("Jet_eta", "Jet_pt")
histo_sf_nominal.axes.name = ("Jet_eta", "Jet_pt")
histo_sf_up.axes.name = ("Jet_eta", "Jet_pt")
histo_sf_down.axes.name = ("Jet_eta", "Jet_pt")

## Make the reference resolution correction
res_corr = correctionlib.convert.from_histogram(histo_res)
res_corr.name = "L1JER"
res_corr.output.name = "JER"
res_corr.output.description = "Reference JER"
res_corr.data.flow = "clamp"

cset_res_corr = cs.CorrectionSet(
    schema_version = 2,
    description = "L1 JER",
    corrections=[res_corr],
)
if hasattr(cset_res_corr, "model_dump_json"):
    json_text_res = cset_res_corr.model_dump_json(exclude_unset=True, indent=2)
else:
    json_text_res = cset_res_corr.json(exclude_unset=True, indent=2)
with open(output_file_res, "w") as fout:
    fout.write(json_text_res)

## Make the SF corrections
sf_corr_nominal = correctionlib.convert.from_histogram(histo_sf_nominal)
sf_corr_up = correctionlib.convert.from_histogram(histo_sf_up)
sf_corr_down = correctionlib.convert.from_histogram(histo_sf_down)

sf_corr_nominal.data.flow = "clamp"
sf_corr_up.data.flow = "clamp"
sf_corr_down.data.flow = "clamp"

sf_corr = cs.Correction(
    name = "L1JERSF",
    description = "L1 Jet Data/MC resolution smearing SF",
    version = 1,
    inputs = [
        cs.Variable(name="Jet_eta", type="real", description="Jet eta"),
        cs.Variable(name="Jet_pt", type="real", description="Jet pt"),
        cs.Variable(name="ValType", type="string", description="sf | systup | systdown"),
    ],
    output = cs.Variable(name="JERSF", type="real", description="JER Scale factor"),
    data = cs.Category(
        nodetype="category",
        input="ValType",
        content=[
            cs.CategoryItem(key="sf", value=sf_corr_nominal.data),
            cs.CategoryItem(key="systup", value=sf_corr_up.data),
            cs.CategoryItem(key="systdown", value=sf_corr_down.data),
        ],
    ),
)

cset_sf_corr = cs.CorrectionSet(
    schema_version = 2,
    description = "L1 JER",
    corrections = [sf_corr],
)
if hasattr(cset_sf_corr, "model_dump_json"):
    json_text_sf = cset_sf_corr.model_dump_json(exclude_unset=True, indent=2)
else:
    json_text_sf = cset_sf_corr.json(exclude_unset=True, indent=2)
with open(output_file_sf, "w") as fout:
    fout.write(json_text_sf)

## Create the smearing factor
if args.skiprand:
    print("\nSkipping random term")
    smear_corr = cs.Correction(
        name = "L1JERSmear",
        description = "L1 Jet Data/MC resolution smearing",
        version = 1,
        inputs = [
            cs.Variable(name="JER", type="real", description="Reference jet energy resolution"),
            cs.Variable(name="JERSF", type="real", description="Jet energy resolution scale factor"),
            cs.Variable(name="RandSmear", type="real", description="Random multiplicative factor from Normal dist"),
        ],
        output = cs.Variable(name="smear", type="real", description="Smear factor"), 
        data = cs.Formula(
                nodetype="formula",
                parser="TFormula",
                expression="1 + sqrt(max(x*x - 1, 0)) * y * z",
                variables=["JERSF", "JER", "RandSmear"]
        ),
    )

else:
    smear_corr = cs.Correction(
        name = "L1JERSmear",
        description = "L1 Jet Data/MC resolution smearing",
        version = 1,
        inputs = [
            cs.Variable(name="Jet_eta", type="real", description="Jet eta"),
            cs.Variable(name="Jet_pt", type="real", description="Jet pt"),
            cs.Variable(name="JER", type="real", description="Reference jet energy resolution"),
            cs.Variable(name="JERSF", type="real", description="Jet energy resolution scale factor"),
            cs.Variable(name="RandSmear", type="real", description="Random multiplicative factor from Normal dist"),
            cs.Variable(name="EventID", type="real", description="EventID"),
        ],
        output = cs.Variable(name="smear", type="real", description="Smear factor"), 
        data = cs.Transform(
            nodetype="transform",
            input="RandSmear",
            rule=cs.HashPRNG(
                nodetype="hashprng",
                inputs=["Jet_eta", "EventID"],
                distribution="normal",
            ),
            content=cs.Formula(
                nodetype="formula",
                parser="TFormula",
                expression="1 + sqrt(max(x*x - 1, 0)) * y * z",
                variables=["JERSF", "JER", "RandSmear"]
            ),
        ),
    )

cset_smear_corr = cs.CorrectionSet(
    schema_version = 2,
    description = "L1 JER",
    corrections = [smear_corr],
)
if hasattr(cset_smear_corr, "model_dump_json"):
    json_text_smear = cset_smear_corr.model_dump_json(exclude_unset=True, indent=2)
else:
    json_text_smear = cset_smear_corr.json(exclude_unset=True, indent=2)
with open(output_file_smear, "w") as fout:
    fout.write(json_text_smear)


