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
        df = df.Filter("nJet > 1").Filter("(Jet_pt[0] > 30)").Filter("(Jet_pt[1] > 30)")
        df = df.Filter("std::abs(Jet_eta[0]) < 2.5").Filter("std::abs(Jet_eta[1]) < 2.5") # Inclusive selection
        #Event vetoes
        df = df.Filter("Sum(Jet_pt == 1023.5)==0", "Saturated jet veto")

        #Define quantities
        df = df.Define("mjj", "getDijetMass(Jet_pt, Jet_eta, Jet_phi)")
        df = df.Define("deta", "std::abs(Jet_eta[0] - Jet_eta[1])").Define("dphi", "getDijetDPhi(Jet_phi)").Define("pt", "getDijetPt(Jet_pt, Jet_eta, Jet_phi)")

        #Further event selections
        df = df.Filter("dphi > 1.047")

        return df, ["mjj", "deta", "dphi", "pt"]

def InclusiveDijetSelection(*args, **kwargs):
    return lambda: InclusiveDijetSelectionProducer()


# Barrel version
class BarrelDijetSelectionProducer():
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
        df = df.Filter("nJet > 1").Filter("(Jet_pt[0] > 30)").Filter("(Jet_pt[1] > 30)")
        df = df.Filter("std::abs(Jet_eta[0]) < 1.3").Filter("std::abs(Jet_eta[1]) < 1.3") # Barrel selection
        #Event vetoes
        df = df.Filter("Sum(Jet_pt == 1023.5)==0", "Saturated jet veto")

        #Define quantities
        df = df.Define("mjj", "getDijetMass(Jet_pt, Jet_eta, Jet_phi)")
        df = df.Define("deta", "std::abs(Jet_eta[0] - Jet_eta[1])").Define("dphi", "getDijetDPhi(Jet_phi)").Define("pt", "getDijetPt(Jet_pt, Jet_eta, Jet_phi)")

        #Further event selections
        df = df.Filter("dphi > 1.047")

        return df, ["mjj", "deta", "dphi", "pt"]

def BarrelDijetSelection(*args, **kwargs):
    return lambda: BarrelDijetSelectionProducer()

################### Isolation calculations #####################


################### Regressed jet selections #####################

class RegressedInclusiveDijetSelectionProducer():
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
        # These selections are still done with the non-regressed quantities
        df = df.Filter("nJet > 1").Filter("(Jet_pt[0] > 30)").Filter("(Jet_pt[1] > 30)")
        df = df.Filter("std::abs(Jet_eta[0]) < 2.5").Filter("std::abs(Jet_eta[1]) < 2.5") # Inclusive selection
        #Event vetoes
        df = df.Filter("Sum(Jet_pt == 1023.5)==0", "Saturated jet veto")

        #Define quantities (Done with regressed pT)
        df = df.Define("mjj_orig", "getDijetMass(Jet_pt, Jet_eta, Jet_phi)")
        df = df.Define("mjj", "getDijetMass(Jet_pt_regressed, Jet_eta, Jet_phi)")
        df = df.Define("deta", "std::abs(Jet_eta[0] - Jet_eta[1])").Define("dphi", "getDijetDPhi(Jet_phi)").Define("pt", "getDijetPt(Jet_pt_regressed, Jet_eta, Jet_phi)")

        #Further event selections
        df = df.Filter("dphi > 1.047")

        return df, ["mjj_orig", "mjj", "deta", "dphi", "pt"]

def RegressedInclusiveDijetSelection(*args, **kwargs):
    return lambda: RegressedInclusiveDijetSelectionProducer()


# Barrel version
class RegressedBarrelDijetSelectionProducer():
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
        # These selections are still done with the non-regressed quantities 
        df = df.Filter("nJet > 1").Filter("(Jet_pt[0] > 30)").Filter("(Jet_pt[1] > 30)")
        df = df.Filter("std::abs(Jet_eta[0]) < 1.3").Filter("std::abs(Jet_eta[1]) < 1.3") # Barrel selection
        #Event vetoes
        df = df.Filter("Sum(Jet_pt == 1023.5)==0", "Saturated jet veto")

        #Define quantities (Done with regressed pT)
        df = df.Define("mjj_orig", "getDijetMass(Jet_pt, Jet_eta, Jet_phi)")
        df = df.Define("mjj", "getDijetMass(Jet_pt_regressed, Jet_eta, Jet_phi)")
        df = df.Define("deta", "std::abs(Jet_eta[0] - Jet_eta[1])").Define("dphi", "getDijetDPhi(Jet_phi)").Define("pt", "getDijetPt(Jet_pt_regressed, Jet_eta, Jet_phi)")

        #Further event selections
        df = df.Filter("dphi > 1.047")

        return df, ["mjj_orig", "mjj", "deta", "dphi", "pt"]

def RegressedBarrelDijetSelection(*args, **kwargs):
    return lambda: RegressedBarrelDijetSelectionProducer()
