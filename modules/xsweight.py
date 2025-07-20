# Add xs weight to MC
from analysis_tools.utils import import_root
ROOT = import_root()

# Weights per pb^-1
class EventWeightProducer():
    def __init__(self, *args, **kwargs):
        #self.lumi_pb = kwargs.pop("lumi_pb", 0.446)
        self.xs = kwargs.pop("xs", 1.0)
        self.nr_incl = kwargs.pop("nr_incl", 1)

    def run(self, df):
        df = df.Define("xs_weight", f"{self.xs} / {self.nr_incl}")
        return df, ["xs_weight"]
    
def EventWeight(*args, **kwargs):
    return lambda: EventWeightProducer(*args, **kwargs)


# Pileup veto
class PileupVetoProducer():
    def __init__(self, *args, **kwargs):
        ROOT.gInterpreter.Declare("""
            using Vfloat = ROOT::RVec<float>;
            // Vetoes event if any of the pileup pT hats are greater than the gen pT hat
            bool vetoPileupPtHat(float genPtHat, Vfloat PileupPtHats){
                bool veto = false;
                for(auto pthat : PileupPtHats){
                    if(pthat > genPtHat){
                    veto = true;
                    }
                }
                return veto;
            }
        """
        )

    def run(self, df):
        df = df.Define("pileup_veto", "vetoPileupPtHat(genPtHat, PileupPtHats)")
        return df, ["pileup_veto"]
    
def PileupVeto(*args, **kwargs):
    return lambda: PileupVetoProducer(*args, **kwargs)