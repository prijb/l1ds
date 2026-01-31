import os
from Corrections.LUM.puWeight import puWeightRDFProducer, puWeightDummyRDFProducer

# pufile_data = "%s/../modules/dataParkingPileupHistogram.root" % os.environ['CMT_BASE']
# pufile_data = "%s/../modules/parking_pu2018.root" % os.environ['CMT_BASE']
pufile_data = "%s/../data/dataPileupHistogram-2024G_Golden-69200ub_norm.root" % os.environ['CMT_BASE']
pufile_mc = "%s/../data/qcdPileupHistogram2024_norm.root" % os.environ['CMT_BASE']
puWeight_RDF = lambda: puWeightRDFProducer(
    pufile_mc, pufile_data, "ntrueint", "pileup", verbose=False, doSysVar=False)


def puWeightRDF(**kwargs):
    isMC = kwargs.pop("isMC")
    year = int(kwargs.pop("year"))

    if not isMC:
        return lambda: puWeightDummyRDFProducer()
    else:
        return eval("puWeight_RDF")
