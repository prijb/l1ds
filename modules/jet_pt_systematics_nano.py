# Jet pT scale and resolution corrections 
import os

from Corrections.JME.PUjetID_SF import PUjetID_SFRDFProducer
from analysis_tools.utils import import_root
import correctionlib

ROOT = import_root()
correctionlib.register_pyroot_binding()

# Correcting MC to data
class JetPtScaleProducer():
    def __init__(self, *args, **kwargs):

        filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_scale.json"

        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        if self.isMC:
            #print("__init__ scale correction for MC")
            if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gInterpreter.Load("libCorrectionsWrapper.so")

            #print("\nWrapper loaded, declaring correction function")
            ROOT.gInterpreter.Declare(os.path.expandvars(
                '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_scale = MyCorrections("{os.path.expandvars(filename)}", '
                    '"NUM_Data_DEN_MC_jet_pt_scale");'
            )
            #print("\nDeclaration done, defining correction function")

            if not os.getenv("_JetPtScale"):
                os.environ["_JetPtScale"] = "JetPtScale"
                ROOT.gInterpreter.Declare("""
                    using Vfloat = ROOT::RVec<float>;
                    using Vint = ROOT::RVec<int>;
                    using Vbool = ROOT::RVec<bool>;
                    auto get_jet_pt_scale(Vfloat pt, Vfloat eta, std::string syst){
                        Vfloat scale_factor;
                        
                        
                        // Applying corrections to all jets
                        for (size_t i=0; i < pt.size(); i++){
                            float scale = corr_scale.eval({eta[i], pt[i], syst});
                            scale_factor.push_back(1./scale);
                        }
                        
                        /*
                        // Applying corrections to only first two jets
                        for (size_t i=0; i < pt.size(); i++){
                            float scale = corr_scale.eval({eta[i], pt[i], syst});
                            if (i < 2) {
                                scale_factor.push_back(1./scale);
                            }
                            else {
                                scale_factor.push_back(1.0);
                            }
                        }
                        */
                        return scale_factor;
                    }
                """)
            #print("\nDefinition done")

    def run(self, df):
        if self.isMC:
            print("\nRunning scale correction to Data for MC")
            branches = ["pt_scale_residual", "pt_scale_residual_up", "pt_scale_residual_down"]
            jet_branches = []
            for branch_name, syst in zip(branches, ["sf", "systup", "systdown"]):
                df = df.Define(branch_name, """get_jet_pt_scale(L1Jet_pt, L1Jet_eta, "%s")""" % syst)
                df = df.Define(f"L1Jet_{branch_name}", f"L1Jet_pt * {branch_name}")
                jet_branches.append(f"L1Jet_{branch_name}")

        else:
            branches = []
            jet_branches = []
        return df, (branches + jet_branches)


def JetPtScale(**kwargs):
    return lambda: JetPtScaleProducer(**kwargs)

# Correcting MC to 1.0
class JetPtScaleMCProducer():
    def __init__(self, *args, **kwargs):

        filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_scale_mc.json"

        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        if self.isMC:
            #print("__init__ scale correction for MC")
            print(f"\nLoading scale corrections from {filename}")

            if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gInterpreter.Load("libCorrectionsWrapper.so")

            #print("\nWrapper loaded, declaring correction function")
            ROOT.gInterpreter.Declare(os.path.expandvars(
                '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_scale = MyCorrections("{os.path.expandvars(filename)}", '
                    '"NUM_Data_DEN_MC_jet_pt_scale_mc");'
            )
            #print("\nDeclaration done, defining correction function")

            if not os.getenv("_JetPtScaleMC"):
                os.environ["_JetPtScaleMC"] = "JetPtScaleMC"
                ROOT.gInterpreter.Declare("""
                    using Vfloat = ROOT::RVec<float>;
                    using Vint = ROOT::RVec<int>;
                    using Vbool = ROOT::RVec<bool>;
                    auto get_jet_pt_scale_mc(Vfloat pt, Vfloat eta, std::string syst){
                        Vfloat scale_factor;
                        
                        
                        // Applying corrections to all jets
                        for (size_t i=0; i < pt.size(); i++){
                            float scale = corr_scale.eval({eta[i], pt[i], syst});
                            scale_factor.push_back(1./scale);
                        }
                        
                        /*
                        // Applying corrections to only first two jets
                        for (size_t i=0; i < pt.size(); i++){
                            float scale = corr_scale.eval({eta[i], pt[i], syst});
                            if (i < 2) {
                                scale_factor.push_back(1./scale);
                            }
                            else {
                                scale_factor.push_back(1.0);
                            }
                        }
                        */
                        return scale_factor;
                    }
                """)
            #print("\nDefinition done")

    def run(self, df):
        if self.isMC:
            print("\nRunning scale correction to unity for MC")
            branches = ["pt_scale_corr", "pt_scale_corr_up", "pt_scale_corr_down"]
            jet_branches = []
            for branch_name, syst in zip(branches, ["sf", "systup", "systdown"]):
                df = df.Define(branch_name, """get_jet_pt_scale_mc(L1Jet_pt, L1Jet_eta, "%s")""" % syst)
                df = df.Define(f"L1Jet_{branch_name}", f"L1Jet_pt * {branch_name}")
                jet_branches.append(f"L1Jet_{branch_name}")

        else:
            branches = []
            jet_branches = []
        return df, (branches + jet_branches)

def JetPtScaleMC(**kwargs):
    return lambda: JetPtScaleMCProducer(**kwargs)

# Correcting Data to 1.0
class JetPtScaleDataProducer():
    def __init__(self, *args, **kwargs):

        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_scale_data.json"

        if "2024" in self.runPeriod:
            filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_scale_data_2024.json"
        elif "2025" in self.runPeriod:
            filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_scale_data_2025.json"
        else:
            filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_scale_data_2025.json"

        if not self.isMC:
            #print("__init__ scale correction for MC")
            print(f"\nLoading scale corrections from {filename}")

            if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gInterpreter.Load("libCorrectionsWrapper.so")

            #print("\nWrapper loaded, declaring correction function")
            ROOT.gInterpreter.Declare(os.path.expandvars(
                '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_scale = MyCorrections("{os.path.expandvars(filename)}", '
                    '"NUM_Data_DEN_MC_jet_pt_scale_data");'
            )
            #print("\nDeclaration done, defining correction function")

            if not os.getenv("_JetPtScaleData"):
                os.environ["_JetPtScaleData"] = "JetPtScaleData"
                ROOT.gInterpreter.Declare(
                """
                    using Vfloat = ROOT::RVec<float>;
                    using Vint = ROOT::RVec<int>;
                    using Vbool = ROOT::RVec<bool>;
                    auto get_jet_pt_scale_data(Vfloat pt, Vfloat eta, std::string syst){
                        Vfloat scale_factor;
                        
                        
                        // Applying corrections to all jets
                        for (size_t i=0; i < pt.size(); i++){
                            float scale = corr_scale.eval({eta[i], pt[i], syst});
                            scale_factor.push_back(1./scale);
                        }
                        
                        /*
                        // Applying corrections to only first two jets
                        for (size_t i=0; i < pt.size(); i++){
                            float scale = corr_scale.eval({eta[i], pt[i], syst});
                            if (i < 2) {
                                scale_factor.push_back(1./scale);
                            }
                            else {
                                scale_factor.push_back(1.0);
                            }
                        }
                        */
                        return scale_factor;
                    }
                """)
            #print("\nDefinition done")

    def run(self, df):
        if not self.isMC:
            print("\nRunning scale correction to unity for Data")
            branches = ["pt_scale_corr", "pt_scale_corr_up", "pt_scale_corr_down"]
            jet_branches = []
            for branch_name, syst in zip(branches, ["sf", "systup", "systdown"]):
                df = df.Define(branch_name, """get_jet_pt_scale_data(L1Jet_pt, L1Jet_eta, "%s")""" % syst)
                df = df.Define(f"L1Jet_{branch_name}", f"L1Jet_pt * {branch_name}")
                jet_branches.append(f"L1Jet_{branch_name}")
                

        else:
            branches = []
            jet_branches = []
        return df, (branches + jet_branches)

def JetPtScaleData(**kwargs):
    return lambda: JetPtScaleDataProducer(**kwargs)

# Smear MC jets to data (Done AFTER scale correction)
class JetPtResolutionProducer():
    def __init__(self, *args, **kwargs):

        filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_resolution.json"
        filename_ref = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jet_pt_resolution_ref.json"
        year = "2025"
        # TO DO: Add the data resolution json which the smear is multiplied by

        if "2024" in self.runPeriod:
            filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_resolution_2024.json"
            filename_ref = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jet_pt_resolution_ref_2024.json"
            year = "2024"
        elif "2025" in self.runPeriod:
            filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_resolution_2025.json"
            filename_ref = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jet_pt_resolution_ref_2025.json"
            year = "2025"
        else:
            filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/NUM_Data_DEN_MC_jet_pt_resolution_2025.json"
            filename_ref = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jet_pt_resolution_ref_2025.json"
            year = "2025"

        if self.isMC:
            print(f"\nLoading resolution corrections from {filename_smear}")
            print(f"Loading ref resolution from {filename_ref}")
            if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gInterpreter.Load("libCorrectionsWrapper.so")

            ROOT.gInterpreter.Declare(os.path.expandvars(
                '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_resolution = MyCorrections("{os.path.expandvars(filename_smear)}", '
                    '"NUM_Data_DEN_MC_jet_pt_resolution");'
            )
            ROOT.gInterpreter.ProcessLine(
                f'auto ref_resolution = MyCorrections("{os.path.expandvars(filename_ref)}", '
                    '"jet_pt_resolution_ref");'
            )

            if not os.getenv("_JetPtResolution"):
                os.environ["_JetPtResolution"] = "JetPtResolution"
                ROOT.gInterpreter.Declare(
                """
                    using Vfloat = ROOT::RVec<float>;
                    using Vint = ROOT::RVec<int>;
                    using Vbool = ROOT::RVec<bool>;

                    // Get the z factor for smearing 
                    Vfloat get_jet_pt_resolution_z(Vfloat pt, Vfloat eta, Vfloat phi){
                        Vfloat smear_z;
                        float z;

                        // Seed is unique for each jet for determinism
                        for (size_t i=0; i < pt.size(); i++){
                            TRandom3 jer_rand;
                            jer_rand.SetSeed(abs(static_cast<int>((eta[i] + 0.1)*phi[i]*1e4)));
                            z = jer_rand.Gaus(0.0, 1.0);
                            smear_z.push_back(z);
                        }
                        
                        return smear_z;
                    }

                    // Convert the z factor to a smearing factor
                    Vfloat get_jet_pt_smeared(Vfloat pt, Vfloat eta, Vfloat z_factor, std::string syst){
                        Vfloat jet_pt_smeared;
                        std::string default_syst = "sf";

                        for (size_t i=0; i < pt.size(); i++){
                            float scale_factor = corr_resolution.eval({eta[i], pt[i], syst});
                            float data_resolution = ref_resolution.eval({eta[i], pt[i], default_syst});
                            float width_factor = data_resolution * std::sqrt(std::max(0.0, (scale_factor * scale_factor) - 1));
                            float pt_smeared = pt[i] * std::max(0.0, 1.0 + (z_factor[i] * width_factor));
                            jet_pt_smeared.push_back(pt_smeared);
                        }
                        return jet_pt_smeared;
                    }

                """)

    def run(self, df):
        if self.isMC:
            # Up/Down scale
            branches_scale = ["pt_scale_corr_up", "pt_scale_corr_down"]
            for branch_name in branches_scale:
                df = df.Define(f"L1Jet_{branch_name}_resolution", f"""get_jet_pt_resolution(L1Jet_{branch_name}, L1Jet_eta, "sf")""")
            # Up/Down res
            branches_res = ["pt_scale_corr_resolution", "pt_scale_corr_resolution_up", "pt_scale_corr_resolution_down"]
            for branch_name, syst in zip(branches_res, ["sf", "systup", "systdown"]):
                df = df.Define(f"L1Jet_{branch_name}", """get_jet_pt_resolution(L1Jet_pt_scale_corr, L1Jet_eta, "%s")""" % syst)
        # Make some redundant branches for data which isn't smeared
        else:
            # Up/Down scale
            branches_scale = ["pt_scale_corr_up", "pt_scale_corr_down"]
            for branch_name in branches_scale:
                df = df.Define(f"L1Jet_{branch_name}_resolution", f"L1Jet_{branch_name}")
            # Up/Down res
            branches_res = ["pt_scale_corr_resolution", "pt_scale_corr_resolution_up", "pt_scale_corr_resolution_down"]
            for branch_name in branches_res:
                df = df.Define(f"L1Jet_{branch_name}",  "L1Jet_pt_scale_corr")

        branches = ["L1Jet_pt_scale_corr_resolution", "L1Jet_pt_scale_corr_up_resolution", "L1Jet_pt_scale_corr_down_resolution", "L1Jet_pt_scale_corr_resolution_up", "L1Jet_pt_scale_corr_resolution_down"]
        return df, branches

def JetPtResolution(**kwargs):
    return lambda: JetPtResolutionProducer(**kwargs)


##### Doing things with the corrected pT #####
# Reshuffle the jets 
class JetPtReshuffleProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        # Manually defining the order subtraction
        ROOT.gInterpreter.Declare(
        """
            using Vfloat = ROOT::RVec<float>;
            using Vul = ROOT::RVec<unsigned long>;
            using Vbool = ROOT::RVec<bool>;
            Vint get_order_shift(Vul order_orig, Vul order_new){
                Vint order_shift_vec;
                for (size_t i=0; i < order_orig.size(); i++){
                    int order_shift = static_cast<int>(order_new[i]) - static_cast<int>(order_orig[i]);
                    order_shift_vec.push_back(order_shift);
                }
                return order_shift_vec;
            }
        """)

    def run(self, df):
        # Sort jets by uncorrected pT
        df = df.Define("L1Jet_pt_order", "Reverse(Argsort(L1Jet_pt))")
        df = df.Redefine("L1Jet_pt", "Take(L1Jet_pt, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_eta", "Take(L1Jet_eta, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_phi", "Take(L1Jet_phi, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_pt_scale_corr", "Take(L1Jet_pt_scale_corr, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_up", "Take(L1Jet_pt_scale_corr_up, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_down", "Take(L1Jet_pt_scale_corr_down, L1Jet_pt_order)")

        # Get the starting order
        df = df.Redefine("L1Jet_pt_order", "Reverse(Argsort(L1Jet_pt))")

        # Get the order of the scale corrected jets
        df = df.Define("L1Jet_pt_scale_corr_order", "Reverse(Argsort(L1Jet_pt_scale_corr))")

        # Get the order difference wrt to the starting order
        df = df.Define("L1Jet_pt_scale_corr_order_shift", "get_order_shift(L1Jet_pt_order, L1Jet_pt_scale_corr_order)")

        return df, ["L1Jet_pt_order", "L1Jet_pt_scale_corr_order", "L1Jet_pt_scale_corr_order_shift"]


def JetPtReshuffle(**kwargs):
    return lambda: JetPtReshuffleProducer(**kwargs)

# Reorder the jets according to scale corrected pT
class JetPtReshuffleReorderProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

    def run(self, df):
        # Sort jets by pT
        df = df.Define("L1Jet_eta_scale_corr", "Take(L1Jet_eta, L1Jet_pt_scale_corr_order)")
        df = df.Define("L1Jet_phi_scale_corr", "Take(L1Jet_phi, L1Jet_pt_scale_corr_order)")
        df = df.Redefine("L1Jet_pt_scale_corr", "Take(L1Jet_pt_scale_corr, L1Jet_pt_scale_corr_order)")

        return df, ["L1Jet_eta_scale_corr", "L1Jet_phi_scale_corr", "L1Jet_pt_scale_corr"]
    
def JetPtReshuffleReorder(**kwargs):
    return lambda: JetPtReshuffleReorderProducer(**kwargs)