from analysis_tools import Feature
from plotting_tools import Label

# Encoding function to convert -2.5 to "neg2p5" and 2.5 to "pos2p5"
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

# Response features (binning can be different even if variables are shared with above)
response_features = [
    Feature("pt", "L1Jet_pt",
        binning=(1000, 0, 1000),
        x_title=Label("L1Jet_pt")
    ),
    Feature("eta", "L1Jet_eta",
        binning=(100, -5.0, 5.0),
        x_title=Label("L1Jet_eta")  
    ),
    Feature("phi", "L1Jet_phi",
        binning=(70, -3.5, 3.5),
        x_title=Label("L1Jet_phi")
    ),
    Feature("scale", "L1Jet_scale",
        binning=(200, 0.0, 5.0),
        x_title=Label("L1Jet_scale")
    ),
    Feature("gen_pt", "L1Jet_matchedGenPt",
        binning=(1000, 0, 1000),
        x_title=Label("Matched GenJet_pt")   
    ),
]

eta_edges = [-2.5, -2.0, -1.3, -0.5, 0.0, 0.5, 1.3, 2.0, 2.5]

for i_bin in range(len(eta_edges) - 1):
    eta_low = eta_edges[i_bin]
    eta_high = eta_edges[i_bin + 1]
    eta_cut = f"(L1Jet_eta >= {eta_low}) && (L1Jet_eta < {eta_high})"
    eta_cut_string = f"{convert_eta_float_to_str(eta_low)}to{convert_eta_float_to_str(eta_high)}"

    response_features_i = [
        Feature(f"pt_{eta_cut_string}", f"L1Jet_pt[{eta_cut}]",
            binning=(1000, 0, 1000),
            x_title=Label("L1Jet_pt")
        ),
        Feature(f"eta_{eta_cut_string}", f"L1Jet_eta[{eta_cut}]",
            binning=(100, -5.0, 5.0),
            x_title=Label("L1Jet_eta")  
        ),
        Feature(f"phi_{eta_cut_string}", f"L1Jet_phi[{eta_cut}]",
            binning=(70, -3.5, 3.5),
            x_title=Label("L1Jet_phi")
        ),
        Feature(f"scale_{eta_cut_string}", f"L1Jet_scale[{eta_cut}]",
            binning=(200, 0.0, 5.0),
            x_title=Label("L1Jet_scale")
        ),
        Feature(f"gen_pt_{eta_cut_string}", f"L1Jet_matchedGenPt[{eta_cut}]",
            binning=(1000, 0, 1000),
            x_title=Label("Matched GenJet_pt")   
        ),
    ]
    response_features += response_features_i


eta_low = eta_edges[0]
eta_high = eta_edges[-1]
eta_cut = f"(L1Jet_eta >= {eta_low}) && (L1Jet_eta < {eta_high})"
eta_cut_string = f"{convert_eta_float_to_str(eta_low)}to{convert_eta_float_to_str(eta_high)}"

response_features_lastbin = [
    Feature(f"pt_{eta_cut_string}", f"L1Jet_pt[{eta_cut}]",
        binning=(1000, 0, 1000),
        x_title=Label("L1Jet_pt")
    ),
    Feature(f"eta_{eta_cut_string}", f"L1Jet_eta[{eta_cut}]",
        binning=(100, -5.0, 5.0),
        x_title=Label("L1Jet_eta")  
    ),
    Feature(f"phi_{eta_cut_string}", f"L1Jet_phi[{eta_cut}]",
        binning=(70, -3.5, 3.5),
        x_title=Label("L1Jet_phi")
    ),
    Feature(f"scale_{eta_cut_string}", f"L1Jet_scale[{eta_cut}]",
        binning=(200, 0.0, 5.0),
        x_title=Label("L1Jet_scale")
    ),
    Feature(f"gen_pt_{eta_cut_string}", f"L1Jet_matchedGenPt[{eta_cut}]",
        binning=(1000, 0, 1000),
        x_title=Label("Matched GenJet_pt")   
    ),
]

features_genscale = base_features + response_features + response_features_lastbin