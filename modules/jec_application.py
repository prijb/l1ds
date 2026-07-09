# Script for applying JECs
import os

from Corrections.JME.PUjetID_SF import PUjetID_SFRDFProducer
from analysis_tools.utils import import_root

ROOT = import_root()

import correctionlib
correctionlib.register_pyroot_binding()

"""
# Lazy correctionlib fix (need to be more robust)
# Fix is for CMSSW_14_1_0_pre4 -> Try without fix for CMSSW_15_0_10
from pathlib import Path
import correctionlib
from cppyy import gbl

base = Path(correctionlib.__file__).resolve().parent
lib = base / "lib" / "libcorrectionlib.so"
inc = base / "include"

ret = gbl.gSystem.Load(str(lib))
print("libcorrectionlib load return:", ret)
gbl.gInterpreter.AddIncludePath(str(inc))
gbl.gROOT.ProcessLine('#include "correction.h"')
"""


############### Offline corrections ###############
# Scale
class RecoJetPtScaleProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = None
        jerctag = None
        jercunctag = None

        # Select the JEC file (MC is corrected to 2024 by default)
        if (self.runPeriod == "2024") or self.isMC:
            filename = f"{os.environ['CMT_BASE']}/../data/offline_jec/jet_2024_jerc_v3.json"
            jerctag = "Summer24Prompt24_V3"
            jercunctag = "Summer24Prompt24_V3_MC"
        elif self.runPeriod == "2025":
            filename = f"{os.environ['CMT_BASE']}/../data/offline_jec/jet_2025_jerc_v3.json"
            jerctag = "Winter25Prompt25_V3"
            jercunctag = "Winter25Prompt25_V3_MC"
        else:
            print("No year specified, falling back to 2025")
            filename = f"{os.environ['CMT_BASE']}/../data/offline_jec/jet_2025_jerc_v3.json"
            jerctag = "Winter25Prompt25_V3"
            jercunctag = "Winter25Prompt25_V3_MC"

        # Add data vs MC tag
        if self.isMC:
            jerctag += "_MC"
        else:
            jerctag += "_DATA"

        print(f"Loading offline scale corrections from {filename} with tag {jerctag}")

        if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
            ROOT.gInterpreter.Load("libCorrectionsWrapper.so")

        ROOT.gInterpreter.Declare(os.path.expandvars(
            '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
        # Load the corrections
        ROOT.gInterpreter.ProcessLine(
            f'auto corr_l1fastjet = MyCorrections("{os.path.expandvars(filename)}", "{jerctag}_L1FastJet_AK4PFPuppi");'
        )
        ROOT.gInterpreter.ProcessLine(
            f'auto corr_l2relative = MyCorrections("{os.path.expandvars(filename)}", "{jerctag}_L2Relative_AK4PFPuppi");'
        )
        ROOT.gInterpreter.ProcessLine(
            f'auto corr_l3absolute = MyCorrections("{os.path.expandvars(filename)}", "{jerctag}_L3Absolute_AK4PFPuppi");'
        )
        ROOT.gInterpreter.ProcessLine(
            f'auto corr_l2l3residual = MyCorrections("{os.path.expandvars(filename)}", "{jerctag}_L2L3Residual_AK4PFPuppi");'
        )
        # Uncertainty on JES
        ROOT.gInterpreter.ProcessLine(
            f'auto corr_jes_unc = MyCorrections("{os.path.expandvars(filename)}", "{jercunctag}_Regrouped_Total_AK4PFPuppi");'
        )

        if not os.getenv("_RecoJetPtScale"):
            os.environ["_RecoJetPtScale"] = "RecoJetPtScale"
            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;

                // Get the raw pT of the reco jet
                auto get_jet_pt_raw(Vfloat Jet_pt, Vfloat Jet_rawFactor){
                    Vfloat jet_pt_raw;

                    for (size_t i=0; i < Jet_pt.size(); i++){
                        float rawfactor = Jet_rawFactor[i];
                        jet_pt_raw.push_back(Jet_pt[i] * (1.0 - rawfactor));
                    }

                    return jet_pt_raw;
                }

                // Takes raw pT
                auto get_jet_pt_l1fastjet(Vfloat Jet_area, Vfloat Jet_eta, Vfloat Jet_pt, float Rho){
                    Vfloat jet_pt_l1fastjet;

                    // Apply L1 (pileup) corrections to jets
                    for (size_t i=0; i < Jet_pt.size(); i++){
                        float scale = corr_l1fastjet.eval({Jet_area[i], Jet_eta[i], Jet_pt[i], Rho});
                        jet_pt_l1fastjet.push_back(Jet_pt[i] * scale);
                    }

                    return jet_pt_l1fastjet;
                }

                // Takes L1 corrected pT
                auto get_jet_pt_l2relative(Vfloat Jet_eta, Vfloat Jet_phi, Vfloat Jet_pt){
                    Vfloat jet_pt_l2relative;

                    // Apply L2 corrections to jets
                    for (size_t i=0; i < Jet_pt.size(); i++){
                        float scale = corr_l2relative.eval({Jet_eta[i], Jet_phi[i], Jet_pt[i]});
                        jet_pt_l2relative.push_back(Jet_pt[i] * scale);
                    }

                    return jet_pt_l2relative;
                }

                // Takes L2 corrected pT
                auto get_jet_pt_l3absolute(Vfloat Jet_eta, Vfloat Jet_pt){
                    Vfloat jet_pt_l3absolute;

                    // Apply L3 corrections to jets
                    for (size_t i=0; i < Jet_pt.size(); i++){
                        float scale = corr_l3absolute.eval({Jet_eta[i], Jet_pt[i]});
                        jet_pt_l3absolute.push_back(Jet_pt[i] * scale);
                    }

                    return jet_pt_l3absolute;
                }

                // Takes L3 corrected pT
                auto get_jet_pt_l2l3residual_data(float run, Vfloat Jet_eta, Vfloat Jet_pt){
                    Vfloat jet_pt_l2l3residual;

                    // Apply residual corrections for data jets
                    for (size_t i=0; i < Jet_pt.size(); i++){
                        float scale = corr_l2l3residual.eval({float(run), Jet_eta[i], Jet_pt[i]});
                        jet_pt_l2l3residual.push_back(Jet_pt[i] * scale);
                    }

                    return jet_pt_l2l3residual;
                }

                // Takes L3 corrected pT
                auto get_jet_pt_l2l3residual_mc(float run, Vfloat Jet_eta, Vfloat Jet_pt){
                    Vfloat jet_pt_l2l3residual;

                    // Apply residual corrections for MC jets (should be trivial)
                    for (size_t i=0; i < Jet_pt.size(); i++){
                        float scale = corr_l2l3residual.eval({Jet_eta[i], Jet_pt[i]});
                        jet_pt_l2l3residual.push_back(Jet_pt[i] * scale);
                        // DEBUG
                        //std::cout << "Scale correction for MC L2L3Residual: " << scale << std::endl;
                    }

                    return jet_pt_l2l3residual;
                }

                // Get the jet pT variations due to systematic uncertainties 
                auto get_jet_pt_jes_var(Vfloat Jet_pt_nom, Vfloat Jet_eta, std::string syst){
                    Vfloat jet_pt_var;

                    for (size_t i = 0; i < Jet_pt_nom.size(); i++){
                        float unc = corr_jes_unc.eval({Jet_eta[i], Jet_pt_nom[i]});

                        if (syst == "up"){
                            jet_pt_var.push_back(Jet_pt_nom[i] * (1.0 + unc));
                        }
                        else if (syst == "down"){
                            jet_pt_var.push_back(Jet_pt_nom[i] * (1.0 - unc));
                        }
                        else{
                            jet_pt_var.push_back(Jet_pt_nom[i]);
                        }
                    }

                    return jet_pt_var;
                }
            """)
    
    def run(self, df):
        df = df.Define("Jet_pt_raw", "get_jet_pt_raw(Jet_pt, Jet_rawFactor)")
        df = df.Define("Jet_pt_orig", "Jet_pt")
        df = df.Redefine("Jet_pt", "get_jet_pt_l1fastjet(Jet_area, Jet_eta, Jet_pt_raw, Rho_fixedGridRhoFastjetAll)")
        df = df.Redefine("Jet_pt", "get_jet_pt_l2relative(Jet_eta, Jet_phi, Jet_pt)")
        df = df.Redefine("Jet_pt", "get_jet_pt_l3absolute(Jet_eta, Jet_pt)")
        # Residual corrections are only for data
        #if not self.isMC:
        #    print("\nApplying L2L3 residual corrections to data")
        if self.isMC:
            df = df.Redefine("Jet_pt", "get_jet_pt_l2l3residual_mc(run, Jet_eta, Jet_pt)")
        else:

            df = df.Redefine("Jet_pt", "get_jet_pt_l2l3residual_data(run, Jet_eta, Jet_pt)")
        # Add systematic vartions
        df = df.Define('Jet_pt_OfflineJESUp', 'get_jet_pt_jes_var(Jet_pt, Jet_eta, "up")')
        df = df.Define('Jet_pt_OfflineJESDown', 'get_jet_pt_jes_var(Jet_pt, Jet_eta, "down")')


        return df, ["Jet_pt_raw", "Jet_pt_orig", "Jet_pt", "Jet_pt_OfflineJESUp", "Jet_pt_OfflineJESDown"]

def RecoJetPtScale(**kwargs):
    return lambda: RecoJetPtScaleProducer(**kwargs)

# Resolution
class RecoJetPtResolutionProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = None
        jerctag = None

        # Smearing tool filename 
        filename_smear = f"{os.environ['CMT_BASE']}/../data/offline_jec/jer_smear.json"

        # Select the JEC file
        if (self.runPeriod == "2024") or self.isMC:
            filename = f"{os.environ['CMT_BASE']}/../data/offline_jec/jet_2024_jerc_v3.json"
            jerctag = "Summer24Prompt24_JRV1"
        elif self.runPeriod == "2025":
            filename = f"{os.environ['CMT_BASE']}/../data/offline_jec/jet_2025_jerc_v3.json"
            jerctag = "Summer24Prompt25_JRV1"
        else:
            print("No year specified, falling back to 2025")
            filename = f"{os.environ['CMT_BASE']}/../data/offline_jec/jet_2025_jerc_v3.json"
            jerctag = "Summer24Prompt25_JRV1"

        # Load if MC 
        if self.isMC:
            print(f"Loading offline MC resolution smearing from {filename} with tag {jerctag}")

            if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gInterpreter.Load("libCorrectionsWrapper.so")

            ROOT.gInterpreter.Declare(os.path.expandvars(
                '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
            # Load the reference resolution
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_resolution = MyCorrections("{os.path.expandvars(filename)}", "{jerctag}_MC_PtResolution_AK4PFPuppi");'
            )
            # Load the SF
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_sf = MyCorrections("{os.path.expandvars(filename)}", "{jerctag}_MC_ScaleFactor_AK4PFPuppi");'
            )
            # JER scale factor uncertainty
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_sf_unc = MyCorrections("{os.path.expandvars(filename)}", "{jerctag}_MC_SFUncertainty_AK4PFPuppi");'
            )
            # Load the smearing tool
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_smear = MyCorrections("{os.path.expandvars(filename_smear)}", "JERSmear");'
            )

            # GenJet matching and smearing
            if not os.getenv("_RecoJetPtResolution"):
                os.environ["_RecoJetPtResolution"] = "RecoJetPtResolution"
                ROOT.gInterpreter.Declare(
                """
                    using Vfloat = ROOT::RVec<float>;
                    using Vint = ROOT::RVec<int>;
                    using Vbool = ROOT::RVec<bool>;

                    // Match to GenJets (dpT criterion active)
                    auto getMatchedPtResolution(Vfloat RefJet_pt, Vfloat RefJet_eta, Vfloat RefJet_phi, Vfloat Jet_pt, Vfloat Jet_eta, Vfloat Jet_phi, float Rho){
                        Vfloat matchedPt(Jet_eta.size(), -1);
                        Vint matchedRefJetIdx(Jet_eta.size(), -1);

                        for(size_t i = 0; i < Jet_pt.size(); ++i){
                            float minDR = 9999;
                            int bestRefJetIdx = -1;
                            float jet_pt_resolution = corr_resolution.eval({Jet_eta[i], Jet_pt[i], Rho});
                            float maxdpT = 3.0 * jet_pt_resolution * Jet_pt[i];

                            for(size_t j = 0; j < RefJet_pt.size(); ++j){
                                if (std::find(matchedRefJetIdx.begin(), matchedRefJetIdx.end(), j) != matchedRefJetIdx.end()) continue;

                                float dEta = Jet_eta[i] - RefJet_eta[j];
                                float dPhi = TVector2::Phi_mpi_pi(Jet_phi[i] - RefJet_phi[j]);
                                float dr = std::sqrt(dEta*dEta + dPhi*dPhi);
                                float dpT = std::fabs(Jet_pt[i] - RefJet_pt[j]);
                                
                                if((dr < minDR) && (dr < 0.2) && (dpT < maxdpT)){
                                    minDR = dr;
                                    matchedPt[i] = RefJet_pt[j];
                                    bestRefJetIdx = j;
                                }
                            }
                            matchedRefJetIdx[i] = bestRefJetIdx;
                        } 
                        return matchedPt;  
                    }

                    // Smear the jets (Resolution and SF are loaded dynamically)
                    Vfloat get_jet_pt_smear(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat GenJet_pt, float Rho, int EventID){
                        Vfloat jet_pt_smear;

                        // Nominal SF
                        // Note: New versions of JER do not have a third argument
                        for (size_t i=0; i < Jet_pt.size(); i++){
                            float resolution = corr_resolution.eval({Jet_eta[i], Jet_pt[i], Rho});
                            //float sf = corr_sf.eval({Jet_eta[i], Jet_pt[i], "nom"});
                            float sf = corr_sf.eval({Jet_eta[i], Jet_pt[i]});
                            float smear = corr_smear.eval({Jet_pt[i], Jet_eta[i], GenJet_pt[i], Rho, EventID, resolution, sf});
                            float smeared_pt = Jet_pt[i] * smear;
                            if (smeared_pt < 1.e-2) smeared_pt = 1.e-2;
                            jet_pt_smear.push_back(smeared_pt);
                        }
                        return jet_pt_smear;
                    }

                    // Smear jets with nominal/up/down JER SF.
                    Vfloat get_jet_pt_smear_syst(Vfloat Jet_pt, Vfloat Jet_eta, Vfloat GenJet_pt, float Rho, int EventID, std::string syst){
                        Vfloat jet_pt_smear;

                        for (size_t i = 0; i < Jet_pt.size(); i++){
                            float resolution = corr_resolution.eval({Jet_eta[i], Jet_pt[i], Rho});
                            float sf_nom = corr_sf.eval({Jet_eta[i], Jet_pt[i]});
                            float sf_unc = corr_sf_unc.eval({Jet_eta[i], Jet_pt[i]});
                            float sf = sf_nom;
                            if (syst == "up"){
                                sf = sf_nom + sf_unc;
                            }
                            else if (syst == "down"){
                                sf = sf_nom - sf_unc;
                            }
                            float smear = corr_smear.eval({Jet_pt[i], Jet_eta[i], GenJet_pt[i], Rho, EventID, resolution, sf});
                            float smeared_pt = Jet_pt[i] * smear;
                            if (smeared_pt < 1.e-2) smeared_pt = 1.e-2;
                            jet_pt_smear.push_back(smeared_pt);
                        }

                        return jet_pt_smear;
                    }
                """)
    
    def run(self, df):
        if self.isMC:
            print(f"\nSmearing MC")
            df = df.Define("Jet_genmatchedPt", "getMatchedPtResolution(GenJet_pt, GenJet_eta, GenJet_phi, Jet_pt, Jet_eta, Jet_phi, Rho_fixedGridRhoFastjetAll)")
            df = df.Define("Jet_pt_scale_orig", "Jet_pt")
            #df = df.Redefine("Jet_pt", "get_jet_pt_smear(Jet_pt, Jet_eta, Jet_genmatchedPt, Rho_fixedGridRhoFastjetAll, event)")
            df = df.Define("Jet_pt_JERNom", 'get_jet_pt_smear_syst(Jet_pt, Jet_eta, Jet_genmatchedPt, Rho_fixedGridRhoFastjetAll, event, "nom")')
            df = df.Define("Jet_pt_OfflineJERUp",'get_jet_pt_smear_syst(Jet_pt, Jet_eta, Jet_genmatchedPt, Rho_fixedGridRhoFastjetAll, event, "up")')
            df = df.Define("Jet_pt_OfflineJERDown", 'get_jet_pt_smear_syst(Jet_pt, Jet_eta, Jet_genmatchedPt, Rho_fixedGridRhoFastjetAll, event, "down")')
            # Smearing JES varied jets
            df = df.Define("Jet_pt_OfflineJESUp_JERNom", 'get_jet_pt_smear_syst(Jet_pt_OfflineJESUp, Jet_eta, Jet_genmatchedPt, Rho_fixedGridRhoFastjetAll, event, "nom")')
            df = df.Define("Jet_pt_OfflineJESDown_JERNom",'get_jet_pt_smear_syst(Jet_pt_OfflineJESDown, Jet_eta, Jet_genmatchedPt, Rho_fixedGridRhoFastjetAll, event, "nom")')
            # Renaming
            df = df.Redefine("Jet_pt", "Jet_pt_JERNom")
            df = df.Redefine("Jet_pt_OfflineJESUp", "Jet_pt_OfflineJESUp_JERNom")
            df = df.Redefine("Jet_pt_OfflineJESDown", "Jet_pt_OfflineJESDown_JERNom")
        else:
            print(f"\nRunning on data, no smearing applied to Reco jets")
            df = df.Define("Jet_pt_scale_orig", "Jet_pt")
            df = df.Define("Jet_pt_OfflineJERUp", "Jet_pt")
            df = df.Define("Jet_pt_OfflineJERDown", "Jet_pt")

        return df, ["Jet_pt_scale_orig", "Jet_pt", "Jet_pt_OfflineJESUp", "Jet_pt_OfflineJESDown", "Jet_pt_OfflineJERUp", "Jet_pt_OfflineJERDown"]
    
def RecoJetPtResolution(**kwargs):
    return lambda: RecoJetPtResolutionProducer(**kwargs)

############### L1 corrections ###############
# Note: SFs are already divided by 1
# MC derived


# Tag-and-probe derived
class JetPtScaleTnPProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = "data/dummy.json"

        if self.isMC:
            print("\nSample: MC")
            filename = f"{os.environ['CMT_BASE']}/../data/jec_300626/jet_pt_scale_tnp_mc_2024.json"
        else:
            print("\nSample: Data")
            if "2024" in self.runPeriod:
                print("Year: 2024")
                filename = f"{os.environ['CMT_BASE']}/../data/jec_300626/jet_pt_scale_tnp_data_2024.json" 
            elif "2025" in self.runPeriod:
                print("Year: 2025")
                filename = f"{os.environ['CMT_BASE']}/../data/jec_300626/jet_pt_scale_tnp_data_2025.json"
            else:
                print("No year specified, falling back to 2025")
                filename = f"{os.environ['CMT_BASE']}/../data/jec_300626/jet_pt_scale_tnp_data_2025.json"

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
                    
                    // Applying corrections to all jets
                    for (size_t i=0; i < pt.size(); i++){
                        float scale = corr_scale.eval({eta[i], pt[i], syst});
                        scale_factor.push_back(scale); 
                    }
                    return scale_factor;
                }
            """)

    def run(self, df):
        branches = ["pt_scale_corr_nominal", "pt_scale_corr_up", "pt_scale_corr_down"]
        jet_branches = []
        for branch_name, syst in zip(branches, ["sf", "systup", "systdown"]):
            df = df.Define(branch_name, """get_jet_pt_scale(L1Jet_pt, L1Jet_eta, "%s")""" % syst)
            df = df.Define(f"L1Jet_{branch_name}", f"L1Jet_pt * {branch_name}")
            jet_branches.append(f"L1Jet_{branch_name}")

        return df, jet_branches

def JetPtScaleTnP(**kwargs):
    return lambda: JetPtScaleTnPProducer(**kwargs)


#### Redefine jets after only scale corrections (used for L1 JEC closure tests)
class JetPtScaleRedefineProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

    def run(self, df):
        # Removing events with saturated towers (JEC closure)
        df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")
        df = df.Define("L1Jet_pt_orig", "L1Jet_pt")
        df = df.Redefine("L1Jet_pt", "L1Jet_pt_scale_corr_nominal")

        return df, ["L1Jet_pt_orig"]
    
def JetPtScaleRedefine(**kwargs):
    return lambda: JetPtScaleRedefineProducer(**kwargs)

# Tag-and-probe derived resolution
class JetPtResolutionTnPProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename_ref = "data/dummy.json"
        filename_sf = "data/dummy.json"
        #filename_smear = f"{os.environ['CMT_BASE']}/../data/jec_300626/jer_smear.json"
        # Version where original pT is used to ensure stochastic behaviour is common for up/down (uses get_jet_pt_smear_origpt as function)
        filename_smear = f"{os.environ['CMT_BASE']}/../data/jec_300626/jer_smear_stochasticonly.json"

        ## Hardcode to smear to 2025 data using 2024 MC as reference
        filename_ref = f"{os.environ['CMT_BASE']}/../data/jec_300626/jet_pt_resolution_tnp_mc_2024.json"
        filename_sf = f"{os.environ['CMT_BASE']}/../data/jec_300626/jet_pt_resolution_tnp_sf_2025.json"

        if self.isMC:
            print(f"\nLoading resolution corrections for MC (L1 to Reco)")
            print(f"Ref: {filename_ref}")
            print(f"SF: {filename_sf}")

            if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
                ROOT.gInterpreter.Load("libCorrectionsWrapper.so")
            ROOT.gInterpreter.Declare(os.path.expandvars(
                '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
            
            # Load the reference res and SF
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_ref = MyCorrections("{os.path.expandvars(filename_ref)}", '
                    '"L1JER");'
            )
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_sf = MyCorrections("{os.path.expandvars(filename_sf)}", '
                    '"L1JERSF");'
            )
            # Load the smearing tool
            ROOT.gInterpreter.ProcessLine(
                f'auto corr_smear = MyCorrections("{os.path.expandvars(filename_smear)}", "JERSmear");'
            )

            if not os.getenv("_JetPtResolution"):
                os.environ["_JetPtResolution"] = "JetPtResolution"

                ROOT.gInterpreter.Declare(
                """
                    using Vfloat = ROOT::RVec<float>;
                    using Vint = ROOT::RVec<int>;
                    using Vbool = ROOT::RVec<bool>;

                    // Smear the jets
                    Vfloat get_jet_pt_smear(Vfloat Jet_pt, Vfloat Jet_eta, float Rho, int EventID, std::string syst){
                        Vfloat jet_pt_smear;

                        for (size_t i = 0; i < Jet_pt.size(); i++){
                            // Gen pT hardcoded to -1.0 to make smearing always stochastic
                            float genpt = -1.0;

                            float resolution_ref = corr_ref.eval({Jet_eta[i], Jet_pt[i]});
                            float resolution_sf = corr_sf.eval({Jet_eta[i], Jet_pt[i], syst});

                            float smear = corr_smear.eval({Jet_pt[i], Jet_eta[i], genpt, Rho, EventID, resolution_ref, resolution_sf});

                            float smeared_pt = Jet_pt[i] * smear;
                            if (smeared_pt < 1.e-2) smeared_pt = 1.e-2;
                            jet_pt_smear.push_back(smeared_pt);
                        }

                        return jet_pt_smear;
                    }

                    // Smear the jets (use original pT for fixed stochastic nature)
                    Vfloat get_jet_pt_smear_origpt(Vfloat Jet_pt_orig, Vfloat Jet_pt, Vfloat Jet_eta, float Rho, int EventID, std::string syst){
                        Vfloat jet_pt_smear;

                        for (size_t i = 0; i < Jet_pt.size(); i++){
                            // Gen pT hardcoded to -1.0 to make smearing always stochastic
                            float resolution_ref = corr_ref.eval({Jet_eta[i], Jet_pt[i]});
                            float resolution_sf = corr_sf.eval({Jet_eta[i], Jet_pt[i], syst});

                            float smear = corr_smear.eval({Jet_pt[i], Jet_eta[i], Jet_pt_orig[i], Rho, EventID, resolution_ref, resolution_sf});

                            float smeared_pt = Jet_pt[i] * smear;
                            if (smeared_pt < 1.e-2) smeared_pt = 1.e-2;
                            jet_pt_smear.push_back(smeared_pt);
                        }

                        return jet_pt_smear;
                    }
                """)

    def run(self, df):
        if self.isMC:
            ## Initial version
            # Nominal scale
            #df = df.Define("L1Jet_pt_scale_corr_nominal_resolution_smear_nominal", 'get_jet_pt_smear(L1Jet_pt_scale_corr_nominal, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "sf")')
            #df = df.Define("L1Jet_pt_scale_corr_nominal_resolution_smear_up", 'get_jet_pt_smear(L1Jet_pt_scale_corr_nominal, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "systup")')
            #df = df.Define("L1Jet_pt_scale_corr_nominal_resolution_smear_down", 'get_jet_pt_smear(L1Jet_pt_scale_corr_nominal, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "systdown")')
            # Scale up
            #df = df.Define("L1Jet_pt_scale_corr_up_resolution_smear_nominal", 'get_jet_pt_smear(L1Jet_pt_scale_corr_up, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "sf")')
            # Scale down
            #df = df.Define("L1Jet_pt_scale_corr_down_resolution_smear_nominal", 'get_jet_pt_smear(L1Jet_pt_scale_corr_down, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "sf")')

            ## Use original pT for stochastic consistency
            df = df.Define("L1Jet_pt_scale_corr_nominal_resolution_smear_nominal", 'get_jet_pt_smear_origpt(L1Jet_pt, L1Jet_pt_scale_corr_nominal, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "sf")')
            df = df.Define("L1Jet_pt_scale_corr_nominal_resolution_smear_up", 'get_jet_pt_smear_origpt(L1Jet_pt, L1Jet_pt_scale_corr_nominal, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "systup")')
            df = df.Define("L1Jet_pt_scale_corr_nominal_resolution_smear_down", 'get_jet_pt_smear_origpt(L1Jet_pt, L1Jet_pt_scale_corr_nominal, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "systdown")')
            # Scale up
            df = df.Define("L1Jet_pt_scale_corr_up_resolution_smear_nominal", 'get_jet_pt_smear_origpt(L1Jet_pt, L1Jet_pt_scale_corr_up, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "sf")')
            # Scale down
            df = df.Define("L1Jet_pt_scale_corr_down_resolution_smear_nominal", 'get_jet_pt_smear_origpt(L1Jet_pt, L1Jet_pt_scale_corr_down, L1Jet_eta, Rho_fixedGridRhoFastjetAll, event, "sf")')
        else:
            print("\nRunning on data, no smearing applied to L1 jets to Reco")
            df = df.Define("L1Jet_pt_scale_corr_nominal_resolution_smear_nominal", "L1Jet_pt_scale_corr_nominal")
            df = df.Define("L1Jet_pt_scale_corr_nominal_resolution_smear_up", "L1Jet_pt_scale_corr_nominal")
            df = df.Define("L1Jet_pt_scale_corr_nominal_resolution_smear_down", "L1Jet_pt_scale_corr_nominal")
            df = df.Define("L1Jet_pt_scale_corr_up_resolution_smear_nominal", "L1Jet_pt_scale_corr_up")
            df = df.Define("L1Jet_pt_scale_corr_down_resolution_smear_nominal", "L1Jet_pt_scale_corr_down")

        output_branches = [
            "L1Jet_pt_scale_corr_nominal_resolution_smear_nominal",
            "L1Jet_pt_scale_corr_nominal_resolution_smear_up",
            "L1Jet_pt_scale_corr_nominal_resolution_smear_down",
            "L1Jet_pt_scale_corr_up_resolution_smear_nominal",
            "L1Jet_pt_scale_corr_down_resolution_smear_nominal"
        ]
        return df, output_branches

def JetPtResolutionTnP(**kwargs):
    return lambda: JetPtResolutionTnPProducer(**kwargs)

######### Redefine jets after scale and resolution corrections (used for L1 JEC closure tests)
class JetPtScaleResolutionRedefineProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

    def run(self, df):
        # Removing events with saturated towers (JEC closure)
        df = df.Filter("Sum(L1Jet_pt == 1023.5) == 0", "Saturated L1 jet veto")
        df = df.Define("L1Jet_pt_orig", "L1Jet_pt")
        df = df.Redefine("L1Jet_pt", "L1Jet_pt_scale_corr_nominal_resolution_smear_nominal")

        return df, ["L1Jet_pt_orig"]
    
def JetPtScaleResolutionRedefine(**kwargs):
    return lambda: JetPtScaleResolutionRedefineProducer(**kwargs)

############# Common corrections #################
# Veto maps
## Apply jet veto maps to data and MC
class JetVetoMapProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = None
        jvmtag = None 

        if (self.runPeriod == "2024") or self.isMC:
            filename = f"{os.environ['CMT_BASE']}/../data/jvm/jetvetomaps_2024.json"
            jvmtag = "Summer24Prompt24_RunBCDEFGHI_V1"
        elif self.runPeriod == "2025":
            filename = f"{os.environ['CMT_BASE']}/../data/jvm/jetvetomaps_2025.json"
            jvmtag = "Winter25Prompt25_RunCDEFG_V1"
        else:
            print("No year specified, falling back to 2025")
            filename = f"{os.environ['CMT_BASE']}/../data/jvm/jetvetomaps_2025.json"
            jvmtag = "Winter25Prompt25_RunCDEFG_V1"

        print(f"Loading jet veto maps from {filename} with tag {jvmtag}")

        if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
            ROOT.gInterpreter.Load("libCorrectionsWrapper.so")

        ROOT.gInterpreter.Declare(os.path.expandvars(
            '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
        
        # Load the correction
        ROOT.gInterpreter.ProcessLine(
            f'auto corr_jvm = MyCorrections("{os.path.expandvars(filename)}", "{jvmtag}");'
        )
        if not os.getenv("_JetVetoMap"):
            os.environ["_JetVetoMap"] = "JetVetoMap"
            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;

                // Get the jet veto decision
                auto get_jet_veto(Vfloat Jet_eta, Vfloat Jet_phi){
                    Vbool jet_veto;

                    for (size_t i=0; i < Jet_eta.size(); i++){
                        bool veto = corr_jvm.eval({"jetvetomap", Jet_eta[i], Jet_phi[i]});
                        jet_veto.push_back(veto);
                    }

                    return jet_veto;

                }
            """)

    def run(self, df):
        df = df.Define("L1Jet_veto", "get_jet_veto(L1Jet_eta, L1Jet_phi)")
        df = df.Define("Jet_veto", "get_jet_veto(Jet_eta, Jet_phi)")

        df = df.Define("jvm_event_veto_offline", "Sum(Jet_veto) > 0")
        df = df.Define("jvm_event_veto_l1", "Sum(L1Jet_veto) > 0")
        df = df.Define("jvm_event_veto", "(jvm_event_veto_offline)||(jvm_event_veto_l1)")

        return df, ["L1Jet_veto", "Jet_veto", "jvm_event_veto_l1", "jvm_event_veto_offline", "jvm_event_veto"]

def JetVetoMap(**kwargs):
    return lambda: JetVetoMapProducer(**kwargs)

## Apply jet veto maps to data and MC for ONLY L1 Jets
class L1JetVetoMapProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = None
        jvmtag = None 

        if (self.runPeriod == "2024") or self.isMC:
            filename = f"{os.environ['CMT_BASE']}/../data/jvm/jetvetomaps_2024.json"
            jvmtag = "Summer24Prompt24_RunBCDEFGHI_V1"
        elif self.runPeriod == "2025":
            filename = f"{os.environ['CMT_BASE']}/../data/jvm/jetvetomaps_2025.json"
            jvmtag = "Winter25Prompt25_RunCDEFG_V1"
        else:
            print("No year specified, falling back to 2025")
            filename = f"{os.environ['CMT_BASE']}/../data/jvm/jetvetomaps_2025.json"
            jvmtag = "Winter25Prompt25_RunCDEFG_V1"

        print(f"Loading jet veto maps from {filename} with tag {jvmtag}")

        if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
            ROOT.gInterpreter.Load("libCorrectionsWrapper.so")

        ROOT.gInterpreter.Declare(os.path.expandvars(
            '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
        
        # Load the correction
        ROOT.gInterpreter.ProcessLine(
            f'auto corr_jvm = MyCorrections("{os.path.expandvars(filename)}", "{jvmtag}");'
        )
        if not os.getenv("_L1JetVetoMap"):
            os.environ["_L1JetVetoMap"] = "L1JetVetoMap"
            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;

                // Get the jet veto decision
                auto get_jet_veto(Vfloat Jet_eta, Vfloat Jet_phi){
                    Vbool jet_veto;

                    for (size_t i=0; i < Jet_eta.size(); i++){
                        bool veto = corr_jvm.eval({"jetvetomap", Jet_eta[i], Jet_phi[i]});
                        jet_veto.push_back(veto);
                    }

                    return jet_veto;

                }
            """)

    def run(self, df):
        df = df.Define("L1Jet_veto", "get_jet_veto(L1Jet_eta, L1Jet_phi)")
        df = df.Define("jvm_event_veto_l1", "Sum(L1Jet_veto) > 0")

        return df, ["L1Jet_veto", "jvm_event_veto_l1"]

def L1JetVetoMap(*args, **kwargs):
    return lambda: L1JetVetoMapProducer(*args, **kwargs)