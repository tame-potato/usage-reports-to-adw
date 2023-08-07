##########################################################################
# Create signer shared function
#   Creates a signer for use with the OCI API using intant principles if cmd.profile is not defined or defined as "local". 
#   For any other value in cmd.profile the matching profile from ~/.oci/config will be loaded.
##########################################################################

import oci

def create_signer(profile, config_file = None):

    # assign default values
    config_file = oci.config.DEFAULT_LOCATION if config_file is None else config_file.name
    config_section = oci.config.DEFAULT_PROFILE
    instant_principals = True

    if profile:
        instant_principals = (profile == 'local')
        config_section = profile

    if instant_principals:
        try:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            config = {'region': signer.region, 'tenancy': signer.tenancy_id}
            return config, signer
        except Exception:
            print("Error obtaining instance principals certificate, aborting...")
            raise SystemExit
    else:
        config = oci.config.from_file(config_file, config_section)
        signer = oci.signer.Signer(
            tenancy=config["tenancy"],
            user=config["user"],
            fingerprint=config["fingerprint"],
            private_key_file_location=config.get("key_file"),
            pass_phrase=oci.config.get_config_value_or_default(config, "pass_phrase"),
            private_key_content=config.get("key_content")
        )
        return config, signer