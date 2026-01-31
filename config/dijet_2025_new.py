# Using EOS ntuples
from analysis_tools import ObjectCollection, Category, Process, Dataset, Feature, Systematic
from analysis_tools.utils import DotDict
from analysis_tools.utils import join_root_selection as jrs
from plotting_tools import Label
from collections import OrderedDict

from cmt.config.base_config import Config as cmt_config
from config.qcd_datasets_new import Config as qcd_config
from cmt.base_tasks.base import Task

class Config(qcd_config, cmt_config):
    def add_categories(self, **kwargs):
        categories = [
            Category("base", "base", selection="nL1Jet > -1"),
            Category("dum", "Nonzero jets", selection="nL1Jet > 0"),
            #########################################################
            ## Stream efficiency measurements
            # SR (data only)
            Category("eta1p1_deta1p1", "|eta| < 1.1, dEta < 1.1", selection="(dphi > 1.047) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1)"),
            Category("eta0p9_deta1p1", "|eta| < 0.957, dEta < 1.1", selection="(dphi > 1.047) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("eta0p9_deta0p4", "|eta| < 0.957, dEta < 0.4", selection="(dphi > 1.047) && (deta < 0.4) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("pt30_eta1p1_deta1p1", "pT > 30, |eta| < 1.1, dEta < 1.1", selection="(dphi > 1.047) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),
            Category("pt30_eta0p9_deta1p1", "pT > 30, |eta| < 0.957, dEta < 1.1", selection="(dphi > 1.047) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),
            Category("pt30_eta0p9_deta0p4", "pT > 30, |eta| < 0.957, dEta < 0.4", selection="(dphi > 1.047) && (deta < 0.4) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),
            # SR (template method)
            Category("eta2p5_sr", "|eta| < 2.5, dEta < 1.1", selection="(dphi > 1.047) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5)"),
            Category("eta1p1_sr", "|eta| < 1.1, dEta < 0.8", selection="(dphi > 1.047) && (deta < 0.8) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1)"),
            Category("eta0p9_sr", "|eta| < 0.957, dEta < 0.8", selection="(dphi > 1.047) && (deta < 0.8) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("pt30_eta2p5_sr", "pT > 30, |eta| < 2.5, dEta < 1.1", selection="(dphi > 1.047) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),
            Category("pt30_eta1p1_sr", "pT > 30, |eta| < 1.1, dEta < 0.8", selection="(dphi > 1.047) && (deta < 0.8) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),
            Category("pt30_eta0p9_sr", "pT > 30, |eta| < 0.957, dEta < 0.8", selection="(dphi > 1.047) && (deta < 0.8) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),
            # CR (template method)
            Category("eta2p5_cr", "|eta| < 2.5, 1.5 <= dEta < 2.6", selection="(dphi > 1.047) && (deta >= 1.5) && (deta < 2.6) && (abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5)"),
            Category("eta1p1_cr", "|eta| < 1.1, 1.3 <= dEta < 2.2", selection="(dphi > 1.047) && (deta >= 1.3) && (deta < 2.2) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1)"),
            Category("eta0p9_cr", "|eta| < 0.957, 1.3 <= dEta < 1.8", selection="(dphi > 1.047) && (deta >= 1.3) && (deta < 1.8) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("pt30_eta2p5_cr", "pT > 30, |eta| < 2.5, 1.5 <= dEta < 2.6", selection="(dphi > 1.047) && (deta >= 1.5) && (deta < 2.6) && (abs(L1Jet_eta[0]) < 2.5) && (abs(L1Jet_eta[1]) < 2.5) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),
            Category("pt30_eta1p1_cr", "pT > 30, |eta| < 1.1, 1.3 <= dEta < 2.2", selection="(dphi > 1.047) && (deta >= 1.3) && (deta < 2.2) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),
            Category("pt30_eta0p9_cr", "pT > 30, |eta| < 0.957, 1.3 <= dEta < 1.8", selection="(dphi > 1.047) && (deta >= 1.3) && (deta < 1.8) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 30) && (L1Jet_pt[1] > 30)"),
            #########################################################
            ## dPhi regions
            Category("sr_dphi", "dPhi > 2.7", selection="(dphi > 2.7)"),
            Category("cr_dphi", "dPhi <= 2.7", selection="(dphi <= 2.7)"),
            Category("cr_dphi_1", "2.5 < dPhi <= 2.7", selection="(dphi > 2.5) && (dphi <= 2.7)"),
            Category("cr_dphi_2", "2.3 < dPhi <= 2.5", selection="(dphi > 2.3) && (dphi <= 2.5)"),
            Category("cr_dphi_3", "2.1 < dPhi <= 2.3", selection="(dphi > 2.1) && (dphi <= 2.3)"),
            Category("cr_dphi_4", "1.9 < dPhi <= 2.1", selection="(dphi > 1.9) && (dphi <= 2.1)"),
            Category("cr_dphi_5", "1.7 < dPhi <= 1.9", selection="(dphi > 1.7) && (dphi <= 1.9)"),
            #########################################################
            ## Template method analyses
            # pT > 30, eta < 2.5
            Category("sr", "dEta < 1.1", selection="dphi > 1.047 && deta < 1.1"),
            Category("vr", "1.1 <= dEta < 1.5", selection="dphi > 1.047 && deta >= 1.1 && deta < 1.5"),
            Category("cr", "1.5 <= dEta < 2.6", selection="dphi > 1.047 && deta >= 1.5 && deta < 2.6"),
            # pT > 30, eta < 1.3
            Category("base_eta1p3", "|eta < 1.3|", selection="(dphi > 1.047) && (abs(L1Jet_eta[0]) < 1.3) && (abs(L1Jet_eta[1]) < 1.3)"),
            Category("sr_eta1p3", "dEta < 1.1, |eta < 1.3|", selection="(dphi > 1.047) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 1.3) && (abs(L1Jet_eta[1]) < 1.3)"),
            Category("vr_eta1p3", "1.1 <= dEta < 1.5, |eta < 1.3|", selection="(dphi > 1.047) && (deta >= 1.1) && (deta < 1.5) && (abs(L1Jet_eta[0]) < 1.3) && (abs(L1Jet_eta[1]) < 1.3)"),
            Category("cr_eta1p3", "1.5 <= dEta < 2.6, |eta < 1.3|", selection="(dphi > 1.047) && (deta >= 1.5) && (deta < 2.6) && (abs(L1Jet_eta[0]) < 1.3) && (abs(L1Jet_eta[1]) < 1.3)"),
            # pT > 30, eta < 1.1
            Category("base_eta1p1", "|eta < 1.1|", selection="(dphi > 1.047) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1)"),
            Category("sr_eta1p1", "dEta < 0.8, |eta < 1.1|", selection="(dphi > 1.047) && (deta < 0.8) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1)"),
            Category("vr_eta1p1", "0.8 <= dEta < 1.3, |eta < 1.1|", selection="(dphi > 1.047) && (deta >= 0.8) && (deta < 1.3) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1)"),
            Category("cr_eta1p1", "1.3 <= dEta < 2.2, |eta < 1.1|", selection="(dphi > 1.047) && (deta >= 1.3) && (deta < 2.2) && (abs(L1Jet_eta[0]) < 1.1) && (abs(L1Jet_eta[1]) < 1.1)"),
            # pT > 30, eta < 0.957
            Category("base_eta0p9", "|eta < 0.957|", selection="(dphi > 1.047) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("sr_eta0p9", "dEta < 0.8, |eta < 0.957|", selection="(dphi > 1.047) && (deta < 0.8) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("vr_eta0p9", "0.8 <= dEta < 1.3, |eta < 0.957|", selection="(dphi > 1.047) && (deta >= 0.8) && (deta < 1.3) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("cr_eta0p9", "1.3 <= dEta < 1.8, |eta < 0.957|", selection="(dphi > 1.047) && (deta >= 1.3) && (deta < 1.8) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            # pT > 50, eta < 2.5
            Category("sr_pt50", "dEta < 1.1, pT > 50", selection="(dphi > 1.047) && (deta < 1.1) && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            Category("vr_pt50", "1.1 <= dEta < 1.5, pT > 50", selection="(dphi > 1.047) && deta >= 1.1 && deta < 1.5 && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            Category("cr_pt50", "1.5 <= dEta < 2.6, pT > 50", selection="(dphi > 1.047) && deta >= 1.5 && deta < 2.6 && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            # pT > 50, eta < 0.957
            Category("sr_pt50_eta0p9", "dEta < 0.8, |eta < 0.957|, pT > 50", selection="(dphi > 1.047) && (deta < 0.8) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            Category("vr_pt50_eta0p9", "0.8 <= dEta < 1.3, |eta < 0.957|, pT > 50", selection="(dphi > 1.047) && deta >= 0.8 && deta < 1.3 && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            Category("cr_pt50_eta0p9", "1.3 <= dEta < 1.8, |eta < 0.957|, pT > 50", selection="(dphi > 1.047) && deta >= 1.3 && deta < 1.8 && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            #########################################################
            ## For data driven analyses
            # pT > 30, eta < 0.957, tight dEta
            Category("sr_barrel_full_inclusive", "dEta < 1.1, |eta| < 0.957", selection="(dphi > 1.047) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("sr_barrel_full_1", "dEta < 0.4, |eta| < 0.957", selection="(dphi > 1.047) && (deta < 0.4) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("sr_barrel_full_2", "0.4 <= dEta < 0.8, |eta| < 0.957", selection="(dphi > 1.047) && (deta >= 0.4) && (deta < 0.8) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            Category("sr_barrel_full_3", "0.8 <= dEta < 1.1, |eta| < 0.957", selection="(dphi > 1.047) && (deta >= 0.8) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957)"),
            # pT > 50, eta < 0.957, tight dEta
            Category("sr_pt50_barrel_full_inclusive", "dEta < 1.1, |eta| < 0.957, pT > 50", selection="(dphi > 1.047) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            Category("sr_pt50_barrel_full_1", "dEta < 0.4, |eta| < 0.957, pT > 50", selection="(dphi > 1.047) && (deta < 0.4) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            Category("sr_pt50_barrel_full_2", "0.4 <= dEta < 0.8, |eta| < 0.957, pT > 50", selection="(dphi > 1.047) && (deta >= 0.4) && (deta < 0.8) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            Category("sr_pt50_barrel_full_3", "0.8 <= dEta < 1.1, |eta| < 0.957, pT > 50", selection="(dphi > 1.047) && (deta >= 0.8) && (deta < 1.1) && (abs(L1Jet_eta[0]) < 0.957) && (abs(L1Jet_eta[1]) < 0.957) && (L1Jet_pt[0] > 50) && (L1Jet_pt[1] > 50)"),
            #########################################################
            ## Selections on corrected jets
            Category("sr_scale_corr", "dEta < 1.1", selection="dphi_scale_corr > 1.047 && deta_scale_corr < 1.1"),
            Category("vr_scale_corr", "1.1 <= dEta < 1.5", selection="dphi_scale_corr > 1.047 && deta_scale_corr >= 1.1 && deta_scale_corr < 1.5"),
            Category("cr_scale_corr", "1.5 <= dEta < 2.6", selection="dphi_scale_corr > 1.047 && deta_scale_corr >= 1.5 && deta_scale_corr < 2.6"),
            Category("sr_eta0p9_scale_corr", "dEta < 0.8, |eta < 0.957|", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr < 0.8) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957)"),
            Category("vr_eta0p9_scale_corr", "0.8 <= dEta < 1.3, |eta < 0.957|", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 0.8) && (deta_scale_corr < 1.3) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957)"),
            Category("cr_eta0p9_scale_corr", "1.3 <= dEta < 1.8, |eta < 0.957|", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 1.3) && (deta_scale_corr < 1.8) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957)"),
            # pT > 30 cut on the reordered jets
            Category("sr_pt30_scale_corr", "pT > 30, dEta < 1.1", selection="dphi_scale_corr > 1.047 && deta_scale_corr < 1.1 && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            Category("vr_pt30_scale_corr", "pT > 30, 1.1 <= dEta < 1.5", selection="dphi_scale_corr > 1.047 && deta_scale_corr >= 1.1 && deta_scale_corr < 1.5 && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            Category("cr_pt30_scale_corr", "pT > 30, 1.5 <= dEta < 2.6", selection="dphi_scale_corr > 1.047 && deta_scale_corr >= 1.5 && deta_scale_corr < 2.6 && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            Category("sr_pt30_eta0p9_scale_corr", "pT > 30, dEta < 0.8, |eta < 0.957|", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr < 0.8) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            Category("vr_pt30_eta0p9_scale_corr", "pT > 30, 0.8 <= dEta < 1.3, |eta < 0.957|", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 0.8) && (deta_scale_corr < 1.3) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            Category("cr_pt30_eta0p9_scale_corr", "pT > 30, 1.3 <= dEta < 1.8, |eta < 0.957|", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 1.3) && (deta_scale_corr < 1.8) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            # pT > 50 cut on the reordered jets
            Category("sr_pt50_scale_corr", "pT > 50, dEta < 1.1", selection="dphi_scale_corr > 1.047 && deta_scale_corr < 1.1 && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
            Category("vr_pt50_scale_corr", "pT > 50, 1.1 <= dEta < 1.5", selection="dphi_scale_corr > 1.047 && deta_scale_corr >= 1.1 && deta_scale_corr < 1.5 && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
            Category("cr_pt50_scale_corr", "pT > 50, 1.5 <= dEta < 2.6", selection="dphi_scale_corr > 1.047 && deta_scale_corr >= 1.5 && deta_scale_corr < 2.6 && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
            Category("sr_pt50_eta0p9_scale_corr", "pT > 50, dEta < 0.8, |eta < 0.957|", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr < 0.8) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
            Category("vr_pt50_eta0p9_scale_corr", "pT > 50, 0.8 <= dEta < 1.3, |eta < 0.957|", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 0.8) && (deta_scale_corr < 1.3) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
            Category("cr_pt50_eta0p9_scale_corr", "pT > 50, 1.3 <= dEta < 1.8, |eta < 0.957|", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 1.3) && (deta_scale_corr < 1.8) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
            # pT > 30, eta < 0.957, tight dEta
            Category("sr_pt30_barrel_full_inclusive_scale_corr", "pT > 30, dEta < 1.1, |eta| < 0.957", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr < 1.1) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            Category("sr_pt30_barrel_full_1_scale_corr", "pT > 30, dEta < 0.4, |eta| < 0.957", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr < 0.4) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            Category("sr_pt30_barrel_full_2_scale_corr", "pT > 30, 0.4 <= dEta < 0.8, |eta| < 0.957", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 0.4) && (deta_scale_corr < 0.8) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            Category("sr_pt30_barrel_full_3_scale_corr", "pT > 30, 0.8 <= dEta < 1.1, |eta| < 0.957", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 0.8) && (deta_scale_corr < 1.1) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 30) && (L1Jet_pt_scale_corr[1] > 30)"),
            # pT > 50, eta < 0.957, tight dEta
            Category("sr_pt50_barrel_full_inclusive_scale_corr", "dEta < 1.1, |eta| < 0.957, pT > 50", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr < 1.1) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
            Category("sr_pt50_barrel_full_1_scale_corr", "dEta < 0.4, |eta| < 0.957, pT > 50", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr < 0.4) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
            Category("sr_pt50_barrel_full_2_scale_corr", "0.4 <= dEta < 0.8, |eta| < 0.957, pT > 50", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 0.4) && (deta_scale_corr < 0.8) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
            Category("sr_pt50_barrel_full_3_scale_corr", "0.8 <= dEta < 1.1, |eta| < 0.957, pT > 50", selection="(dphi_scale_corr > 1.047) && (deta_scale_corr >= 0.8) && (deta_scale_corr < 1.1) && (abs(L1Jet_eta_scale_corr[0]) < 0.957) && (abs(L1Jet_eta_scale_corr[1]) < 0.957) && (L1Jet_pt_scale_corr[0] > 50) && (L1Jet_pt_scale_corr[1] > 50)"),
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
            Dataset("DataDijet",
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
            Dataset("DataZB",
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
                runPeriod = "2024",
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
                runPeriod = "2024",
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
                runPeriod = "2024",
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
                runPeriod = "2024",
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
                runPeriod = "2024",
            ),
        ]

        return ObjectCollection(datasets) + qcd_datasets

    def add_features(self):
        from config.features_dijet_2025 import features
        return ObjectCollection(features)

    def add_weights(self):
        weights = DotDict()
        weights.default = "1"

        #weights.total_events_weights = ["event_weight"]
        #weights.total_events_weights = ["puWeight_weight"]
        #weights.total_events_weights = ["1"]
        #weights.total_events_weights = ["qcd_weight"]
        # Adding the nTrueInt reweight
        weights.total_events_weights = ["qcd_weight", "puWeight"]

        #weights.base = ["event_weight"]
        #weights.base = ["1"]
        #weights.base = ["puWeight_weight"]
        #weights.base = ["qcd_weight"]
        weights.base = ["qcd_weight", "puWeight"]

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


config = Config("dijet_2025", year=2025, ecm=13.6, lumi_pb=45.0)