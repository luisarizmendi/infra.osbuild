#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: inject_ks
short_description: Inject Kickstart into composed ISO image.
description:
    - Inject Kickstart into composed ISO image.
author:
- Adam Miller (@maxamillion)
options:
    kickstart:
        description:
            - Path to kickstart file
        type: str
        required: true
    src_iso:
        description:
            - Path to ISO file that will be used as source to create new ISO with kickstart injected
        type: str
        required: true
    dest_iso:
        description:
            - Path the ISO file with kickstart injected into it should be in
        type: str
        required: true
    workdir:
        description:
            - A working directory to expand the ISO into
        type: str
        required: true
    version:
        description:
            - RHEL version to validate the kickstart against, styled as "RHEL8", "RHEL9", etc
        type: str
        required: false
        default: "RHEL8"
        choices: ["RHEL8","RHEL9"]

requires:
- coreutils-single
- glibc-minimal-langpack
- pykickstart
- mtools
- xorriso
- genisoimage
- syslinux
- isomd5sum
- lorax
"""

EXAMPLES = """
- name: inject kickstart into ISO
  osbuild.composer.inject_ks:
    kickstart: "/tmp/mykickstart.ks"
    src_iso: "/tmp/previously_composed.iso"
    dest_iso: "/tmp/with_my_kickstart.iso"
    workdir: "/root/edgeiso/
"""


import os
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native, to_text
from ansible.module_utils.common.locale import get_best_parsable_locale

import os

def run_cmd(module, cmd_list):

    # get local for shelling out
    locale = get_best_parsable_locale(module)
    lang_env = dict(LANG=locale, LC_ALL=locale, LC_MESSAGES=locale)

    rc, out, err = module.run_command(cmd_list, environ_update=lang_env)
    if (rc != 0) or err:
        module.fail_json("ERROR: Command '%s' failed with return code: %s and error message, '%s'" % (' '.join(cmd_list), rc, err))

    return out

def main():

    arg_spec=dict(
        kickstart=dict(type="str", required=True),
        src_iso=dict(type="str", required=True),
        dest_iso=dict(type="str", required=True),
        workdir=dict(type="str", required=True),
        version=dict(type="str", required=False, default="RHEL8", choices=['RHEL8', 'RHEL9']),
    )

    module = AnsibleModule(
        argument_spec=arg_spec,
    )

    # Sanity checking the paths exist
    for key in arg_spec:
        if key != "version":
            if not os.path.exists(module.params[key]):
                module.fail_json("No such file found: %s" % fname)

    # define paths to things we need
    isolinux_config = os.path.join(module.params['workdir'], '/isolinux/isolinux.cfg')
    efi_grub_config = os.path.join(module.params['workdir'], '/EFI/BOOT/grub.cfg')
    efi_dir = os.path.join(module.params['workdir'], '/EFI/BOOT')
    efiboot_imagepath = os.path.join(module.params['workdir'], '/images/efiboot.img')

    # get binary paths
    ksvalidator = module.get_bin_path('ksvalidator')
    isoinfo = module.get_bin_path('isoinfo')
    xorriso = module.get_bin_path('xorriso')
    mtype = module.get_bin_path('mtype')
    mcopy = module.get_bin_path('mcopy')
    mkefiboot = module.get_bin_path('mkefiboot')
    genisoimage = module.get_bin_path('genisoimage')
    isohybrid = module.get_bin_path('isohybrid')
    implantisomd5 = module.get_bin_path('implantisomd5')

    # validate the kickstart
    ksvalidator_cmd = [
        ksvalidator, '-v', module.params['version'], module.params['kickstart']
    ]
    ksvalidator_out = run_cmd(module, ksvalidator_cmd)

    # validate the kickstart
    isovolid_cmd = [isoinfo, '-d', '-i', module.params['src_']]
    isovolid_out = run_cmd(module, isovolid_cmd)
    # FIXME - need to make sure I'm 


    module.exit_json(msg=f'Blueprint file written to location: {module.params["dest"]}')


if __name__ == "__main__":
    main()
