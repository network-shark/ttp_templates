Reference path:
```
ttp://misc/Netbox/parse_cisco_xr_config.txt
```

---

No `<doc>` tags found

---

<details><summary>Template Content</summary>
```
<template name="netbox_data" results="per_template">
<input>
commands = [
    "show running-config"
]
</input>

<macro>
def add_interface_type(data):
    data["interface_type"] = "other"    
    if any(
        i in data["name"].lower() for i in [
            "bvi", ".", "loopback", "tunnel"
        ]
    ):
        data["interface_type"] = "virtual"
    elif "bundle" in data["name"].lower():
        data["interface_type"] = "lag"    
    return data
    
def add_parent_interface(data):
    if "lag_id" in data:
        data["parent"] = "Bundle-Ether{}".format(data["lag_id"])
    elif "." in data["name"]:
        data["parent"] = data["name"].split(".")[0]
    return data
</macro>

## ------------------------------------------------------------------------------------------
## Global Configuration facts
## ------------------------------------------------------------------------------------------
<group name="facts**" method="table">
hostname {{ hostname }}
!! IOS XR Configuration {{ os_version }}
!! Last configuration change at {{ config_changed_last }} by {{ config_changed_by }}
fpd auto-upgrade enable {{ fpd_auto_upgrade_enabled | set(True) }}
domain name {{ domain_name }}
</group>

## ------------------------------------------------------------------------------------------
## DNS Servers configuration
## ------------------------------------------------------------------------------------------
<group name="nameservers**.{{ vrf }}" method="table">
domain vrf {{ vrf }} name-server {{ name_server }}
domain vrf {{ vrf }} lookup source-interface {{ source_interface }}
</group>

## ------------------------------------------------------------------------------------------
## Logging and Archive configuration
## ------------------------------------------------------------------------------------------
<group name="logging**" method="table">
logging buffered {{ logging_buffered_size }}
logging buffered {{ logging_buffered_severity }}
logging facility {{ facility }}
logging source-interface {{ source }} vrf {{ vrf }}
logging source-interface {{ source }}

<group name="logging_hosts" method="table">
logging {{ host }} vrf {{ vrf }}
logging {{ host }}
</group>

<group name="archive">
logging archive {{ _start_ }}
 device {{ device }}
 severity {{ severity }}
 file-size {{ file_size }}
 frequency {{ frequency }}
 threshold {{ threshold }}
 archive-size {{ archive_size }}
 archive-length {{ archive_length }}
!{{ _end_ }}
</group>
</group>

## ------------------------------------------------------------------------------------------
## Users configuration
## ------------------------------------------------------------------------------------------
<group name="users*">
username {{ username }}
 group {{ group | joinmatches }}
</group>

## ------------------------------------------------------------------------------------------
## AAA configuration
## ------------------------------------------------------------------------------------------
<group name="aaa">
tacacs source-interface {{ tacacs_source }} vrf {{ tacacs_vrf }}
aaa authorization exec default group {{ authorization_exec | PHRASE }}
aaa authorization commands default group {{ authorization_commands | PHRASE }}
aaa authentication login default group {{ authentication_login | PHRASE }}
</group>

## ------------------------------------------------------------------------------------------
## gRPC configuration
## ------------------------------------------------------------------------------------------
<group name="grpc">
grpc {{ _start_ }}
 vrf {{ vrf }}
 port {{ port }}
 tls-mutual {{ tls_mutual | set(True) }}
 address-family {{ address_family }}
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## VRFs configuration
## ------------------------------------------------------------------------------------------
<group name="vrf*">
vrf {{ name}}
 rd {{ rd }}
 description {{ description | re(".+") | default("") }}
 
 <group name="afi.{{ afi }}_{{ sub_afi }}">
 address-family {{ afi }} {{ sub_afi }}
  import route-policy {{ rpl_import }}
  export route-policy {{ rpl_export }}
  
  <group name="route_target**">
  import route-target {{ _start_ }}
   {{ import | contains(":") | to_list | joinmatches }}
  ! {{ _end_ }}
  </group>

  <group name="route_target**">
  export route-target {{ _start_ }}
   {{ export | contains(":") | to_list | joinmatches }}
  ! {{ _end_ }}
  </group>
  
 ! {{ _end_ }}
 </group>
 
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## NTP configuration
## ------------------------------------------------------------------------------------------
<group name="ntp">
ntp {{ _start_ }}
 <group name="servers*" method="table">
 server vrf {{ vrf }} {{ server }} source {{ source }}
 server vrf {{ vrf }} {{ server }}
 server {{ server }}
 </group>
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## Interfaces configuration
## ------------------------------------------------------------------------------------------
<group name="interfaces*" functions="contains('name') | macro('add_interface_type') | macro('add_parent_interface')">
interface {{ name | _start_ }}
interface {{ name | _start_ }} l2transport
interface preconfigure {{ name | _start_ | let("preconfigure", True) }}
 description {{ description | re(".*") | default("") }}
 mtu {{ mtu | to_int }}
 service-policy input {{ qos_policy_in }}
 service-policy output {{ qos_policy_out }}
 encapsulation dot1q {{ dot1q }}
 vrf {{ vrf }}
 bundle id {{ lag_id }} mode {{ lacp_mode }}
 lacp period {{ lacp_period }}
 shutdown {{ enabled | set(False) | default(True) }}
 rewrite ingress tag {{ rewrite_ingress_tag | PHRASE }}
 ipv4 access-group {{ ipv4_acl_in | _exact_ }} ingress
 ipv4 access-group {{ ipv4_acl_out | _exact_ }} egress
 ipv6 access-group {{ ipv6_acl_in | _exact_ }} ingress
 ipv6 access-group {{ ipv6_acl_out | _exact_ }} egress
 mac-address {{ mac_address }}
 host-routing {{ host_routing | set(True) }}
 arp timeout {{ arp_timeout }}
 load-interval {{ load_interval }}
 
 <group name="ipv4*" method="table">
 ipv4 address {{ ip | _exact_ }} {{ mask }}
 ipv4 address {{ ip | _exact_ | let("secondary", True) }} {{ mask}} secondary
 </group>
 
 <group name="ipv6*" method="table"> 
 ipv6 address {{ ip | _exact_ }}/{{ mask }}
 </group>
 
 <group name="lldp">
 lldp {{ _start_ }}
  enable {{ lldp_enabled | set(True) }}
  transmit disable {{ transmit_disabled | set(True) }}
 </group>

!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## VRRP configuration
## ------------------------------------------------------------------------------------------
<group name="vrrp*">
router vrrp {{ _start_ }}
 <group name="interfaces*">
 interface {{ interface }}
  <group name="{{ afi }}_afi">
  address-family {{ afi }}
   <group name="groups*">
   vrrp {{ vrrp_group }}
    priority {{ priority }}
    address {{ address }}
    address global {{ address }}
    text-authentication {{ ignore | let("auth_enabled", True)}} 
   !{{ _end_ }}
   </group>
  !{{ _end_ }}
  </group>
 !{{ _end_ }}
 </group>
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## DHCP configuration
## ------------------------------------------------------------------------------------------
<group name="dhcp.{{ afi }}_afi">
dhcp {{ afi }}
 <group name="dhcp_profiles*">
 profile {{ profile_name }} relay
  relay information option {{ relay_information_option | set(True) }}
  <group name="helpers*">
  helper-address vrf {{ vrf }} {{ helper_address }}
  </group>
 !{{ _end_ }}
 </group>
 
 <group name="interfaces*.{{ interface }}">
 interface {{ interface }} relay profile {{ profile_name }}
 <group name="dhcp_options*">
 interface {{ interface }} relay information option {{ option | PHRASE }}
 </group>
 </group>
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## SSH configuration
## ------------------------------------------------------------------------------------------
<group name="ssh_server**" method="table">
ssh timeout {{ timeout }}
ssh server rate-limit {{ rate_limit }}
ssh server session-limit {{ session_limit }}
ssh server {{ version }}
<group name="vrfs*" itemize="vrf">
ssh server vrf {{ vrf }}
</group>
</group>

## ------------------------------------------------------------------------------------------
## L2VPN configuration
## ------------------------------------------------------------------------------------------
<group name="l2vpn**">
l2vpn {{ _start_ }}
 <group name="bridge_groups*">
 bridge group {{ bridge_group_name }}
  <group name="bridge_domains*">
  bridge-domain {{ bridge_domain_name }}
   description {{ description | re(".+") }}
   multicast-source {{ multicast_source }}
   igmp snooping profile {{ igmp_snooping_profile }}
   routed interface {{ routed_interface }}
   evi {{ evi }}
   <group name="interfaces*">
   interface {{ name }}
   !{{ _end_ }}
   </group>
  !{{ _end_ }}
  </group>
 !{{ _end_ }}
 </group>
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## BGP configuration
## ------------------------------------------------------------------------------------------
<group name="bgp">
router bgp {{ asn }}
 bgp router-id {{ rid }}
 bgp log neighbor changes detail {{ bgp_log_neighbor_changes | set(True) }}
 ibgp policy out enforce-modifications {{ ibgp_policy_out_enforce_modifications | set(True) }}
 bgp bestpath as-path multipath-relax {{ bgp_bestpath_as_path_multipath_relax | set(True) }}
 
 <group name="afi.{{ afi }}_{{ sub_afi }}">
 address-family {{ afi }} {{ sub_afi }}
  maximum-paths eibgp {{ eibgp_max_path }}  
  redistribute {{ redistribute | ORPHRASE | to_list | joinmatches }}
  bgp implicit-import {{ bgp_implicit_import | set(True) }}
 !{{ _end_ }}
 </group>
 
 <group name="neighbor_groups*">
 neighbor-group {{ name }}
  timers {{ keepalive }} {{ holdtime }}
  bfd fast-detect {{ bfd_fast_detect | set(True) }}
  bfd multiplier {{ bfd_multiplier }}
  bfd minimum-interval {{ bfd_minimum_interval }}
  password encrypted {{ ignore }} {{ hello_auth_enabled | set(True) }}
  description {{ description | re(".+") }}
  update-source {{ update_source }} 
  
  <group name="afi.{{ afi }}_{{ sub_afi }}">
  address-family {{ afi }} {{ sub_afi }}
   send-community-ebgp {{ send_community_ebgp | set(True) }}
   multipath {{ multipath_enabled | set(True) }}
   route-policy {{ rpl_in }} in
   route-policy {{ rpl_out }} out
   soft-reconfiguration inbound {{ soft_reconfiguration_inbound }}
   route-reflector-client {{ route_reflector_client | set(True) }}
  !{{ _end_ }}
  </group>  
  
 !{{ _end_ }}
 </group>
 
 <group name="neighbors**.{{ neighbor_ip }}">
 neighbor {{ neighbor_ip }}
  remote-as {{ neighbor_asn }}
  use neighbor-group {{ neighbor_group }}
  description {{ description | re(".+") }}
  update-source {{ update_source }}
 </group>   
  
 <group name="vrf**.{{ vrf }}">
 vrf {{ vrf }}
 
  <group name="afi.{{ afi }}_{{ sub_afi }}">
  address-family {{ afi }} {{ sub_afi }}
   maximum-paths eibgp {{ eibgp_max_path }}  
   redistribute {{ redistribute | ORPHRASE | to_list | joinmatches }}
  !{{ _end_ }}
  </group>
  
  <group name="neighbors**.{{ neighbor_ip }}">
  neighbor {{ neighbor_ip }}
   remote-as {{ neighbor_asn }}
   use neighbor-group {{ neighbor_group }}
   description {{ description | re(".+") }}
   
   <group name="afi.{{ afi }}_{{ sub_afi }}">
   address-family {{ afi }} {{ sub_afi }}
    send-community-ebgp {{ send_community_ebgp | set(True) }}
    multipath {{ multipath_enabled | set(True) }}
    route-policy {{ rpl_in }} in
    route-policy {{ rpl_out }} out
    soft-reconfiguration inbound {{ soft_reconfiguration_inbound }}
    route-reflector-client {{ route_reflector_client | set(True) }}
   !{{ _end_ }}
  </group>
   
  !{{ _end_ }}
  </group>
 !{{ _end_ }}
 </group>
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## EVPN configuration
## ------------------------------------------------------------------------------------------
<group name="evpn">
evpn {{ _start_ }}

 <group name="evi**.{{ evi }}">
 evi {{ evi }}
  advertise-mac {{ advertise_mac }}
  <group name="bgp">
  bgp {{ _start_ }}
   route-target import {{ rt_import | ORPHRASE | to_list | joinmatches }}
   route-target export {{ rt_export | ORPHRASE | to_list | joinmatches }}
  !{{ _end_ }}
  </group>
 !{{ _end_ }}
 </group>

 <group name="groups**.{{ group_id }}">
 group {{ group_id }}
  <group name="core_interfaces*" itemize="interface">
  core interface {{ interface }}
  </group>
 !{{ _end_ }}
 </group>
 
 <group name="interfaces**.{{ name }}">
 interface {{ name }}
  <group name="ethernet_segment">
  ethernet-segment {{ _start_ }}
   identifier type {{ identifier_type | PHRASE }}
  !{{ _end_ }}
  </group>
 !{{ _end_ }}
 </group>
 
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## Multicast configuration
## ------------------------------------------------------------------------------------------
<group name="multicast_routing">
multicast-routing {{ _start_ }}
<group name="afi.{{ afi }}">
 address-family {{ afi }}
  interface all enable {{ interface_all_enable | set(True) }}
 !{{ _end_ }}
 </group>
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## IGMP configuration
## ------------------------------------------------------------------------------------------
<group name="igmp">
router igmp {{ _start_ }}
 <group name="interfaces*">
 interface {{ interface }}
  version {{ version }}
 !{{ _end_ }}
 </group>
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## PIM configuration
## ------------------------------------------------------------------------------------------
<group name="pim">
router pim {{ _start_ }}
<group name="afi.{{ afi }}">
 address-family {{ afi }}
  sg-expiry-timer {{ sg_expiry_timer }}
  rp-address {{ rp_address }} {{ acl }}
  <group name="interfaces*">
  interface {{ interface }}
   enable {{ enabled | set(True) }}
  !{{ _end_ }}
  </group>  
 !{{ _end_ }}
 </group>
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## IGMP Snooping configuration
## ------------------------------------------------------------------------------------------
<group name="igmp_snooping">
igmp snooping profile {{ profile_name }}
</group>

## ------------------------------------------------------------------------------------------
## IPSLA configuration
## ------------------------------------------------------------------------------------------
<group name="ipsla">
ipsla {{ _start_ }}
 hw-timestamp {{ hw_timestamp }}
 
 <group name="responder">
 responder {{ _start_ }}
  <group name="twamp">
  twamp {{ _start_ }}
   timeout {{ timeout }}
  !{{ _end_ }}
  </group>
 !{{ _end_ }}
 </group>
 
 <group name="twamp">
 server twamp {{ _start_ }}
  timer inactivity {{ timer_inactivity }}
 !{{ _end_ }}
 </group>
!{{ _end_ }}
</group>

## ------------------------------------------------------------------------------------------
## ISIS configuration
## ------------------------------------------------------------------------------------------
<group name="isis**.{{ isis_process }}">
router isis {{ isis_process | _start_ }}
router isis {{ isis_process | _start_ }} vrf-context {{ vrf }}
 is-type {{ is_type }}
 net {{ net_id }}
 segment-routing global-block {{ segment_routing_global_block | PHRASE }}
 distribute link-state  {{ distribute_link_state | set(True) }}
 log adjacency changes {{ log_adjacency_changes | set(True) }}
 log pdu drops {{ log_pdu_drops | set(True) }}
 lsp-password hmac-md5 encrypted {{ ignore }} {{ lsp_hmac_md5_auth_enabled | set(True) }}
 
 <group name="afi.{{ afi }}_{{ sub_afi }}">
 address-family {{ afi }} {{ sub_afi }}
  metric-style {{ metric_style }}
  advertise link attributes {{ advertise_link_attributes | set(True) }}
  maximum-paths {{ maximum_path }}
  router-id {{ rid }}
  single-topology {{ single_topology | set(True) }}
  segment-routing mpls {{ sr_mpls_enabled | set(True) }}
  segment-routing mpls sr-prefer {{ sr_mpls_sr_prefer | set(True) }}
  segment-routing prefix-sid-map advertise-local {{ sr_prefix_sid_map_advertise_local | set(True) }}
  spf prefix-priority critical tag {{ spf_prefix_priority_critical_tag }}
 !{{ _end_ }}
 </group>
 
 <group name="interfaces*">
 interface {{ interface }}
  passive {{ is_passive | set(True) }}
  bfd minimum-interval {{ bfd_minimum_interval }}
  bfd multiplier {{ bfd_multiplier }}
  bfd fast-detect {{ bfd_fast_detect }}
  point-to-point {{ link_type | set("point-to-point") }}
  hello-password hmac-md5 encrypted {{ ignore }} {{ hello_hmac_md5_auth_enabled | set(True) }}
  
  <group name="afi.{{ afi }}_{{ sub_afi }}">
  address-family {{ afi }} {{ sub_afi }}
   prefix-sid index {{ prefix_sid_index | ORPHRASE }}
   fast-reroute per-prefix level {{ fast_reroute_per_prefix_level }}
   fast-reroute per-prefix tiebreaker {{ fast_reroute_per_prefix_tiebreaker | PHRASE }}
   fast-reroute per-prefix ti-lfa level {{ fast_reroute_per_prefix_ti_lfa_level }}
   metric {{ metric }}
  !{{ _end_ }}
  </group>
 !{{ _end_ }}
 </group>
!{{ _end_ }}
</group>

</template>
```
</details>