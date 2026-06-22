import os
from analysis_tools.utils import import_root
ROOT = import_root()

class InclusiveDijetSelectionProducer():
    def __init__(self, *args, **kwargs):
        ROOT.gInterpreter.Declare("""
            using Vbool = ROOT::RVec<bool>;
            using Vint = ROOT::RVec<int>;
            using Vfloat = ROOT::RVec<float>;
            using Vdouble = ROOT::RVec<double>;

            auto getDijetMass(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi){
                float mjj = -1;
                if(Jet_pt.size() > 1){
                    ROOT::Math::PtEtaPhiMVector jet1(Jet_pt[0], Jet_eta[0], Jet_phi[0], 0);
                    ROOT::Math::PtEtaPhiMVector jet2(Jet_pt[1], Jet_eta[1], Jet_phi[1], 0);
                    mjj = (jet1 + jet2).M();
                }

                return mjj;
            }

            auto getDijetPt(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi){
                float ptjj = -1;
                if(Jet_pt.size() > 1){
                    ROOT::Math::PtEtaPhiMVector jet1(Jet_pt[0], Jet_eta[0], Jet_phi[0], 0);
                    ROOT::Math::PtEtaPhiMVector jet2(Jet_pt[1], Jet_eta[1], Jet_phi[1], 0);
                    ptjj = (jet1 + jet2).Pt();
                }

                return ptjj;
            }

            auto getDijetDPhi(Vfloat Jet_phi){
                float dijet_dphi = -1;
                if(Jet_phi.size() > 1){
                float dphi = std::abs(TVector2::Phi_mpi_pi(Jet_phi[0] - Jet_phi[1]));  
                dijet_dphi = dphi;             
                }
                return dijet_dphi;
            }
        """)

    def run(self, df):
        df = df.Filter("nL1Jet > 1")

        # Sort jets by pT
        df = df.Define( "L1Jet_pt_order", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_pt_order)")
        
        # Inclusive selection
        df = df.Filter("(L1Jet_pt[0] > 30)").Filter("(L1Jet_pt[1] > 30)")
        df = df.Filter("std::abs(L1Jet_eta[0]) < 2.5").Filter("std::abs(L1Jet_eta[1]) < 2.5") 
        #Event vetoes
        df = df.Filter("Sum(L1Jet_pt == 1023.5)==0", "Saturated jet veto")

        #Define quantities
        df = df.Define("mjj", "getDijetMass(L1Jet_pt, L1Jet_eta, L1Jet_phi)")
        df = df.Define("deta", "std::abs(L1Jet_eta[0] - L1Jet_eta[1])").Define("dphi", "getDijetDPhi(L1Jet_phi)").Define("pt", "getDijetPt(L1Jet_pt, L1Jet_eta, L1Jet_phi)")

        #Further event selections
        df = df.Filter("dphi > 1.047")

        return df, ["mjj", "deta", "dphi", "pt"]

def InclusiveDijetSelection(*args, **kwargs):
    return lambda: InclusiveDijetSelectionProducer(*args, **kwargs)


# Selection for ZB ntuples
class InclusiveDijetSelectionZBProducer():
    def __init__(self, *args, **kwargs):
        ROOT.gInterpreter.Declare("""
            using Vbool = ROOT::RVec<bool>;
            using Vint = ROOT::RVec<int>;
            using Vfloat = ROOT::RVec<float>;
            using Vdouble = ROOT::RVec<double>;

            auto getDijetMass(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi){
                float mjj = -1;
                if(Jet_pt.size() > 1){
                    ROOT::Math::PtEtaPhiMVector jet1(Jet_pt[0], Jet_eta[0], Jet_phi[0], 0);
                    ROOT::Math::PtEtaPhiMVector jet2(Jet_pt[1], Jet_eta[1], Jet_phi[1], 0);
                    mjj = (jet1 + jet2).M();
                }

                return mjj;
            }

            auto getDijetPt(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi){
                float ptjj = -1;
                if(Jet_pt.size() > 1){
                    ROOT::Math::PtEtaPhiMVector jet1(Jet_pt[0], Jet_eta[0], Jet_phi[0], 0);
                    ROOT::Math::PtEtaPhiMVector jet2(Jet_pt[1], Jet_eta[1], Jet_phi[1], 0);
                    ptjj = (jet1 + jet2).Pt();
                }

                return ptjj;
            }

            auto getDijetDPhi(Vfloat Jet_phi){
                float dijet_dphi = -1;
                if(Jet_phi.size() > 1){
                float dphi = std::abs(TVector2::Phi_mpi_pi(Jet_phi[0] - Jet_phi[1]));  
                dijet_dphi = dphi;             
                }
                return dijet_dphi;
            }
        """)
    
    # These selections are common to all denominator events
    def run(self, df):
        df = df.Filter("nL1Jet > 1")

        # Sort jets by pT
        df = df.Define( "L1Jet_pt_order", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_pt_order)")
        
        # Inclusive selection
        #Event vetoes
        df = df.Filter("std::abs(L1Jet_eta[0]) < 2.5").Filter("std::abs(L1Jet_eta[1]) < 2.5") 
        df = df.Filter("Sum(L1Jet_pt == 1023.5)==0", "Saturated jet veto")

        #Define quantities
        df = df.Define("mjj", "getDijetMass(L1Jet_pt, L1Jet_eta, L1Jet_phi)")
        df = df.Define("deta", "std::abs(L1Jet_eta[0] - L1Jet_eta[1])").Define("dphi", "getDijetDPhi(L1Jet_phi)").Define("pt", "getDijetPt(L1Jet_pt, L1Jet_eta, L1Jet_phi)")

        #Further event selections
        df = df.Filter("dphi > 1.047")

        return df, ["mjj", "deta", "dphi", "pt"]
    
def InclusiveDijetSelectionZB(*args, **kwargs):
    return lambda: InclusiveDijetSelectionZBProducer(*args, **kwargs)


############## Matching to offline and gen jets ##########################
class L1MatchToRecoProducer():
    def __init__(self, *args, **kwargs):
        if not os.getenv("_L1Match"):
            os.environ["_L1Match"] = "L1Match"
            ROOT.gInterpreter.Declare(
            """
                using Vbool = ROOT::RVec<bool>;
                using Vint = ROOT::RVec<int>;
                using Vfloat = ROOT::RVec<float>;

                auto getJetEt(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi, Vfloat Jet_mass){
                    Vfloat Jet_et(Jet_pt.size());
                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        ROOT::Math::PtEtaPhiMVector jet(Jet_pt[i], Jet_eta[i], Jet_phi[i], Jet_mass[i]);
                        Jet_et[i] = jet.Et();
                    }
                    return Jet_et;
                }

                // Get the matched reco jet quantity
                auto getMatchedQty(Vfloat RecoJet_qty, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedQty(Jet_eta.size(), -999);
                    Vint matchedRecoJetIdx(Jet_eta.size(), -1);

                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        float minDR = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_qty.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            
                            if((dr < minDR) && (dr < 0.2)){
                                minDR = dr;
                                matchedQty[i] = RecoJet_qty[j];
                                bestRecoJetIdx = j;
                            }

                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedQty;
                }
                                
            """)
    
    def run(self, df):
        
        # Match L1Jets to Offline
        df = df.Define("L1Jet_matchedRecoPt", "getMatchedQty(Jet_pt, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedRecoEta", "getMatchedQty(Jet_eta, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedRecoPhi", "getMatchedQty(Jet_phi, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")

        # Match L1Jets to Gen
        df = df.Define("L1Jet_matchedGenPt", "getMatchedQty(GenJet_pt, GenJet_eta, GenJet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedGenEta", "getMatchedQty(GenJet_eta, GenJet_eta, GenJet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedGenPhi", "getMatchedQty(GenJet_phi, GenJet_eta, GenJet_phi, L1Jet_eta, L1Jet_phi)")

        return df, ["L1Jet_matchedRecoPt", "L1Jet_matchedRecoEta", "L1Jet_matchedRecoPhi", "L1Jet_matchedGenPt", "L1Jet_matchedGenEta", "L1Jet_matchedGenPhi"]
    
def L1MatchToReco(*args, **kwargs):
    return lambda: L1MatchToRecoProducer(*args, **kwargs)

############## Get mjj and scale with respect to offline and gen jets ##########################
# With JECs applied
class InclusiveDijetSelectionRecoCorrProducer():
    def __init__(self, *args, **kwargs):
        ROOT.gInterpreter.Declare(
        """
            using Vbool = ROOT::RVec<bool>;
            using Vint = ROOT::RVec<int>;
            using Vfloat = ROOT::RVec<float>;
            using Vdouble = ROOT::RVec<double>;

            auto getDijetMass(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi){
                float mjj = -1;
                if(Jet_pt.size() > 1){
                    if((Jet_pt[0] > 0) && (Jet_pt[1] > 0)){
                        ROOT::Math::PtEtaPhiMVector jet1(Jet_pt[0], Jet_eta[0], Jet_phi[0], 0);
                        ROOT::Math::PtEtaPhiMVector jet2(Jet_pt[1], Jet_eta[1], Jet_phi[1], 0);
                        mjj = (jet1 + jet2).M();
                    }
                }
                return mjj;
            }
        """)

    def run(self, df):
        # Sort reco and gen jets by pT
        df = df.Define("Jet_pt_order", "Reverse(Argsort(Jet_pt))")
        df = df.Redefine("Jet_pt", "Take(Jet_pt, Jet_pt_order)")
        df = df.Redefine("Jet_eta", "Take(Jet_eta, Jet_pt_order)")
        df = df.Redefine("Jet_phi", "Take(Jet_phi, Jet_pt_order)")

        df = df.Define("GenJet_pt_order", "Reverse(Argsort(GenJet_pt))")
        df = df.Redefine("GenJet_pt", "Take(GenJet_pt, GenJet_pt_order)")
        df = df.Redefine("GenJet_eta", "Take(GenJet_eta, GenJet_pt_order)")
        df = df.Redefine("GenJet_phi", "Take(GenJet_phi, GenJet_pt_order)")

        df = df.Define("mjj_reco", "getDijetMass(Jet_pt, Jet_eta, Jet_phi)")
        df = df.Define("mjj_gen", "getDijetMass(GenJet_pt, GenJet_eta, GenJet_phi)")

        # Also create scale variables
        df = df.Define("L1Jet_recoScale", "L1Jet_pt/L1Jet_matchedRecoPt")
        df = df.Define("L1Jet_recoScaleCorr", "L1Jet_pt_scale_corr_nominal_resolution_smear_nominal/L1Jet_matchedRecoPt")
        df = df.Define("L1Jet_genScale", "L1Jet_pt/L1Jet_matchedGenPt")
        df = df.Define("L1Jet_genScaleCorr", "L1Jet_pt_scale_corr_nominal_resolution_smear_nominal/L1Jet_matchedGenPt")

        return df, ["mjj_reco", "mjj_gen", "L1Jet_recoScale", "L1Jet_recoScaleCorr", "L1Jet_genScale", "L1Jet_genScaleCorr"]
    
def InclusiveDijetSelectionRecoCorr(*args, **kwargs):
    return lambda: InclusiveDijetSelectionRecoCorrProducer(*args, **kwargs)

### Version with no JECs
class InclusiveDijetSelectionRecoProducer():
    def __init__(self, *args, **kwargs):
        ROOT.gInterpreter.Declare(
        """
            using Vbool = ROOT::RVec<bool>;
            using Vint = ROOT::RVec<int>;
            using Vfloat = ROOT::RVec<float>;
            using Vdouble = ROOT::RVec<double>;

            auto getDijetMass(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi){
                float mjj = -1;
                if(Jet_pt.size() > 1){
                    if((Jet_pt[0] > 0) && (Jet_pt[1] > 0)){
                        ROOT::Math::PtEtaPhiMVector jet1(Jet_pt[0], Jet_eta[0], Jet_phi[0], 0);
                        ROOT::Math::PtEtaPhiMVector jet2(Jet_pt[1], Jet_eta[1], Jet_phi[1], 0);
                        mjj = (jet1 + jet2).M();
                    }
                }
                return mjj;
            }
        """)

    def run(self, df):
        # Sort reco and gen jets by pT
        df = df.Define("Jet_pt_order", "Reverse(Argsort(Jet_pt))")
        df = df.Redefine("Jet_pt", "Take(Jet_pt, Jet_pt_order)")
        df = df.Redefine("Jet_eta", "Take(Jet_eta, Jet_pt_order)")
        df = df.Redefine("Jet_phi", "Take(Jet_phi, Jet_pt_order)")

        df = df.Define("GenJet_pt_order", "Reverse(Argsort(GenJet_pt))")
        df = df.Redefine("GenJet_pt", "Take(GenJet_pt, GenJet_pt_order)")
        df = df.Redefine("GenJet_eta", "Take(GenJet_eta, GenJet_pt_order)")
        df = df.Redefine("GenJet_phi", "Take(GenJet_phi, GenJet_pt_order)")

        df = df.Define("mjj_reco", "getDijetMass(Jet_pt, Jet_eta, Jet_phi)")
        df = df.Define("mjj_gen", "getDijetMass(GenJet_pt, GenJet_eta, GenJet_phi)")

        # Also create scale variables
        df = df.Define("L1Jet_recoScale", "L1Jet_pt/L1Jet_matchedRecoPt")
        df = df.Define("L1Jet_genScale", "L1Jet_pt/L1Jet_matchedGenPt")

        return df, ["mjj_reco", "mjj_gen", "L1Jet_recoScale", "L1Jet_genScale"]
    
def InclusiveDijetSelectionReco(*args, **kwargs):
    return lambda: InclusiveDijetSelectionRecoProducer(*args, **kwargs)

### Version without matching (just take leading two jets of each type) #######
class InclusiveDijetSelectionRecoNoMatchProducer():
    def __init__(self, *args, **kwargs):
        ROOT.gInterpreter.Declare(
        """
            using Vbool = ROOT::RVec<bool>;
            using Vint = ROOT::RVec<int>;
            using Vfloat = ROOT::RVec<float>;
            using Vdouble = ROOT::RVec<double>;

            auto getDijetMass(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi){
                float mjj = -1;
                if(Jet_pt.size() > 1){
                    if((Jet_pt[0] > 0) && (Jet_pt[1] > 0)){
                        ROOT::Math::PtEtaPhiMVector jet1(Jet_pt[0], Jet_eta[0], Jet_phi[0], 0);
                        ROOT::Math::PtEtaPhiMVector jet2(Jet_pt[1], Jet_eta[1], Jet_phi[1], 0);
                        mjj = (jet1 + jet2).M();
                    }
                }
                return mjj;
            }
        """)

    def run(self, df):
        # Sort reco and gen jets by pT
        df = df.Define("Jet_pt_order", "Reverse(Argsort(Jet_pt))")
        df = df.Redefine("Jet_pt", "Take(Jet_pt, Jet_pt_order)")
        df = df.Redefine("Jet_eta", "Take(Jet_eta, Jet_pt_order)")
        df = df.Redefine("Jet_phi", "Take(Jet_phi, Jet_pt_order)")

        df = df.Define("GenJet_pt_order", "Reverse(Argsort(GenJet_pt))")
        df = df.Redefine("GenJet_pt", "Take(GenJet_pt, GenJet_pt_order)")
        df = df.Redefine("GenJet_eta", "Take(GenJet_eta, GenJet_pt_order)")
        df = df.Redefine("GenJet_phi", "Take(GenJet_phi, GenJet_pt_order)")

        # Sort L1 jets
        df = df.Define("L1Jet_pt_order", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_pt_order)")

        df = df.Define("mjj_reco", "getDijetMass(Jet_pt, Jet_eta, Jet_phi)")
        df = df.Define("mjj_gen", "getDijetMass(GenJet_pt, GenJet_eta, GenJet_phi)")


        return df, ["mjj_reco", "mjj_gen"]
    
def InclusiveDijetSelectionRecoNoMatch(*args, **kwargs):
    return lambda: InclusiveDijetSelectionRecoNoMatchProducer(*args, **kwargs)
