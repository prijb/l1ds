# Dijet selections applied for L1DS
import os
from analysis_tools.utils import import_root
ROOT = import_root()

#################### Selections ######################
# Perform trigger level selections and basic vetoes on lead and sublead jets (pre-corrected pT)
class InclusiveDijetPreSelectionProducer():
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
        
        # Trigger (selection stream) selection
        df = df.Filter("(L1Jet_pt[0] > 30)").Filter("(L1Jet_pt[1] > 30)")
        # Event vetoes (saturated jets)
        df = df.Filter("Sum(L1Jet_pt == 1023.5)==0", "Saturated jet veto")

        # Define quantities
        df = df.Define("mjj", "getDijetMass(L1Jet_pt, L1Jet_eta, L1Jet_phi)")
        df = df.Define("deta", "std::abs(L1Jet_eta[0] - L1Jet_eta[1])").Define("dphi", "getDijetDPhi(L1Jet_phi)").Define("pt", "getDijetPt(L1Jet_pt, L1Jet_eta, L1Jet_phi)")

        return df, ["mjj", "deta", "dphi", "pt"]

def InclusiveDijetPreSelection(*args, **kwargs):
    return lambda: InclusiveDijetPreSelectionProducer(*args, **kwargs)

## Preselections for ZB data (to estimate trigger efficiency)
class InclusiveDijetPreSelectionZBProducer():
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
        
        # Event vetoes (saturated jets)
        df = df.Filter("Sum(L1Jet_pt == 1023.5)==0", "Saturated jet veto")

        # Define quantities
        df = df.Define("mjj", "getDijetMass(L1Jet_pt, L1Jet_eta, L1Jet_phi)")
        df = df.Define("deta", "std::abs(L1Jet_eta[0] - L1Jet_eta[1])").Define("dphi", "getDijetDPhi(L1Jet_phi)").Define("pt", "getDijetPt(L1Jet_pt, L1Jet_eta, L1Jet_phi)")

        return df, ["mjj", "deta", "dphi", "pt"]

def InclusiveDijetPreSelectionZB(*args, **kwargs):
    return lambda: InclusiveDijetPreSelectionZBProducer(*args, **kwargs)

## Post-JEC variable definitions

################## Matching #######################