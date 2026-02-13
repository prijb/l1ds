# Repeat of dijet_2025 but with all of the categorization in the plotting step
from analysis_tools import ObjectCollection, Category, Process, Dataset, Feature, Systematic
from analysis_tools.utils import DotDict
from analysis_tools.utils import join_root_selection as jrs
from plotting_tools import Label
from collections import OrderedDict

from cmt.config.base_config import Config as cmt_config
from config.qcd_datasets_new import Config as qcd_config
from cmt.base_tasks.base import Task

# Which data year to smear MC to ("2024" or "2025")
correct_mc_to_year = "2025"

class Config(qcd_config, cmt_config):
    def add_categories(self, **kwargs):
        categories = [
            Category("base", "base", selection="nL1Jet > -1"),
            Category("dum", "Nonzero jets", selection="nL1Jet > 0"),
            ## Selection stream
            Category("dijet30", "pT > 30", selection="(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),   
            Category("dijet30_eta2p5", "pT > 30, |eta| < 2.5", selection="(abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),   
        ]
        return ObjectCollection(categories)
    
    def add_processes(self):
        qcd_processes = super(Config, self).add_qcd_processes()
        processes = [
            Process("data", Label("Data"), color=(0, 0, 0), isData=True),
            Process("ztoqq", Label("Z'"), color=(0, 0, 255), isData=False),
            Process("ztoqq_250", Label("Z' (250 GeV)"), color=(0, 0, 255), isData=False, parent_process="ztoqq"),
            Process("ztoqq_350", Label("Z' (350 GeV)"), color=(0, 0, 255), isData=False, parent_process="ztoqq"),
            Process("ztoqq_450", Label("Z' (450 GeV)"), color=(0, 0, 255), isData=False, parent_process="ztoqq"),
            Process("ztoqq_500", Label("Z' (500 GeV)"), color=(0, 0, 255), isData=False, parent_process="ztoqq"),
            Process("ztoqq_600", Label("Z' (600 GeV)"), color=(0, 0, 255), isData=False, parent_process="ztoqq"),
        ]

        process_group_names = {
            "default": [
                "data",
                "qcd",
                "ztoqq"
            ],
            "data": [
                "data"
            ],
            "signal": [
                "ztoqq"
            ],
            "bkg": [
                "qcd"
            ],
            "databkg": [
                "data",
                "qcd"
            ]
        }

        process_training_names = {}

        # adding reweighed processes
        processes = ObjectCollection(processes)

        return ObjectCollection(processes) + qcd_processes, process_group_names, process_training_names
    
    def add_datasets(self):
        self.tree_name = "Events"
        qcd_datasets = super(Config, self).add_qcd_datasets()
        datasets = [
            Dataset("DataDijet25",
                folder = "/eos/cms/store/cmst3/group/daql1scout/run3/ntuples/selection/dijet30/run392542/L1ScoutingSelection/dijetEt30Eta25_20250526/250526_160646/0000",
                process = self.processes.get("data"),
                file_pattern = "l1nano_selbx_run382650(.*).root",
                prefix = "eoscms.cern.ch/",
                tags = ["ul"],
                check_empty = False,
                xs = 1.0,
                nr_incl = 1,
                skip_logs = True,
                runPeriod = "2025",
            ),
            Dataset("DataZB25",
                folder = "/eos/cms/store/cmst3/group/daql1scout/run3/ntuples/zb/run392672/L1Scouting/ntuples-L1Scouting-Run2025C-v1-L1SCOUT-392672/251025_140947",
                process = self.processes.get("data"),
                prefix = "eoscms.cern.ch/",
                tags = ["ul"],
                check_empty = False,
                xs = 1.0,
                nr_incl = 1,
                skip_logs = True,
                runPeriod = "2025",
            ),
            Dataset("DataDijet24",
                folder = "/eos/cms/store/group/phys_exotica/l1ds/Data/run383996/L1ScoutingSelection/251019_143234",
                process = self.processes.get("data"),
                prefix = "eoscms.cern.ch/",
                tags = ["ul"],
                check_empty = False,
                xs = 1.0,
                nr_incl = 1,
                skip_logs = True,
                runPeriod = "2024",
            ),
            Dataset("ztoqq_mlm_250",
                folder = "/eos/cms/store/group/phys_exotica/l1ds/samples/ZPrime_Run3Summer24_NANOAODv14/ztoqq_mlm_250/251021_011916/0000",
                process = self.processes.get("ztoqq_250"),
                prefix = "eoscms.cern.ch/",
                tags = ["ul"],
                check_empty = True,
                xs = 10000.0,
                nr_incl = 421817,
                skip_logs = True,
                runPeriod = correct_mc_to_year,
            ),
            Dataset("ztoqq_mlm_350",
                folder = "/eos/cms/store/group/phys_exotica/l1ds/samples/ZPrime_Run3Summer24_NANOAODv14/ztoqq_mlm_350/251021_011948/0000",
                process = self.processes.get("ztoqq_350"),
                prefix = "eoscms.cern.ch/",
                tags = ["ul"],
                check_empty = True,
                xs = 1000.0,
                nr_incl = 186432,
                skip_logs = True,
                runPeriod = correct_mc_to_year,
            ),
            Dataset("ztoqq_mlm_450",
                folder = "/eos/cms/store/group/phys_exotica/l1ds/samples/ZPrime_Run3Summer24_NANOAODv14/ztoqq_mlm_450/251021_012022/0000",
                process = self.processes.get("ztoqq_450"),
                prefix = "eoscms.cern.ch/",
                tags = ["ul"],
                check_empty = True,
                xs = 100.0,
                nr_incl = 417989,
                skip_logs = True,
                runPeriod = correct_mc_to_year,
            ),
            Dataset("ztoqq_mlm_500",
                folder = "/eos/cms/store/group/phys_exotica/l1ds/samples/ZPrime_Run3Summer24_NANOAODv14/ztoqq_mlm_500/251021_012058/0000",
                process = self.processes.get("ztoqq_500"),
                prefix = "eoscms.cern.ch/",
                tags = ["ul"],
                check_empty = True,
                xs = 10.0,
                nr_incl = 469523,
                skip_logs = True,
                runPeriod = correct_mc_to_year,
            ),
            Dataset("ztoqq_mlm_600",
                folder = "/eos/cms/store/group/phys_exotica/l1ds/samples/ZPrime_Run3Summer24_NANOAODv14/ztoqq_mlm_600/251021_012143/0000",
                process = self.processes.get("ztoqq_600"),
                prefix = "eoscms.cern.ch/",
                tags = ["ul"],
                check_empty = True,
                xs = 1.0,
                nr_incl = 379415,
                skip_logs = True,
                runPeriod = correct_mc_to_year,
            ),
        ]

        return ObjectCollection(datasets) + qcd_datasets
    
    # Define categories, then apply variations
    def add_features(self):
        categories = {
            "sr_pt30_eta2p5": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5) && (dphi > 1.047) && (deta < 1.1)",
            "sr_pt30_eta0p9": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta < 0.8)",
            "sr_pt30_barrel_full_1": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta < 0.4)",
            "sr_pt50_eta2p5": "(L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50) && (abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5) && (dphi > 1.047) && (deta < 1.1)",
            "sr_pt50_eta0p9": "(L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta < 0.8)",
            "sr_pt50_barrel_full_1": "(L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta < 0.4)",
            "sr_pt30_w1": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta < 0.02175)",
            "sr_pt30_w2": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.02175) && (deta < 0.10875)",
            "sr_pt30_w3": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.10875) && (deta < 0.19575)",
            "sr_pt30_w4": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.19575) && (deta < 0.28275)",
            "sr_pt30_w5": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.28275) && (deta < 0.36975)",
            "sr_pt30_w6": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.36975) && (deta < 0.45675)",
            "sr_pt30_w7": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.45675) && (deta < 0.54375)",
            "sr_pt30_w8": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.54375) && (deta < 0.63075)",
            "sr_pt30_w9": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.63075) && (deta < 0.71775)",
            "sr_pt30_w10": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.71775) && (deta < 0.80475)",
            "sr_pt30_w11": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.80475) && (deta < 0.89175)",
            "sr_pt30_w12": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.89175) && (deta < 0.97875)",
            "sr_pt30_w13": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta >= 0.97875) && (deta < 1.06575)",
            "pt30_eta0p9": "(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047)",
        }
        features_to_vary = ["mjj", "deta", "deta_full", "dphi", "dphi_full", "lead_pt", "sublead_pt", "lead_eta", "sublead_eta", "lead_phi", "sublead_phi"]
        vars_to_vary = ["L1Jet_pt", "L1Jet_eta", "L1Jet_phi", "mjj", "deta", "dphi"]
        systematic_variations = ["scale_corr_nominal_resolution_smear_nominal", "scale_corr_up_resolution_smear_nominal", "scale_corr_down_resolution_smear_nominal", "scale_corr_nominal_resolution_smear_up", "scale_corr_nominal_resolution_smear_down"]

        from config.features_dijet_analysis import features
        features_ext = []
        # Selections for sanity checking
        selections_ext = []

        # Add categories to every variable 
        for category_key in categories.keys():
            # Add categories to all variables without systematic variations
            for feature in features:
                #if feature.name in features_to_vary:
                feature_name = feature.name
                feature_expr = feature.expression
                feature_var = feature.expression.split("[")[0]
                feature_selection = feature.selection

                # Add category key to name and add category selections
                feature_name_syst = f"{feature_name}_{category_key}"
                feature_expr_syst = feature_expr
                if feature_selection is not None:
                    feature_selection_syst = f"{feature_selection} && {categories[category_key]}"
                else:
                    feature_selection_syst = f"{categories[category_key]}"

                feature_syst = Feature(
                    feature_name_syst, 
                    feature_expr_syst,
                    binning = feature.binning,
                    x_title = feature.aux['x_title'],
                    selection = feature_selection_syst,
                    systematics = feature.systematics,
                ) 
                features_ext.append(feature_syst)
                selections_ext.append(feature_selection_syst)

            # Apply systematic variations to each new category for features to vary
            for systematic_variation in systematic_variations:
                for feature in features:
                    if feature.name in features_to_vary:
                        feature_name = feature.name
                        feature_expr = feature.expression
                        feature_var = feature.expression.split("[")[0]
                        feature_selection = feature.selection

                        # Add category key to name and add category selections
                        feature_name_syst = f"{feature_name}_{category_key}"
                        feature_expr_syst = feature_expr
                        if feature_selection is not None:
                            feature_selection_syst = f"{feature_selection} && {categories[category_key]}"
                        else:
                            feature_selection_syst = f"{categories[category_key]}"
                        
                        # Apply systematic variations
                        feature_name_syst = f"{feature_name_syst}_{systematic_variation}"
                        feature_expr_syst = feature_expr_syst.replace(feature_var, f"{feature_var}_{systematic_variation}")
                        for var_to_vary in vars_to_vary:
                            feature_selection_syst = feature_selection_syst.replace(var_to_vary, f"{var_to_vary}_{systematic_variation}")

                        feature_syst = Feature(
                            feature_name_syst, 
                            feature_expr_syst,
                            binning = feature.binning,
                            x_title = feature.aux['x_title'],
                            selection = feature_selection_syst,
                        ) 
                        features_ext.append(feature_syst)
                        selections_ext.append(feature_selection_syst)
        
        #print(f"\nSelections added: {selections_ext}")

        ## Add auxillary features manually without having to do all systematic variations in JECs (for utility purposes)
        features_aux = [
            # Denominator for sel eff
            Feature("mjj_sr_eta0p9", "mjj",
                binning=(1000, 0, 1000),
                x_title=Label("mjj"),
                selection="(abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta < 0.8)",
            ),
            Feature("mjj_sr_eta0p9_scale_corr_nominal_resolution_smear_nominal", "mjj_scale_corr_nominal_resolution_smear_nominal",
                binning=(1000, 0, 1000),
                x_title=Label("mjj"),
                selection="(abs(L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[0]) < 0.957) && (abs(L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[1]) < 0.957) && (dphi_scale_corr_nominal_resolution_smear_nominal > 1.047) && (deta_scale_corr_nominal_resolution_smear_nominal < 0.8)",
            ),
            Feature("mjj_sr_barrel_full_1", "mjj",
                binning=(1000, 0, 1000),
                x_title=Label("mjj"),
                selection="(abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta < 0.8)",
            ),
            Feature("mjj_sr_barrel_full_1_scale_corr_nominal_resolution_smear_nominal", "mjj_scale_corr_nominal_resolution_smear_nominal",
                binning=(1000, 0, 1000),
                x_title=Label("mjj"),
                selection="(abs(L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[0]) < 0.957) && (abs(L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[1]) < 0.957) && (dphi_scale_corr_nominal_resolution_smear_nominal > 1.047) && (deta_scale_corr_nominal_resolution_smear_nominal < 0.4)",
            ),
            # Numerator for sel eff
            Feature("mjj_sr_eta0p9_selstream", "mjj",
                binning=(1000, 0, 1000),
                x_title=Label("mjj"),
                selection="(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta < 0.8)",
            ),
            Feature("mjj_sr_eta0p9_selstream_scale_corr_nominal_resolution_smear_nominal", "mjj_scale_corr_nominal_resolution_smear_nominal",
                binning=(1000, 0, 1000),
                x_title=Label("mjj"),
                selection="(L1Jet_pt_scale_corr_nominal_resolution_smear_nominal[0] > 30) && (L1Jet_pt_scale_corr_nominal_resolution_smear_nominal[1] > 30) && (abs(L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[0]) < 0.957) && (abs(L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[1]) < 0.957) && (dphi_scale_corr_nominal_resolution_smear_nominal > 1.047) && (deta_scale_corr_nominal_resolution_smear_nominal < 0.8)",
            ),
            Feature("mjj_sr_barrel_full_1_selstream", "mjj",
                binning=(1000, 0, 1000),
                x_title=Label("mjj"),
                selection="(L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (dphi > 1.047) && (deta < 0.8)",
            ),
            Feature("mjj_sr_barrel_full_1_selstream_scale_corr_nominal_resolution_smear_nominal", "mjj_scale_corr_nominal_resolution_smear_nominal",
                binning=(1000, 0, 1000),
                x_title=Label("mjj"),
                selection="(L1Jet_pt_scale_corr_nominal_resolution_smear_nominal[0] > 30) && (L1Jet_pt_scale_corr_nominal_resolution_smear_nominal[1] > 30) && (abs(L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[0]) < 0.957) && (abs(L1Jet_eta_scale_corr_nominal_resolution_smear_nominal[1]) < 0.957) && (dphi_scale_corr_nominal_resolution_smear_nominal > 1.047) && (deta_scale_corr_nominal_resolution_smear_nominal < 0.4)",
            ),
        ]

        return ObjectCollection(features + features_ext + features_aux)

    def add_weights(self):
        weights = DotDict()
        weights.default = "1"

        # Note: For ztoqq, we need to use pileup weights w/o QCD stitching

        # Weight for data
        #weights.total_events_weights = ["1"]
        # Weight for pileup (w/o QCD stitching)
        weights.total_events_weights = ["puWeight"]
        # Weight for QCD (w/o pileup)
        #weights.total_events_weights = ["qcd_weight"]
        # Weight for QCD (pileup)
        #weights.total_events_weights = ["qcd_weight", "puWeight"]

        # Weight for data
        #weights.base = ["1"]
        # Weight for pileup (w/o QCD stitching)
        weights.base = ["puWeight"]
        # Weight for QCD (w/o pileup)
        #weights.base = ["qcd_weight"]
        # Weight for QCD (pileup)
        #weights.base = ["qcd_weight", "puWeight"]

        for category in self.categories:
            weights[category.name] = weights.base

        return weights

    def add_systematics(self):
        systematics = [
            Systematic("pu", "", up="Up", down="Down", alias="CMS_l1ds_pileup_2024")
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


config = Config("dijet_2025", year=2025, ecm=13.6, lumi_pb=228)