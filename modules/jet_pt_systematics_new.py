# New systematics treatement 
import os

from Corrections.JME.PUjetID_SF import PUjetID_SFRDFProducer
from analysis_tools.utils import import_root

ROOT = import_root()

#import correctionlib
#correctionlib.register_pyroot_binding()

# Lazy correctionlib fix (need to be more robust)
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

# Correct the reco scale
class RecoJetPtScaleProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = None
        jerctag = None

        # Select the JEC file (MC is corrected to 2024 by default)
        if (self.runPeriod == "2024") or self.isMC:
            filename = "/vols/cms/pb4918/L1Scouting/Feb26/l1ds/data/offline_jec/jet_2024_jerc_v2.json"
            jerctag = "Summer24Prompt24_V2"
        elif self.runPeriod == "2025":
            filename = "/vols/cms/pb4918/L1Scouting/Feb26/l1ds/data/offline_jec/jet_2025_jerc_v1.json"
            jerctag = "Winter25Prompt25_V3"
        else:
            print("No year specified, falling back to 2025")
            filename = "/vols/cms/pb4918/L1Scouting/Feb26/l1ds/data/offline_jec/jet_2025_jerc_v1.json"
            jerctag = "Winter25Prompt25_V3"
        
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

        return df, ["Jet_pt_raw", "Jet_pt_orig", "Jet_pt"]

def RecoJetPtScale(**kwargs):
    return lambda: RecoJetPtScaleProducer(**kwargs)

# Apply smearing to reco jets 
class RecoJetPtResolutionProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = None
        jerctag = None
        # Smearing tool filename 
        filename_smear = "/vols/cms/pb4918/L1Scouting/Feb26/l1ds/data/offline_jec/jer_smear.json"

        # Select the JEC file
        if (self.runPeriod == "2024") or self.isMC:
            filename = "/vols/cms/pb4918/L1Scouting/Feb26/l1ds/data/offline_jec/jet_2024_jerc_v2.json"
            jerctag = "Summer23BPixPrompt23_RunD_JRV1"
        elif self.runPeriod == "2025":
            filename = "/vols/cms/pb4918/L1Scouting/Feb26/l1ds/data/offline_jec/jet_2025_jerc_v1.json"
            jerctag = "Summer23BPixPrompt23_RunD_JRV1"
        else:
            print("No year specified, falling back to 2025")
            filename = "/vols/cms/pb4918/L1Scouting/Feb26/l1ds/data/offline_jec/jet_2025_jerc_v1.json"
            jerctag = "Summer23BPixPrompt23_RunD_JRV1"

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
                        for (size_t i=0; i < Jet_pt.size(); i++){
                            float resolution = corr_resolution.eval({Jet_eta[i], Jet_pt[i], Rho});
                            float sf = corr_sf.eval({Jet_eta[i], Jet_pt[i], "nom"});
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
            df = df.Redefine("Jet_pt", "get_jet_pt_smear(Jet_pt, Jet_eta, Jet_genmatchedPt, Rho_fixedGridRhoFastjetAll, event)")
        else:
            print(f"\nRunning on data, no smearing applied to Reco jets")
            df = df.Define("Jet_pt_scale_orig", "Jet_pt")

        return df, ["Jet_pt_scale_orig", "Jet_pt"]
    
def RecoJetPtResolution(**kwargs):
    return lambda: RecoJetPtResolutionProducer(**kwargs)

## Apply jet veto maps to data and MC
class JetVetoMapProducer():
    def __init__(self, *args, **kwargs):
        self.runPeriod = kwargs.pop("runPeriod")
        self.isMC = kwargs.pop("isMC")

        filename = None
        jvmtag = None 

        if (self.runPeriod == "2024") or self.isMC:
            filename = "/vols/cms/pb4918/L1Scouting/Apr26/l1ds/data/jvm/jetvetomaps_2024.json"
            jvmtag = "Summer24Prompt24_RunBCDEFGHI_V1"
        elif self.runPeriod == "2025":
            filename = "/vols/cms/pb4918/L1Scouting/Apr26/l1ds/data/jvm/jetvetomaps_2025.json"
            jvmtag = "Winter25Prompt25_RunCDEFG_V1"
        else:
            print("No year specified, falling back to 2025")
            filename = "/vols/cms/pb4918/L1Scouting/Apr26/l1ds/data/jvm/jetvetomaps_2025.json"
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