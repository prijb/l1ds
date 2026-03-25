import os 
import argparse
import ROOT

cwd = os.getcwd()

parser = argparse.ArgumentParser(description="Take a given file with a histogram and return a copy with the hist normalized to unit area")
parser.add_argument("--infile", type=str, required=True, help="Path to the input file")
parser.add_argument("--histname", type=str, required=True, help="Histogram name")
args = parser.parse_args()

infile = args.infile
histname = args.histname

infile_path, infile_name = os.path.split(infile)

f_in = ROOT.TFile.Open(infile, "READ")
h = f_in.Get(histname)
norm = h.Integral()

#h_norm = h.Clone(f"{histname}_norm")
h_norm = h.Clone(f"{histname}")
h_norm.Scale((1.0/norm))

f_out = ROOT.TFile.Open(infile.replace(".root", "_norm.root"), "RECREATE")
h_norm.Write()
f_out.Close()
f_in.Close()