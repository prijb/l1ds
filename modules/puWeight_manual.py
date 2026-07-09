# Manual correctionlib usage instead of the Corrections.LUM package
import os
from analysis_tools.utils import import_root
ROOT = import_root()

import correctionlib
correctionlib.register_pyroot_binding()

class puWeightRDFProducer():
    def __init__(self, *args, **kwargs):
        self.isMC = kwargs.pop("isMC")
        self.year = int(kwargs.pop("year"))
        self.process = kwargs.pop("process")

        pufile = "%s/../data/pileup/puweight_correction_qcd_2025.json" % os.environ['CMT_BASE']
        if "qcd" in self.process:
            print(f"Process {self.process} registered as QCD")
            pufile = "%s/../data/pileup/puweight_correction_qcd_2025.json" % os.environ['CMT_BASE']
        elif "ztoqq" in self.process:
            print(f"Process {self.process} registered as Z' signal")
            pufile = "%s/../data/pileup/puweight_correction_ztoqq_summer24_2025.json" % os.environ['CMT_BASE']
        else:
            print("Unknown process, falling back to QCD")

        print(f"Using json {pufile} to apply Pileup_nTrueInt reweighting")

        if "/libCorrectionsWrapper.so" not in ROOT.gSystem.GetLibraries():
            ROOT.gInterpreter.Load("libCorrectionsWrapper.so")
        ROOT.gInterpreter.Declare(os.path.expandvars(
            '#include "$CMSSW_BASE/src/Base/Modules/interface/correctionWrapper.h"'))
        
        ROOT.gInterpreter.ProcessLine(
            f'auto corr = MyCorrections("{os.path.expandvars(pufile)}", '
                '"PUWeight");'
        )

        # Derive weight
        if not os.getenv("_nTrueIntReweight"):
            os.environ["_nTrueIntReweight"] = "nTrueIntReweight"

            ROOT.gInterpreter.Declare(
            """
                using Vfloat = ROOT::RVec<float>;
                using Vint = ROOT::RVec<int>;
                using Vbool = ROOT::RVec<bool>;

                auto get_puweight(float ntrueint, std::string syst){
                    float puweight;

                    puweight = corr.eval({ntrueint, syst});

                    return puweight;
                }
            """)

    def run(self, df):
        if self.isMC:
            print(f"\nCorrecting pileup in MC")
            df = df.Define("puWeight", """get_puweight(Pileup_nTrueInt, "sf")""")
            df = df.Define("puWeightUp", """get_puweight(Pileup_nTrueInt, "systup")""")
            df = df.Define("puWeightDown", """get_puweight(Pileup_nTrueInt, "systdown")""")
        else:
            print(f"\nSample is data, no PU correction applied")
            df = df.Define("puWeight", "1.0")
            df = df.Define("puWeightUp", "1.0")
            df = df.Define("puWeightDown", "1.0")
        
        return df, ["puWeight", "puWeightUp", "puWeightDown"]
    
def puWeightRDF(*args, **kwargs):
    return lambda: puWeightRDFProducer(*args, **kwargs)