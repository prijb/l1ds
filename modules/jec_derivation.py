# Script for deriving JECs
import os
from analysis_tools.utils import import_root
ROOT = import_root()

############# L1-Gen response (MC) ##########
class L1GenResponseProducer():
    def __init__(self, *args, **kwargs):

        self.isMC = kwargs.pop("isMC")

        if not os.getenv("_L1GenResponse"):
            os.environ["_L1GenResponse"] = "L1GenResponse"
            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;

                // Match L1 to Gen jets
                auto getMatchedGenPt(Vfloat GenJet_pt, Vfloat GenJet_eta, Vfloat GenJet_phi, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedGenPt(Jet_eta.size(), -999);
                    Vint matchedGenJetIdx(Jet_eta.size(), -1);

                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        float minDR = 9999;
                        int bestGenJetIdx = -1;

                        for(size_t j = 0; j < GenJet_pt.size(); ++j){
                            if (std::find(matchedGenJetIdx.begin(), matchedGenJetIdx.end(), j) != matchedGenJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - GenJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - GenJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            
                            if((dr < minDR) && (dr < 0.2)){
                                minDR = dr;
                                matchedGenPt[i] = GenJet_pt[j];
                                bestGenJetIdx = j;
                            }

                        }
                        matchedGenJetIdx[i] = bestGenJetIdx;
                    }
                    return matchedGenPt;
                }
            """)

    def run(self, df):
        if self.isMC:
            print(f"Deriving L1/Gen scale for MC")
            # Sort L1 collections by pT
            df = df.Define("L1Jet_ptorder", "Reverse(Argsort(L1Jet_pt))")
            df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_ptorder)")
            df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_ptorder)")
            df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_ptorder)")

            # Apply basic selections
            df = df.Filter("nL1Jet > 0").Filter("nGenJet > 0")
            df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")
            df = df.Filter("(jvm_event_veto == false)")

            # Apply basic skims to jets
            df = df.Define("L1Jet_sel", "(L1Jet_pt > 10) && (abs(L1Jet_eta) < 2.5)")
            df = df.Redefine("L1Jet_pt", "L1Jet_pt[L1Jet_sel]")
            df = df.Redefine("L1Jet_eta", "L1Jet_eta[L1Jet_sel]")
            df = df.Redefine("L1Jet_phi", "L1Jet_phi[L1Jet_sel]")

            # Match to gen jets
            df = df.Define("L1Jet_matchedGenPt", "getMatchedGenPt(GenJet_pt, GenJet_eta, GenJet_phi, L1Jet_eta, L1Jet_phi)")
            df = df.Redefine("L1Jet_pt", "L1Jet_pt[(L1Jet_matchedGenPt > 0)]")
            df = df.Redefine("L1Jet_eta", "L1Jet_eta[(L1Jet_matchedGenPt > 0)]")
            df = df.Redefine("L1Jet_phi", "L1Jet_phi[(L1Jet_matchedGenPt > 0)]")
            df = df.Redefine("L1Jet_matchedGenPt", "L1Jet_matchedGenPt[(L1Jet_matchedGenPt > 0)]")
            df = df.Filter("(L1Jet_pt.size() > 0)")

            # Create scale quantities
            df = df.Define("L1Jet_scale", "L1Jet_pt/L1Jet_matchedGenPt")

            return df, ["L1Jet_matchedGenPt", "L1Jet_scale"]

        else:
            print(f"Skipping L1/Gen scale for data")
            return df, []

def L1GenResponse(**kwargs):
    return lambda: L1GenResponseProducer(**kwargs)

############# L1-Reco with dijet tag-and-probe (Data and MC) ##########

class L1RecoDijetTnPProducer():
    def __init__(self, *args, **kwargs):
        
        self.isMC = kwargs.pop("isMC")
        self.triggerType = kwargs.pop("triggerType")

        if not os.getenv("_L1RecoDijetTnP"):
            os.environ["_L1RecoDijetTnP"] = "L1RecoDijetTnP"
            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;

                // Match L1 to Reco jets
                auto getMatchedRecoPt(Vfloat RecoJet_pt, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedRecoPt(Jet_eta.size(), -999);
                    Vint matchedRecoJetIdx(Jet_eta.size(), -1);

                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        float minDR = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_pt.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            
                            if((dr < minDR) && (dr < 0.2)){
                                minDR = dr;
                                matchedRecoPt[i] = RecoJet_pt[j];
                                bestRecoJetIdx = j;
                            }

                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedRecoPt;
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
        df = df.Define("L1Jet_matchedRecoPt", "getMatchedRecoPt(Jet_pt, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Filter("(L1Jet_matchedRecoPt[0] > 0) && (L1Jet_matchedRecoPt[1] > 0)")

        # Dijet selections
        df = df.Define("L1Dijet_dphi", "TVector2::Phi_mpi_pi(L1Jet_phi[0] - L1Jet_phi[1])").Filter("abs(L1Dijet_dphi) > 2.8")
        
        # Filter jets to only have those matched to reco and apply average pT selection to third jet to eliminate noise
        df = df.Define("L1Jet_matchedToReco", "L1Jet_matchedRecoPt > 0")
        df = df.Redefine("L1Jet_pt", "L1Jet_pt[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_eta", "L1Jet_eta[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_phi", "L1Jet_phi[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_matchedRecoPt", "L1Jet_matchedRecoPt[L1Jet_matchedToReco]")
        df = df.Define("passSelection", "averageDijetPtSelection(L1Jet_pt)").Filter("(passSelection == true)")

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
    
def L1RecoDijetTnP(**kwargs):
    return lambda: L1RecoDijetTnPProducer(**kwargs)

### With systematic variations
class L1RecoDijetTnPSystProducer():
    def __init__(self, *args, **kwargs):
        
        self.isMC = kwargs.pop("isMC")
        self.triggerType = kwargs.pop("triggerType")

        if not os.getenv("_L1RecoDijetTnP"):
            os.environ["_L1RecoDijetTnP"] = "L1RecoDijetTnP"
            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;

                // Match L1 jets to nominal reco jets and return matched reco index.
                // The index can then be used to retrieve nominal/JES/JER varied reco pT.
                auto getMatchedRecoIdx(
                    Vfloat RecoJet_pt,
                    Vfloat RecoJet_eta,
                    Vfloat RecoJet_phi,
                    Vfloat Jet_eta,
                    Vfloat Jet_phi
                ){
                    Vint matchedRecoJetIdx(Jet_eta.size(), -1);
                    Vint usedRecoJetIdx;

                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        float minDR = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_pt.size(); ++j){
                            if (std::find(usedRecoJetIdx.begin(), usedRecoJetIdx.end(), j) != usedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            
                            if((dr < minDR) && (dr < 0.2)){
                                minDR = dr;
                                bestRecoJetIdx = j;
                            }
                        }

                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                        if(bestRecoJetIdx >= 0) usedRecoJetIdx.push_back(bestRecoJetIdx);
                    }

                    return matchedRecoJetIdx;
                }

                // Extract reco pT from a chosen reco-pT collection using matched reco indices.
                auto getMatchedRecoPtFromIdx(Vfloat RecoJet_pt, Vint matchedRecoJetIdx){
                    Vfloat matchedRecoPt;

                    for(size_t i = 0; i < matchedRecoJetIdx.size(); ++i){
                        int idx = matchedRecoJetIdx[i];

                        if(idx >= 0 && idx < int(RecoJet_pt.size())){
                            matchedRecoPt.push_back(RecoJet_pt[idx]);
                        }
                        else{
                            matchedRecoPt.push_back(-999.0);
                        }
                    }

                    return matchedRecoPt;
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
        # Sort reco collection by nominal corrected pT.
        # Important: sort all reco systematic pT branches with the same nominal ordering.
        df = df.Define("Jet_ptorder", "Reverse(Argsort(Jet_pt))")

        df = df.Redefine("Jet_pt", "Take(Jet_pt, Jet_ptorder)")
        df = df.Redefine("Jet_eta", "Take(Jet_eta, Jet_ptorder)")
        df = df.Redefine("Jet_phi", "Take(Jet_phi, Jet_ptorder)")

        df = df.Redefine("Jet_pt_OfflineJESUp", "Take(Jet_pt_OfflineJESUp, Jet_ptorder)")
        df = df.Redefine("Jet_pt_OfflineJESDown", "Take(Jet_pt_OfflineJESDown, Jet_ptorder)")
        df = df.Redefine("Jet_pt_OfflineJERUp", "Take(Jet_pt_OfflineJERUp, Jet_ptorder)")
        df = df.Redefine("Jet_pt_OfflineJERDown", "Take(Jet_pt_OfflineJERDown, Jet_ptorder)")

        # Sort L1 collection by pT
        df = df.Define("L1Jet_ptorder", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_ptorder)")

        # Apply basic selections to nominal reco and L1 collections
        df = df.Filter("nJet > 1")
        df = df.Filter("(Jet_pt[0] > 10.0) && (Jet_pt[1] > 10.0) && (abs(Jet_eta[0]) < 2.5) && (abs(Jet_eta[1]) < 2.5)")

        df = df.Filter("nL1Jet > 1")
        df = df.Filter("(L1Jet_pt[0] > 10.0) && (L1Jet_pt[1] > 10.0) && (abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5)")

        df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")
        df = df.Filter("(jvm_event_veto == false)")
        
        # Only for data: require passing Scouting/HLT Jet trigger
        if not self.isMC:
            if self.triggerType == "DST_PFScouting_JetHT":
                print(f"\nRequiring data to pass trigger {self.triggerType} in Dijet Tag and Probe producer with lead pT > 250 GeV")
                df = df.Filter("DST_PFScouting_JetHT == true")
                df = df.Filter("Jet_pt[0] > 250.0")

            elif self.triggerType == "HLT_PFJet40":
                print(f"\nRequiring data to pass trigger {self.triggerType} in Dijet Tag and Probe producer with lead pT > 70 GeV")
                df = df.Filter("HLT_PFJet40 == true")
                df = df.Filter("Jet_pt[0] > 70.0")

            elif self.triggerType == "HLT_PFJet60":
                print(f"\nRequiring data to pass trigger {self.triggerType} in Dijet Tag and Probe producer with lead pT > 90 GeV")
                df = df.Filter("HLT_PFJet60 == true")
                df = df.Filter("Jet_pt[0] > 90.0")

        # Match L1 jets to nominal reco jets once (get idx instead of pT to reuse for systematic variations)
        df = df.Define("L1Jet_matchedRecoIdx","getMatchedRecoIdx(Jet_pt, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")
        
        # Nominal matched reco pT
        df = df.Define("L1Jet_matchedRecoPt", "getMatchedRecoPtFromIdx(Jet_pt, L1Jet_matchedRecoIdx)")
        # Offline JES-varied matched reco pT
        df = df.Define("L1Jet_matchedRecoPt_OfflineJESUp", "getMatchedRecoPtFromIdx(Jet_pt_OfflineJESUp, L1Jet_matchedRecoIdx)")
        df = df.Define("L1Jet_matchedRecoPt_OfflineJESDown", "getMatchedRecoPtFromIdx(Jet_pt_OfflineJESDown, L1Jet_matchedRecoIdx)")
        # Offline JER-varied matched reco pT
        df = df.Define("L1Jet_matchedRecoPt_OfflineJERUp", "getMatchedRecoPtFromIdx(Jet_pt_OfflineJERUp, L1Jet_matchedRecoIdx)")
        df = df.Define("L1Jet_matchedRecoPt_OfflineJERDown", "getMatchedRecoPtFromIdx(Jet_pt_OfflineJERDown, L1Jet_matchedRecoIdx)")

        # Require leading two L1 jets to have nominal reco matches
        df = df.Filter("(L1Jet_matchedRecoPt[0] > 0) && (L1Jet_matchedRecoPt[1] > 0)")
        # Dijet selections
        df = df.Define("L1Dijet_dphi", "TVector2::Phi_mpi_pi(L1Jet_phi[0] - L1Jet_phi[1])")
        df = df.Filter("abs(L1Dijet_dphi) > 2.8")
        
        # Filter L1 jets to only those matched to nominal reco jets
        df = df.Define("L1Jet_matchedToReco", "L1Jet_matchedRecoPt > 0")
        df = df.Redefine("L1Jet_pt", "L1Jet_pt[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_eta", "L1Jet_eta[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_phi", "L1Jet_phi[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_matchedRecoIdx", "L1Jet_matchedRecoIdx[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_matchedRecoPt", "L1Jet_matchedRecoPt[L1Jet_matchedToReco]")
        # Variations
        df = df.Redefine("L1Jet_matchedRecoPt_OfflineJESUp", "L1Jet_matchedRecoPt_OfflineJESUp[L1Jet_matchedToReco]" )
        df = df.Redefine("L1Jet_matchedRecoPt_OfflineJESDown", "L1Jet_matchedRecoPt_OfflineJESDown[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_matchedRecoPt_OfflineJERUp", "L1Jet_matchedRecoPt_OfflineJERUp[L1Jet_matchedToReco]")
        df = df.Redefine("L1Jet_matchedRecoPt_OfflineJERDown", "L1Jet_matchedRecoPt_OfflineJERDown[L1Jet_matchedToReco]")

        # Third-jet veto on matched L1 collection
        df = df.Define("passSelection", "averageDijetPtSelection(L1Jet_pt)")
        df = df.Filter("(passSelection == true)")

        # Create nominal tag and probe pairs 
        df = df.Define("tag_l1pt", "Take(L1Jet_pt, {0, 1})")
        df = df.Define("tag_l1eta", "Take(L1Jet_eta, {0, 1})")
        df = df.Define("tag_recopt", "Take(L1Jet_matchedRecoPt, {0, 1})")
        df = df.Define("probe_l1pt", "Take(L1Jet_pt, {1, 0})")
        df = df.Define("probe_l1eta", "Take(L1Jet_eta, {1, 0})")
        df = df.Define("probe_recopt", "Take(L1Jet_matchedRecoPt, {1, 0})")
        # Create OfflineJES varied tag/probe reco pT branches
        df = df.Define("tag_recopt_OfflineJESUp", "Take(L1Jet_matchedRecoPt_OfflineJESUp, {0, 1})")
        df = df.Define("tag_recopt_OfflineJESDown", "Take(L1Jet_matchedRecoPt_OfflineJESDown, {0, 1})")
        df = df.Define("probe_recopt_OfflineJESUp", "Take(L1Jet_matchedRecoPt_OfflineJESUp, {1, 0})")
        df = df.Define("probe_recopt_OfflineJESDown", "Take(L1Jet_matchedRecoPt_OfflineJESDown, {1, 0})")
        # Create OfflineJER varied tag/probe reco pT branches
        df = df.Define("tag_recopt_OfflineJERUp", "Take(L1Jet_matchedRecoPt_OfflineJERUp, {0, 1})")
        df = df.Define("tag_recopt_OfflineJERDown", "Take(L1Jet_matchedRecoPt_OfflineJERDown, {0, 1})")
        df = df.Define("probe_recopt_OfflineJERUp", "Take(L1Jet_matchedRecoPt_OfflineJERUp, {1, 0})")
        df = df.Define("probe_recopt_OfflineJERDown", "Take(L1Jet_matchedRecoPt_OfflineJERDown, {1, 0})")

        # Nominal scale variables
        df = df.Define("probe_l1pt_over_tag_recopt", "probe_l1pt / tag_recopt")
        df = df.Define("probe_recopt_over_tag_recopt", "probe_recopt / tag_recopt")
        df = df.Define("probe_l1pt_over_probe_recopt", "probe_l1pt / probe_recopt")
        # OfflineJES varied direct response
        df = df.Define("probe_l1pt_over_probe_recopt_OfflineJESUp", "probe_l1pt / probe_recopt_OfflineJESUp")
        df = df.Define("probe_l1pt_over_probe_recopt_OfflineJESDown", "probe_l1pt / probe_recopt_OfflineJESDown")
        # OfflineJER varied direct response
        df = df.Define("probe_l1pt_over_probe_recopt_OfflineJERUp", "probe_l1pt / probe_recopt_OfflineJERUp")
        df = df.Define("probe_l1pt_over_probe_recopt_OfflineJERDown", "probe_l1pt / probe_recopt_OfflineJERDown")
        # OfflineJES varied balance 
        df = df.Define("probe_l1pt_over_tag_recopt_OfflineJESUp", "probe_l1pt / tag_recopt_OfflineJESUp")
        df = df.Define("probe_l1pt_over_tag_recopt_OfflineJESDown", "probe_l1pt / tag_recopt_OfflineJESDown")
        df = df.Define("probe_recopt_over_tag_recopt_OfflineJESUp", "probe_recopt_OfflineJESUp / tag_recopt_OfflineJESUp")
        df = df.Define("probe_recopt_over_tag_recopt_OfflineJESDown", "probe_recopt_OfflineJESDown / tag_recopt_OfflineJESDown")
        # OfflineJER varied balance-style components
        df = df.Define("probe_l1pt_over_tag_recopt_OfflineJERUp", "probe_l1pt / tag_recopt_OfflineJERUp")
        df = df.Define("probe_l1pt_over_tag_recopt_OfflineJERDown", "probe_l1pt / tag_recopt_OfflineJERDown")
        df = df.Define("probe_recopt_over_tag_recopt_OfflineJERUp", "probe_recopt_OfflineJERUp / tag_recopt_OfflineJERUp")
        df = df.Define("probe_recopt_over_tag_recopt_OfflineJERDown", "probe_recopt_OfflineJERDown / tag_recopt_OfflineJERDown")

        branches = [
            "L1Dijet_dphi",
            "passSelection",
            "tag_l1pt",
            "tag_l1eta",
            "tag_recopt",
            "probe_l1pt",
            "probe_l1eta",
            "probe_recopt",
            "tag_recopt_OfflineJESUp",
            "tag_recopt_OfflineJESDown",
            "probe_recopt_OfflineJESUp",
            "probe_recopt_OfflineJESDown",
            "tag_recopt_OfflineJERUp",
            "tag_recopt_OfflineJERDown",
            "probe_recopt_OfflineJERUp",
            "probe_recopt_OfflineJERDown",
            "probe_l1pt_over_tag_recopt",
            "probe_recopt_over_tag_recopt",
            "probe_l1pt_over_probe_recopt",
            "probe_l1pt_over_probe_recopt_OfflineJESUp",
            "probe_l1pt_over_probe_recopt_OfflineJESDown",
            "probe_l1pt_over_probe_recopt_OfflineJERUp",
            "probe_l1pt_over_probe_recopt_OfflineJERDown",
            "probe_l1pt_over_tag_recopt_OfflineJESUp",
            "probe_l1pt_over_tag_recopt_OfflineJESDown",
            "probe_recopt_over_tag_recopt_OfflineJESUp",
            "probe_recopt_over_tag_recopt_OfflineJESDown",
            "probe_l1pt_over_tag_recopt_OfflineJERUp",
            "probe_l1pt_over_tag_recopt_OfflineJERDown",
            "probe_recopt_over_tag_recopt_OfflineJERUp",
            "probe_recopt_over_tag_recopt_OfflineJERDown",
        ]

        return df, branches
    
def L1RecoDijetTnPSyst(**kwargs):
    return lambda: L1RecoDijetTnPSystProducer(**kwargs)