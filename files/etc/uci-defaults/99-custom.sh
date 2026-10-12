
#!/bin/sh

# 首次启动配置：取消注释并修改参数即可启用

# Wi-Fi
# wlan_name="ImmortalWrt"
# wlan_password="12345678"

# 管理员密码（LuCI / SSH）
# root_password="admin"

# LAN IP（25.12+ 使用 CIDR）
# lan_ip_address="192.168.2.1/24"

# PPPoE 账号和密码
# pppoe_username=""
# pppoe_password=""

exec >/tmp/setup.log 2>&1

if [ -n "$root_password" ]; then
  printf '%s\n%s\n' "$root_password" "$root_password" | passwd root >/dev/null || exit 1
fi

if [ -n "$lan_ip_address" ]; then
  uci set network.lan.ipaddr="$lan_ip_address" || exit 1
  uci -q delete network.lan.netmask || :
  uci commit network || exit 1
fi

if [ -n "$wlan_name" ] && [ -n "$wlan_password" ] && [ "${#wlan_password}" -ge 8 ]; then
  uci set 'wireless.@wifi-device[0].disabled=0' || exit 1
  uci set 'wireless.@wifi-iface[0].disabled=0' || exit 1
  uci set 'wireless.@wifi-iface[0].encryption=psk2' || exit 1
  uci set "wireless.@wifi-iface[0].ssid=$wlan_name" || exit 1
  uci set "wireless.@wifi-iface[0].key=$wlan_password" || exit 1
  uci commit wireless || exit 1
fi

if [ -n "$pppoe_username" ] && [ -n "$pppoe_password" ]; then
  uci set network.wan.proto=pppoe || exit 1
  uci set network.wan.username="$pppoe_username" || exit 1
  uci set network.wan.password="$pppoe_password" || exit 1
  uci commit network || exit 1
fi

echo 'All done!'
exit 0
