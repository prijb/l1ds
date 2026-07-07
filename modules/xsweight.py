# Add xs weight to MC
from analysis_tools.utils import import_root
ROOT = import_root()

# Weights per pb^-1
class EventWeightProducer():
    def __init__(self, *args, **kwargs):
        #self.lumi_pb = kwargs.pop("lumi_pb", 0.446)
        self.xs = kwargs.pop("xs", 1.0)
        self.nr_incl = kwargs.pop("nr_incl", 1)
        self.isMC = kwargs.pop("isMC")

    def run(self, df):
        if self.isMC:
            print(f"\nSetting xs_weight for sample xs {self.xs:.3e} pb and {self.nr_incl} events")
            df = df.Define("xs_weight", f"{self.xs} / {self.nr_incl}")
        else:
            print("\nSetting xs_weight to 1.0 for data")
            df = df.Define("xs_weight", "1.0")
        return df, ["xs_weight"]
    
def EventWeight(*args, **kwargs):
    return lambda: EventWeightProducer(*args, **kwargs)


# Pileup veto
class PileupVetoProducer():
    def __init__(self, *args, **kwargs):
        
        self.isMC = kwargs.pop("isMC")

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
        if self.isMC:
            print("\nEvaluating pileup veto")
            df = df.Define("pileup_veto", "vetoPileupPtHat(genPtHat, PileupPtHats)")
        else:
            print("\nPileup veto set to false for data")
            df = df.Define("pileup_veto", "false")
        return df, ["pileup_veto"]
    
def PileupVeto(*args, **kwargs):
    return lambda: PileupVetoProducer(*args, **kwargs)


# Pileup veto (nanoaod)
class PileupVetoNanoProducer():
    def __init__(self, *args, **kwargs):
        
        self.isMC = kwargs.pop("isMC")

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
        if self.isMC:
            print("\nEvaluating pileup veto")
            df = df.Define("pileup_veto", "vetoPileupPtHat(GenPtHat_hardPtHat, PileupPtHat_puPtHats)")
        else:
            print("\nPileup veto set to false for data")
            df = df.Define("pileup_veto", "false")
        return df, ["pileup_veto"]
    
def PileupVetoNano(*args, **kwargs):
    return lambda: PileupVetoNanoProducer(*args, **kwargs)

class EventPtHatsProducer():
    def __init__(self, *args, **kwargs):

        self.isMC = kwargs.pop("isMC")

        ROOT.gInterpreter.Declare(
            """
            using Vfloat = ROOT::RVec<float>;
            // Makes an array with both the gen and PileupPtHat
            auto getEventPtHats(float genPtHat, Vfloat PileupPtHats){
                Vfloat EventPtHatsVector;
                for(auto pthat : PileupPtHats){
                    EventPtHatsVector.push_back(pthat);
                }
                EventPtHatsVector.push_back(genPtHat);
                Vfloat EventPtHatsVectorSorted = Reverse(Sort(EventPtHatsVector));
                return EventPtHatsVectorSorted;
            }
        """)

    def run(self, df):
        if self.MC:
            print("\nMaking combined vector of pileup pT hats and hard scatter pT hat")
            df = df.Define("EventPtHats", "getEventPtHats(GenPtHat_hardPtHat, PileupPtHat_puPtHats)")
            return df, ["EventPtHats"]
        else:
            print("\nSkipping pT hat creation for data")
            return df, []
    
def EventPtHats(*args, **kwargs):
    return lambda: EventPtHatsProducer(*args, **kwargs)