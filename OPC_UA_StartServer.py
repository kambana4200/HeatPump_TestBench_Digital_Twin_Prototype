import sys
sys.path.insert(0, "..")
import time
from opcua import ua, uamethod, Server, Client, Node
from datetime import datetime
import csv
import keyboard
import os
import ipaddress

#Global variable declaration
ENDPOINT = "opc.tcp://10.34.0.81:4840/" #Public IP of the server
CERTIFICATE = 'C:\\Users\\utilisateur\\Documents\\python_OPC_UA_SERVER\\DT_Server_SIMULATOR\\certificate\\digitaltwincert.der'
PRIVATE_KEY = 'C:\\Users\\utilisateur\\Documents\\python_OPC_UA_SERVER\\DT_Server_SIMULATOR\\certificate\\key2.pem'
INDUSTRIAL_DATA_FLOW = 'C:\\Users\\utilisateur\\Documents\\python_OPC_UA_SERVER\\DT_Server_SIMULATOR\\certificate\\valuespace.csv'
SEUIL_AEROTHERME = 35 #in degree Celcius

def configure_connection_parameters():
    global ENDPOINT
    global CERTIFICATE
    global PRIVATE_KEY
    global INDUSTRIAL_DATA_FLOW

    # Public IP Address
    while True:
        ip = input("Enter the public IP address of the OPC UA Server: ").strip()

        try:
            ipaddress.ip_address(ip)

            ENDPOINT = f"opc.tcp://{ip}:4840/"
            print(f"Endpoint configured: {ENDPOINT}")
            break

        except ValueError:
            print("Invalid IP address. Please enter a valid IPv4 or IPv6 address.")

    # Certificate (.der)
    while True:

        cert = input(
            "Enter the full path of the server certificate (.der): "
        ).strip().strip('"')

        cert = os.path.normpath(cert)

        if not os.path.isfile(cert):
            print("File not found. Please enter an existing file.")
            continue

        if not cert.lower().endswith(".der"):
            print("Invalid certificate file. A '.der' file is required.")
            continue

        CERTIFICATE = cert

        print(f"Certificate configured:\n{CERTIFICATE}")
        break

    # Private key (.pem)
    while True:

        key = input(
            "Enter the full path of the private key (.pem): "
        ).strip().strip('"')

        key = os.path.normpath(key)

        if not os.path.isfile(key):
            print("File not found. Please enter an existing file.")
            continue

        if not key.lower().endswith(".pem"):
            print("Invalid private key file. A '.pem' file is required.")
            continue

        PRIVATE_KEY = key

        print(f"Private key configured:\n{PRIVATE_KEY}")
        break
    
class GestionSouscription():
    def notification_datachgmnt(self, node: Node, val, data):
        print(str(datetime.now().strftime("%Y-%m-%d %H:%M %p")) + " : " + str(node) + " : " + str(val))

def launch_server():

    server = Server()
    server.set_endpoint(ENDPOINT)
    # configure security layer for OPC UA Serveur / client with TLS
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
    # public key  for encrytion
    server.load_certificate(CERTIFICATE)
    # private key for decryption
    server.load_private_key(PRIVATE_KEY)
    # save the namespace of the server
    uri = "urn:DigitalTwinv1:YRPolytechAngers"
    idx = server.register_namespace(uri)

    #name of the adress space
    nom = "OPC_UA_for_DT"
    namespace = server.register_namespace(nom) 

    #Configure aquisition data for OPC UA Server
    noeud_racine = server.get_root_node()
    noeud_objet = server.get_objects_node()

    monObj = noeud_objet.add_object(idx, "Variables")
    heatExchanger = noeud_objet.add_object(idx, "HeatExchanger")
    aerotherme = noeud_objet.add_object(idx, "Aerotherme")
    flowrate = noeud_objet.add_object(idx, "Flowrate")
    temperature = noeud_objet.add_object(idx, "Temperature")
    current = noeud_objet.add_object(idx, "Current")
    geoHeatpump = noeud_objet.add_object(idx, "GEOHeatpump")
    aerothermeAquis = noeud_objet.add_object(idx, "Aerotherme_Aquisition")
    waterGlycolTankAquis = noeud_objet.add_object(idx, "WaterGlycolTank_Aquisition")
    processValue = noeud_objet.add_object(idx, "processValue")

    #initialize data for each variables
    OutHeatExchanger = heatExchanger.add_variable(idx, "OutHeatExchanger", 0.0, ua.VariantType.Float)
    OutAerotherme = aerotherme.add_variable(idx, "OutAerotherme", 0.0, ua.VariantType.Float)
    FroidFlowrate = flowrate.add_variable(idx, "FroidFlowrate", 0.0, ua.VariantType.Float)
    ChaudFlowrate = flowrate.add_variable(idx, "ChaudFlowrate", 0.0, ua.VariantType.Float)
    MixingCycleFlowrate = flowrate.add_variable(idx, "MixingCycleFlowrate", 0.0, ua.VariantType.Float)
    AmbiantTemperature = temperature.add_variable(idx, "AmbiantTemperature", 0.0, ua.VariantType.Float)
    Current = current.add_variable(idx, "Current", 0.0, ua.VariantType.Float)
    TempInChaud = geoHeatpump.add_variable(idx, "TempInChaud", 0.0, ua.VariantType.Float)
    TempInFroid = geoHeatpump.add_variable(idx, "TempInFroid", 0.0, ua.VariantType.Float)
    TempOutChaud = geoHeatpump.add_variable(idx, "TempOutChaud", 0.0, ua.VariantType.Float)
    TempOutFroid = geoHeatpump.add_variable(idx, "TempOutFroid", 0.0, ua.VariantType.Float)
    SetPointInChaudAquis = aerothermeAquis.add_variable(idx, "SetPointInChaudAquis", 0.0, ua.VariantType.Float)
    SetPointInFroidAquis = waterGlycolTankAquis.add_variable(idx, "SetPointInFroidAquis", 0.0, ua.VariantType.Float)
    ProcessValue = processValue.add_variable(idx, "ProcessValue", 0.0, ua.VariantType.Float)

    OutHeatExchanger.set_writable() #writing right onto variable from OPC UA Client
    OutAerotherme.set_writable()
    FroidFlowrate.set_writable()
    ChaudFlowrate.set_writable()
    MixingCycleFlowrate.set_writable()
    AmbiantTemperature.set_writable()
    Current.set_writable()
    TempInChaud.set_writable()
    TempInFroid.set_writable()
    TempOutChaud.set_writable()
    TempOutFroid.set_writable()
    SetPointInChaudAquis.set_writable()
    SetPointInFroidAquis.set_writable()
    ProcessValue.set_writable()

    #Configure nodes for control command on OPC UA Server   
    
    aerotherme_Control = noeud_objet.add_object(idx, "Aerotherme_Control")
    waterGlycolTank_Control = noeud_objet.add_object(idx, "WaterGlycolTank_Control")

    #initialize data for each control command variable
    SetPointInChaud = aerotherme_Control.add_variable(idx, "SetPointInChaud", 0.0, ua.VariantType.Float)
    SetPointInFroid = waterGlycolTank_Control.add_variable(idx, "SetPointInFroid", 0.0, ua.VariantType.Float)

    SetPointInChaud.set_writable() #writing right onto variable from OPC UA Client
    SetPointInFroid.set_writable() #writing right onto variable from OPC UA Client

    server.start()

def main():
    launch_server()

    while True:
        if keyboard.is_pressed('q'):
            print("Stopping OPC UA Server...")
            os._exit(0)


if __name__ == "__main__":
    configure_connection_parameters()
    main()
