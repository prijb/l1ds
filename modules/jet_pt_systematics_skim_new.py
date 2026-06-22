# Skim nano ntuples for L1JEC measurement (tag-and-probe approach) 
import os
from analysis_tools.utils import import_root
ROOT = import_root()

## Redefinition of L1 jets

# Basic dijet tag and probe
class DijetTagAndProbeProducer():
    def __init__(self, *args, **kwargs):
        
        self.isMC = kwargs.pop("isMC")
        self.triggerType = kwargs.pop("triggerType")

        if not os.getenv("_DijetTagAndProbe"):
            os.environ["_DijetTagAndProbe"] = "DijetTagAndProbe"
            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;

                // Match L1 to Reco jets
                auto getMatchedPt(Vfloat RefJet_pt, Vfloat RefJet_eta, Vfloat RefJet_phi, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedPt(Jet_eta.size(), -999);
                    Vint matchedRefJetIdx(Jet_eta.size(), -1);

                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        float minDR = 9999;
                        int bestRefJetIdx = -1;

                        for(size_t j = 0; j < RefJet_pt.size(); ++j){
                            if (std::find(matchedRefJetIdx.begin(), matchedRefJetIdx.end(), j) != matchedRefJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RefJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RefJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            
                            if((dr < minDR) && (dr < 0.2)){
                                minDR = dr;
                                matchedPt[i] = RefJet_pt[j];
                                bestRefJetIdx = j;
                            }

                        }
                        matchedRefJetIdx[i] = bestRefJetIdx;
                    }
                    return matchedPt;
                }

                // Apply average pT selection
                auto averageDijetPtSelection(Vfloat Jet_pt){
                    bool passSelection = true;
                    if (Jet_pt.size() > 2){
                        float averageDijetPt = 0.5 * (Jet_pt[0] + Jet_pt[1]);
                        if (Jet_pt[2] >= (0.3 * averageDijetPt)) passSelection = false;
                    }
                    return passSelection;
                }

                // Apply average pT selection (require third jet to be clean)
                auto averageDijetPtSelectionClean(Vfloat Jet_pt, Vfloat Jet_clean){
                    bool passSelection = true;
                    if (Jet_pt.size() > 2){
                        float averageDijetPt = 0.5 * (Jet_pt[0] + Jet_pt[1]);
                        if ((Jet_pt[2] >= (0.3 * averageDijetPt)) && (Jet_clean[2] == true)) passSelection = false;
                    }
                    return passSelection;
                }
            """)

    def run(self, df):
        # Sort both collections by pT
        df = df.Define("Jet_ptorder", "Reverse(Argsort(Jet_pt))")
        df = df.Redefine("Jet_pt", "Take(Jet_pt, Jet_ptorder)")
        df = df.Redefine("Jet_eta", "Take(Jet_eta, Jet_ptorder)")
        df = df.Redefine("Jet_phi", "Take(Jet_phi, Jet_ptorder)")

        df = df.Define( "L1Jet_ptorder", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_ptorder)")

        # Apply basic selections to both collections
        df = df.Filter("nJet > 1").Filter("(Jet_pt[0] > 10.0) && (Jet_pt[1] > 10) && (abs(Jet_eta[0]) < 2.5) && (abs(Jet_eta[1]) < 2.5)")
        df = df.Filter("nL1Jet > 1").Filter("(L1Jet_pt[0] > 10.0) && (L1Jet_pt[1] > 10) && (abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5)")
        df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")

        # Apply jet veto map
        df = df.Filter("(jvm_event_veto == false)")
        
        # Only for Data (require passing Scouting JetHT trigger)
        if not self.isMC:
            if self.triggerType == "DST_PFScouting_JetHT":
                print(f"\nRequiring data to pass trigger {self.triggerType} in Dijet Tag and Probe producer with lead pT > 250 GeV")
                df = df.Filter("DST_PFScouting_JetHT == true").Filter("Jet_pt[0] > 250.0")
            elif self.triggerType == "HLT_PFJet40":
                print(f"\nRequiring data to pass trigger {self.triggerType} in Dijet Tag and Probe producer with lead pT > 70 GeV")
                df = df.Filter("HLT_PFJet40 == true").Filter("Jet_pt[0] > 70.0")
            elif self.triggerType == "HLT_PFJet60":
                print(f"\nRequiring data to pass trigger {self.triggerType} in Dijet Tag and Probe producer with lead pT > 90 GeV")
                df = df.Filter("HLT_PFJet60 == true").Filter("Jet_pt[0] > 90.0")


        # Match L1 jets to reco jets
        df = df.Define("L1Jet_matchedRecoPt", "getMatchedPt(Jet_pt, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Filter("(L1Jet_matchedRecoPt[0] > 0) && (L1Jet_matchedRecoPt[1] > 0)")

        # Dijet selections
        df = df.Define("L1Dijet_dphi", "TVector2::Phi_mpi_pi(L1Jet_phi[0] - L1Jet_phi[1])").Filter("abs(L1Dijet_dphi) > 2.8")
        #df = df.Define("passSelection", "averageDijetPtSelection(L1Jet_pt)").Filter("(passSelection == true)")
        
        # Filter jets to only have those matched to reco and apply average pT selection to third jet
        df = df.Define("L1Jet_matchedToReco", "L1Jet_matchedRecoPt > 0")
        df = df.Redefine("L1Jet_pt", "L1Jet_pt[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_eta", "L1Jet_eta[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_phi", "L1Jet_phi[L1Jet_matchedToReco]")
        df = df.Define("passSelection", "averageDijetPtSelection(L1Jet_pt)").Filter("(passSelection == true)")

        # Version where the third jet is required to be matched to reco to be checked against balance (eliminate noise)
        #df = df.Define("L1Jet_matchedToReco", "L1Jet_matchedRecoPt > 0").Define("passSelection", "averageDijetPtSelectionClean(L1Jet_pt, L1Jet_matchedToReco)").Filter("(passSelection == true)")

        # Create tag and probe pairs 
        df = df.Define("tag_l1pt", "Take(L1Jet_pt, {0, 1})")
        df = df.Define("tag_l1eta", "Take(L1Jet_eta, {0, 1})")
        df = df.Define("tag_recopt", "Take(L1Jet_matchedRecoPt, {0, 1})")
        df = df.Define("probe_l1pt", "Take(L1Jet_pt, {1, 0})")
        df = df.Define("probe_l1eta", "Take(L1Jet_eta, {1, 0})")
        df = df.Define("probe_recopt", "Take(L1Jet_matchedRecoPt, {1, 0})")

        # Define some relevant scale variables
        df = df.Define("probe_l1pt_over_tag_recopt", "probe_l1pt/tag_recopt")
        df = df.Define("probe_recopt_over_tag_recopt", "probe_recopt/tag_recopt")
        df = df.Define("probe_l1pt_over_probe_recopt", "probe_l1pt/probe_recopt")

        return df, ["L1Dijet_dphi", "passSelection", "tag_l1pt", "tag_l1eta", "tag_recopt", "probe_l1pt", "probe_l1eta", "probe_recopt", "probe_l1pt_over_tag_recopt", "probe_recopt_over_tag_recopt", "probe_l1pt_over_probe_recopt"]
    
def DijetTagAndProbe(**kwargs):
    return lambda: DijetTagAndProbeProducer(**kwargs)


# Basic dijet tag and probe
class DijetTagAndProbeNoSelProducer():
    def __init__(self, *args, **kwargs):
        
        self.isMC = kwargs.pop("isMC")
        self.triggerType = kwargs.pop("triggerType")

        if not os.getenv("_DijetTagAndProbe"):
            os.environ["_DijetTagAndProbe"] = "DijetTagAndProbe"
            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;

                // Match L1 to Reco jets
                auto getMatchedPt(Vfloat RefJet_pt, Vfloat RefJet_eta, Vfloat RefJet_phi, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedPt(Jet_eta.size(), -999);
                    Vint matchedRefJetIdx(Jet_eta.size(), -1);

                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        float minDR = 9999;
                        int bestRefJetIdx = -1;

                        for(size_t j = 0; j < RefJet_pt.size(); ++j){
                            if (std::find(matchedRefJetIdx.begin(), matchedRefJetIdx.end(), j) != matchedRefJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RefJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RefJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            
                            if((dr < minDR) && (dr < 0.2)){
                                minDR = dr;
                                matchedPt[i] = RefJet_pt[j];
                                bestRefJetIdx = j;
                            }

                        }
                        matchedRefJetIdx[i] = bestRefJetIdx;
                    }
                    return matchedPt;
                }

                // Apply average pT selection
                auto averageDijetPtSelection(Vfloat Jet_pt){
                    bool passSelection = true;
                    if (Jet_pt.size() > 2){
                        float averageDijetPt = 0.5 * (Jet_pt[0] + Jet_pt[1]);
                        if (Jet_pt[2] >= (0.3 * averageDijetPt)) passSelection = false;
                    }
                    return passSelection;
                }
            """)

    def run(self, df):
        # Sort both collections by pT
        df = df.Define("Jet_ptorder", "Reverse(Argsort(Jet_pt))")
        df = df.Redefine("Jet_pt", "Take(Jet_pt, Jet_ptorder)")
        df = df.Redefine("Jet_eta", "Take(Jet_eta, Jet_ptorder)")
        df = df.Redefine("Jet_phi", "Take(Jet_phi, Jet_ptorder)")

        df = df.Define( "L1Jet_ptorder", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_ptorder)")

        # Apply basic selections to both collections
        df = df.Filter("nJet > 1").Filter("(Jet_pt[0] > 10.0) && (Jet_pt[1] > 10) && (abs(Jet_eta[0]) < 2.5) && (abs(Jet_eta[1]) < 2.5)")
        df = df.Filter("nL1Jet > 1").Filter("(L1Jet_pt[0] > 10.0) && (L1Jet_pt[1] > 10) && (abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5)")
        df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")

        # Only for Data (require passing Scouting JetHT trigger)
        if not self.isMC:
            if self.triggerType == "DST_PFScouting_JetHT":
                print(f"\nRequiring data to pass trigger {self.triggerType} in Dijet Tag and Probe producer with lead pT > 250 GeV")
                df = df.Filter("DST_PFScouting_JetHT == true").Filter("Jet_pt[0] > 250.0")
            elif self.triggerType == "HLT_PFJet40":
                print(f"\nRequiring data to pass trigger {self.triggerType} in Dijet Tag and Probe producer with lead pT > 70 GeV")
                df = df.Filter("HLT_PFJet40 == true").Filter("Jet_pt[0] > 70.0")
            elif self.triggerType == "HLT_PFJet60":
                print(f"\nRequiring data to pass trigger {self.triggerType} in Dijet Tag and Probe producer with lead pT > 90 GeV")
                df = df.Filter("HLT_PFJet60 == true").Filter("Jet_pt[0] > 90.0")


        # Match L1 jets to reco jets
        df = df.Define("L1Jet_matchedRecoPt", "getMatchedPt(Jet_pt, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Filter("(L1Jet_matchedRecoPt[0] > 0) && (L1Jet_matchedRecoPt[1] > 0)")

        # Dijet selections
        df = df.Define("L1Dijet_dphi", "TVector2::Phi_mpi_pi(L1Jet_phi[0] - L1Jet_phi[1])")
        df = df.Define("passSelection", "averageDijetPtSelection(L1Jet_pt)")

        # Create tag and probe pairs 
        df = df.Define("tag_l1pt", "Take(L1Jet_pt, {0, 1})")
        df = df.Define("tag_l1eta", "Take(L1Jet_eta, {0, 1})")
        df = df.Define("tag_recopt", "Take(L1Jet_matchedRecoPt, {0, 1})")
        df = df.Define("probe_l1pt", "Take(L1Jet_pt, {1, 0})")
        df = df.Define("probe_l1eta", "Take(L1Jet_eta, {1, 0})")
        df = df.Define("probe_recopt", "Take(L1Jet_matchedRecoPt, {1, 0})")

        # Define some relevant scale variables
        df = df.Define("probe_l1pt_over_tag_recopt", "probe_l1pt/tag_recopt")
        df = df.Define("probe_recopt_over_tag_recopt", "probe_recopt/tag_recopt")
        df = df.Define("probe_l1pt_over_probe_recopt", "probe_l1pt/probe_recopt")

        return df, ["L1Dijet_dphi", "passSelection", "tag_l1pt", "tag_l1eta", "tag_recopt", "probe_l1pt", "probe_l1eta", "probe_recopt", "probe_l1pt_over_tag_recopt", "probe_recopt_over_tag_recopt", "probe_l1pt_over_probe_recopt"]
    
def DijetTagAndProbeNoSel(**kwargs):
    return lambda: DijetTagAndProbeNoSelProducer(**kwargs)