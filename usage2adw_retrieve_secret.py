#!/usr/bin/env python3
##########################################################################
# Copyright (c) 2023, Oracle and/or its affiliates.                                                  
# Licensed under the Universal Permissive License v 1.0 as shown at  https://oss.oracle.com/licenses/upl/ 
#
# DISCLAIMER This is not an official Oracle application,  It does not supported by Oracle Support.
#
# usage2adw_retrieve_secret.py
#
# @author: Adi Zohar
#
# Supports Python 3 and above
#
# coding: utf-8
##########################################################################
# This script required policy to allow to retrieve secret from kms vault
#   Allow group UsageDownloadGroup to read secret-bundles in compartment {APPCOMP}
#
##########################################################################
#
# Modules Included:
# - oci.secrets.SecretsClient
#
# APIs Used:
# - get_secret_bundle
#
##########################################################################

import argparse
import datetime
import oci
import oci_utils 
import base64

version = "23.08.01"


##########################################################################
# Get Currnet Date Time
##########################################################################
def get_current_date_time():
    return str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

##########################################################################
# set parser
##########################################################################
def set_parser_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', type=argparse.FileType('r'), dest='config', help="Config File")
    parser.add_argument('-t', default="", dest='profile', help='Config file section to use (local for instance principle)')
    parser.add_argument('-p', default="", dest='proxy', help='Set Proxy (i.e. www-proxy-server.com:80) ')

    parser.add_argument('-secret', default="", dest='secret', help='Secret OCID')
    parser.add_argument('-check', action='store_true', default=False, dest='check', help='Run check for Secret Retrival')

    parser.add_argument('--version', action='version', version='%(prog)s ' + version)

    result = parser.parse_args()

    if not (result.secret):
        parser.print_help()
        print("You must specify secret ocid in order to generate wallet!")
        return None

    return result


##########################################################################
# get_secret_password
##########################################################################
def get_secret_password(config, signer, proxy, secret_id):

    try:
        print("\nConnecting to Secret Client Service...")
        secret_client = oci.secrets.SecretsClient(config, signer=signer)
        if proxy:
            secret_client.base_client.session.proxies = {'https': proxy}
        print("Connected.")

        secret_data = secret_client.get_secret_bundle(secret_id).data

        print("Secret Retrieved.")
        secret_bundle_content = secret_data.secret_bundle_content
        secret_base64 = secret_bundle_content.content
        secret_text_bytes = base64.b64decode(secret_base64)
        secret_text = secret_text_bytes.decode('ASCII')
        return secret_text

    except oci.exceptions.ServiceError as e:
        print("\ServiceError retrieving secret at get_secret_password !")
        print("\n" + str(e) + "\n")
        raise SystemExit

    except Exception as e:
        print("\Exception retrieving secret at get_secret_password !")
        print("\n" + str(e) + "\n")
        raise SystemExit


##########################################################################
# Main
##########################################################################
def main_process():
    try: 

        cmd = set_parser_arguments()
        if cmd is None:
            exit()
        config, signer = oci_utils.create_signer(cmd.profile, cmd.config)

        print("\nRunning Secret Retrieval from Vault")
        print("Starts at " + get_current_date_time())
        
        secret_text = get_secret_password(config, signer, cmd.proxy, cmd.secret)

        if cmd.check:
            print("Secret Okay")
        else:
            print("Secret=" + str(secret_text))

    except Exception as e:
        print("\nError at main_process !")
        print("\n" + str(e) + "\n")
        raise SystemExit


##########################################################################
# Execute Main Process
##########################################################################
main_process()
