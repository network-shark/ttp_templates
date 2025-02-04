Reference path:
```
ttp://misc/Netbox/parse_juniper_junos_config.txt
```

---

No `<doc>` tags found

---

<details><summary>Template Content</summary>
```
<template name="netbox_data" results="per_template">
<input>
commands = [
    "show configuration | display set"
]
</input>
    
<macro>    
def postprocess(data):
    # transform vrf dict to list
    data["vrf"] = [{"name": k, **v} for k, v in data.get("vrf", {}).items()]
    
    # update interfaces with VRF reference
    for vrf in data["vrf"]:
        for interface in vrf.get("interfaces", []):
            data["interfaces"][interface]["vrf"] = vrf["name"]
            
    # transform interfaces dict to list
    data["interfaces"] = [
        {"name": k, **v} 
        for k, v in data["interfaces"].items()
    ]
    
    # process interfaces further
    for i in data["interfaces"]:
        # add interface type - other, virtual or lag
        i["interface_type"] = "other"    
        if any(
            k in i["name"] for k in [".", "gr-", "lo0"]
        ):
            i["interface_type"] = "virtual"
        elif "ae" in i["name"]:
            i["interface_type"] = "lag"  
            
        # add interface parent details
        if "lag_id" in i:
            i["parent"] = i["lag_id"]
        elif "." in i["name"]:
            i["parent"] = i["name"].split(".")[0]    
            
        # set interface default parameters
        i.setdefault("enabled", True)
        i.setdefault("description", "")
        
    return data
</macro>

## ------------------------------------------------------------------------------------------
## Global Configuration facts
## ------------------------------------------------------------------------------------------
<group name="facts**" method="table">
set version {{ os_version }}
set groups {{ ignore }} system host-name {{ hostname }}
set system host-name {{ hostname }}
set groups {{ ignore }} system domain-name {{ domain_name }}
set system domain-name {{ domain_name }}
</group>

## ------------------------------------------------------------------------------------------
## ROuting-Options Configuration 
## ------------------------------------------------------------------------------------------
<group name="routing_options**" method="table">
set routing-options route-distinguisher-id {{ route_distinguisher }}
set routing-options router-id {{ rid }}
set routing-options autonomous-system {{ asn }}
</group>

## ------------------------------------------------------------------------------------------
## DNS Servers configuration
## ------------------------------------------------------------------------------------------
<group name="nameservers*">
set system name-server {{ name_server | let("vrf", "default") }}
</group>

## ------------------------------------------------------------------------------------------
## Logging and Archive configuration
## ------------------------------------------------------------------------------------------
<group name="logging**" method="table">
set system syslog source-address {{ source }}

<group name="archive" method="table">
set system syslog archive size {{ archive_size }}
set system syslog archive files {{ archive_files_count }}
</group>

<group name="logging_hosts" method="table">
set system syslog host {{ host }} any {{ severity }}
set system syslog host {{ host }} {{ ignore }}
</group>
</group>

## ------------------------------------------------------------------------------------------
## Users configuration
## ------------------------------------------------------------------------------------------
<group name="users*">
set system login user {{ username }} uid {{ uid }}
set system login user {{ ignore }} class {{ group }}
</group>

## ------------------------------------------------------------------------------------------
## AAA configuration
## ------------------------------------------------------------------------------------------
<group name="aaa">
set system authentication-order {{ authentication_login | joinmatches(", ") }}
</group>

<group name="tacacs.servers*">
set system tacplus-server {{ server }} source-address {{ source }}
</group>

## ------------------------------------------------------------------------------------------
## NTP configuration
## ------------------------------------------------------------------------------------------
<group name="ntp">
set system ntp source-address {{ source }}
</group>

<group name="ntp.servers*" method="table">
set system ntp server {{ server }}
</group>

## ------------------------------------------------------------------------------------------
## SSH configuration
## ------------------------------------------------------------------------------------------
<group name="ssh_server**" method="table">
set system services ssh root-login {{ root_login }}
set system services ssh protocol-version {{ version }}
set system services ssh max-sessions-per-connection {{ max_sessions_per_connection }}
set system services ssh sftp-{{ sftp | let("ssh_sftp_server_enable", True) }}
set system services ssh connection-limit {{ session_limit }}
set system services ssh rate-limit {{ rate_limit }}
</group>

## ------------------------------------------------------------------------------------------
## VRFs configuration
## ------------------------------------------------------------------------------------------
<group name="vrf**.{{ vrf }}**" method="table" expand="">
set routing-instances {{ vrf }} description {{ description | re(".+") | default("") }}
set routing-instances {{ vrf }} instance-type {{ instance_type }}
set routing-instances {{ vrf }} routing-options router-id {{ routing_options.rid }}
set routing-instances {{ vrf }} vrf-import {{ rpl_import }}
set routing-instances {{ vrf }} vrf-export {{ rpl_export }}
set routing-instances {{ vrf | let("vrf_table_label", True) }} vrf-table-label
set routing-instances {{ vrf }} vrf-target {{ route_target }}
set routing-instances {{ vrf }} protocols evpn extended-vlan-list {{ evpn.extended_vlan_list }}
set routing-instances {{ vrf }} protocols evpn default-gateway {{ evpn.default_gateway }}
set routing-instances {{ vrf }} vtep-source-interface {{ vtep_source_interface }}
</group>

<group name="vrf**.{{ vrf }}**.interfaces*" method="table" itemize="interface">
set routing-instances {{ vrf }} interface {{ interface }}
</group>

<group name="vrf**.{{ vrf }}**.bridge_domains**.{{ bd_name }}**" method="table">
set routing-instances {{ vrf }} bridge-domains {{ bd_name }} vlan-id {{ vlan_id }}
set routing-instances {{ vrf }} bridge-domains {{ bd_name }} routing-interface {{ routed_interface }}
set routing-instances {{ vrf }} bridge-domains {{ bd_name }} vxlan vni {{ vxlan_vni }}
set routing-instances {{ vrf }} bridge-domains {{ bd_name }} vxlan multicast-group {{ vxlan_multicast_group }}
set routing-instances {{ vrf }} bridge-domains {{ bd_name }} vxlan destination-udp-port {{ vxlan_dst_port }}
set routing-instances {{ vrf }} bridge-domains {{ bd_name }} proxy-mac {{ proxy_mac }}
</group>

## ------------------------------------------------------------------------------------------
## Interfaces configuration
## ------------------------------------------------------------------------------------------
<group name="interfaces**.{{ name }}**" method="table">
set interfaces {{ name }} description "{{ description | re(".+") | default("") }}"
set interfaces {{ name }} mtu {{ mtu | to_int }}
set interfaces {{ name | let("enabled", False) }} disable
set interfaces {{ name }} gigether-options {{ gigether_options }}
set interfaces {{ name }} gigether-options 802.3ad {{ lag_id }}
set interfaces {{ name }} hold-time up {{ hold_time_up }}
set interfaces {{ name }} hold-time down {{ hold_time_down }}
set interfaces {{ name | let("per_unit_scheduler", True) }} per-unit-scheduler
set interfaces {{ name | let("flexible_vlan_tagging", True) }} flexible-vlan-tagging
set interfaces {{ name }} encapsulation {{ encapsulation }}
set interfaces {{ name }} aggregated-ether-options minimum-links {{ lag_min_links }}
set interfaces {{ name }} aggregated-ether-options lacp {{ lacp_mode }}
</group>

<group name="interfaces**.{{ name }}**.damping**" method="table">
set interfaces {{ name }} damping half-life {{ half_life }}
set interfaces {{ name }} damping max-suppress {{ max_suppress }}
set interfaces {{ name }} damping reuse {{ reuse }}
set interfaces {{ name }} damping suppress {{ suppress }}
set interfaces {{ name | let("is_enabled", True) }} damping enable
</group>

<group name="interfaces**.{{ name }}**" functions="sformat('{name}.{unit}', 'name')" method="table">
set interfaces {{ name }} unit {{ unit }} description {{ description | re(".+") | default("") }}
set interfaces {{ name }} unit {{ unit }} vlan-id {{ dot1q }}
</group>

<group name="interfaces**.{{ name }}**.family*" functions="sformat('{name}.{unit}', 'name') | del('unit')" method="table">
set interfaces {{ name }} unit {{ unit }} family {{ afi }}
set interfaces {{ name }} unit {{ unit }} family {{ afi }}
</group>

<group name="interfaces**.{{ name }}**.ipv4_acl_in*" functions="sformat('{name}.{unit}', 'name') | del('unit')" method="table">
set interfaces {{ name }} unit {{ unit }} family inet filter input-list {{ acl }}
</group>

<group name="interfaces**.{{ name }}**.ipv4*" functions="sformat('{name}.{unit}', 'name') | del('unit')" method="table">
set interfaces {{ name }} unit {{ unit }} family inet address {{ ip }}/{{ mask }}
set interfaces {{ name }} unit {{ unit }} family inet address {{ ip }}/{{ mask }} virtual-gateway-address {{ virtual_gateway_address }}
</group>

<group name="interfaces**.{{ name }}**.virtual_gateway**" functions="sformat('{name}.{unit}', 'name') | del('unit')" method="table">
set interfaces {{ name }} unit {{ unit }} virtual-gateway-v4-mac {{ mac }}
set interfaces {{ name }} unit {{ unit | let("accept_data", True) }} virtual-gateway-accept-data
</group>

<group name="interfaces**.{{ name }}**.ipv6*" functions="sformat('{name}.{unit}', 'name') | del('unit')" method="table">
set interfaces {{ name }} unit {{ unit }} family inet6 address {{ ip }}/{{ mask | _exact_ }}
</group>

<group name="interfaces**.{{ name }}**.esi**" functions="sformat('{name}.{unit}', 'name') | del('unit')" method="table">
set interfaces {{ name }} unit {{ unit }} esi {{ esi }}
set interfaces {{ name }} unit {{ unit | let("single_active", True) }} esi single-active
</group>

<group name="interfaces**.{{ name }}**.tunnel**" functions="sformat('{name}.{unit}', 'name') | del('unit')" method="table">
set interfaces {{ name }} unit {{ unit }} tunnel routing-instance destination {{ destination_vrf }}
set interfaces {{ name }} unit {{ unit }} tunnel source {{ source }}
set interfaces {{ name }} unit {{ unit }} tunnel destination {{ destination }}
</group>

## ------------------------------------------------------------------------------------------
## BGP configuration
## ------------------------------------------------------------------------------------------
<group name="bgp**" method="table">
set routing-options router-id {{ rid }}
set routing-options autonomous-system {{ asn }}
</group>

<group name="bgp**.neighbor_groups**.{{ name }}**" method="table">
set protocols bgp group {{ name }} type {{ peering_type }}
set protocols bgp group {{ name }} metric-out {{ metric_out }}
set protocols bgp group {{ name }} peer-as {{ neighbor_asn }}
set protocols bgp group {{ name }} local-as {{ local_asn }}
set protocols bgp group {{ name | let("multipath_enabled", True) }} multipath
set protocols bgp group {{ name }} local-address {{ update_source }}
set protocols bgp group {{ name | let("hello_auth_enabled", True) }} authentication-key {{ ignore }}
set protocols bgp group {{ name }} bfd-liveness-detection minimum-interval {{ bfd_minimum_interval }}
set protocols bgp group {{ name }} bfd-liveness-detection multiplier {{ bfd_multiplier }}\
</group>

<group name="bgp**.neighbor_groups**.{{ name }}**.rpl_out*" method="table">
set protocols bgp group {{ name }} export {{ rpl }}
</group>

<group name="bgp**.neighbor_groups**.{{ name }}**.rpl_in*" method="table">
set protocols bgp group {{ name }} import {{ rpl }}
</group>

<group name="bgp**.neighbors**.{{ neighbor_ip }}**" method="table">
set protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }}
set protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }} description {{ description | re(".+") }}
set protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }} peer-as {{ neighbor_asn }}
set protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }} family {{ ignore(PHRASE) }}
</group>

<group name="bgp**.neighbors**.{{ neighbor_ip }}**.afi.{{ afi }}_{{ sub_afi }}**" method="table" del="neighbor_group">
set protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }} family {{ afi }} {{ sub_afi | let("enabled", True) }}
</group>

<group name="bgp**.neighbor_groups**.{{ name }}**.afi.{{ afi }}_{{ sub_afi }}**" method="table">
set protocols bgp group {{ name }} family {{ afi }} {{ sub_afi | let("add_path_receive", True) }} add-path receive
set protocols bgp group {{ name }} family {{ afi }} {{ sub_afi }} add-path send path-count {{ add_path_advertise }}
set protocols bgp group {{ name }} family {{ afi }} {{ sub_afi | let("enabled", True) }}
set protocols bgp group {{ name }} family {{ afi }} {{ sub_afi | let("signaling", True) }} signaling
</group>

<group name="bgp**.vrf**.{{ vrf }}**" method="table">
set routing-instances {{ vrf }} routing-options autonomous-system 4200020059
</group>

<group name="bgp**.vrf**.{{ vrf }}**.neighbor_groups**.{{ name }}**" method="table">
set routing-instances {{ vrf }} protocols bgp group {{ name }} type {{ peering_type }}
set routing-instances {{ vrf }} protocols bgp group {{ name }} metric-out {{ metric_out }}
set routing-instances {{ vrf }} protocols bgp group {{ name | let("hello_auth_enabled", True) }} authentication-key {{ ignore }}
set routing-instances {{ vrf }} protocols bgp group {{ name }} peer-as {{ neighbor_asn }}
set routing-instances {{ vrf }} protocols bgp group {{ name }} local-as {{ local_asn }}
set routing-instances {{ vrf }} protocols bgp group {{ name }} bfd-liveness-detection minimum-interval {{ bfd_minimum_interval }}
set routing-instances {{ vrf }} protocols bgp group {{ name }} bfd-liveness-detection multiplier {{ bfd_multiplier }}
</group>

<group name="bgp**.vrf**.{{ vrf }}**.neighbor_groups**.{{ name }}**.rpl_out*" method="table">
set routing-instances {{ vrf }} protocols bgp group {{ name }} export {{ rpl }}
</group>

<group name="bgp**.vrf**.{{ vrf }}**.neighbor_groups**.{{ name }}**.rpl_in*" method="table">
set routing-instances {{ vrf }} protocols bgp group {{ name }} import {{ rpl }}
</group>

<group name="bgp**.vrf**.{{ vrf }}**.neighbors**.{{ neighbor_ip }}**" method="table">
set routing-instances {{ vrf }} protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }}
set routing-instances {{ vrf }} protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }} description {{ description | re(".+") }}
set routing-instances {{ vrf }} protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }} peer-as {{ neighbor_asn }}
set routing-instances {{ vrf }} protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }} family {{ ignore(PHRASE) }}
</group>

<group name="bgp**.vrf**.{{ vrf }}**.neighbors**.{{ neighbor_ip }}**.afi.{{ afi }}_{{ sub_afi }}**" method="table" del="neighbor_group">
set routing-instances {{ vrf }} protocols bgp group {{ neighbor_group }} neighbor {{ neighbor_ip }} family {{ afi }} {{ sub_afi | let("enabled", True) }}
</group>

## ------------------------------------------------------------------------------------------
## PIM configuration
## ------------------------------------------------------------------------------------------
<group name="pim**" method="table">
set protocols pim rp bidirectional address {{ rp_didir }} group-ranges {{ rp_group_range }}
</group>

<group name="pim**.interfaces**.{{ interface }}**" method="table">
set protocols pim interface{{ interface }} mode {{ mode }}
</group>

## ------------------------------------------------------------------------------------------
## IGMP configuration
## ------------------------------------------------------------------------------------------
<group name="igmp**.interfaces**.{{ interface }}**" method="table">
set protocols igmp interface {{ interface }} version {{ version }}
</group>

## ------------------------------------------------------------------------------------------
## ISIS configuration
## ------------------------------------------------------------------------------------------
<group name="isis**.level_{{ level }}**" method="table">
set protocols isis level {{ level | let("enabled", False) }} disable
set protocols isis level {{ level | let("lsp_hmac_md5_auth_enabled", True) }} authentication-key {{ ignore }}
set protocols isis level {{ level | let("metric_style", "wide_metrics_only") }} wide-metrics-only
set protocols isis level {{ level }} prefix-export-limit {{ prefix_export_limit }}
</group>

<group name="isis**.interfaces**.{{ interface }}**.level_{{ level }}**" method="table">
set protocols isis interface {{ interface }} level {{ level }} post-convergence-lfa node-protection cost {{ lfa_node_prot_cost }}
set protocols isis interface {{ interface }} level {{ level }} metric {{ metric }}
set protocols isis interface {{ interface }} level {{ level | let("hello_hmac_md5_auth_enabled", True) }} hello-authentication-key {{ ignore }}
</group>

<group name="isis**.interfaces**.{{ interface }}**" method="table">
set protocols isis interface {{ interface }} hello-padding {{ hello_padding }}
set protocols isis interface {{ interface | let("link_type", "point-to-point") }} point-to-point
set protocols isis interface {{ interface | let("is_passive", True) }} passive
</group>

<group name="isis**.interfaces**.{{ interface }}**.afi.{{ afi }}" method="table">
set protocols isis interface {{ interface }} family {{ afi }} bfd-liveness-detection minimum-interval {{ bfd_minimum_interval }}
set protocols isis interface {{ interface }} family {{ afi }} bfd-liveness-detection multiplier {{ bfd_multiplier }}
</group>

<output name="postprocess" macro="postprocess"/>
</template>
```
</details>