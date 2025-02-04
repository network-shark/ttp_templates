Reference path:
```
ttp://misc/N2G/cli_l2_data/cisco_xr.txt
```

---



This template designed to parse Cisco IOSXR configuration and CDP and LLDP neighbors.

Commands parsed:

- show lldp - to extract LLDP System Name
- show lldp neighbors detail - to extract LLDP neighbors
- show running-config interface - to extract interfaces description and LAGs
- show run | inc domain - to extract domain name in case "show lldp" fails
- show run | inc hostname - to extract hostname in case "show lldp" fails
- show cdp neighbors detail - show extract CDP neighbors
- show interfaces - to extract interface state to add all connected nodes



---

<details><summary>Template Content</summary>
```
bash-4.4# cat /usr/local/lib/python3.9/site-packages/ttp_templates/misc/N2G/cli_l2_data/cisco_xr.txt 
<template name="cisco_xr" results="per_template">

<doc>
This template designed to parse Cisco IOSXR configuration and CDP and LLDP neighbors.

Commands parsed:

- show lldp - to extract LLDP System Name
- show lldp neighbors detail - to extract LLDP neighbors
- show running-config interface - to extract interfaces description and LAGs
- show run | inc domain - to extract domain name in case "show lldp" fails
- show run | inc hostname - to extract hostname in case "show lldp" fails
- show cdp neighbors detail - show extract CDP neighbors
- show interfaces - to extract interface state to add all connected nodes
</doc>

<input load="python">
commands = [
    "show cdp neighbor detail",
    "show lldp neighbor detail",
    "show lldp",
    "show run | inc domain",
    "show run | inc hostname",
    "show running-config interface",
    "show interfaces",
]
kwargs = {"strip_prompt": False}
method = "send_command"
platform = ["cisco_xr"]
</input>

<macro>
def check_is_physical_port(data):
    for item in _ttp_["vars"]["physical_ports"]:
        if data.startswith(item) and not "." in item:
            return data, {"is_physical_port": True}
    return data
    
def add_lldp_target_id(data):
    """
    Some LLDP peers output does not contain System Name, this macro 
    is to make sure we assign chassis_id as target.id in that case.
    """
    if (
        not data.get("target", {}).get("id") and 
        data.get("data", {}).get("chassis_id")
    ):
        data.setdefault("target", {})
        data["target"]["id"] = data["data"]["chassis_id"]
    return data

def form_local_hostname(data):
    if "hostname" in data and "domain_name" in data:
        data["local_hostname"] = "{}.{}".format(
            data["hostname"], data["domain_name"]
        )
    return data
</macro>

<!-- show lldp - parse global params -->
<group void="">
Global LLDP information: {{ _start_ }}
        LLDP System Name: {{ local_hostname | record("local_hostname") }}
</group>

<group functions="macro('form_local_hostname') | record('local_hostname') | void()">
domain name {{ domain_name }}
hostname {{ hostname }}
</group>


<!-- Interfaces configuration group -->
<group name="{{ local_hostname }}.interfaces**.{{ interface }}**">
interface {{ interface | resuball(IfsNormalize) }}
 mtu {{ mtu }}
 vrf {{ vrf }}
 description {{ description | re(".+") }}
 ipv4 address {{ ip | PHRASE | joinmatches(",") }}
 ipv4 address {{ ip | PHRASE | joinmatches(",") }} secondary
 ipv6 address {{ ip | joinmatches(",") }}
 bundle id {{ lag_id | DIGIT }} mode {{ lag_mode }}
</group>

<!-- Interfaces state group -->
<group name="{{ local_hostname }}.interfaces**.{{ interface }}**.state">
{{ interface | _start_ | resuball(IfsNormalize) | macro("check_is_physical_port") }} is {{ admin | ORPHRASE }}, line protocol is {{ line | ORPHRASE }}
  Hardware is {{ hardware }} interface(s)
  Hardware is {{ hardware }} interface
  Hardware is {{ hardware | ORPHRASE }} interface(s), address is {{ mac }}
  Hardware is {{ hardware | ORPHRASE }}, address is {{ mac }} (bia {{ ignore }})
  Description: {{ description | re(".+") }}
  Internet address is {{ ip }}
  MTU {{ mtu }} bytes, BW {{ bw_kbits }} Kbit (Max: 1000000 Kbit)
  MTU {{ mtu }} bytes, BW {{ bw_kbits }} Kbit
  {{ duplex }}-duplex, {{ link_speed }}
  {{ duplex }}-duplex, {{ link_speed }}, link type is {{ link_type }}
  {{ duplex }}-duplex, {{ link_speed }}, {{ media_type }}, link type is {{ link_type }}
      {{ lag_members | joinmatches(" ") }}  {{ ignore }}-duplex  {{ ignore }} {{ ignore }}
</group>

<!-- LLDP peers group -->
<group name="{{ local_hostname }}.lldp_peers*" functions="expand() | macro(add_lldp_target_id) | set('local_hostname', 'source')">
Local Interface: {{ src_label | resuball(IfsNormalize) }}
Chassis id: {{ data.chassis_id }}
Port id: {{ trgt_label | ORPHRASE | resuball(IfsNormalize) }}
Port Description: {{ data.peer_port_description | re(".+") }}
System Name: {{ target.id | split("(") | item(0) }}
System Name: {{ data.peer_system_name | PHRASE }}
System Capabilities: {{ data.peer_capabilities | ORPHRASE }}
  IPv4 address: {{ target.top_label }}

<group name="data**">
System Description: {{ _start_ }}
 {{ peer_system_description | ORPHRASE | contains(",") }}
{{ peer_system_description | ORPHRASE | contains(",") }}
{{ _end_ }}
</group>

</group>


<!-- CDP peers group -->
<group name="{{ local_hostname }}.cdp_peers*" expand="" set="local_hostname, source">
Device ID: {{ target.id | split(".") | item(0) | split("(") | item(0) }}
  IPv4 address: {{ target.top_label }}
Platform: {{ target.bottom_label | ORPHRASE }},  Capabilities: {{ data.peer_capabilities | ORPHRASE }}
Interface: {{ src_label | resuball(IfsNormalize) }}
Port ID (outgoing port): {{ trgt_label | ORPHRASE | resuball(IfsNormalize) }}
</group>
</template>
```
</details>