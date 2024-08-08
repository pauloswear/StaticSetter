import subprocess
import os
import sys
import yaml

def is_admin():
    return os.getuid() == 0

def select_interface():
    interfaces = subprocess.run(["ip", "link", "show"], capture_output=True, text=True)
    print("Interfaces de rede disponíveis:")
    print(interfaces.stdout)

    interface_index = input("Digite o número do índice da interface que deseja configurar: ")
    return interface_index

def get_interface_name_by_index(index):
    interfaces_info = subprocess.run(["ip", "link", "show"], capture_output=True, text=True)
    for line in interfaces_info.stdout.split('\n'):
        if line.strip().startswith(index + ":"):
            interface_name = line.strip().split(":")[1].split('@')[0].strip()
            return interface_name

    return None

def get_user_choice():
    choice = input("Você quer configurar um endereço IP estático ou usar DHCP? (estático/dhcp): ").strip().lower()
    if choice in ['estatico', 'static', 'dhcp']:
        return choice
    else:
        print("Escolha inválida. Por favor, escolha 'estático' ou 'dhcp'.")
        return None

def get_user_input():
    ip_address = input("- Endereço IPv4 estático: ")
    gateway = "192.168.0.1"

    if not ip_address:
        print("O endereço IPv4 estático não pode estar vazio.")
        return None

    return ip_address, gateway

def generate_netplan_config(interface_name, ip_address=None, gateway=None, use_dhcp=False):
    if use_dhcp:
        config = {
            "network": {
                "version": 2,
                "ethernets": {
                    interface_name: {
                        "dhcp4": True
                    }
                }
            }
        }
    else:
        config = {
            "network": {
                "version": 2,
                "ethernets": {
                    interface_name: {
                        "addresses": [f"{ip_address}/24"],
                        "routes": [{"to": "0.0.0.0/0", "via": gateway}],
                        "nameservers": {
                            "addresses": ["8.8.8.8", "8.8.4.4"],
                            "search": []
                        }
                    }
                }
            }
        }
    return yaml.dump(config)

def apply_netplan_config(config):
    with open("/tmp/netplan_temp.yaml", "w") as f:
        f.write(config)

    subprocess.run(["sudo", "mv", "/tmp/netplan_temp.yaml", "/etc/netplan/00-installer-config.yaml"])
    subprocess.run(["sudo", "netplan", "apply"])
    print("Configuração concluída.")

if __name__ == "__main__":
    if not is_admin():
        print("Este script requer permissões de administrador. Por favor, execute-o como administrador.")
        sys.exit(1)
    else:
        interface_index = select_interface()
        interface_name = get_interface_name_by_index(interface_index)
        if interface_name:
            print("Configurando a interface:", interface_name)
            choice = get_user_choice()
            if choice == 'dhcp':
                netplan_config = generate_netplan_config(interface_name, use_dhcp=True)
                apply_netplan_config(netplan_config)
            elif choice == 'estatico' or choice == 'static':
                user_input = get_user_input()
                if user_input:
                    ip_address, gateway = user_input
                    netplan_config = generate_netplan_config(interface_name, ip_address, gateway)
                    apply_netplan_config(netplan_config)
        else:
            print("O número do índice da interface fornecido não é válido.")
