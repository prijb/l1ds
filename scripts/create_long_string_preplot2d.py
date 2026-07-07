# Long string generation for 2D plots with systematics
def convert_eta_float_to_str(eta):
    if eta < 0:
        return "neg" + str(abs(eta)).replace(".", "p")
    else:
        return "pos" + str(eta).replace(".", "p")


eta_edges = [-2.5, -2.0, -1.3, -0.5, 0.0, 0.5, 1.3, 2.0, 2.5]

# Include nominal plus all explicit variations
variations = [
    "",
    "_OfflineJESUp",
    "_OfflineJESDown",
    "_OfflineJERUp",
    "_OfflineJERDown",
]

# Y-axis variables to plot against tag_recopt
response_vars = [
    "probe_l1pt_over_tag_recopt",
    "probe_recopt_over_tag_recopt",
    "probe_l1pt_over_probe_recopt",
    "probe_l1pt",
]

feature_pairs = []

# Per-eta-bin features
for i_bin in range(len(eta_edges) - 1):
    eta_low = eta_edges[i_bin]
    eta_high = eta_edges[i_bin + 1]
    eta_cut_string = (
        f"{convert_eta_float_to_str(eta_low)}"
        f"to"
        f"{convert_eta_float_to_str(eta_high)}"
    )

    for var in response_vars:
        for syst in variations:
            # Do not add offline JES/JER suffixes to pure L1 variables
            if var == "probe_l1pt" and syst != "":
                continue

            x_name = f"tag_recopt_{eta_cut_string}{syst}"
            y_name = f"{var}_{eta_cut_string}{syst}"

            # For pure L1 y-variable, use nominal y with varied x only if desired.
            # Usually keep only nominal probe_l1pt.
            if var == "probe_l1pt":
                x_name = f"tag_recopt_{eta_cut_string}"
                y_name = f"probe_l1pt_{eta_cut_string}"

            feature_pairs.append(f"{x_name}:{y_name}")


# Inclusive eta bin
inclusive_eta_string = "neg2p5topos2p5"

for var in response_vars:
    for syst in variations:
        if var == "probe_l1pt" and syst != "":
            continue

        x_name = f"tag_recopt_{inclusive_eta_string}{syst}"
        y_name = f"{var}_{inclusive_eta_string}{syst}"

        if var == "probe_l1pt":
            x_name = f"tag_recopt_{inclusive_eta_string}"
            y_name = f"probe_l1pt_{inclusive_eta_string}"

        feature_pairs.append(f"{x_name}:{y_name}")


feature_string = ",".join(feature_pairs)

print(feature_string)