# Using ntuples for deriving dijet systematics (WJet and Muon data)
from analysis_tools import ObjectCollection, Category, Process, Dataset, Feature, Systematic
from analysis_tools.utils import DotDict
from analysis_tools.utils import join_root_selection as jrs
from plotting_tools import Label
from collections import OrderedDict

from cmt.config.base_config import Config as cmt_config
from cmt.base_tasks.base import Task

class Config(cmt_config):
    def add_categories(self, **kwargs):
        categories = [
            Category("base", "base", selection="nL1Jet > -1"),
            Category("dum", "Nonzero jets", selection="nL1Jet > 0"),
        ]
        return ObjectCollection(categories)

    def add_processes(self):
        processes = [
            Process("wjet", Label("WJet"), color=(0, 0, 255), isData=False),
            Process("dy", Label("DY"), color=(0, 0, 255), isData=False),
            Process("data", Label("Data"), color=(0, 0, 0), isData=True),
        ]

        process_group_names = {
            "default": [
                "wjet",
                "dy",
                "data"
            ],
            "data": [
                "data"
            ],
            "mc": [
                "wjet",
                "dy"
            ],
        }

        process_training_names = {}

        # adding reweighed processes
        processes = ObjectCollection(processes)

        return ObjectCollection(processes), process_group_names, process_training_names

    def add_datasets(self):
        self.tree_name = "Events"
        datasets = [
            Dataset("Muon0_2024G",
                folder = "/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/Muon0/v2/250921_144145",
                process = self.processes.get("data"),
                prefix = "gfe02.grid.hep.ph.ic.ac.uk",
                tags = ["ul"],
                check_empty = False,
                xs = 1.0,
                nr_incl = 1,
                skip_logs = True,
                runPeriod = "2024",
            ),
            Dataset("Muon0_2025C_v1",
                folder = "/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/Muon0/v1/251211_002847",
                process = self.processes.get("data"),
                prefix = "gfe02.grid.hep.ph.ic.ac.uk",
                tags = ["ul"],
                check_empty = False,
                xs = 1.0,
                nr_incl = 1,
                skip_logs = True,
                runPeriod = "2025",
            ),
            Dataset("WJet_2024",
                folder = "/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/WtoMuNu-4Jets_TuneCP5_13p6TeV_madgraphMLM-pythia8/Summer24NanoV14WithL1/251209_061949",
                process = self.processes.get("wjet"),
                prefix = "gfe02.grid.hep.ph.ic.ac.uk",
                tags = ["ul"],
                check_empty = False,
                xs = 1.0,
                nr_incl = 1,
                skip_logs = True,
                runPeriod = "2024",
            ),
            # Change runPeriod to smear it to a given year
            Dataset("WJet_2024_V15",
                folder = "/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/ppradeep/L1Scouting/WtoMuNu-4Jets_TuneCP5_13p6TeV_madgraphMLM-pythia8/Summer24NanoV15WithL1/251217_045803",
                process = self.processes.get("wjet"),
                prefix = "gfe02.grid.hep.ph.ic.ac.uk",
                tags = ["ul"],
                check_empty = False,
                xs = 1.0,
                nr_incl = 1,
                skip_logs = True,
                runPeriod = "2024",
            ),
        ]

        return ObjectCollection(datasets)

    def add_features(self):
        from config.features_dijet_syst import features
        return ObjectCollection(features)

    def add_weights(self):
        weights = DotDict()
        weights.default = "1"

        weights.total_events_weights = ["1"]

        weights.base = ["1"]

        for category in self.categories:
            weights[category.name] = weights.base

        return weights

    def add_systematics(self):
        systematics = [
        ]
        return ObjectCollection(systematics)
    
    def add_default_module_files(self):
        defaults = {}
        return defaults


    # other methods
    def get_norm_systematics(self, processes_datasets, region):
        """
        Method to extract all normalization systematics from the KLUB files.
        It considers the processes given by the process_group_name and their parents.
        """
        # systematics
        systematics = {}
        all_signal_names = []
        all_background_names = []
        for p in self.processes:
            if p.isSignal:
                all_signal_names.append(p.get_aux("llr_name")
                    if p.get_aux("llr_name", None) else p.name)
            elif not p.isData:
                all_background_names.append(p.get_aux("llr_name")
                    if p.get_aux("llr_name", None) else p.name)

        from cmt.analysis.systReader import systReader
        syst_folder = "config/systematics/"
        filename = f"systematics_{self.year}.cfg"
        if self.get_aux("isUL", False):
            filename = f"systematics_UL{str(self.year)[2:]}.cfg"
        syst = systReader(Task.retrieve_file(self, syst_folder + filename),
            all_signal_names, all_background_names, None)
        syst.writeOutput(False)
        syst.verbose(False)
        syst.writeSystematics()
        for isy, syst_name in enumerate(syst.SystNames):
            if "CMS_scale_t" in syst.SystNames[isy] or "CMS_scale_j" in syst.SystNames[isy]:
                continue
            for process in processes_datasets:
                original_process = process
                found = False
                while True:
                    process_name = (process.get_aux("llr_name")
                        if process.get_aux("llr_name", None) else process.name)
                    if process_name in syst.SystProcesses[isy]:
                        iproc = syst.SystProcesses[isy].index(process_name)
                        systVal = syst.SystValues[isy][iproc]
                        if syst_name not in systematics:
                            systematics[syst_name] = {}
                        systematics[syst_name][original_process.name] = eval(systVal)
                        found = True
                        break
                    elif process.parent_process:
                        process=self.processes.get(process.parent_process)
                    else:
                        break
                if not found:
                    for children_process in self.get_children_from_process(original_process.name):
                        if children_process.name in syst.SystProcesses[isy]:
                            if syst_name not in systematics:
                                systematics[syst_name] = {}
                            iproc = syst.SystProcesses[isy].index(children_process.name)
                            systVal = syst.SystValues[isy][iproc]
                            systematics[syst_name][original_process.name] = eval(systVal)
                            break
        return systematics


config = Config("dijet_syst", year=2025, ecm=13.6, lumi_pb=45.0)