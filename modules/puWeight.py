import os
from Corrections.LUM.puWeight import puWeightRDFProducer, puWeightDummyRDFProducer

# pufile_data = "%s/../modules/dataParkingPileupHistogram.root" % os.environ['CMT_BASE']
# pufile_data = "%s/../modules/parking_pu2018.root" % os.environ['CMT_BASE']

def puWeightRDF(**kwargs):
    isMC = kwargs.pop("isMC")
    year = int(kwargs.pop("year"))
    process = kwargs.pop("process")
    
    # To do: Making this year specific when 2025 data pileup is available
    pufile_mc = "%s/../data/pileup/qcdPileupHistogram2024_norm.root" % os.environ['CMT_BASE']
    if "qcd" in process:
        print(f"Process {process} registered as QCD")
        pufile_mc = "%s/../data/pileup/qcdPileupHistogram2024_norm.root" % os.environ['CMT_BASE']
    elif "ztoqq" in process:
        print(f"Process {process} registered as Z' signal")
        pufile_mc = "%s/../data/pileup/signal_ztoqq_250_summer24_norm.root" % os.environ['CMT_BASE']
    else:
        print("Unknown process, falling back to QCD")

    #pufile_data = "%s/../data/pileup/dataPileupHistogram-2024G_Golden-69200ub_norm.root" % os.environ['CMT_BASE']
    #pufile_data = "%s/../data/pileup/dataPileupHistogram-2024G_Golden_norm.root" % os.environ['CMT_BASE']
    pufile_data = "%s/../data/pileup/dataPileupHistogram-2025pp_Golden_norm.root" % os.environ['CMT_BASE']
    puWeight_RDF = lambda: puWeightRDFProducer(
        pufile_mc, pufile_data, "ntrueint", "pileup", verbose=False, doSysVar=True)

    if not isMC:
        return lambda: puWeightDummyRDFProducer()
    else:
        return eval("puWeight_RDF")
