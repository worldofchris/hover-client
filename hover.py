#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from hover.client import HoverClient, HoverException
    HAS_LIB=True
except:
    HAS_LIB=False

def main():

    module = AnsibleModule(
        argument_spec=dict(
            domain=dict(required=True, default=None),
            username=dict(required=True, default=None),
            password=dict(required=True, default=None),
            state=dict(choices=['present', 'absent'], default='present'),
            type=dict(choices=['A',
                               'ALIAS',
                               'CNAME',
                               'MX',
                               'SPF',
                               'URL',
                               'TXT',
                               'NS',
                               'SRV',
                               'NAPTR',
                               'PTR',
                               'AAAA',
                               'SSHFP',
                               'HINFO',
                               'POOL'], default='A'),
            name=dict(required=True, default=None),
            value=dict(required=True, default=None),
        ),
        add_file_common_args=True,
        supports_check_mode=False
    )

    if not HAS_LIB:
        module.fail_json(msg="Requires hover module")

    params = module.params
    changed = False

    try:
        hc = HoverClient(username=params['username'],
                         password=params['password'],
                         domain_name=params['domain'])

        record = hc.get_record(name=params['name'], type=params['type'])

        if params['state'] == 'present':

            if record is None:
                hc.add_record(name=params['name'],
                              type=params['type'],
                              content=params['value'])
                changed = True
            else:

                if record['content'] != params['value']:
                    hc.update_record(name=params['name'],
                                     type=params['type'],
                                     content=params['value'])
                    changed = True
        else:
            if record is not None:
                hc.remove_record(name=params['name'],
                                 type=params['type'])
                changed = True
    except HoverException as e:
        module.fail_json(msg=str(e))

    module.exit_json(changed=changed)

# import module snippets
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
