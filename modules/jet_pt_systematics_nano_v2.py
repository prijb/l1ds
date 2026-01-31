# New version of Jet pT scale and resolution corrections
import os

from Corrections.JME.PUjetID_SF import PUjetID_SFRDFProducer
from analysis_tools.utils import import_root

ROOT = import_root()
import correctionlib
correctionlib.register_pyroot_binding()

# Correcting jet scale
class JetPtScaleProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = "data/dummy.json"

        if self.isMC:
            print("\nSample: MC")
            filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_scale_mc.json"
        else:
            print("\nSample: Data")
            if "2024" in self.runPeriod:
                print("Year: 2024")
                filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_scale_data_2024.json" 
            elif "2025" in self.runPeriod:
                print("Year: 2025")
                filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_scale_data_2025.json"
            else:
                print("No year specified, falling back to 2025")
                filename = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_scale_data_2025.json"


        print(f"Loading scale corrections from {filename}") 

        if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
            ROOT.gInterpreter.Load("libCorrectionsWrapper.so")

        ROOT.gInterpreter.Declare(os.path.expandvars(
            '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
        ROOT.gInterpreter.ProcessLine(
            f'auto corr_scale = MyCorrections("{os.path.expandvars(filename)}", '
                '"L1JES");'
        )

        if not os.getenv("_JetPtScaleData"):
            os.environ["_JetPtScaleData"] = "JetPtScaleData"
            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;
                auto get_jet_pt_scale(Vfloat pt, Vfloat eta, std::string syst){
                    Vfloat scale_factor;
                    
                    // Applying corrections to all jets with pT >= 20
                    for (size_t i=0; i < pt.size(); i++){
                        float scale = corr_scale.eval({eta[i], pt[i], syst});
                        if (pt[i] >= 20) {
                            scale_factor.push_back(1./scale); 
                        }
                        else{
                            scale_factor.push_back(1.0);  
                        }
                    }
                    return scale_factor;
                }
            """)

    def run(self, df):
        branches = ["pt_scale_corr", "pt_scale_corr_up", "pt_scale_corr_down"]
        jet_branches = []
        for branch_name, syst in zip(branches, ["sf", "systup", "systdown"]):
            df = df.Define(branch_name, """get_jet_pt_scale(L1Jet_pt, L1Jet_eta, "%s")""" % syst)
            df = df.Define(f"L1Jet_{branch_name}", f"L1Jet_pt * {branch_name}")
            jet_branches.append(f"L1Jet_{branch_name}")

        return df, jet_branches

def JetPtScale(**kwargs):
    return lambda: JetPtScaleProducer(**kwargs)

# Smear MC jets to data (Done AFTER scale correction)
class JetPtResolutionProducer():
    def __init__(self, *args, **kwargs):

        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename_ref = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_mc.json"
        filename_sf = "data/dummy_sf.json"
        filename_smear = "data/dummy_smear.json"

        if "2024" in self.runPeriod:
            print("Year: 2024")
            filename_sf = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_sf_2024.json"
            filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_smear_2024.json"
        elif "2025" in self.runPeriod:
            print("Year: 2025")
            filename_sf = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_sf_2025.json"
            filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_smear_2025.json"
        else:
            print("No year specified, falling back to 2025")
            filename_sf = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_sf_2025.json"
            filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_smear_2025.json"

        if self.isMC:
            print(f"Loading resolution corrections for year: {self.runPeriod}")
            
            if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gInterpreter.Load("libCorrectionsWrapper.so")
            ROOT.gInterpreter.Declare(os.path.expandvars(
                '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
            
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_ref = MyCorrections("{os.path.expandvars(filename_ref)}", '
                    '"L1JER");'
            )
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_sf = MyCorrections("{os.path.expandvars(filename_sf)}", '
                    '"L1JERSF");'
            )
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_smear = MyCorrections("{os.path.expandvars(filename_smear)}", '
                    '"L1JERSmear");'
            )

            if not os.getenv("_JetPtResolution"):
                os.environ["_JetPtResolution"] = "JetPtResolution"
                ROOT.gInterpreter.Declare(
                """
                    using Vfloat = ROOT::RVec<float>;
                    using Vint = ROOT::RVec<int>;
                    using Vbool = ROOT::RVec<bool>;

                    // Get the reference resolution
                    Vfloat get_jet_pt_resolution_ref(Vfloat pt, Vfloat eta){
                        Vfloat pt_resolution_ref;

                        for (size_t i=0; i < pt.size(); i++){
                            float resolution_ref = corr_ref.eval({eta[i], pt[i]});
                            pt_resolution_ref.push_back(resolution_ref); 
                        }
                        return pt_resolution_ref;
                    }

                    // Get the scale factor for smearing
                    Vfloat get_jet_pt_resolution_sf(Vfloat pt, Vfloat eta, std::string syst){
                        Vfloat pt_resolution_sf;

                        for (size_t i=0; i < pt.size(); i++){
                            float resolution_sf = corr_sf.eval({eta[i], pt[i], syst});
                            pt_resolution_sf.push_back(resolution_sf);
                        }
                        return pt_resolution_sf;
                    }

                    // Smear the jets using the above two inputs (cast event id to float)
                    Vfloat get_jet_pt_resolution_smear(Vfloat pt, Vfloat eta, Vfloat jer, Vfloat jersf, ULong64_t eventid){
                        Vfloat pt_resolution_smear;

                        // Applying corrections to all jets with pT > 20
                        for (size_t i=0; i < pt.size(); i++){
                            float smear = corr_smear.eval({eta[i], pt[i], jer[i], jersf[i], 1.0, (double)eventid});
                            if (pt[i] >= 20) {
                                pt_resolution_smear.push_back(smear); 
                            }
                            else{
                                pt_resolution_smear.push_back(1.0);  
                            }
                        }
                        return pt_resolution_smear;
                    }
                """)

    def run(self, df):
        if self.isMC:
            # Up/Down scale to nominal res
            branches_scale = ["pt_scale_corr_up", "pt_scale_corr_down"]
            for branch_name in branches_scale:
                df = df.Define(f"{branch_name}_resolution_ref", f"""get_jet_pt_resolution_ref(L1Jet_{branch_name}, L1Jet_eta)""")
                df = df.Define(f"{branch_name}_resolution_sf", f"""get_jet_pt_resolution_sf(L1Jet_{branch_name}, L1Jet_eta, "sf")""")
                df = df.Define(f"{branch_name}_resolution_smear", f"""get_jet_pt_resolution_smear(L1Jet_{branch_name}, L1Jet_eta, {branch_name}_resolution_ref, {branch_name}_resolution_sf, event)""")
                df = df.Define(f"L1Jet_{branch_name}_resolution_smear", f"L1Jet_{branch_name} * {branch_name}_resolution_smear")

            # Nominal scale to Up/Down res
            df = df.Define(f"pt_scale_corr_resolution_ref", f"""get_jet_pt_resolution_ref(L1Jet_pt_scale_corr, L1Jet_eta)""")
            branches_res = ["resolution_smear", "resolution_smear_up", "resolution_smear_down"]
            for branch_name, syst in zip(branches_res, ["sf", "systup", "systdown"]):
                df = df.Define(f"pt_scale_corr_{branch_name.replace('smear', 'sf')}", """get_jet_pt_resolution_sf(L1Jet_pt_scale_corr, L1Jet_eta, "%s")"""%syst)
                df = df.Define(f"pt_scale_corr_{branch_name}", f"""get_jet_pt_resolution_smear(L1Jet_pt_scale_corr, L1Jet_eta, pt_scale_corr_resolution_ref, pt_scale_corr_{branch_name.replace('smear', 'sf')}, event)""")
                df = df.Define(f"L1Jet_pt_scale_corr_{branch_name}", f"L1Jet_pt_scale_corr * pt_scale_corr_{branch_name}")

        # Make some redundant branches for data which isn't smeared
        else:
            print("\nRunning on data, no smearing applied")
            # Up/Down scale to nominal res
            branches_scale = ["pt_scale_corr_up", "pt_scale_corr_down"]
            for branch_name in branches_scale:
                df = df.Define(f"{branch_name}_resolution_ref", "L1Jet_pt")
                df = df.Define(f"{branch_name}_resolution_sf", "L1Jet_pt")
                df = df.Define(f"{branch_name}_resolution_smear", f"L1Jet_pt")
                df = df.Define(f"L1Jet_{branch_name}_resolution_smear", f"L1Jet_{branch_name}")

            # Nominal scale to Up/Down res
            df = df.Define(f"pt_scale_corr_resolution_ref", f"L1Jet_pt")
            branches_res = ["resolution_smear", "resolution_smear_up", "resolution_smear_down"]
            for branch_name, syst in zip(branches_res, ["sf", "systup", "systdown"]):
                df = df.Define(f"pt_scale_corr_{branch_name.replace('smear', 'sf')}", f"L1Jet_pt")
                df = df.Define(f"pt_scale_corr_{branch_name}", f"L1Jet_pt")
                df = df.Define(f"L1Jet_pt_scale_corr_{branch_name}", f"L1Jet_pt_scale_corr")

        # Add the branches
        branches = ["L1Jet_pt_scale_corr_resolution_smear", "L1Jet_pt_scale_corr_up_resolution_smear", "L1Jet_pt_scale_corr_down_resolution_smear", "L1Jet_pt_scale_corr_resolution_smear_up", "L1Jet_pt_scale_corr_resolution_smear_down"]
        return df, branches
        
def JetPtResolution(**kwargs):
    return lambda: JetPtResolutionProducer(**kwargs)

# Smear MC jets to data with manual random seed generation (Done AFTER scale correction)
class JetPtResolutionAltProducer():
    def __init__(self, *args, **kwargs):

        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename_ref = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_mc.json"
        filename_sf = "data/dummy_sf.json"
        filename_smear = "data/dummy_smear.json"

        if "2024" in self.runPeriod:
            print("Year: 2024")
            filename_sf = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_sf_2024.json"
            filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_smear_2024.json"
        elif "2025" in self.runPeriod:
            print("Year: 2025")
            filename_sf = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_sf_2025.json"
            filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_smear_2025.json"
        else:
            print("No year specified, falling back to 2025")
            filename_sf = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_sf_2025.json"
            filename_smear = "/vols/cms/pb4918/L1Scouting/Sep25/l1ds/data/jec_290126/jet_pt_resolution_smear_2025.json"

        if self.isMC:
            print(f"Loading resolution corrections for year: {self.runPeriod}")
            
            if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gInterpreter.Load("libCorrectionsWrapper.so")
            ROOT.gInterpreter.Declare(os.path.expandvars(
                '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
            
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_ref = MyCorrections("{os.path.expandvars(filename_ref)}", '
                    '"L1JER");'
            )
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_sf = MyCorrections("{os.path.expandvars(filename_sf)}", '
                    '"L1JERSF");'
            )
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_smear = MyCorrections("{os.path.expandvars(filename_smear)}", '
                    '"L1JERSmear");'
            )

            if not os.getenv("_JetPtResolutionAlt"):
                os.environ["_JetPtResolutionAlt"] = "JetPtResolutionAlt"

                # Introduce an RNG seed to bypass correctionlib's lack of support for HashPRNG for CMSSW_13_0_13
                ROOT.gInterpreter.Declare(
                """
                #include <random>
                #include <cmath>
                #include <cstdint>

                static inline uint64_t mix64(uint64_t x){
                    x ^= x >> 33; x *= 0xff51afd7ed558ccdULL;
                    x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL;
                    x ^= x >> 33; return x;
                }

                float stable_gauss(ULong64_t eventid, float eta, float phi){
                    int64_t eta_q = llround((double)eta * 1e6);
                    int64_t phi_q = llround((double)phi * 1e6);

                    uint64_t seed = (uint64_t)eventid;
                    seed ^= mix64((uint64_t)eta_q);
                    seed ^= mix64((uint64_t)phi_q);

                    std::mt19937_64 gen(seed);
                    std::normal_distribution<double> nd(0.0, 1.0);
                    return (float)nd(gen);
                }
                """)

                ROOT.gInterpreter.Declare(
                """
                    using Vfloat = ROOT::RVec<float>;
                    using Vint = ROOT::RVec<int>;
                    using Vbool = ROOT::RVec<bool>;

                    // Get the rept_scale_corr_resolution_refference resolution
                    Vfloat get_jet_pt_resolution_ref(Vfloat pt, Vfloat eta){
                        Vfloat pt_resolution_ref;

                        for (size_t i=0; i < pt.size(); i++){
                            float resolution_ref = corr_ref.eval({eta[i], pt[i]});
                            pt_resolution_ref.push_back(resolution_ref); 
                        }
                        return pt_resolution_ref;
                    }

                    // Get the scale factor for smearing
                    Vfloat get_jet_pt_resolution_sf(Vfloat pt, Vfloat eta, std::string syst){
                        Vfloat pt_resolution_sf;

                        for (size_t i=0; i < pt.size(); i++){
                            float resolution_sf = corr_sf.eval({eta[i], pt[i], syst});
                            pt_resolution_sf.push_back(resolution_sf);
                        }
                        return pt_resolution_sf;
                    }

                    // Smear the jets using the above two inputs (cast event id to float)
                    Vfloat get_jet_pt_resolution_smear(Vfloat pt, Vfloat eta, Vfloat phi, Vfloat jer, Vfloat jersf, ULong64_t eventid){
                        Vfloat pt_resolution_smear;

                        // Applying corrections to all jets with pT > 20
                        for (size_t i=0; i < pt.size(); i++){
                            //Get the random factor
                            float rand = stable_gauss(eventid, eta[i], phi[i]);
                            float smear = corr_smear.eval({jer[i], jersf[i], rand});
                            if (pt[i] >= 20) {
                                pt_resolution_smear.push_back(smear); 
                            }
                            else{
                                pt_resolution_smear.push_back(1.0);  
                            }
                        }
                        return pt_resolution_smear;
                    }
                """)

    def run(self, df):
        if self.isMC:
            # Up/Down scale to nominal res
            branches_scale = ["pt_scale_corr_up", "pt_scale_corr_down"]
            for branch_name in branches_scale:
                df = df.Define(f"{branch_name}_resolution_ref", f"""get_jet_pt_resolution_ref(L1Jet_{branch_name}, L1Jet_eta)""")
                df = df.Define(f"{branch_name}_resolution_sf", f"""get_jet_pt_resolution_sf(L1Jet_{branch_name}, L1Jet_eta, "sf")""")
                df = df.Define(f"{branch_name}_resolution_smear", f"""get_jet_pt_resolution_smear(L1Jet_{branch_name}, L1Jet_eta, L1Jet_phi, {branch_name}_resolution_ref, {branch_name}_resolution_sf, event)""")
                df = df.Define(f"L1Jet_{branch_name}_resolution_smear", f"L1Jet_{branch_name} * {branch_name}_resolution_smear")

            # Nominal scale to Up/Down res
            df = df.Define(f"pt_scale_corr_resolution_ref", f"""get_jet_pt_resolution_ref(L1Jet_pt_scale_corr, L1Jet_eta)""")
            branches_res = ["resolution_smear", "resolution_smear_up", "resolution_smear_down"]
            for branch_name, syst in zip(branches_res, ["sf", "systup", "systdown"]):
                df = df.Define(f"pt_scale_corr_{branch_name.replace('smear', 'sf')}", """get_jet_pt_resolution_sf(L1Jet_pt_scale_corr, L1Jet_eta, "%s")"""%syst)
                df = df.Define(f"pt_scale_corr_{branch_name}", f"""get_jet_pt_resolution_smear(L1Jet_pt_scale_corr, L1Jet_eta, L1Jet_phi, pt_scale_corr_resolution_ref, pt_scale_corr_{branch_name.replace('smear', 'sf')}, event)""")
                df = df.Define(f"L1Jet_pt_scale_corr_{branch_name}", f"L1Jet_pt_scale_corr * pt_scale_corr_{branch_name}")

        # Make some redundant branches for data which isn't smeared
        else:
            print("\nRunning on data, no smearing applied")
            # Up/Down scale to nominal res
            branches_scale = ["pt_scale_corr_up", "pt_scale_corr_down"]
            for branch_name in branches_scale:
                df = df.Define(f"{branch_name}_resolution_ref", "L1Jet_pt")
                df = df.Define(f"{branch_name}_resolution_sf", "L1Jet_pt")
                df = df.Define(f"{branch_name}_resolution_smear", f"L1Jet_pt")
                df = df.Define(f"L1Jet_{branch_name}_resolution_smear", f"L1Jet_{branch_name}")

            # Nominal scale to Up/Down res
            df = df.Define(f"pt_scale_corr_resolution_ref", f"L1Jet_pt")
            branches_res = ["resolution_smear", "resolution_smear_up", "resolution_smear_down"]
            for branch_name, syst in zip(branches_res, ["sf", "systup", "systdown"]):
                df = df.Define(f"pt_scale_corr_{branch_name.replace('smear', 'sf')}", f"L1Jet_pt")
                df = df.Define(f"pt_scale_corr_{branch_name}", f"L1Jet_pt")
                df = df.Define(f"L1Jet_pt_scale_corr_{branch_name}", f"L1Jet_pt_scale_corr")

        # Add the branches
        branches = ["L1Jet_pt_scale_corr_resolution_smear", "L1Jet_pt_scale_corr_up_resolution_smear", "L1Jet_pt_scale_corr_down_resolution_smear", "L1Jet_pt_scale_corr_resolution_smear_up", "L1Jet_pt_scale_corr_resolution_smear_down"]
        return df, branches

def JetPtResolutionAlt(**kwargs):
    return lambda: JetPtResolutionAltProducer(**kwargs)

##### Doing things with the corrected pT #####
# Reshuffle the jets after only scaling
class JetPtReshuffleScaleProducer():
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
        df = df.Define("L1Jet_pt_scale_corr_up_order", "Reverse(Argsort(L1Jet_pt_scale_corr_up))")
        df = df.Define("L1Jet_pt_scale_corr_down_order", "Reverse(Argsort(L1Jet_pt_scale_corr_down))")

        # Get the order difference wrt to the starting order
        df = df.Define("L1Jet_pt_scale_corr_order_shift", "get_order_shift(L1Jet_pt_order, L1Jet_pt_scale_corr_order)")

        # Reorder the jets according to the scale corrected pT
        df = df.Define("L1Jet_eta_scale_corr", "Take(L1Jet_eta, L1Jet_pt_scale_corr_order)")
        df = df.Define("L1Jet_phi_scale_corr", "Take(L1Jet_phi, L1Jet_pt_scale_corr_order)")
        df = df.Redefine("L1Jet_pt_scale_corr", "Take(L1Jet_pt_scale_corr, L1Jet_pt_scale_corr_order)")
        # Up
        df = df.Define("L1Jet_eta_scale_corr_up", "Take(L1Jet_eta, L1Jet_pt_scale_corr_up_order)")
        df = df.Define("L1Jet_phi_scale_corr_up", "Take(L1Jet_phi, L1Jet_pt_scale_corr_up_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_up", "Take(L1Jet_pt_scale_corr_up, L1Jet_pt_scale_corr_up_order)")
        # Down
        df = df.Define("L1Jet_eta_scale_corr_down", "Take(L1Jet_eta, L1Jet_pt_scale_corr_down_order)")
        df = df.Define("L1Jet_phi_scale_corr_down", "Take(L1Jet_phi, L1Jet_pt_scale_corr_down_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_down", "Take(L1Jet_pt_scale_corr_down, L1Jet_pt_scale_corr_down_order)")

        return df, ["L1Jet_pt_order", "L1Jet_pt_scale_corr_order", "L1Jet_pt_scale_corr_order_shift", "L1Jet_eta_scale_corr", "L1Jet_phi_scale_corr", "L1Jet_pt_scale_corr", "L1Jet_eta_scale_corr_up", "L1Jet_phi_scale_corr_up", "L1Jet_pt_scale_corr_up","L1Jet_eta_scale_corr_down", "L1Jet_phi_scale_corr_down", "L1Jet_pt_scale_corr_down"]


def JetPtReshuffleScale(**kwargs):
    return lambda: JetPtReshuffleScaleProducer(**kwargs)

# Reshuffle the jets after both scaling and smearing
class JetPtReshuffleScaleResolutionProducer():
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
        df = df.Redefine("L1Jet_pt_scale_corr_resolution_smear", "Take(L1Jet_pt_scale_corr_resolution_smear, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_up_resolution_smear", "Take(L1Jet_pt_scale_corr_up_resolution_smear, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_down_resolution_smear", "Take(L1Jet_pt_scale_corr_down_resolution_smear, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_resolution_smear_up", "Take(L1Jet_pt_scale_corr_resolution_smear_up, L1Jet_pt_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_resolution_smear_down", "Take(L1Jet_pt_scale_corr_resolution_smear_down, L1Jet_pt_order)")

        # Get the starting order
        df = df.Redefine("L1Jet_pt_order", "Reverse(Argsort(L1Jet_pt))")

        # Get the order of the scale corrected jets
        df = df.Define("L1Jet_pt_scale_corr_resolution_smear_order", "Reverse(Argsort(L1Jet_pt_scale_corr_resolution_smear))")
        df = df.Define("L1Jet_pt_scale_corr_up_resolution_smear_order", "Reverse(Argsort(L1Jet_pt_scale_corr_up_resolution_smear))")
        df = df.Define("L1Jet_pt_scale_corr_down_resolution_smear_order", "Reverse(Argsort(L1Jet_pt_scale_corr_down_resolution_smear))")
        df = df.Define("L1Jet_pt_scale_corr_resolution_smear_up_order", "Reverse(Argsort(L1Jet_pt_scale_corr_resolution_smear_up))")
        df = df.Define("L1Jet_pt_scale_corr_resolution_smear_down_order", "Reverse(Argsort(L1Jet_pt_scale_corr_resolution_smear_down))")

        # Get the order difference wrt to the starting order
        df = df.Define("L1Jet_pt_scale_corr_resolution_smear_order_shift", "get_order_shift(L1Jet_pt_order, L1Jet_pt_scale_corr_resolution_smear_order)")

        # Reorder the jets according to the scale corrected pT
        df = df.Define("L1Jet_eta_scale_corr_resolution_smear", "Take(L1Jet_eta, L1Jet_pt_scale_corr_resolution_smear_order)")
        df = df.Define("L1Jet_phi_scale_corr_resolution_smear", "Take(L1Jet_phi, L1Jet_pt_scale_corr_resolution_smear_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_resolution_smear", "Take(L1Jet_pt_scale_corr_resolution_smear, L1Jet_pt_scale_corr_resolution_smear_order)")
        # Scale up
        df = df.Define("L1Jet_eta_scale_corr_up_resolution_smear", "Take(L1Jet_eta, L1Jet_pt_scale_corr_up_resolution_smear_order)")
        df = df.Define("L1Jet_phi_scale_corr_up_resolution_smear", "Take(L1Jet_phi, L1Jet_pt_scale_corr_up_resolution_smear_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_up_resolution_smear", "Take(L1Jet_pt_scale_corr_up_resolution_smear, L1Jet_pt_scale_corr_up_resolution_smear_order)")
        # Scale down
        df = df.Define("L1Jet_eta_scale_corr_down_resolution_smear", "Take(L1Jet_eta, L1Jet_pt_scale_corr_down_resolution_smear_order)")
        df = df.Define("L1Jet_phi_scale_corr_down_resolution_smear", "Take(L1Jet_phi, L1Jet_pt_scale_corr_down_resolution_smear_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_down_resolution_smear", "Take(L1Jet_pt_scale_corr_down_resolution_smear, L1Jet_pt_scale_corr_down_resolution_smear_order)")
        # Smear up
        df = df.Define("L1Jet_eta_scale_corr_resolution_smear_up", "Take(L1Jet_eta, L1Jet_pt_scale_corr_resolution_smear_up_order)")
        df = df.Define("L1Jet_phi_scale_corr_resolution_smear_up", "Take(L1Jet_phi, L1Jet_pt_scale_corr_resolution_smear_up_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_resolution_smear_up", "Take(L1Jet_pt_scale_corr_resolution_smear_up, L1Jet_pt_scale_corr_resolution_smear_up_order)")
        # Smear Down
        df = df.Define("L1Jet_eta_scale_corr_resolution_smear_down", "Take(L1Jet_eta, L1Jet_pt_scale_corr_resolution_smear_down_order)")
        df = df.Define("L1Jet_phi_scale_corr_resolution_smear_down", "Take(L1Jet_phi, L1Jet_pt_scale_corr_resolution_smear_down_order)")
        df = df.Redefine("L1Jet_pt_scale_corr_resolution_smear_down", "Take(L1Jet_pt_scale_corr_resolution_smear_down, L1Jet_pt_scale_corr_resolution_smear_down_order)")

        branches_nominal = ["L1Jet_pt_order", "L1Jet_pt_scale_corr_resolution_smear_order", "L1Jet_pt_scale_corr_resolution_smear_order_shift", "L1Jet_pt_scale_corr_resolution_smear", "L1Jet_eta_scale_corr_resolution_smear", "L1Jet_phi_scale_corr_resolution_smear"]
        branches_scale_up_smear_nominal = ["L1Jet_pt_scale_corr_up_resolution_smear", "L1Jet_eta_scale_corr_up_resolution_smear", "L1Jet_phi_scale_corr_up_resolution_smear"]
        branches_scale_down_smear_nominal = ["L1Jet_pt_scale_corr_down_resolution_smear", "L1Jet_eta_scale_corr_down_resolution_smear", "L1Jet_phi_scale_corr_down_resolution_smear"]
        branches_scale_nominal_smear_up = ["L1Jet_pt_scale_corr_resolution_smear_up", "L1Jet_eta_scale_corr_resolution_smear_up", "L1Jet_phi_scale_corr_resolution_smear_up"]
        branches_scale_nominal_smear_down = ["L1Jet_pt_scale_corr_resolution_smear_down", "L1Jet_eta_scale_corr_resolution_smear_down", "L1Jet_phi_scale_corr_resolution_smear_down"]

        return df, (branches_nominal + branches_scale_up_smear_nominal + branches_scale_down_smear_nominal + branches_scale_nominal_smear_up + branches_scale_nominal_smear_down)


def JetPtReshuffleScaleResolution(**kwargs):
    return lambda: JetPtReshuffleScaleResolutionProducer(**kwargs)