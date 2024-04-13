import subprocess
import os
import sys
import yaml

def is_admin():
    return os.getuid() == 0

def select_interface():
    # Obter a lista de interfaces conectadas
    interfaces = subprocess.run(["ip", "link", "show"], capture_output=True, text=True)
    print("Interfaces de rede disponíveis:")
    print(interfaces.stdout)

    # Solicitar o número do índice da interface selecionada
    interface_index = input("Digite o número do índice da interface que deseja configurar: ")

    return interface_index

def get_interface_name_by_index(index):
    # Obter o nome da interface com base no índice fornecido
    interfaces_info = subprocess.run(["ip", "link", "show"], capture_output=True, text=True)
    for line in interfaces_info.stdout.split('\n'):
        if line.strip().startswith(index + ":"):
            interface_name = line.strip().split(":")[1].split('@')[0].strip()
            return interface_name

    return None

def get_user_input():
    # Solicitar o endereço IPv4 estático
    ip_address = input("- Endereço IPv4 estático: ")

    # Validar a entrada de IP
    if not ip_address:
        print("O endereço IPv4 estático não pode estar vazio.")
        return None

    # Solicitar o gateway
    # gateway = input("- Gateway: ")
    gateway = "192.168.0.1"

    # Validar a entrada do gateway
    if not gateway:
        print("O gateway não pode estar vazio.")
        return None

    return ip_address, gateway

def generate_netplan_config(interface_name, ip_address, gateway):
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
    # Escrever o arquivo de configuração Netplan temporário
    with open("/tmp/netplan_temp.yaml", "w") as f:
        f.write(config)

    # Renomear o arquivo de configuração Netplan temporário para ser o arquivo ativo
    subprocess.run(["sudo", "mv", "/tmp/netplan_temp.yaml", "/etc/netplan/00-installer-config.yaml"])

    # Aplicar a configuração Netplan
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
            print("Configurando endereço estático para a interface:", interface_name)
            user_input = get_user_input()
            if user_input:
                ip_address, gateway = user_input
                netplan_config = generate_netplan_config(interface_name, ip_address, gateway)
                apply_netplan_config(netplan_config)
        else:
            print("O número do índice da interface fornecido não é válido.")
