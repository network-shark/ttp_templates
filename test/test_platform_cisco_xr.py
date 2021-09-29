import sys
import pprint

sys.path.insert(0, "..")

from ttp_templates import get_template
from ttp import ttp


def test_cisco_ios_show_ip_ospf_database_router():
    with open(
        "./mock_data/cisco_xr_show_isis_database_verbose.txt", "r"
    ) as f:
        data = f.read()
    template = get_template(
        platform="cisco_xr", command="show isis database verbose"
    )
    # print(template)
    parser = ttp(data=data, template=template)
    parser.parse()
    res = parser.result()
    # pprint.pprint(res)
    assert res == [[{'isis_processes': {'100': {'LSP': [{'hostname': 'R1-X1',
                                       'isis_area': '49.0001',
                                       'level': 'Level-2',
                                       'links': [{'affinity': '0x00000000',
                                                  'bw_kbit': '10000000',
                                                  'local_intf_id': '9',
                                                  'local_ip': '10.123.0.17',
                                                  'metric': '16777214',
                                                  'peer_intf_id': '50',
                                                  'peer_ip': '10.123.0.18',
                                                  'peer_name': 'R1-X2'},
                                                 {'affinity': '0x00000000',
                                                  'bw_kbit': '10000000',
                                                  'local_intf_id': '7',
                                                  'local_ip': '10.123.0.25',
                                                  'metric': '123',
                                                  'peer_intf_id': '53',
                                                  'peer_ip': '10.123.0.26',
                                                  'peer_name': 'R2-X1'}],
                                       'lsp_id': 'R1-X1',
                                       'networks': [{'metric': '0',
                                                     'network': '10.111.1.1/32'}],
                                       'rid': '10.111.1.1'},
                                      {'hostname': 'R1-X2',
                                       'isis_area': '49.0001',
                                       'level': 'Level-2',
                                       'links': [{'affinity': '0x00000000',
                                                  'bw_kbit': '10000000',
                                                  'local_intf_id': '48',
                                                  'local_ip': '10.123.0.33',
                                                  'metric': '456',
                                                  'peer_intf_id': '53',
                                                  'peer_ip': '10.123.0.34',
                                                  'peer_name': 'R2-X2'},
                                                 {'affinity': '0x00000000',
                                                  'bw_kbit': '10000000',
                                                  'local_intf_id': '50',
                                                  'local_ip': '10.123.0.18',
                                                  'metric': '123',
                                                  'peer_intf_id': '9',
                                                  'peer_ip': '10.123.0.17',
                                                  'peer_name': 'R1-X1'}],
                                       'lsp_id': 'R1-X2',
                                       'networks': [{'metric': '0',
                                                     'network': '10.111.1.2/32'}],
                                       'rid': '10.111.1.2'}]},
                      '200': {'LSP': [{'hostname': 'R1-X1',
                                       'isis_area': '49.0001',
                                       'level': 'Level-2',
                                       'links': [{'bw_kbit': '10000000',
                                                  'delay_avg_us': '1',
                                                  'delay_max_us': '1',
                                                  'delay_min_us': '1',
                                                  'delay_variation_us': '0',
                                                  'local_intf_id': '68',
                                                  'metric': '10',
                                                  'peer_intf_id': '57',
                                                  'peer_name': 'R2-X1',
                                                  'srv6_endx_sid': [{'algo': '0',
                                                                     'args_length': '0',
                                                                     'block_length': '32',
                                                                     'func_length': '16',
                                                                     'node_id_length': '16',
                                                                     'sid': 'fdff:0:1:e000::'},
                                                                    {'algo': '128',
                                                                     'args_length': '0',
                                                                     'block_length': '32',
                                                                     'func_length': '16',
                                                                     'node_id_length': '16',
                                                                     'sid': 'fdff:0:1001:e001::'}]}],
                                       'lsp_id': 'R1-X1',
                                       'networks': [{'metric': '0',
                                                     'network': 'fddd:2:c101::1/128'},
                                                    {'metric': '1',
                                                     'network': 'fdff:0:1::/48'},
                                                    {'metric': '0',
                                                     'network': 'fdff:3::/36'},
                                                    {'metric': '0',
                                                     'network': 'fdff::/36'}],
                                       'rid': 'fddd:2:c101::1',
                                       'srv6_locators': [{'algo': '0',
                                                          'locator': 'fdff:0:1::',
                                                          'mask': '48'},
                                                         {'algo': '128',
                                                          'locator': 'fdff:0:1001::',
                                                          'mask': '48'}]},
                                      {'hostname': 'R1-X2',
                                       'isis_area': '49.0001',
                                       'level': 'Level-2',
                                       'links': [{'bw_kbit': '10000000',
                                                  'delay_avg_us': '1',
                                                  'delay_max_us': '1',
                                                  'delay_min_us': '1',
                                                  'delay_variation_us': '0',
                                                  'local_intf_id': '68',
                                                  'metric': '10',
                                                  'peer_intf_id': '60',
                                                  'peer_name': 'R2-X2',
                                                  'srv6_endx_sid': [{'algo': '0',
                                                                     'args_length': '0',
                                                                     'block_length': '32',
                                                                     'func_length': '16',
                                                                     'node_id_length': '16',
                                                                     'sid': 'fdff:0:2:e000::'},
                                                                    {'algo': '128',
                                                                     'args_length': '0',
                                                                     'block_length': '32',
                                                                     'func_length': '16',
                                                                     'node_id_length': '16',
                                                                     'sid': 'fdff:0:4444:e001::'}]}],
                                       'lsp_id': 'R1-X2',
                                       'networks': [{'metric': '0',
                                                     'network': 'fdff::/36'},
                                                    {'metric': '1',
                                                     'network': 'fdff:0:2::/48'},
                                                    {'metric': '0',
                                                     'network': 'fdff:2::/36'},
                                                    {'metric': '0',
                                                     'network': 'fdff:3::/36'},
                                                    {'metric': '0',
                                                     'network': 'fddd:2:c101::2/128'}],
                                       'rid': 'fddd:2:c101::2',
                                       'srv6_locators': [{'algo': '0',
                                                          'locator': 'fdff:0:2::',
                                                          'mask': '48'},
                                                         {'algo': '128',
                                                          'locator': 'fdff:0:4444::',
                                                          'mask': '48'}]}]}}}]]
                                                           
# test_cisco_ios_show_ip_ospf_database_router()