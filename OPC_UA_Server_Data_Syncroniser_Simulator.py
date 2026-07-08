import sys
sys.path.insert(0, "..")
import time
from opcua import ua, uamethod, Server, Client, Node
from datetime import datetime
import csv
import keyboard
import os
import re

#Global variable declaration
ENDPOINT = ""
CERTIFICATE = ''
PRIVATE_KEY = ''
INDUSTRIAL_DATA_FLOW = ''
SEUIL_AEROTHERME = 35 #in degree Celcius

def configure_connection_parameters():
    global CERTIFICATE
    global PRIVATE_KEY
    global INDUSTRIAL_DATA_FLOW
    global ENDPOINT

    
    # IPv4 address
    while True:

        ip = input(
            "Enter only either the internal IPv4 address of your Dedicated VPN or the internal NAT IPv4 address from your internet provider : "
        ).strip()

        ipv4_regex = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
                    r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
                    r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
                    r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"

        if not re.match(ipv4_regex, ip):
            print("Invalid IPv4 address. Please enter a valid IPv4 address.")
            continue

        ENDPOINT = "opc.tcp://"+ ip +":4840/"
        
        print(f"IPv4 address configured:\n{ENDPOINT}")
        break

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

    # Industrial data flow retained
    while True:

        data_retained = input(
            "Enter the full path of the Industrial data flow retained (.csv): "
        ).strip().strip('"')

        data_retained = os.path.normpath(data_retained)

        if not os.path.isfile(data_retained):
            print("File not found. Please enter an existing file.")
            continue

        if not data_retained.lower().endswith(".csv"):
            print("Invalid industrial data flow retained file. A '.csv' file is required.")
            continue

        INDUSTRIAL_DATA_FLOW = data_retained

        print(f"Industrial data flow retained file configured:\n{INDUSTRIAL_DATA_FLOW}")
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

def update_data_server(aquired_current, ambiant_temperature, mixing_cycle_flowrate, chaud_flowrate, froid_flowrate, out_aerotherme, out_heat_exchanger, temp_out_froid, temp_in_froid, temp_out_chaud, temp_in_chaud, aerotherme_aquis, process_value):
    print("CURENT : ", aquired_current)
    print("AMBIANT TEMPERATURE : ", ambiant_temperature)

    client = Client(ENDPOINT)

    try:
        security = (
            "Basic256Sha256,SignAndEncrypt,"
            + CERTIFICATE + ","
            + PRIVATE_KEY
        )

        client.set_security_string(security)

        client.application_uri = "urn:DigitalTwinv1:YRPolytechAngers"
        client.secure_channel_timeout = 10000
        client.session_timeout = 10000

        client.connect()

        # Write value each t= 1s 
        OUTHEATEXCHANGER = float(out_heat_exchanger)
        OUTAEROTHERME = float(out_aerotherme)
        FROIDFLOWRATE = float(froid_flowrate)
        CHAUDFLOWRATE = float(chaud_flowrate)
        MIXINGCYCLEFLOWRATE = float(mixing_cycle_flowrate)
        AMBIENTTEMPERATURE = float(ambiant_temperature)
        CURRENT = float(aquired_current)
        TEMPINCHAUD = float(temp_in_chaud)
        TEMPINFROID = float(temp_in_froid)
        TEMPOUTCHAUD = float(temp_out_chaud)
        TEMPOUTFROID = float(temp_out_froid)
        #SETPOINTINCHAUD_ACQ = float(aerotherme_aquis)
        PROCESS_VALUE = float(process_value)

        #Directly update OPC UA values on the server
        #Update from node ID
        node_id_OutHeatExchanger = "ns=2;i=11"
        node_id_OutAerotherme = "ns=2;i=12"
        node_id_FroidFlowrate = "ns=2;i=13"
        node_id_ChaudFlowrate = "ns=2;i=14"
        node_id_MixingCycleFlowrate = "ns=2;i=15"
        node_id_AmbiantTemperature = "ns=2;i=16"
        node_id_Current = "ns=2;i=17"
        node_id_TempInChaud = "ns=2;i=18"
        node_id_TempInFroid = "ns=2;i=19"
        node_id_TempOutChaud = "ns=2;i=20"
        node_id_TempOutFroid = "ns=2;i=21"
        node_id_SetPointInChaudAquis = "ns=2;i=22"
        node_id_ProcessValue = "ns=2;i=23"

        #Write new value each t= 1s
        client.get_node(node_id_OutHeatExchanger).set_value(OUTHEATEXCHANGER)
        client.get_node(node_id_OutAerotherme).set_value(OUTAEROTHERME)
        client.get_node(node_id_FroidFlowrate).set_value(FROIDFLOWRATE)
        client.get_node(node_id_ChaudFlowrate).set_value(CHAUDFLOWRATE)
        client.get_node(node_id_MixingCycleFlowrate).set_value(MIXINGCYCLEFLOWRATE)
        client.get_node(node_id_AmbiantTemperature).set_value(AMBIENTTEMPERATURE)
        client.get_node(node_id_Current).set_value(CURRENT)
        client.get_node(node_id_TempInChaud).set_value(TEMPINCHAUD)
        client.get_node(node_id_TempInFroid).set_value(TEMPINFROID)
        client.get_node(node_id_TempOutChaud).set_value(TEMPOUTCHAUD)
        client.get_node(node_id_TempOutFroid).set_value(TEMPOUTFROID)
        client.get_node(node_id_ProcessValue).set_value(PROCESS_VALUE)
        #grab avlue from ICS
        aerotherme_Control = client.get_node("ns=2;i=27")
        aerotherme_Control_val = aerotherme_Control.get_value()
        #UpdatecSETPOINT for Hot cycle aquisition for the simulation from industrial data flow retained
        client.get_node(node_id_SetPointInChaudAquis).set_value(aerotherme_Control_val)

    except TimeoutError:
        print(f"Impossible to connect to the OPC UA server ({ENDPOINT}).")
        return

    except ConnectionRefusedError:
        print(f"Connection refused by the serveur ({ENDPOINT}).")
        return

    except Exception as e:
        print(f"OPC UA Error: {e}")
        return

    finally:
        try:
            client.disconnect()
        except:
            pass

def provide_sensor_data():
    data = []

    if not os.path.isfile(INDUSTRIAL_DATA_FLOW):
        print(f"File not found : {INDUSTRIAL_DATA_FLOW}")
        return

    try:
        with open(INDUSTRIAL_DATA_FLOW, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)

            for row in reader:
                try:
                    float_row = [float(cell.strip()) for cell in row]
                    data.append(float_row)
                except ValueError:
                    print(f"Ligne ignorée : {row}")

    except Exception as e:
        print(f"Erreur when opening the file : {e}")
        return

    interval = 1

    for line in data:
        start_time = time.perf_counter()

        formatted_line = [f"{num:.3f}" for num in line]
        update_data_server(*formatted_line)

        elapsed = time.perf_counter() - start_time
        time.sleep(max(0, interval - elapsed))

def main():
    launch_server()

    print("Hit 'p' ou 'P' to stop providing sensor data to OPC UA Server or stop OPC UA Server.")
    while True:
        provide_sensor_data()
        if keyboard.is_pressed('p'):
            print("Stop providing data")
            break 

    print("Hit 'q' ou 'Q' to stop OPC UA Server.")
    while True:
        if keyboard.is_pressed('q'):
            print("Stopping OPC UA Server...")
            os._exit(0)


if __name__ == "__main__":
    configure_connection_parameters()
    main()
