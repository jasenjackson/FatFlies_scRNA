#!/usr/bin/env python3
"""
@author: Timothy Baker
@version: 1.0.0

scrna_configure_pipeline.py

"""


import os
import shlex
import argparse
import subprocess
import logging
from collections import OrderedDict
import yaml
from samplesheet_parser import SampleSheetParser
from zumi_config_builder import ZumiConfigBuilder

LOG_DIR = 'logs'

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)
    print("Made logs directory.")

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
FORMATTER = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s:%(message)s')
FILE_HANDLER = logging.FileHandler("logs/qc_log.log")
FILE_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLER)


def arg_parser():
    """ Argument input from command line """

    parser = argparse.ArgumentParser(
        description='Runs the single-cell RNA-seq pipeline.'
    )
    parser.add_argument('sample_sheet', type=str, help='Enter absolute/path/to/sample_sheet.csv')

    return parser.parse_args()


def represent_dictionary_order(self, dict_data):
    """ instantiates yaml dict mapping """
    return self.represent_mapping('tag:yaml.org,2002:map', dict_data.items())


def setup_yaml():
    """ adds the representer to the yaml instance """
    yaml.add_representer(OrderedDict, represent_dictionary_order)





def main():
    """ parses sample sheet object, creates various config files, and tracks threads """

    args = arg_parser()

    setup_yaml()

    LOGGER.info("Input args: %s", args)

    sample_sheet = args.sample_sheet

    LOGGER.info("Created SampleSheetParser Object")
    sample_obj = SampleSheetParser(sample_sheet)

    sample_obj.run_parsing_methods()
    LOGGER.info("Parsed sample sheet.")

    # creating barcode white list text file for zUMI
    sample_obj.create_adapter_whitelist()
    LOGGER.info("Created Barcode whitelist for zUMI.")

    # dict contains all relevant file paths
    file_path_info = sample_obj.return_path_info()

    # dict contains adapter trimming sequences
    adapter_info = sample_obj.return_adapters()


    run_qc_cmd = """python3 scrna_qc_pipeline.py
                    -t {threads}
                    -f {fastq_r1}
                    -p {fastq_r2}
                    -i {trimmed_r1}
                    -d {trimmed_r2}
                    -a {adapter_3}
                    -A {adapter_5}
                    -m 12
                    -M 20""".format(**kwargs)

    run_qc_formatted_args = shlex.split(run_qc_cmd)

    subprocess.run(run_qc_formatted_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == '__main__':
    main()
