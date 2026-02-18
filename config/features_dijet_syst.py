from analysis_tools import Feature
from plotting_tools import Label

# Encoding function to convert -3.0 to "neg3p0" and 3.0 to "pos3p0"
def convert_eta_float_to_str(eta):
    if eta < 0:
        return "neg" + str(abs(eta)).replace(".", "p")
    else:
        return "pos" + str(eta).replace(".", "p")

base_features = [
    #############
    # Reco JETS #
    #############
    Feature("jet_pt", "Jet_pt",
        binning=(220, 0, 1100),
        x_title=Label("Jet_pt"),
    ),
    Feature("jet_eta", "Jet_eta",
        binning=(60, -3.0, 3.0),
        x_title=Label("Jet_eta"),
    ),
    Feature("jet_phi", "Jet_phi",
        binning=(70, -3.5, 3.5),
        x_title=Label("Jet_phi"),
    ),
    Feature("jet_lead_pt", "Jet_pt[0]",
        binning=(220, 0, 1100),
        x_title=Label("Jet_pt"),
    ),
    Feature("jet_lead_eta", "Jet_eta[0]",
        binning=(60, -3.0, 3.0),
        x_title=Label("Jet_eta"),
    ),
    Feature("jet_lead_phi", "Jet_phi[0]",
        binning=(70, -3.5, 3.5),
        x_title=Label("Jet_phi"),
    ),
    Feature("jet_sublead_pt", "Jet_pt[1]",
        binning=(220, 0, 1100),
        x_title=Label("Jet_pt"),
    ),
    Feature("jet_sublead_eta", "Jet_eta[1]",
        binning=(60, -3.0, 3.0),
        x_title=Label("Jet_eta"),
    ),
    Feature("jet_sublead_phi", "Jet_phi[1]",
        binning=(70, -3.5, 3.5),
        x_title=Label("Jet_phi"),
    ),
    ###########
    # L1 JETS #
    ###########
    Feature("l1jet_pt", "L1Jet_pt",
        binning=(220, 0, 1100),
        x_title=Label("L1Jet_pt"),
    ),
    Feature("l1jet_eta", "L1Jet_eta",
        binning=(60, -3.0, 3.0),
        x_title=Label("L1Jet_eta"),
    ),
    Feature("l1jet_phi", "L1Jet_phi",
        binning=(70, -3.5, 3.5),
        x_title=Label("L1Jet_phi"),
    ),
    Feature("l1jet_lead_pt", "L1Jet_pt[0]",
        binning=(220, 0, 1100),
        x_title=Label("L1Jet_pt"),
    ),
    Feature("l1jet_lead_eta", "L1Jet_eta[0]",
        binning=(60, -3.0, 3.0),
        x_title=Label("L1Jet_eta"),
    ),
    Feature("l1jet_lead_phi", "L1Jet_phi[0]",
        binning=(70, -3.5, 3.5),
        x_title=Label("L1Jet_phi"),
    ),
    Feature("l1jet_sublead_pt", "L1Jet_pt[1]",
        binning=(220, 0, 1100),
        x_title=Label("L1Jet_pt"),
    ),
    Feature("l1jet_sublead_eta", "L1Jet_eta[1]",
        binning=(60, -3.0, 3.0),
        x_title=Label("L1Jet_eta"),
    ),
    Feature("l1jet_sublead_phi", "L1Jet_phi[1]",
        binning=(70, -3.5, 3.5),
        x_title=Label("L1Jet_phi"),
    ),
]

# Response features
response_features = [
    Feature("pt", "MatchedJet_pt",
        binning=(500, 0, 500),
        x_title=Label("MatchedJet_pt")
    ),
    Feature("eta", "MatchedJet_eta",
        binning=(100, -5.0, 5.0),
        x_title=Label("MatchedJet_eta")
    ),
    Feature("phi", "MatchedJet_phi",
        binning=(70, -3.5, 3.5),
        x_title=Label("MatchedJet_phi")
    ),
    Feature("eta", "MatchedJet_eta",
        binning=(100, -5.0, 5.0),
        x_title=Label("MatchedJet_eta")
    ),
    Feature("scale", "MatchedJet_ptScale",
        binning=(50, 0.0, 3.0),
        x_title=Label("MatchedJet_ptScale")
    ),
    Feature("diff", "MatchedJet_ptDiff",
        binning=(100, -100, 100),
        x_title=Label("MatchedJet_ptDiff")
    ),
]

eta_edges = [-3.0, -2.5, -2.0, -1.3, -0.5, 0.0, 0.5, 1.3, 2.0, 2.5, 3.0]

for i_bin in range(len(eta_edges) - 1):
    eta_low = eta_edges[i_bin]
    eta_high = eta_edges[i_bin + 1]
    eta_cut = f"(MatchedJet_eta >= {eta_low}) && (MatchedJet_eta < {eta_high})"
    eta_cut_string = f"{convert_eta_float_to_str(eta_low)}to{convert_eta_float_to_str(eta_high)}"

    response_features_i = [
        Feature(f"pt_{eta_cut_string}", f"MatchedJet_pt[{eta_cut}]",
            binning=(500, 0, 500),
            x_title=Label("MatchedJet_pt")
        ),
        Feature(f"eta_{eta_cut_string}", f"MatchedJet_eta[{eta_cut}]",
            binning=(100, -5.0, 5.0),
            x_title=Label("MatchedJet_eta")
        ),
        Feature(f"phi_{eta_cut_string}", f"MatchedJet_phi[{eta_cut}]",
            binning=(70, -3.5, 3.5),
            x_title=Label("MatchedJet_phi")
        ),
        Feature(f"eta_{eta_cut_string}", f"MatchedJet_eta[{eta_cut}]",
            binning=(100, -5.0, 5.0),
            x_title=Label("MatchedJet_eta")
        ),
        Feature(f"scale_{eta_cut_string}", f"MatchedJet_ptScale[{eta_cut}]",
            binning=(50, 0.0, 3.0),
            x_title=Label("MatchedJet_ptScale")
        ),
        Feature(f"diff_{eta_cut_string}", f"MatchedJet_ptDiff[{eta_cut}]",
            binning=(100, -100, 100),
            x_title=Label("MatchedJet_ptDiff")
        ),
    ]

    response_features += response_features_i

features = base_features + response_features