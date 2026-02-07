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

# Just filter out events with saturated towers
class BasicDijetFilterProducer():
    def __init__(self, *args, **kwargs):
        self.year = kwargs.pop("year")

    def run(self, df):
        df = df.Filter("nL1Jet > 1")
        df = df.Filter("Sum(L1Jet_pt == 1023.5)==0", "Saturated jet veto")

        return df, []
    
def BasicDijetFilter(*args, **kwargs):
    return lambda: BasicDijetFilterProducer(*args, **kwargs)

############## Using corrected and reordered jets ##########################
# Obtains the corrected kinematics after JES
# Dependency: JetPtReshuffleScale from modules.jet_pt_systematics_nano_v2
class InclusiveDijetSelectionScaleProducer():
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
        # Get mjj, deta and dphi
        # Nominal
        df = df.Define("mjj_scale_corr_nominal", "getDijetMass(L1Jet_pt_scale_corr_nominal, L1Jet_eta_scale_corr_nominal, L1Jet_phi_scale_corr_nominal)")
        df = df.Define("deta_scale_corr_nominal", "std::abs(L1Jet_eta_scale_corr_nominal[0] - L1Jet_eta_scale_corr_nominal[1])").Define("dphi_scale_corr_nominal", "getDijetDPhi(L1Jet_phi_scale_corr_nominal)").Define("pt_scale_corr_nominal", "getDijetPt(L1Jet_pt_scale_corr_nominal, L1Jet_eta_scale_corr_nominal, L1Jet_phi_scale_corr_nominal)")

        # Up
        df = df.Define("mjj_scale_corr_up", "getDijetMass(L1Jet_pt_scale_corr_up, L1Jet_eta_scale_corr_up, L1Jet_phi_scale_corr_up)")
        df = df.Define("deta_scale_corr_up", "std::abs(L1Jet_eta_scale_corr_up[0] - L1Jet_eta_scale_corr_up[1])").Define("dphi_scale_corr_up", "getDijetDPhi(L1Jet_phi_scale_corr_up)").Define("pt_scale_corr_up", "getDijetPt(L1Jet_pt_scale_corr_up, L1Jet_eta_scale_corr_up, L1Jet_phi_scale_corr_up)")

        # Down
        df = df.Define("mjj_scale_corr_down", "getDijetMass(L1Jet_pt_scale_corr_down, L1Jet_eta_scale_corr_down, L1Jet_phi_scale_corr_down)")
        df = df.Define("deta_scale_corr_down", "std::abs(L1Jet_eta_scale_corr_down[0] - L1Jet_eta_scale_corr_down[1])").Define("dphi_scale_corr_down", "getDijetDPhi(L1Jet_phi_scale_corr_down)").Define("pt_scale_corr_down", "getDijetPt(L1Jet_pt_scale_corr_down, L1Jet_eta_scale_corr_down, L1Jet_phi_scale_corr_down)")

        branches_nominal = ["mjj_scale_corr_nominal", "deta_scale_corr_nominal", "dphi_scale_corr_nominal"]
        branches_up = ["mjj_scale_corr_up", "deta_scale_corr_up", "dphi_scale_corr_up"]
        branches_down = ["mjj_scale_corr_down", "deta_scale_corr_down", "dphi_scale_corr_down"]


        return df, (branches_nominal + branches_up + branches_down)

def InclusiveDijetSelectionScale(*args, **kwargs):
    return lambda: InclusiveDijetSelectionScaleProducer(*args, **kwargs)

# Obtains the corrected kinematics after JES and JER
# Dependency: JetPtReshuffleScaleResolution from modules.jet_pt_systematics_nano_v2
class InclusiveDijetSelectionScaleResolutionProducer():
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
        # Nominal JES, Nominal JER
        df = df.Define("mjj_scale_corr_nominal_resolution_smear_nominal", "getDijetMass(L1Jet_pt_scale_corr_nominal_resolution_smear_nominal, L1Jet_eta_scale_corr_nominal_resolution_smear_nominal, L1Jet_phi_scale_corr_nominal_resolution_smear_nominal)")
        df = df.Define("deta_scale_corr_nominal_resolution_smear_nominal", "std::abs(L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[0] - L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[1])").Define("dphi_scale_corr_nominal_resolution_smear_nominal", "getDijetDPhi(L1Jet_phi_scale_corr_nominal_resolution_smear_nominal)").Define("pt_scale_corr_nominal_resolution_smear_nominal", "getDijetPt(L1Jet_pt_scale_corr_nominal_resolution_smear_nominal, L1Jet_eta_scale_corr_nominal_resolution_smear_nominal, L1Jet_phi_scale_corr_nominal_resolution_smear_nominal)")

        # Up JES, Nominal JER
        df = df.Define("mjj_scale_corr_up_resolution_smear_nominal", "getDijetMass(L1Jet_pt_scale_corr_up_resolution_smear_nominal, L1Jet_eta_scale_corr_up_resolution_smear_nominal, L1Jet_phi_scale_corr_up_resolution_smear_nominal)")
        df = df.Define("deta_scale_corr_up_resolution_smear_nominal", "std::abs(L1Jet_eta_scale_corr_up_resolution_smear_nominal[0] - L1Jet_eta_scale_corr_up_resolution_smear_nominal[1])").Define("dphi_scale_corr_up_resolution_smear_nominal", "getDijetDPhi(L1Jet_phi_scale_corr_up_resolution_smear_nominal)").Define("pt_scale_corr_up_resolution_smear_nominal", "getDijetPt(L1Jet_pt_scale_corr_up_resolution_smear_nominal, L1Jet_eta_scale_corr_up_resolution_smear_nominal, L1Jet_phi_scale_corr_up_resolution_smear_nominal)")

        # Down JES, Nominal JER
        df = df.Define("mjj_scale_corr_down_resolution_smear_nominal", "getDijetMass(L1Jet_pt_scale_corr_down_resolution_smear_nominal, L1Jet_eta_scale_corr_down_resolution_smear_nominal, L1Jet_phi_scale_corr_down_resolution_smear_nominal)")
        df = df.Define("deta_scale_corr_down_resolution_smear_nominal", "std::abs(L1Jet_eta_scale_corr_down_resolution_smear_nominal[0] - L1Jet_eta_scale_corr_down_resolution_smear_nominal[1])").Define("dphi_scale_corr_down_resolution_smear_nominal", "getDijetDPhi(L1Jet_phi_scale_corr_down_resolution_smear_nominal)").Define("pt_scale_corr_down_resolution_smear_nominal", "getDijetPt(L1Jet_pt_scale_corr_down_resolution_smear_nominal, L1Jet_eta_scale_corr_down_resolution_smear_nominal, L1Jet_phi_scale_corr_down_resolution_smear_nominal)")

        # Nominal JES, Up JER
        df = df.Define("mjj_scale_corr_nominal_resolution_smear_up", "getDijetMass(L1Jet_pt_scale_corr_nominal_resolution_smear_up, L1Jet_eta_scale_corr_nominal_resolution_smear_up, L1Jet_phi_scale_corr_nominal_resolution_smear_up)")
        df = df.Define("deta_scale_corr_nominal_resolution_smear_up", "std::abs(L1Jet_eta_scale_corr_nominal_resolution_smear_up[0] - L1Jet_eta_scale_corr_nominal_resolution_smear_up[1])").Define("dphi_scale_corr_nominal_resolution_smear_up", "getDijetDPhi(L1Jet_phi_scale_corr_nominal_resolution_smear_up)").Define("pt_scale_corr_nominal_resolution_smear_up", "getDijetPt(L1Jet_pt_scale_corr_nominal_resolution_smear_up, L1Jet_eta_scale_corr_nominal_resolution_smear_up, L1Jet_phi_scale_corr_nominal_resolution_smear_up)")

        # Nominal JES, Down JER
        df = df.Define("mjj_scale_corr_nominal_resolution_smear_down", "getDijetMass(L1Jet_pt_scale_corr_nominal_resolution_smear_down, L1Jet_eta_scale_corr_nominal_resolution_smear_down, L1Jet_phi_scale_corr_nominal_resolution_smear_down)")
        df = df.Define("deta_scale_corr_nominal_resolution_smear_down", "std::abs(L1Jet_eta_scale_corr_nominal_resolution_smear_down[0] - L1Jet_eta_scale_corr_nominal_resolution_smear_down[1])").Define("dphi_scale_corr_nominal_resolution_smear_down", "getDijetDPhi(L1Jet_phi_scale_corr_nominal_resolution_smear_down)").Define("pt_scale_corr_nominal_resolution_smear_down", "getDijetPt(L1Jet_pt_scale_corr_nominal_resolution_smear_down, L1Jet_eta_scale_corr_nominal_resolution_smear_down, L1Jet_phi_scale_corr_nominal_resolution_smear_down)")

        branches_scale_nominal_smear_nominal = ["mjj_scale_corr_nominal_resolution_smear_nominal", "deta_scale_corr_nominal_resolution_smear_nominal", "dphi_scale_corr_nominal_resolution_smear_nominal"]
        branches_scale_up_smear_nominal = ["mjj_scale_corr_up_resolution_smear_nominal", "deta_scale_corr_up_resolution_smear_nominal", "dphi_scale_corr_up_resolution_smear_nominal"]
        branches_scale_down_smear_nominal = ["mjj_scale_corr_down_resolution_smear_nominal", "deta_scale_corr_down_resolution_smear_nominal", "dphi_scale_corr_down_resolution_smear_nominal"]
        branches_scale_nominal_smear_up = ["mjj_scale_corr_nominal_resolution_smear_up", "deta_scale_corr_nominal_resolution_smear_up", "dphi_scale_corr_nominal_resolution_smear_up"]
        branches_scale_nominal_smear_down = ["mjj_scale_corr_nominal_resolution_smear_down", "deta_scale_corr_nominal_resolution_smear_down", "dphi_scale_corr_nominal_resolution_smear_down"]


        return df, (branches_scale_nominal_smear_nominal + branches_scale_up_smear_nominal + branches_scale_down_smear_nominal + branches_scale_nominal_smear_up + branches_scale_nominal_smear_down)

def InclusiveDijetSelectionScaleResolution(*args, **kwargs):
    return lambda: InclusiveDijetSelectionScaleResolutionProducer(*args, **kwargs)

