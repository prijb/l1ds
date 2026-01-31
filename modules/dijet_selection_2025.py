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
        
        df = df.Filter("(L1Jet_pt[0] > 30)").Filter("(L1Jet_pt[1] > 30)")
        df = df.Filter("std::abs(L1Jet_eta[0]) < 2.5").Filter("std::abs(L1Jet_eta[1]) < 2.5") # Inclusive selection
        #Event vetoes
        df = df.Filter("Sum(L1Jet_pt == 1023.5)==0", "Saturated jet veto")

        #Define quantities
        df = df.Define("mjj", "getDijetMass(L1Jet_pt, L1Jet_eta, L1Jet_phi)")
        df = df.Define("deta", "std::abs(L1Jet_eta[0] - L1Jet_eta[1])").Define("dphi", "getDijetDPhi(L1Jet_phi)").Define("pt", "getDijetPt(L1Jet_pt, L1Jet_eta, L1Jet_phi)")

        #Further event selections
        #df = df.Filter("dphi > 1.047")

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
        
        df = df.Filter("std::abs(L1Jet_eta[0]) < 2.5").Filter("std::abs(L1Jet_eta[1]) < 2.5") # Inclusive selection
        #Event vetoes
        df = df.Filter("Sum(L1Jet_pt == 1023.5)==0", "Saturated jet veto")

        #Define quantities
        df = df.Define("mjj", "getDijetMass(L1Jet_pt, L1Jet_eta, L1Jet_phi)")
        df = df.Define("deta", "std::abs(L1Jet_eta[0] - L1Jet_eta[1])").Define("dphi", "getDijetDPhi(L1Jet_phi)").Define("pt", "getDijetPt(L1Jet_pt, L1Jet_eta, L1Jet_phi)")

        #Further event selections
        #df = df.Filter("dphi > 1.047")

        return df, ["mjj", "deta", "dphi", "pt"]
    
def InclusiveDijetSelectionZB(*args, **kwargs):
    return lambda: InclusiveDijetSelectionZBProducer(*args, **kwargs)

############## Reorder jets according to correction and do selections wrt to this ##########################
# Obtains the corrected kinematics after reordering in pT
# Dependency: JetPtReshuffle from modules.jet_pt_systematics_nano
class InclusiveDijetSelectionReshuffleProducer():
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

        df = df.Define("L1Jet_eta_scale_corr", "Take(L1Jet_eta, L1Jet_pt_scale_corr_order)")
        df = df.Define("L1Jet_phi_scale_corr", "Take(L1Jet_phi, L1Jet_pt_scale_corr_order)")
        df = df.Redefine("L1Jet_pt_scale_corr", "Take(L1Jet_pt_scale_corr, L1Jet_pt_scale_corr_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_up", "Take(L1Jet_pt_scale_corr_up, L1Jet_pt_scale_corr_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_down", "Take(L1Jet_pt_scale_corr_down, L1Jet_pt_scale_corr_order)")

        # Get mjj, deta and dphi
        df = df.Define("mjj_scale_corr", "getDijetMass(L1Jet_pt_scale_corr, L1Jet_eta_scale_corr, L1Jet_phi_scale_corr)")
        df = df.Define("deta_scale_corr", "std::abs(L1Jet_eta_scale_corr[0] - L1Jet_eta_scale_corr[1])").Define("dphi_scale_corr", "getDijetDPhi(L1Jet_phi_scale_corr)").Define("pt_scale_corr", "getDijetPt(L1Jet_pt_scale_corr, L1Jet_eta_scale_corr, L1Jet_phi_scale_corr)")


        return df, ["L1Jet_eta_scale_corr", "L1Jet_phi_scale_corr", "L1Jet_pt_scale_corr", "L1Jet_pt_scale_corr_up", "L1Jet_pt_scale_corr_down", "mjj_scale_corr", "deta_scale_corr", "dphi_scale_corr"]

def InclusiveDijetSelectionReshuffle(*args, **kwargs):
    return lambda: InclusiveDijetSelectionReshuffleProducer(*args, **kwargs)