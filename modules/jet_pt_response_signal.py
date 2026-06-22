# Measure the jet pT response for L1 jets as a function of matched reco and gen jets
import os
from analysis_tools.utils import import_root
ROOT = import_root()

class L1MatchToRecoProducer():
    def __init__(self, *args, **kwargs):
        if not os.getenv("_L1MatchToReco"):
            os.environ["_L1MatchToReco"] = "L1MatchToReco"
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

                // Get the matched reference jet quantity
                auto getMatchedQty(Vfloat RefJet_qty, Vfloat RefJet_eta, Vfloat RefJet_phi, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedQty(Jet_eta.size(), -999);
                    Vint matchedRefJetIdx(Jet_eta.size(), -1);

                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        float minDR = 9999;
                        int bestRefJetIdx = -1;

                        for(size_t j = 0; j < RefJet_qty.size(); ++j){
                            if (std::find(matchedRefJetIdx.begin(), matchedRefJetIdx.end(), j) != matchedRefJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RefJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RefJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            
                            if((dr < minDR) && (dr < 0.2)){
                                minDR = dr;
                                matchedQty[i] = RefJet_qty[j];
                                bestRefJetIdx = j;
                            }

                        }
                        matchedRefJetIdx[i] = bestRefJetIdx;
                    }
                    return matchedQty;
                }
                                
            """)

    def run(self, df):
        # Sort L1 jets
        df = df.Define("L1Jet_pt_order", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_pt_order)")


        # Match L1Jets to Offline
        df = df.Define("L1Jet_matchedRecoPt", "getMatchedQty(Jet_pt, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedRecoEta", "getMatchedQty(Jet_eta, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedRecoPhi", "getMatchedQty(Jet_phi, Jet_eta, Jet_phi, L1Jet_eta, L1Jet_phi)")

        # Match L1Jets to Gen
        df = df.Define("L1Jet_matchedGenPt", "getMatchedQty(GenJet_pt, GenJet_eta, GenJet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedGenEta", "getMatchedQty(GenJet_eta, GenJet_eta, GenJet_phi, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedGenPhi", "getMatchedQty(GenJet_phi, GenJet_eta, GenJet_phi, L1Jet_eta, L1Jet_phi)")

        # Also create scale variables
        df = df.Define("L1Jet_recoScale", "L1Jet_pt/L1Jet_matchedRecoPt")
        df = df.Define("L1Jet_genScale", "L1Jet_pt/L1Jet_matchedGenPt")

        return df, ["L1Jet_matchedRecoPt", "L1Jet_matchedRecoEta", "L1Jet_matchedRecoPhi", "L1Jet_matchedGenPt", "L1Jet_matchedGenEta", "L1Jet_matchedGenPhi", "L1Jet_recoScale", "L1Jet_genScale"]

def L1MatchToReco(*args, **kwargs):
    return lambda: L1MatchToRecoProducer(*args, **kwargs)

# Get dijet quantities 
class RecoDijetProducer():
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
        df = df.Define("mjj_reco", "getDijetMass(L1Jet_matchedRecoPt, L1Jet_matchedRecoEta, L1Jet_matchedRecoPhi)")
        df = df.Define("mjj_gen", "getDijetMass(L1Jet_matchedGenPt, L1Jet_matchedGenPt, L1Jet_matchedGenPt)")

        return df, ["mjj_reco", "mjj_gen"]

def RecoDijet(*args, **kwargs):
    return lambda: RecoDijetProducer(*args, **kwargs)