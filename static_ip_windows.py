import subprocess
import os
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def select_interface():
    # Obter a lista de interfaces conectadas
    interfaces = subprocess.run(["netsh", "interface", "ipv4", "show", "interfaces"], capture_output=True, text=True)
    print("Interfaces de rede disponíveis:")
    print(interfaces.stdout)

    # Solicitar o número do índice da interface selecionada
    interface_index = input("Digite o número do índice da interface que deseja configurar: ")

    # Obter o nome da interface com base no índice fornecido
    selected_interface = ""
    for line in interfaces.stdout.split('\n'):
        if line.strip().startswith(interface_index):
            selected_interface = line.strip().split()[-1]
            break

    if not selected_interface:
        print("O número do índice da interface fornecido não é válido.")
        return None
    else:
        print(f"Você selecionou a interface: {selected_interface}\n")
        return selected_interface

def configure_static_ip(interface_name):
    # Solicitar o endereço IPv4 estático
    ip_address = input("- Endereço IPv4 estático: ")

    # Validar a entrada de IP
    if not ip_address:
        print("O endereço IPv4 estático não pode estar vazio.")
        return

    # Solicitar o gateway
    # gateway = input("- Gateway: ")
    gateway = "192.168.0.1"

    # Validar a entrada do gateway
    if not gateway:
        print("O gateway não pode estar vazio.")
        return

    print(f"Configurando endereço estático para a interface {interface_name}")

    # Configurar o endereço IP estático
    os.system(f"netsh interface ipv4 set address name={interface_name} static {ip_address} 255.255.255.0 {gateway}")
    
    # Configurar os servidores DNS
    os.system(f"netsh interface ipv4 set dns name={interface_name} static 8.8.8.8")

    os.system(f"netsh interface ipv4 add dns name={interface_name} addr=8.8.4.4 index=2")
    print("Configuração concluída.")

if __name__ == "__main__":
    if not is_admin():
        print("Este script requer permissões de administrador. Por favor, execute-o como administrador.")
        # Obtém o caminho do script atual
        script_path = os.path.abspath(__file__)
        # Solicita permissões de administrador
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}"', None, 1)
    else:
        interface_name = select_interface()
        if interface_name:
            configure_static_ip(interface_name)
            input()
