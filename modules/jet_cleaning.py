# Jet cleaning studies (matching to clean reco jets)
from analysis_tools.utils import import_root
ROOT = import_root()

# Produce jet isolation variables
class L1JetIsolationProducer():
    def __init__(self, *args, **kwargs):
        ROOT.gInterpreter.Declare(
            """
            using Vbool = ROOT::RVec<bool>;
            using Vint = ROOT::RVec<int>;
            using Vfloat = ROOT::RVec<float>;
            using Vdouble = ROOT::RVec<double>;

            auto getCandIso(Vfloat L1Jet_pt, Vfloat L1Jet_eta, Vfloat L1Jet_phi, Vfloat L1Cand_pt, Vfloat L1Cand_eta, Vfloat L1Cand_phi){
                Vfloat CandIsoVector(L1Jet_pt.size(), 0);

                for(size_t i = 0; i < L1Jet_pt.size(); i++){
                    float CandIso = 0;

                    for(size_t j = 0; j < L1Cand_pt.size(); j++){
                        float dEta = L1Jet_eta[i] - L1Cand_eta[j];
                        float dPhi = TVector2::Phi_mpi_pi(L1Jet_phi[i] - L1Cand_phi[j]);
                        float dr = std::sqrt(dEta*dEta + dPhi*dPhi);

                        if (dr < 0.4){
                            CandIso += L1Cand_pt[j];
                        }
                    }
                    CandIsoVector[i] = CandIso/L1Jet_pt[i];
                }
                return CandIsoVector;
            }
        """)

    def run(self, df):
        df = df.Define("L1Jet_EGIso", "getCandIso(L1Jet_pt, L1Jet_eta, L1Jet_phi, L1EG_pt, L1EG_eta, L1EG_phi)")
        df = df.Define("L1Jet_MuIso", "getCandIso(L1Jet_pt, L1Jet_eta, L1Jet_phi, L1Mu_pt, L1Mu_eta, L1Mu_phi)")

        return df, ["L1Jet_EGIso", "L1Jet_MuIso"]

def L1JetIsolation(*args, **kwargs):
    return lambda: L1JetIsolationProducer(*args, **kwargs)

# Match L1 jets to cleaned reco jets
class L1MatchToCleanRecoProducer():
    def __init__(self, *args, **kwargs):
        ROOT.gInterpreter.Declare(
            """
            using Vbool = ROOT::RVec<bool>;
            using Vint = ROOT::RVec<int>;
            using Vfloat = ROOT::RVec<float>;
            using Vdouble = ROOT::RVec<double>;

            auto isMatchedToReco(Vfloat L1_eta, Vfloat L1_phi, Vfloat Reco_eta, Vfloat Reco_phi){
                Vbool isMatched(L1_eta.size(), false);

                for(size_t i = 0; i < L1_eta.size(); ++i){
                    for(size_t j = 0; j < Reco_eta.size(); ++j){
                        float dEta = L1_eta[i] - Reco_eta[j];
                        float dPhi = TVector2::Phi_mpi_pi(L1_phi[i] - Reco_phi[j]);
                        float dr = std::sqrt(dEta*dEta + dPhi*dPhi);

                        if (dr < 0.2){
                            isMatched[i] = true;
                        }
                    }
                }

                return isMatched;
            }                                           
        
        """)

    def run(self, df):
        # Clean reco jets
        df = df.Define("absJetEta", "abs(Jet_eta)")
        df = df.Define("passPFJetID",
            """
            (absJetEta <= 2.6 && Jet_neHEF < 0.90 && Jet_neEmEF < 0.90 && Jet_nConstituents > 1 &&
            Jet_muEF < 0.80 && Jet_chHEF > 0.01 && Jet_chMultiplicity > 0 && Jet_chEmEF < 0.80) ||

            (absJetEta > 2.6 && absJetEta <= 2.7 && Jet_neHEF < 0.90 && Jet_neEmEF < 0.99 &&
            Jet_muEF < 0.80 && Jet_chEmEF < 0.80) ||

            (absJetEta > 2.7 && absJetEta <= 3.0 && Jet_neHEF < 0.9999) ||

            (absJetEta > 3.0 && absJetEta <= 5.0 && Jet_neEmEF < 0.90 && Jet_neMultiplicity > 2)
            """
        )
        df = df.Define('isCleanJet', 'passPFJetID && Jet_muEF < 0.5 && Jet_chEmEF < 0.5')
        # Apply cuts to reco jets
        df = df.Redefine('Jet_pt', 'Jet_pt[isCleanJet]')
        df = df.Redefine('Jet_eta', 'Jet_eta[isCleanJet]')
        df = df.Redefine('Jet_phi', 'Jet_phi[isCleanJet]')

        # Match to reco jets
        df = df.Define("L1Jet_isMatchedToReco", "isMatchedToReco(L1Jet_eta, L1Jet_phi, Jet_eta, Jet_phi)")

        return df, ["L1Jet_isMatchedToReco"]
    

def L1MatchToCleanReco(*args, **kwargs):
    return lambda: L1MatchToCleanRecoProducer(*args, **kwargs)