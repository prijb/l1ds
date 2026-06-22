# Compare the recojet spectra before and after corrections
import os
import argparse
import numpy as np
import uproot 
import awkward as ak
import hist
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import mplhep as hep
hep.style.use("CMS")
plt.rcParams["figure.figsize"] = (12.5, 10) 

parser = argparse.ArgumentParser(description="Compare jet spectra")
parser.add_argument("--infile", type=str, help="Data file")
parser.add_argument("--outdir", type=str, help="Directory to save plots in")
parser.add_argument("--label", type=str, help="Label for file")
parser.add_argument("--addtxt", type=str, help="Additional text")
args = parser.parse_args()

infile = args.infile
outdir = args.outdir
label = args.label
addtxt = args.addtxt
if addtxt is not None:
    addtxt = addtxt.replace("\\n", "\n")

os.makedirs(outdir, exist_ok=True)

f = uproot.open(f"{infile}:Events")
events = f.arrays(f.keys(), library="ak", how="zip")
events = events[events.nJet > 0]
jets = events.Jet

## Sort jets
jets_pt_order = ak.argsort(jets.pt, axis=1, ascending=False)
jets = jets[jets_pt_order]

## Plot weird jets
jets_weird = jets[jets.pt_raw < 9]
h_jet_eta_weird = hist.Hist(hist.axis.Regular(100, -5, 5, name="eta", label="Jet eta"), storage="weight")
h_jet_eta_weird.fill(eta=ak.flatten(jets_weird.eta))

fig, ax = plt.subplots()
hep.histplot(h_jet_eta_weird, histtype="step", ax=ax, label="Raw pT < 9 GeV", color="red", flow=None)
ax.set_xlabel(r"Jet $\eta$")
ax.set_ylabel("Counts")
ax.set_yscale("log")
ax.set_xlim(-5, 5)
ax.legend(loc="upper center")
hep.cms.label(data=False, llabel='Private Work', ax=ax, rlabel=f"{label}")
plt.savefig(f"{outdir}/eta.png")


## Plot 2D
h_jet_pt_eta = hist.Hist(
    hist.axis.Regular(30, 0, 30, name="pt", label="Jet pT"), 
    hist.axis.Regular(50, -5, 5, name="eta", label="Jet eta"), 
    storage="weight",
)
h_jet_pt_phi = hist.Hist(
    hist.axis.Regular(30, 0, 30, name="pt", label="Jet pT"), 
    hist.axis.Regular(50, -3.2, 3.2, name="phi", label="Jet phi"), 
    storage="weight",
)
h_jet_phi_eta = hist.Hist(
    hist.axis.Regular(50, -3.2, 3.2, name="phi", label="Jet phi"), 
    hist.axis.Regular(50, -5, 5, name="eta", label="Jet eta"), 
    storage="weight",
)

h_jet_pt_eta.fill(pt=ak.flatten(jets.pt_raw), eta=ak.flatten(jets.eta))
h_jet_pt_phi.fill(pt=ak.flatten(jets.pt_raw), phi=ak.flatten(jets.phi))
h_jet_phi_eta.fill(phi=ak.flatten(jets.phi), eta=ak.flatten(jets.eta))

fig, ax = plt.subplots()
hep.hist2dplot(h_jet_pt_eta, cbar=True, flow=None)
ax.set_xlabel(r"Jet raw $p_{T}$ [GeV]")
ax.set_ylabel(r"Jet $\eta$")
hep.cms.label(data=False, llabel='Private Work', ax=ax, rlabel=f"{label}")
plt.savefig(f"{outdir}/pt_eta.png")

fig, ax = plt.subplots()
hep.hist2dplot(h_jet_pt_phi, cbar=True, flow=None)
ax.set_xlabel(r"Jet raw $p_{T}$ [GeV]")
ax.set_ylabel(r"Jet $\phi$")
hep.cms.label(data=False, llabel='Private Work', ax=ax, rlabel=f"{label}")
plt.savefig(f"{outdir}/pt_phi.png")

fig, ax = plt.subplots()
hep.hist2dplot(h_jet_phi_eta, cbar=True, flow=None)
ax.set_xlabel(r"Jet $\phi$")
ax.set_ylabel(r"Jet $\eta$")
hep.cms.label(data=False, llabel='Private Work', ax=ax, rlabel=f"{label}")
plt.savefig(f"{outdir}/phi_eta.png")

## Eta cut
jets = jets[(np.abs(jets.eta) > 2.5) & (np.abs(jets.eta) < 3.0)]
#jets = jets[np.abs(jets.eta) < 2.5]
#jets = jets[~ak.is_none(jets)]

h_jet_pt_orig = hist.Hist(hist.axis.Regular(100, 0, 100, name="pt", label="Jet pT [NanoAOD]"), storage="weight")
h_jet_pt_raw = hist.Hist(hist.axis.Regular(100, 0, 100, name="pt", label="Jet pT (raw)"), storage="weight")
h_jet_pt_scale = hist.Hist(hist.axis.Regular(100, 0, 100, name="pt", label="Jet pT (JES)"), storage="weight")
h_jet_pt = hist.Hist(hist.axis.Regular(100, 0, 100, name="pt", label="Jet pT (JES+JER)"), storage="weight")

h_jet_pt_orig_lead = hist.Hist(hist.axis.Regular(100, 0, 100, name="pt", label="Jet pT [NanoAOD]"), storage="weight")
h_jet_pt_raw_lead = hist.Hist(hist.axis.Regular(100, 0, 100, name="pt", label="Jet pT (raw)"), storage="weight")
h_jet_pt_scale_lead = hist.Hist(hist.axis.Regular(100, 0, 100, name="pt", label="Jet pT (JES)"), storage="weight")
h_jet_pt_lead = hist.Hist(hist.axis.Regular(100, 0, 100, name="pt", label="Jet pT (JES+JER)"), storage="weight")

h_jet_pt_orig.fill(pt=ak.flatten(jets.pt_orig))
h_jet_pt_raw.fill(pt=ak.flatten(jets.pt_raw))
h_jet_pt_scale.fill(pt=ak.flatten(jets.pt_scale_orig))
h_jet_pt.fill(pt=ak.flatten(jets.pt))

fig, ax = plt.subplots()
hep.histplot(h_jet_pt_orig, histtype="step", ax=ax, label="NanoAODv15", color="black", flow=None)
hep.histplot(h_jet_pt_raw, histtype="step", ax=ax, label="Raw", color="red", flow=None)
hep.histplot(h_jet_pt_scale, histtype="step", ax=ax, label="JES", linestyle="--", color="blue", flow=None)
hep.histplot(h_jet_pt, histtype="step", ax=ax, label="JES+JER", color="blue", flow=None)
ax.set_xlabel(r"Jet $p_{T}$ [GeV]")
ax.set_ylabel("Counts")
#ax.set_yscale("log")
ax.set_xlim(0, 100)
ax.legend()
if addtxt is not None: ax.text(0.70, 0.70, f"{addtxt}", transform=ax.transAxes, fontsize=16*1.2)
hep.cms.label(data=False, llabel='Private Work', ax=ax, rlabel=f"{label}")
plt.savefig(f"{outdir}/pt.png")

firsts_mask = ~ak.is_none(ak.firsts(jets.pt))
h_jet_pt_orig_lead.fill(pt=ak.firsts(jets.pt_orig)[firsts_mask])
h_jet_pt_raw_lead.fill(pt=ak.firsts(jets.pt_raw)[firsts_mask])
h_jet_pt_scale_lead.fill(pt=ak.firsts(jets.pt_scale_orig)[firsts_mask])
h_jet_pt_lead.fill(pt=ak.firsts(jets.pt)[firsts_mask])

fig, ax = plt.subplots()
hep.histplot(h_jet_pt_orig_lead, histtype="step", ax=ax, label="NanoAODv15", color="black", flow=None)
hep.histplot(h_jet_pt_raw_lead, histtype="step", ax=ax, label="Raw", color="red", flow=None)
hep.histplot(h_jet_pt_scale_lead, histtype="step", ax=ax, label="JES", linestyle="--", color="blue", flow=None)
hep.histplot(h_jet_pt_lead, histtype="step", ax=ax, label="JES+JER", color="blue", flow=None)
ax.set_xlabel(r"Lead Jet $p_{T}$ [GeV]")
ax.set_ylabel("Counts")
#ax.set_yscale("log")
ax.set_xlim(0, 100)
ax.legend()
if addtxt is not None: ax.text(0.70, 0.70, f"{addtxt}", transform=ax.transAxes, fontsize=16*1.2)
hep.cms.label(data=False, llabel='Private Work', ax=ax, rlabel=f"{label}")
plt.savefig(f"{outdir}/lead_pt.png")