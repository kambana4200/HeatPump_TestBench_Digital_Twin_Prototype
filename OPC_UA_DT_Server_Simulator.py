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

    # INDUSTRIAL DATA FLOW (.csv)
    while True:

        data = input(
            "Enter the full path of the industrial data flow retained (.csv): "
        ).strip().strip('"')

        data = os.path.normpath(data)

        if not os.path.isfile(data):
            print("File not found. Please enter an existing file.")
            continue

        if not data.lower().endswith(".csv"):
            print("Invalid file for industrial data flow retained. A '.csv' file is required.")
            continue

        INDUSTRIAL_DATA_FLOW = data

        print(f"file for industrial data flow retained:\n{INDUSTRIAL_DATA_FLOW}")
        break

def ensure_twining_setpoint_chaud():
    client = Client(ENDPOINT)
    # communication security
    str = "Basic256Sha256,SignAndEncrypt,"+CERTIFICATE+","+PRIVATE_KEY
    client.set_security_string(str)
    
    client.application_uri = "urn:DigitalTwinv1:YRPolytechAngers"
    client.secure_channel_timeout = 10000
    client.session_timeout = 10000
    
    try:
        # Connect to the OPC UA Server
        client.connect()

        # Read the  setpoint for hot temperature on aerotherm from the Digital Twin each t = 1 S
        aerothermeAquis = client.get_node("ns=2;i=21")
        aerothermeAquis_val = aerothermeAquis.get_value()
    
        # Read the  setpoint for hot temperature on aerotherm from the Industrial Control System each t = 1 S
        aerotherme_Control = client.get_node("ns=2;i=25")
        aerotherme_Control_val = aerotherme_Control.get_value()
        
    except Exception as e:
        print("Error when reading the values on OPC UA Object", e)

    except ConnectionError:
        print("Unable to connect to OPC UA Server. Please verify URI of OPC UA Connection")

    if aerothermeAquis_val == aerotherme_Control_val : #the variable for control command on DT an the variable for control command on ICS are in phase at instant t (same values)
        if aerotherme_Control_val >= SEUIL_AEROTHERME: # values above the nominal set point of the aerotherme
            client.disconnect()
            return 1 #PROTECTION FOR ICS : DON NOT MODIFY SET POINT ON ICS
        client.disconnect()
        return 1 #DT IS STABLE ie VALEU of CONTROl COMMAND on ICS == #DT IS STABLE ie VALEU of CONTROl COMMAND on DT
    else:
        client.disconnect()
        return 0 #DT IS LATE COMPARING TO THE ICS

def command_setpoint_chaud():
    client = Client(ENDPOINT)
    # communication security
    str = "Basic256Sha256,SignAndEncrypt,"+CERTIFICATE+","+PRIVATE_KEY
    client.set_security_string(str)
    client.application_uri = "urn:DigitalTwinv1:YRPolytechAngers"
    client.secure_channel_timeout = 10000
    client.session_timeout = 10000
    
    try:
        # Connect to the OPC UA server
        client.connect()

        # Read setpoint fo hot temperature on aeerotherm from the Digital Twin 
        aerotherme_Control = client.get_node("ns=2;i=25")
        aerotherme_Control_val = aerotherme_Control.get_value()
        
    except Exception as e:
        print("Error when reading values from the DT", e)

    except ConnectionError:
        print("Unable to connect to OPC UA Server. Please verify URI of OPC UA Connection")

    valeur_de_ctrl = aerotherme_Control_val
    client.disconnect()
    return valeur_de_ctrl


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
        node_id_ProcessValue = "ns=2;i=24"

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

def provide_sensor_data(INDUSTRIAL_DATA_FLOW):
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
    configure_connection_parameters()

    print("Press 'Q' to stop providing sensor data to the OPC UA Server.")

    while True:
        provide_sensor_data(INDUSTRIAL_DATA_FLOW)

        if keyboard.is_pressed('q'):
            print("Stopping data transmission...")
            break

if __name__ == "__main__":
    main()