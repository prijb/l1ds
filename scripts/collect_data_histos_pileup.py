# Collect the nominal, up and down pileup histograms for corrections
import os 
import argparse
import ROOT

cwd = os.getcwd()

parser = argparse.ArgumentParser(description="Take normalized pileup histograms for data and bring them together into one file")
parser.add_argument("--infile_nominal", type=str, required=True, help="Path to the input file (up)")
parser.add_argument("--infile_up", type=str, required=True, help="Path to the input file (up)")
parser.add_argument("--infile_down", type=str, required=True, help="Path to the input file (dpwm)")
parser.add_argument("--histname", type=str, required=True, help="Histogram name")
parser.add_argument("--outfile", type=str, required=True, help="Path to the output file")
args = parser.parse_args()

histname = args.histname

f_nominal = ROOT.TFile.Open(args.infile_nominal, "READ")
h_nominal = f_nominal.Get(histname)

f_up = ROOT.TFile.Open(args.infile_up, "READ")
h_up = f_up.Get(histname).Clone(f"{histname}_plus")

f_down = ROOT.TFile.Open(args.infile_down, "READ")
h_down = f_down.Get(histname).Clone(f"{histname}_minus")

f_out = ROOT.TFile.Open(args.outfile, "RECREATE")
h_nominal.Write()
h_up.Write()
h_down.Write()

f_out.Close()
f_down.Close()
f_up.Close()
f_nominal.Close()
