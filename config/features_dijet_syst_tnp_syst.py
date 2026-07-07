## New version of features_dijet_syst_tnp with systematic variations in JES/JER
# Tag and probe version of systematics 

from analysis_tools import Feature
from plotting_tools import Label

# Encoding function to convert -3.0 to "neg3p0" and 3.0 to "pos3p0"
def convert_eta_float_to_str(eta):
    if eta < 0:
        return "neg" + str(abs(eta)).replace(".", "p")
    else:
        return "pos" + str(eta).replace(".", "p")

# Systematics that are safe to apply automatically only to branch-like expressions
# such as "probe_recopt" or "probe_l1pt_over_probe_recopt".
tnp_systematics = ["offlinejes", "offlinejer"]

tnp_variation_suffixes = [
    "OfflineJESUp",
    "OfflineJESDown",
    "OfflineJERUp",
    "OfflineJERDown",
]

# Add eta-sliced features with explicit varied branch names.
# This avoids expressions of the form
#   branch[mask]_OfflineJESUp
# which are invalid in ROOT/RDataFrame.
def add_sliced_tnp_feature_variations(features, name, branch, cut, binning, x_title):
    features.append(
        Feature(name, f"{branch}[{cut}]",
            binning=binning,
            x_title=x_title,
        )
    )

    for syst_suffix in tnp_variation_suffixes:
        features.append(
            Feature(f"{name}_{syst_suffix}", f"{branch}_{syst_suffix}[{cut}]",
                binning=binning,
                x_title=x_title,
            )
        )

# Dijet features
# Do not attach offline JES/JER systematics here because these are L1-only or
# selection/diagnostic features under the fixed nominal selection scheme.
dijet_features = [
    Feature("dphi", "L1Dijet_dphi",
        binning=(70, -3.5, 3.5),
        x_title=("L1Dijet_dphi")       
    ),
    Feature("absdphi", "abs(L1Dijet_dphi)",
        binning=(35, 0, 3.5),
        x_title=("|L1Dijet_dphi|")       
    ),
    Feature("passSelection", "passSelection",
        binning=(2, 0, 2),
        x_title=("passSelection"),
    ),
    Feature("averagePt", "0.5*(L1Jet_pt[0] + L1Jet_pt[1])",
        binning=(100, 0, 100),
        x_title=("(pT,1 + pT,2)*0.5"),
    ),
    Feature("balancePt", "(L1Jet_pt[2])/(0.5*(L1Jet_pt[0] + L1Jet_pt[1]))",
        binning=(50, 0, 1),
        x_title=("pT,3/((pT,1 + pT,2)*0.5)"),
    ),
    Feature("thirdjet_pt", "L1Jet_pt[2]",
        binning=(100, 0, 100),
        x_title=("Third jet pT"),    
    ),
    Feature("thirdjet_pt_pass", "L1Jet_pt[2]",
        binning=(100, 0, 100),
        selection=("(passSelection == true)"),
        x_title=("Third jet pT (pass selection)"),    
    ),
    Feature("thirdjet_pt_fail", "L1Jet_pt[2]",
        binning=(100, 0, 100),
        selection=("(passSelection == false)"),
        x_title=("Third jet pT (fail selection)"),    
    ),
    Feature("thirdjet_eta", "L1Jet_eta[2]",
        binning=(100, -5.0, 5.0),
        x_title=("Third jet eta"),    
    ),
    Feature("thirdjet_eta_pass", "L1Jet_eta[2]",
        binning=(100, -5.0, 5.0),
        selection=("(passSelection == true)"),
        x_title=("Third jet eta (pass selection)"),    
    ),
    Feature("thirdjet_eta_fail", "L1Jet_eta[2]",
        binning=(100, -5.0, 5.0),
        selection=("(passSelection == false)"),
        x_title=("Third jet eta (fail selection)"),    
    ),
    Feature("thirdjet_phi", "L1Jet_phi[2]",
        binning=(62, -3.2, 3.2),
        x_title=("Third jet phi"),    
    ),
    Feature("thirdjet_phi_pass", "L1Jet_phi[2]",
        binning=(62, -3.2, 3.2),
        selection=("(passSelection == true)"),
        x_title=("Third jet phi (pass selection)"),    
    ),
    Feature("thirdjet_phi_fail", "L1Jet_phi[2]",
        binning=(62, -3.2, 3.2),
        selection=("(passSelection == false)"),
        x_title=("Third jet phi (fail selection)"),    
    ),
    Feature("nL1Jet", "nL1Jet",
        binning=(10, 0, 10),
        x_title=("nL1Jet"),
    ),
    Feature("nL1Jet_pass", "nL1Jet",
        binning=(10, 0, 10),
        selection=("(passSelection == true)"),
        x_title=("nL1Jet (pass selection)"),
    ),
    Feature("nL1Jet_fail", "nL1Jet",
        binning=(10, 0, 10),
        selection=("(passSelection == false)"),
        x_title=("nL1Jet (fail selection)"),
    ),
]

# Response features
# Automatic systematics are safe here because the expressions are simple branch names.
response_features = [
    Feature("tag_l1pt", "tag_l1pt",
        binning=(1000, 0, 1000),
        x_title=Label("Tag L1 pT"),
    ),
    Feature("tag_recopt", "tag_recopt",
        binning=(1000, 0, 1000),
        x_title=Label("Tag Reco pT"),
        systematics=tnp_systematics,
    ),
    Feature("tag_l1eta", "tag_l1eta",
        binning=(100, -5.0, 5.0),
        x_title=Label("Tag L1 eta"),
    ),
    Feature("probe_l1pt", "probe_l1pt",
        binning=(1000, 0, 1000),
        x_title=Label("Probe L1 pT"),
    ),
    Feature("probe_recopt", "probe_recopt",
        binning=(1000, 0, 1000),
        x_title=Label("Probe Reco pT"),
        systematics=tnp_systematics,
    ),
    Feature("probe_l1eta", "probe_l1eta",
        binning=(100, -5.0, 5.0),
        x_title=Label("Probe L1 eta"),
    ),
    Feature("probe_l1pt_over_tag_recopt", "probe_l1pt_over_tag_recopt",
        binning=(200, 0.0, 5.0),
        x_title=Label("pT(L1, Probe)/pT(Reco, Tag)"),
        systematics=tnp_systematics,
    ),
    Feature("probe_recopt_over_tag_recopt", "probe_recopt_over_tag_recopt",
        binning=(200, 0.0, 5.0),
        x_title=Label("pT(Reco, Probe)/pT(Reco, Tag)"),
        systematics=tnp_systematics,
    ),
    Feature("probe_l1pt_over_probe_recopt", "probe_l1pt_over_probe_recopt",
        binning=(200, 0.0, 5.0),
        x_title=Label("pT(L1, Probe)/pT(Reco, Probe)"),
        systematics=tnp_systematics,
    ),
]

eta_edges = [-2.5, -2.0, -1.3, -0.5, 0.0, 0.5, 1.3, 2.0, 2.5]

for i_bin in range(len(eta_edges) - 1):
    eta_low = eta_edges[i_bin]
    eta_high = eta_edges[i_bin + 1]
    eta_cut = f"(probe_l1eta >= {eta_low}) && (probe_l1eta < {eta_high})"
    eta_cut_string = f"{convert_eta_float_to_str(eta_low)}to{convert_eta_float_to_str(eta_high)}"

    response_features_i = [
        Feature(f"tag_l1pt_{eta_cut_string}", f"tag_l1pt[{eta_cut}]",
            binning=(1000, 0, 1000),
            x_title=Label("Tag L1 pT"),
        ),
        Feature(f"tag_l1eta_{eta_cut_string}", f"tag_l1eta[{eta_cut}]",
            binning=(100, -5.0, 5.0),
            x_title=Label("Tag L1 eta"),
        ),
        Feature(f"probe_l1pt_{eta_cut_string}", f"probe_l1pt[{eta_cut}]",
            binning=(1000, 0, 1000),
            x_title=Label("Probe L1 pT"),
        ),
        Feature(f"probe_l1eta_{eta_cut_string}", f"probe_l1eta[{eta_cut}]",
            binning=(100, -5.0, 5.0),
            x_title=Label("Probe L1 eta"),
        ),
    ]

    add_sliced_tnp_feature_variations(
        response_features_i,
        f"tag_recopt_{eta_cut_string}",
        "tag_recopt",
        eta_cut,
        (1000, 0, 1000),
        Label("Tag Reco pT"),
    )

    add_sliced_tnp_feature_variations(
        response_features_i,
        f"probe_recopt_{eta_cut_string}",
        "probe_recopt",
        eta_cut,
        (1000, 0, 1000),
        Label("Probe Reco pT"),
    )

    add_sliced_tnp_feature_variations(
        response_features_i,
        f"probe_l1pt_over_tag_recopt_{eta_cut_string}",
        "probe_l1pt_over_tag_recopt",
        eta_cut,
        (200, 0.0, 5.0),
        Label("pT(L1, Probe)/pT(Reco, Tag)"),
    )

    add_sliced_tnp_feature_variations(
        response_features_i,
        f"probe_recopt_over_tag_recopt_{eta_cut_string}",
        "probe_recopt_over_tag_recopt",
        eta_cut,
        (200, 0.0, 5.0),
        Label("pT(Reco, Probe)/pT(Reco, Tag)"),
    )

    add_sliced_tnp_feature_variations(
        response_features_i,
        f"probe_l1pt_over_probe_recopt_{eta_cut_string}",
        "probe_l1pt_over_probe_recopt",
        eta_cut,
        (200, 0.0, 5.0),
        Label("pT(L1, Probe)/pT(Reco, Probe)"),
    )

    response_features += response_features_i

# Inclusive eta slice, implemented in the same explicit way as the eta bins.
response_features_lastbin = [
    Feature(f"tag_l1pt_neg2p5topos2p5", f"tag_l1pt[(probe_l1eta >= -2.5) && (probe_l1eta < 2.5)]",
        binning=(1000, 0, 1000),
        x_title=Label("Tag L1 pT"),
    ),
    Feature(f"tag_l1eta_neg2p5topos2p5", f"tag_l1eta[(probe_l1eta >= -2.5) && (probe_l1eta < 2.5)]",
        binning=(100, -5.0, 5.0),
        x_title=Label("Tag L1 eta"),
    ),
    Feature(f"probe_l1pt_neg2p5topos2p5", f"probe_l1pt[(probe_l1eta >= -2.5) && (probe_l1eta < 2.5)]",
        binning=(1000, 0, 1000),
        x_title=Label("Probe L1 pT"),
    ),
    Feature(f"probe_l1eta_neg2p5topos2p5", f"probe_l1eta[(probe_l1eta >= -2.5) && (probe_l1eta < 2.5)]",
        binning=(100, -5.0, 5.0),
        x_title=Label("Probe L1 eta"),
    ),
]

inclusive_eta_cut = "(probe_l1eta >= -2.5) && (probe_l1eta < 2.5)"

add_sliced_tnp_feature_variations(
    response_features_lastbin,
    "tag_recopt_neg2p5topos2p5",
    "tag_recopt",
    inclusive_eta_cut,
    (1000, 0, 1000),
    Label("Tag Reco pT"),
)

add_sliced_tnp_feature_variations(
    response_features_lastbin,
    "probe_recopt_neg2p5topos2p5",
    "probe_recopt",
    inclusive_eta_cut,
    (1000, 0, 1000),
    Label("Probe Reco pT"),
)

add_sliced_tnp_feature_variations(
    response_features_lastbin,
    "probe_l1pt_over_tag_recopt_neg2p5topos2p5",
    "probe_l1pt_over_tag_recopt",
    inclusive_eta_cut,
    (200, 0.0, 5.0),
    Label("pT(L1, Probe)/pT(Reco, Tag)"),
)

add_sliced_tnp_feature_variations(
    response_features_lastbin,
    "probe_recopt_over_tag_recopt_neg2p5topos2p5",
    "probe_recopt_over_tag_recopt",
    inclusive_eta_cut,
    (200, 0.0, 5.0),
    Label("pT(Reco, Probe)/pT(Reco, Tag)"),
)

add_sliced_tnp_feature_variations(
    response_features_lastbin,
    "probe_l1pt_over_probe_recopt_neg2p5topos2p5",
    "probe_l1pt_over_probe_recopt",
    inclusive_eta_cut,
    (200, 0.0, 5.0),
    Label("pT(L1, Probe)/pT(Reco, Probe)"),
)

features_tnp = dijet_features + response_features + response_features_lastbin
