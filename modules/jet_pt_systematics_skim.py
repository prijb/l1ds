# Skim nano ntuples for L1 JEC measurement
import os
from analysis_tools.utils import import_root
ROOT = import_root()

# Redefinition of jets after applying JES
class PostJESRedefinitionProducer():
    def __init__(self, *args, **kwargs):
        self.isMC = kwargs.pop("isMC")
    
    def run(self, df):
        # Redefine the L1Jet quantities
        df = df.Redefine("L1Jet_pt", "L1Jet_pt_scale_corr_nominal")
        df = df.Redefine("L1Jet_eta", "L1Jet_eta_scale_corr_nominal")
        df = df.Redefine("L1Jet_phi", "L1Jet_phi_scale_corr_nominal")

        return df, []

def PostJESRedefinition(*args, **kwargs):
    return lambda: PostJESRedefinitionProducer(*args, **kwargs)


# Redefinition of jets after applying JES and JER
class PostJESJERRedefinitionProducer():
    def __init__(self, *args, **kwargs):
        self.isMC = kwargs.pop("isMC")
    
    def run(self, df):
        # Redefine the L1Jet quantities
        df = df.Redefine("L1Jet_pt", "L1Jet_pt_scale_corr_nominal_resolution_smear_nominal")
        df = df.Redefine("L1Jet_eta", "L1Jet_eta_scale_corr_nominal_resolution_smear_nominal")
        df = df.Redefine("L1Jet_phi", "L1Jet_phi_scale_corr_nominal_resolution_smear_nominal")

        return df, []

def PostJESJERRedefinition(*args, **kwargs):
    return lambda: PostJESJERRedefinitionProducer(*args, **kwargs)

# MuonJet method of extracting L1 response
class MuonJetProducer():
    def __init__(self, *args, **kwargs):
        # Preprocess function call
        if not os.getenv("_MuonJet"):
            os.environ["_MuonJet"] = "MuonJet"
            ROOT.gInterpreter.Declare("""
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

                // Get the matched reco jet eT
                auto getMatchedPt(Vfloat RecoJet_et, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedPt(Jet_pt.size(), -1);
                    Vint matchedRecoJetIdx(Jet_pt.size(), -1);

                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        float minDR = 9999;
                        // Doing minDPT instead
                        float minDPT = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_et.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            float dpt = std::abs(Jet_pt[i] - RecoJet_et[j])/RecoJet_et[j];
                            
                            //if((dr < minDR) && (dr < 0.2)){
                            //    minDR = dr;
                            //    matchedPt[i] = RecoJet_et[j];
                            //    bestRecoJetIdx = j;
                            //}

                            // Using dPT matching instead of dR matching
                            if((dpt < minDPT) && (dr < 0.2)){
                                minDPT = dpt;
                                matchedPt[i] = RecoJet_et[j];
                                bestRecoJetIdx = j;
                            }
                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedPt;
                }
                                    
                // Get the matched reco jet eta
                auto getMatchedEta(Vfloat RecoJet_et, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedEta(Jet_pt.size(), -1);
                    Vint matchedRecoJetIdx(Jet_pt.size(), -1);

                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        float minDR = 9999;
                        // Doing minDPT instead
                        float minDPT = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_eta.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            float dpt = std::abs(Jet_pt[i] - RecoJet_et[j])/RecoJet_et[j];

                            //if((dr < minDR) && (dr < 0.2)){
                            //    minDR = dr;
                            //    matchedEta[i] = RecoJet_eta[j];
                            //    bestRecoJetIdx = j;
                            //}

                            // Using dPT matching instead of dR matching
                            if((dpt < minDPT) && (dr < 0.2)){
                                minDPT = dpt;
                                matchedEta[i] = RecoJet_eta[j];
                                bestRecoJetIdx = j;
                            }
                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedEta;
                }

                // Get dR of nearest offline muon
                auto getdRNearestMuon(Vfloat Jet_eta, Vfloat Jet_phi, Vfloat Muon_eta, Vfloat Muon_phi) {
                    Vfloat dRNearestMuon(Jet_eta.size(), 9999);
                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        for(size_t j = 0; j < Muon_eta.size(); ++j){
                            float dEta = Jet_eta[i] - Muon_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - Muon_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            if (dr < dRNearestMuon[i]){
                                dRNearestMuon[i] = dr;
                            }
                        }
                    }    
                    return dRNearestMuon;                     
                }
                                    
                // Pick at most two indicies
                auto getLeadingIndices(Vfloat Jet_pt){
                    Vint LeadingIndices;
                    
                    int idx = 0;
                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        if (idx > 1) break;
                        LeadingIndices.push_back(idx);
                        idx++;
                    }

                    return LeadingIndices;
                }
            """)

    def run(self, df):

        # Event selection (skimming)
        df = df.Filter("HLT_IsoMu24").Filter("nL1Jet > 0").Filter("nJet > 0")
        # Muon pre-selections (akin to MuonJet JEC derivation)
        df = df.Define('Muon_PassTightId','Muon_pfIsoId>=3&&Muon_mediumPromptId')
        df = df.Define('goodmuonPt25','Muon_pt>25&&abs(Muon_pdgId)==13&&Muon_PassTightId')
        df = df.Filter('Sum(goodmuonPt25)>=1','>=1 muon with p_{T}>25 GeV')
        df = df.Define('badmuonPt10','Muon_pt>10&&abs(Muon_pdgId)==13&&Muon_PassTightId==0')
        df = df.Filter('Sum(badmuonPt10)==0','No bad quality muon')

        # RecoJet cleaning (optional)
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
        # Apply cuts to jets
        df = df.Redefine('Jet_pt', 'Jet_pt[isCleanJet]')
        df = df.Redefine('Jet_eta', 'Jet_eta[isCleanJet]')
        df = df.Redefine('Jet_phi', 'Jet_phi[isCleanJet]')

        # Sort jets by pT
        df = df.Define( "L1Jet_ptorder", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_ptorder)")

        # Basic event selection
        #df = df.Filter("nL1Jet > 1").Filter("(L1Jet_pt[0] >= 20) && (L1Jet_pt[1] >= 20)").Filter("std::abs(L1Jet_eta[0]) < 3.0 && std::abs(L1Jet_eta[1]) < 3.0")
        df = df.Filter("(L1Jet_pt[0] >= 20)").Filter("std::abs(L1Jet_eta[0]) < 3.0")
        df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")

        # Get the leading jets
        df = df.Define("L1Jet_leadingindices", "getLeadingIndices(L1Jet_pt)")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_leadingindices)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_leadingindices)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_leadingindices)")

        # Skim out all the jets
        df = df.Define("L1Jet_skim", "(L1Jet_pt >= 20) && (abs(L1Jet_eta) < 3.0)")
        df = df.Redefine("L1Jet_pt", "L1Jet_pt[L1Jet_skim]").Redefine("L1Jet_eta", "L1Jet_eta[L1Jet_skim]").Redefine("L1Jet_phi", "L1Jet_phi[L1Jet_skim]")

        # Define quantities
        df = df.Define("Jet_et", "getJetEt(Jet_pt, Jet_eta, Jet_phi, Jet_mass)") 
        df = df.Define("L1Jet_matchedRecoPt", "getMatchedPt(Jet_pt, Jet_eta, Jet_phi, L1Jet_pt, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedRecoEta", "getMatchedEta(Jet_pt, Jet_eta, Jet_phi, L1Jet_pt, L1Jet_eta, L1Jet_phi)")

        # Filter L1 jets to only those that have matches
        df = df.Define("L1Jet_isMatched", "L1Jet_matchedRecoPt > 0")
        df = df.Define("MatchedJet_pt", "L1Jet_pt[L1Jet_isMatched]")
        df = df.Define("MatchedJet_eta", "L1Jet_eta[L1Jet_isMatched]")
        df = df.Define("MatchedJet_phi", "L1Jet_phi[L1Jet_isMatched]")
        df = df.Define("MatchedJet_matchedRecoPt", "L1Jet_matchedRecoPt[L1Jet_isMatched]")
        df = df.Define("MatchedJet_matchedRecoEta", "L1Jet_matchedRecoEta[L1Jet_isMatched]")
        df = df.Define("MatchedJet_ptDiff", "MatchedJet_pt - MatchedJet_matchedRecoPt")
        df = df.Define("MatchedJet_ptScale", "MatchedJet_pt / MatchedJet_matchedRecoPt")

        return df, ["MatchedJet_pt", "MatchedJet_eta", "MatchedJet_phi", "MatchedJet_matchedRecoPt", "MatchedJet_matchedRecoEta", "MatchedJet_ptDiff", "MatchedJet_ptScale"] 
    
def MuonJet(**kwargs):
    return lambda: MuonJetProducer(**kwargs)
   
# After applying just JES
class MuonJetScaleProducer():
    def __init__(self, *args, **kwargs):
        # Preprocess function call
        if not os.getenv("_MuonJet"):
            os.environ["_MuonJet"] = "MuonJet"
            ROOT.gInterpreter.Declare("""
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

                // Get the matched reco jet eT
                auto getMatchedPt(Vfloat RecoJet_et, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedPt(Jet_pt.size(), -1);
                    Vint matchedRecoJetIdx(Jet_pt.size(), -1);

                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        float minDR = 9999;
                        // Doing minDPT instead
                        float minDPT = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_et.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            float dpt = std::abs(Jet_pt[i] - RecoJet_et[j])/RecoJet_et[j];
                            
                            //if((dr < minDR) && (dr < 0.2)){
                            //    minDR = dr;
                            //    matchedPt[i] = RecoJet_et[j];
                            //    bestRecoJetIdx = j;
                            //}

                            // Using dPT matching instead of dR matching
                            if((dpt < minDPT) && (dr < 0.2)){
                                minDPT = dpt;
                                matchedPt[i] = RecoJet_et[j];
                                bestRecoJetIdx = j;
                            }
                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedPt;
                }
                                    
                // Get the matched reco jet eta
                auto getMatchedEta(Vfloat RecoJet_et, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedEta(Jet_pt.size(), -1);
                    Vint matchedRecoJetIdx(Jet_pt.size(), -1);

                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        float minDR = 9999;
                        // Doing minDPT instead
                        float minDPT = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_eta.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            float dpt = std::abs(Jet_pt[i] - RecoJet_et[j])/RecoJet_et[j];

                            //if((dr < minDR) && (dr < 0.2)){
                            //    minDR = dr;
                            //    matchedEta[i] = RecoJet_eta[j];
                            //    bestRecoJetIdx = j;
                            //}

                            // Using dPT matching instead of dR matching
                            if((dpt < minDPT) && (dr < 0.2)){
                                minDPT = dpt;
                                matchedEta[i] = RecoJet_eta[j];
                                bestRecoJetIdx = j;
                            }
                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedEta;
                }

                // Get dR of nearest offline muon
                auto getdRNearestMuon(Vfloat Jet_eta, Vfloat Jet_phi, Vfloat Muon_eta, Vfloat Muon_phi) {
                    Vfloat dRNearestMuon(Jet_eta.size(), 9999);
                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        for(size_t j = 0; j < Muon_eta.size(); ++j){
                            float dEta = Jet_eta[i] - Muon_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - Muon_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            if (dr < dRNearestMuon[i]){
                                dRNearestMuon[i] = dr;
                            }
                        }
                    }    
                    return dRNearestMuon;                     
                }
                                    
                // Pick at most two indicies
                auto getLeadingIndices(Vfloat Jet_pt){
                    Vint LeadingIndices;
                    
                    int idx = 0;
                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        if (idx > 1) break;
                        LeadingIndices.push_back(idx);
                        idx++;
                    }

                    return LeadingIndices;
                }
            """)

    def run(self, df):

        # Event selection (skimming)
        df = df.Filter("HLT_IsoMu24").Filter("nL1Jet > 0").Filter("nJet > 0")
        # Muon pre-selections (akin to MuonJet JEC derivation)
        df = df.Define('Muon_PassTightId','Muon_pfIsoId>=3&&Muon_mediumPromptId')
        df = df.Define('goodmuonPt25','Muon_pt>25&&abs(Muon_pdgId)==13&&Muon_PassTightId')
        df = df.Filter('Sum(goodmuonPt25)>=1','>=1 muon with p_{T}>25 GeV')
        df = df.Define('badmuonPt10','Muon_pt>10&&abs(Muon_pdgId)==13&&Muon_PassTightId==0')
        df = df.Filter('Sum(badmuonPt10)==0','No bad quality muon')

        # RecoJet cleaning (optional)
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
        # Apply cuts to jets
        df = df.Redefine('Jet_pt', 'Jet_pt[isCleanJet]')
        df = df.Redefine('Jet_eta', 'Jet_eta[isCleanJet]')
        df = df.Redefine('Jet_phi', 'Jet_phi[isCleanJet]')

        # Redefine the L1Jet quantities
        df = df.Redefine("L1Jet_pt", "L1Jet_pt_scale_corr")
        df = df.Redefine("L1Jet_eta", "L1Jet_eta_scale_corr")
        df = df.Redefine("L1Jet_phi", "L1Jet_phi_scale_corr")

        # Sort jets by pT
        df = df.Define( "L1Jet_ptorder", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_ptorder)")

        # Basic event selection
        #df = df.Filter("nL1Jet > 1").Filter("(L1Jet_pt[0] >= 20) && (L1Jet_pt[1] >= 20)").Filter("std::abs(L1Jet_eta[0]) < 3.0 && std::abs(L1Jet_eta[1]) < 3.0")
        df = df.Filter("(L1Jet_pt[0] >= 20)").Filter("std::abs(L1Jet_eta[0]) < 3.0")
        df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")

        # Get the leading jets
        df = df.Define("L1Jet_leadingindices", "getLeadingIndices(L1Jet_pt)")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_leadingindices)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_leadingindices)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_leadingindices)")

        # Skim out all the jets
        df = df.Define("L1Jet_skim", "(L1Jet_pt >= 20) && (abs(L1Jet_eta) < 3.0)")
        df = df.Redefine("L1Jet_pt", "L1Jet_pt[L1Jet_skim]").Redefine("L1Jet_eta", "L1Jet_eta[L1Jet_skim]").Redefine("L1Jet_phi", "L1Jet_phi[L1Jet_skim]")

        # Define quantities
        df = df.Define("Jet_et", "getJetEt(Jet_pt, Jet_eta, Jet_phi, Jet_mass)") 
        df = df.Define("L1Jet_matchedRecoPt", "getMatchedPt(Jet_pt, Jet_eta, Jet_phi, L1Jet_pt, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedRecoEta", "getMatchedEta(Jet_pt, Jet_eta, Jet_phi, L1Jet_pt, L1Jet_eta, L1Jet_phi)")

        # Filter L1 jets to only those that have matches
        df = df.Define("L1Jet_isMatched", "L1Jet_matchedRecoPt > 0")
        df = df.Define("MatchedJet_pt", "L1Jet_pt[L1Jet_isMatched]")
        df = df.Define("MatchedJet_eta", "L1Jet_eta[L1Jet_isMatched]")
        df = df.Define("MatchedJet_phi", "L1Jet_phi[L1Jet_isMatched]")
        df = df.Define("MatchedJet_matchedRecoPt", "L1Jet_matchedRecoPt[L1Jet_isMatched]")
        df = df.Define("MatchedJet_matchedRecoEta", "L1Jet_matchedRecoEta[L1Jet_isMatched]")
        df = df.Define("MatchedJet_ptDiff", "MatchedJet_pt - MatchedJet_matchedRecoPt")
        df = df.Define("MatchedJet_ptScale", "MatchedJet_pt / MatchedJet_matchedRecoPt")

        return df, ["MatchedJet_pt", "MatchedJet_eta", "MatchedJet_phi", "MatchedJet_matchedRecoPt", "MatchedJet_matchedRecoEta", "MatchedJet_ptDiff", "MatchedJet_ptScale"] 
    
def MuonJetScale(**kwargs):
    return lambda: MuonJetScaleProducer(**kwargs)

# After applying both JES and JER
class MuonJetScaleResolutionProducer():
    def __init__(self, *args, **kwargs):
        # Preprocess function call
        if not os.getenv("_MuonJet"):
            os.environ["_MuonJet"] = "MuonJet"
            ROOT.gInterpreter.Declare("""
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

                // Get the matched reco jet eT
                auto getMatchedPt(Vfloat RecoJet_et, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedPt(Jet_pt.size(), -1);
                    Vint matchedRecoJetIdx(Jet_pt.size(), -1);

                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        float minDR = 9999;
                        // Doing minDPT instead
                        float minDPT = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_et.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            float dpt = std::abs(Jet_pt[i] - RecoJet_et[j])/RecoJet_et[j];
                            
                            //if((dr < minDR) && (dr < 0.2)){
                            //    minDR = dr;
                            //    matchedPt[i] = RecoJet_et[j];
                            //    bestRecoJetIdx = j;
                            //}

                            // Using dPT matching instead of dR matching
                            if((dpt < minDPT) && (dr < 0.2)){
                                minDPT = dpt;
                                matchedPt[i] = RecoJet_et[j];
                                bestRecoJetIdx = j;
                            }
                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedPt;
                }
                                    
                // Get the matched reco jet eta
                auto getMatchedEta(Vfloat RecoJet_et, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedEta(Jet_pt.size(), -1);
                    Vint matchedRecoJetIdx(Jet_pt.size(), -1);

                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        float minDR = 9999;
                        // Doing minDPT instead
                        float minDPT = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_eta.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            float dpt = std::abs(Jet_pt[i] - RecoJet_et[j])/RecoJet_et[j];

                            //if((dr < minDR) && (dr < 0.2)){
                            //    minDR = dr;
                            //    matchedEta[i] = RecoJet_eta[j];
                            //    bestRecoJetIdx = j;
                            //}

                            // Using dPT matching instead of dR matching
                            if((dpt < minDPT) && (dr < 0.2)){
                                minDPT = dpt;
                                matchedEta[i] = RecoJet_eta[j];
                                bestRecoJetIdx = j;
                            }
                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedEta;
                }

                // Get dR of nearest offline muon
                auto getdRNearestMuon(Vfloat Jet_eta, Vfloat Jet_phi, Vfloat Muon_eta, Vfloat Muon_phi) {
                    Vfloat dRNearestMuon(Jet_eta.size(), 9999);
                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        for(size_t j = 0; j < Muon_eta.size(); ++j){
                            float dEta = Jet_eta[i] - Muon_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - Muon_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            if (dr < dRNearestMuon[i]){
                                dRNearestMuon[i] = dr;
                            }
                        }
                    }    
                    return dRNearestMuon;                     
                }
                                    
                // Pick at most two indicies
                auto getLeadingIndices(Vfloat Jet_pt){
                    Vint LeadingIndices;
                    
                    int idx = 0;
                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        if (idx > 1) break;
                        LeadingIndices.push_back(idx);
                        idx++;
                    }

                    return LeadingIndices;
                }
            """)

    def run(self, df):

        # Event selection (skimming)
        df = df.Filter("HLT_IsoMu24").Filter("nL1Jet > 0").Filter("nJet > 0")
        # Muon pre-selections (akin to MuonJet JEC derivation)
        df = df.Define('Muon_PassTightId','Muon_pfIsoId>=3&&Muon_mediumPromptId')
        df = df.Define('goodmuonPt25','Muon_pt>25&&abs(Muon_pdgId)==13&&Muon_PassTightId')
        df = df.Filter('Sum(goodmuonPt25)>=1','>=1 muon with p_{T}>25 GeV')
        df = df.Define('badmuonPt10','Muon_pt>10&&abs(Muon_pdgId)==13&&Muon_PassTightId==0')
        df = df.Filter('Sum(badmuonPt10)==0','No bad quality muon')

        # RecoJet cleaning (optional)
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
        # Apply cuts to jets
        df = df.Redefine('Jet_pt', 'Jet_pt[isCleanJet]')
        df = df.Redefine('Jet_eta', 'Jet_eta[isCleanJet]')
        df = df.Redefine('Jet_phi', 'Jet_phi[isCleanJet]')

        # Redefine the L1Jet quantities
        df = df.Redefine("L1Jet_pt", "L1Jet_pt_scale_corr_resolution_smear")
        df = df.Redefine("L1Jet_eta", "L1Jet_eta_scale_corr_resolution_smear")
        df = df.Redefine("L1Jet_phi", "L1Jet_phi_scale_corr_resolution_smear")

        # Sort jets by pT
        df = df.Define( "L1Jet_ptorder", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_ptorder)")

        # Basic event selection
        #df = df.Filter("nL1Jet > 1").Filter("(L1Jet_pt[0] >= 20) && (L1Jet_pt[1] >= 20)").Filter("std::abs(L1Jet_eta[0]) < 3.0 && std::abs(L1Jet_eta[1]) < 3.0")
        df = df.Filter("(L1Jet_pt[0] >= 20)").Filter("std::abs(L1Jet_eta[0]) < 3.0")
        df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")

        # Get the leading jets
        df = df.Define("L1Jet_leadingindices", "getLeadingIndices(L1Jet_pt)")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_leadingindices)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_leadingindices)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_leadingindices)")

        # Skim out all the jets
        df = df.Define("L1Jet_skim", "(L1Jet_pt >= 20) && (abs(L1Jet_eta) < 3.0)")
        df = df.Redefine("L1Jet_pt", "L1Jet_pt[L1Jet_skim]").Redefine("L1Jet_eta", "L1Jet_eta[L1Jet_skim]").Redefine("L1Jet_phi", "L1Jet_phi[L1Jet_skim]")

        # Define quantities
        df = df.Define("Jet_et", "getJetEt(Jet_pt, Jet_eta, Jet_phi, Jet_mass)") 
        df = df.Define("L1Jet_matchedRecoPt", "getMatchedPt(Jet_pt, Jet_eta, Jet_phi, L1Jet_pt, L1Jet_eta, L1Jet_phi)")
        df = df.Define("L1Jet_matchedRecoEta", "getMatchedEta(Jet_pt, Jet_eta, Jet_phi, L1Jet_pt, L1Jet_eta, L1Jet_phi)")

        # Filter L1 jets to only those that have matches
        df = df.Define("L1Jet_isMatched", "L1Jet_matchedRecoPt > 0")
        df = df.Define("MatchedJet_pt", "L1Jet_pt[L1Jet_isMatched]")
        df = df.Define("MatchedJet_eta", "L1Jet_eta[L1Jet_isMatched]")
        df = df.Define("MatchedJet_phi", "L1Jet_phi[L1Jet_isMatched]")
        df = df.Define("MatchedJet_matchedRecoPt", "L1Jet_matchedRecoPt[L1Jet_isMatched]")
        df = df.Define("MatchedJet_matchedRecoEta", "L1Jet_matchedRecoEta[L1Jet_isMatched]")
        df = df.Define("MatchedJet_ptDiff", "MatchedJet_pt - MatchedJet_matchedRecoPt")
        df = df.Define("MatchedJet_ptScale", "MatchedJet_pt / MatchedJet_matchedRecoPt")

        return df, ["MatchedJet_pt", "MatchedJet_eta", "MatchedJet_phi", "MatchedJet_matchedRecoPt", "MatchedJet_matchedRecoEta", "MatchedJet_ptDiff", "MatchedJet_ptScale"] 
    
def MuonJetScaleResolution(**kwargs):
    return lambda: MuonJetScaleResolutionProducer(**kwargs)

## Z + jet balance
class ZJetProducer():
    def __init__(self, *args, **kwargs):
        # Preprocess function call
        if not os.getenv("_ZJet"):
            os.environ["_ZJet"] = "ZJet"
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

                // Get the matched reco jet eT
                auto getMatchedPt(Vfloat RecoJet_et, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedPt(Jet_pt.size(), -1);
                    Vint matchedRecoJetIdx(Jet_pt.size(), -1);

                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        float minDR = 9999;
                        // Doing minDPT instead
                        float minDPT = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_et.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            float dpt = std::abs(Jet_pt[i] - RecoJet_et[j])/RecoJet_et[j];
                            
                            //if((dr < minDR) && (dr < 0.2)){
                            //    minDR = dr;
                            //    matchedPt[i] = RecoJet_et[j];
                            //    bestRecoJetIdx = j;
                            //}

                            // Using dPT matching instead of dR matching
                            if((dpt < minDPT) && (dr < 0.2)){
                                minDPT = dpt;
                                matchedPt[i] = RecoJet_et[j];
                                bestRecoJetIdx = j;
                            }
                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedPt;
                }
                                    
                // Get the matched reco jet eta
                auto getMatchedEta(Vfloat RecoJet_et, Vfloat RecoJet_eta, Vfloat RecoJet_phi, Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi) {
                    Vfloat matchedEta(Jet_pt.size(), -1);
                    Vint matchedRecoJetIdx(Jet_pt.size(), -1);

                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        float minDR = 9999;
                        // Doing minDPT instead
                        float minDPT = 9999;
                        int bestRecoJetIdx = -1;

                        for(size_t j = 0; j < RecoJet_eta.size(); ++j){
                            if (std::find(matchedRecoJetIdx.begin(), matchedRecoJetIdx.end(), j) != matchedRecoJetIdx.end()) continue;

                            float dEta = Jet_eta[i] - RecoJet_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RecoJet_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            float dpt = std::abs(Jet_pt[i] - RecoJet_et[j])/RecoJet_et[j];

                            //if((dr < minDR) && (dr < 0.2)){
                            //    minDR = dr;
                            //    matchedEta[i] = RecoJet_eta[j];
                            //    bestRecoJetIdx = j;
                            //}

                            // Using dPT matching instead of dR matching
                            if((dpt < minDPT) && (dr < 0.2)){
                                minDPT = dpt;
                                matchedEta[i] = RecoJet_eta[j];
                                bestRecoJetIdx = j;
                            }
                        }
                        matchedRecoJetIdx[i] = bestRecoJetIdx;
                    }
                    return matchedEta;
                }

                // Get dR of nearest offline muon
                auto getdRNearestMuon(Vfloat Jet_eta, Vfloat Jet_phi, Vfloat Muon_eta, Vfloat Muon_phi) {
                    Vfloat dRNearestMuon(Jet_eta.size(), 9999);
                    for(size_t i = 0; i < Jet_eta.size(); ++i){
                        for(size_t j = 0; j < Muon_eta.size(); ++j){
                            float dEta = Jet_eta[i] - Muon_eta[j];
                            float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - Muon_phi[j]);
                            float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                            if (dr < dRNearestMuon[i]){
                                dRNearestMuon[i] = dr;
                            }
                        }
                    }    
                    return dRNearestMuon;                     
                }
                                    
                // Pick at most two indicies
                auto getLeadingIndices(Vfloat Jet_pt){
                    Vint LeadingIndices;
                    
                    int idx = 0;
                    for(size_t i = 0; i < Jet_pt.size(); ++i){
                        if (idx > 1) break;
                        LeadingIndices.push_back(idx);
                        idx++;
                    }

                    return LeadingIndices;
                }

                // Z related 
                struct ZSystem{
                    float pt;
                    float eta;
                    float phi;
                    float mass;
                };

                // Make the Z system
                auto makeZSystem(Vfloat Muon_pt, Vfloat Muon_eta, Vfloat Muon_phi){
                    ZSystem Z;
                    TLorentzVector mu1, mu2;
                    mu1.SetPtEtaPhiM(Muon_pt[0], Muon_eta[0], Muon_phi[0], 0.10566);
                    mu2.SetPtEtaPhiM(Muon_pt[1], Muon_eta[1], Muon_phi[1], 0.10566);
                    TLorentzVector Zvec = mu1 + mu2;

                    Z.pt = Zvec.Pt();
                    Z.eta = Zvec.Eta();
                    Z.phi = Zvec.Phi();
                    Z.mass = Zvec.M();
                    return Z;
                }

                // Get dPhi of leading jet with dimuon system
                auto getdPhiZJet(Vfloat Jet_phi, float Z_phi) {
                    float dPhiZJet = 9999;
                    return std::abs(TVector2::Phi_mpi_pi(Jet_phi[0] - Z_phi));
                }

                // Get the ratio of the jet pT to the subleading jet pT
                auto getAlpha(Vfloat Jet_pt) {
                    float alpha = 0;
                    if (Jet_pt.size() > 1){
                        alpha = Jet_pt[1]/Jet_pt[0];
                    }
                    return alpha;
                }

                // Get the ratio of the jet pT to the sum of all the other jet pTs
                auto getAlphaTotal(Vfloat Jet_pt) {
                    float alphaTotal = 0;
                    for (size_t i = 1; i < Jet_pt.size(); ++i){
                        alphaTotal += Jet_pt[i];
                    }
                    return alphaTotal/Jet_pt[0];
                }

                // Trigger matching
                vector<int> MatchObjToTrig(ROOT::VecOps::RVec<float>Obj_eta, ROOT::VecOps::RVec<float>Obj_phi, ROOT::VecOps::RVec<float>TrigObj_pt, ROOT::VecOps::RVec<float>TrigObj_eta, ROOT::VecOps::RVec<float>TrigObj_phi, ROOT::VecOps::RVec<int>TrigObj_id, int Target_id, ROOT::VecOps::RVec<int>filterBits, int filterBitIdx=1, float dRminimum=0.2, float trigObjPtCut = -1.){
                    vector <int> result={};

                    for(unsigned int i = 0; i<Obj_eta.size(); i++){
                        //For HLT-reco matching => can use a small dR cone size. A larger cone size would be needed for L1-reco matching with muons. 
                        double drmin = dRminimum; // Default dRmin = 0.2 
                        int idx = -1;

                        for(unsigned int j = 0; j<TrigObj_eta.size(); j++){
                            if (TrigObj_id[j] != Target_id) continue;
                            if (TrigObj_pt[j] < trigObjPtCut) continue;
                            double deta = abs(TrigObj_eta[j]-Obj_eta[i]);
                            //double dphi = deltaphi_offlinemustation2_l1mu(Muon_charge[i], TrigObj_pt[j], TrigObj_eta[j], TrigObj_phi[j], Muon_phi[i]);
                            double dphi = abs(acos(cos(TrigObj_phi[j]-Obj_phi[i]))); 
                            double dr = sqrt(deta*deta+dphi*dphi);
                            if(dr<=drmin){ 
                                if((filterBits[j]>>filterBitIdx&1) == 1){  // Default FilterBitIdx = 1
                                    drmin = dr; 
                                    idx = j;
                                }
                            }
                        }
                        result.push_back(idx);
                    }
                    return result;
                }

                ROOT::VecOps::RVec <Bool_t> trig_is_filterbit1_set(ROOT::VecOps::RVec<int>Trig_idx, ROOT::VecOps::RVec<int>filterBits, int filterBitIdx=1){
                    vector <bool> result = {};
                    for( unsigned int i = 0; i <Trig_idx.size(); i++){
                        if (Trig_idx[i] == -1) result.push_back(false);
                        else {
                            int idx = Trig_idx[i];
                        if((filterBits[idx]>>filterBitIdx&1) == 1) result.push_back(true);
                            else result.push_back(false);
                        }
                    }
                    return result;
                }

                auto convertFloatToVfloat(float val){
                    Vfloat val_vec;
                    val_vec.push_back(val);
                    return val_vec;
                }

            """)

    def run(self, df):
        # Event selection (skimming)
        df = df.Filter("HLT_IsoMu24").Filter("nL1Jet > 0")

        # Sort the muons by pT
        df = df.Define("Muon_pt_order", "Reverse(Argsort(Muon_pt))")
        df = df.Redefine("Muon_pt", "Take(Muon_pt, Muon_pt_order)")
        df = df.Redefine("Muon_eta", "Take(Muon_eta, Muon_pt_order)")
        df = df.Redefine("Muon_phi", "Take(Muon_phi, Muon_pt_order)")
        df = df.Redefine("Muon_charge", "Take(Muon_charge, Muon_pt_order)")
        df = df.Redefine("Muon_pfIsoId", "Take(Muon_pfIsoId, Muon_pt_order)")
        df = df.Redefine("Muon_mediumPromptId", "Take(Muon_mediumPromptId, Muon_pt_order)")
        df = df.Redefine("Muon_pdgId", "Take(Muon_pdgId, Muon_pt_order)")

        # Muon selection
        df = df.Define('Muon_trig_idx', 'MatchObjToTrig(Muon_eta, Muon_phi, TrigObj_pt, TrigObj_eta, TrigObj_phi, TrigObj_id, 13, TrigObj_filterBits)')
        df = df.Define('Muon_passHLT_IsoMu24', 'trig_is_filterbit1_set(Muon_trig_idx, TrigObj_filterBits)')
        df = df.Define('Muon_PassTightId','Muon_pfIsoId>=3&&Muon_mediumPromptId') 
        df = df.Define('isTag','Muon_pt>25&&abs(Muon_pdgId)==13&&Muon_PassTightId&&Muon_passHLT_IsoMu24')
        df = df.Filter('(isTag[0])||(isTag[1])')
        df = df.Filter("Muon_charge[0] != Muon_charge[1]")

        # Select Z events
        df = df.Define("ZCand", "makeZSystem(Muon_pt, Muon_eta, Muon_phi)").Define("ZCand_pt", "ZCand.pt").Define("ZCand_eta", "ZCand.eta").Define("ZCand_phi", "ZCand.phi").Define("ZCand_mass", "ZCand.mass")
        df = df.Filter("(ZCand_mass > 70) && (ZCand_mass < 110)").Filter("(std::abs(ZCand_eta) < 2.4)")

        # Sort jets by pT
        df = df.Define( "L1Jet_ptorder", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_ptorder)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_ptorder)")

        # Basic event selection
        #df = df.Filter("nL1Jet > 1").Filter("(L1Jet_pt[0] >= 20) && (L1Jet_pt[1] >= 20)").Filter("std::abs(L1Jet_eta[0]) < 3.0 && std::abs(L1Jet_eta[1]) < 3.0")
        df = df.Filter("(L1Jet_pt[0] >= 20)").Filter("std::abs(L1Jet_eta[0]) < 3.0")
        df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")

        # Match leading jet to Z
        df = df.Define("LeadL1Jet_dPhiZ", "getdPhiZJet(L1Jet_phi, ZCand_phi)")
        df = df.Define("LeadL1Jet_alpha", "getAlpha(L1Jet_pt)").Define("LeadL1Jet_alphaTotal", "getAlphaTotal(L1Jet_pt)")

        # Apply dPhi and alpha cuts
        df = df.Filter("LeadL1Jet_dPhiZ > 2.8").Filter("LeadL1Jet_alpha < 0.2")

        # Save some quantities 
        df = df.Define("MatchedJet_pt", "L1Jet_pt[0]")
        df = df.Define("MatchedJet_eta", "L1Jet_eta[0]")
        df = df.Define("MatchedJet_phi", "L1Jet_phi[0]")
        df = df.Define("MatchedJet_alpha", "LeadL1Jet_alpha")
        df = df.Define("MatchedJet_alphaTotal", "LeadL1Jet_alphaTotal")
        df = df.Define("MatchedJet_ptScale", "L1Jet_pt[0] / ZCand_pt")
        df = df.Define("MatchedJet_ptDiff", "L1Jet_pt[0] - ZCand_pt")

        # Set variables to be Vfloats instead of just floats to enable PrePlot selection logic consistency
        df = df.Redefine("MatchedJet_pt", "convertFloatToVfloat(MatchedJet_pt)")
        df = df.Redefine("MatchedJet_eta", "convertFloatToVfloat(MatchedJet_eta)")
        df = df.Redefine("MatchedJet_phi", "convertFloatToVfloat(MatchedJet_phi)")
        df = df.Redefine("MatchedJet_alpha", "convertFloatToVfloat(MatchedJet_alpha)")
        df = df.Redefine("MatchedJet_alphaTotal", "convertFloatToVfloat(MatchedJet_alphaTotal)")
        df = df.Redefine("MatchedJet_ptScale", "convertFloatToVfloat(MatchedJet_ptScale)")
        df = df.Redefine("MatchedJet_ptDiff", "convertFloatToVfloat(MatchedJet_ptDiff)")

        return df, ["MatchedJet_pt", "MatchedJet_eta", "MatchedJet_phi", "MatchedJet_ptDiff", "MatchedJet_ptScale", "MatchedJet_alpha", "MatchedJet_alphaTotal"] 

def ZJet(*args, **kwargs):
    return lambda: ZJetProducer(*args, *kwargs)
