from analysis_tools import Dataset, Process, ObjectCollection
from plotting_tools import Label

class Config():
    def add_ttbar_processes(self):
        processes = [
            Process("ttbar", Label("TTbar"), color=(255, 0, 0)),
            Process("ttbar_2l2nu", Label("TTbarTo2L2Nu"), color=(255, 0, 0), parent_process="ttbar"),
            Process("ttbar_lnu2q", Label("TTbarToLNu2Q"), color=(255, 0, 0), parent_process="ttbar"),
            Process("ttbar_4q", Label("TTbarTo4Q"), color=(255, 0, 0), parent_process="ttbar"),
        ]

        return ObjectCollection(processes)


    def add_ttbar_datasets(self):
        datasets = [
            Dataset("ttbar_inclusive",
                folder="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/TT_TuneCP5_13p6TeV_powheg-pythia8/Winter24/250717_175222/0000",
                process=self.processes.get("ttbar"),
                prefix="gfe02.grid.hep.ph.ic.ac.uk",
                xs=924.6,
                nr_incl=15292102
            ),
            Dataset("ttbar_2l2nu",
                folder="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/v1/250714_155422",
                process=self.processes.get("ttbar_2l2nu"),
                prefix="gfe02.grid.hep.ph.ic.ac.uk",
                xs=97.9,
                nr_incl=470080053
            ),
            Dataset("ttbar_lnu2q",
                folder="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/v1/250714_155309",
                process=self.processes.get("ttbar_lnu2q"),
                prefix="gfe02.grid.hep.ph.ic.ac.uk",
                xs=404.54,
                nr_incl=484298177
            ),
            Dataset("ttbar_4q",
                folder="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/TTto4Q_TuneCP5_13p6TeV_powheg-pythia8/v1/250714_155349",
                process=self.processes.get("ttbar_4q"),
                prefix="gfe02.grid.hep.ph.ic.ac.uk",
                xs=421.16,
                nr_incl=461982592
            ),
        ]
        return ObjectCollection(datasets)

