# Reproducibility Protocol for DT_HP_HWPrototype

## INDUSTRIAL CONTROL SYSTEM (ICS) APPLICATION WITH ITS SYNCHRONISATION LAYER FOR THE DIGITAL TWIN PLATFORM

### Software Requirements

1. Install LabVIEW 2026 Q1 Community Edition (32-bit or 64-bit)

2. Install Python 3.X.X:
   - Use the 32-bit version if LabVIEW is 32-bit.
   - Use the 64-bit version if LabVIEW is 64-bit.

3. Install the required Python packages with pip using the following commands:

```bash
pip install opcua
pip install crypto
pip install keyboard
pip install cryptography
```

### Required Files

1. The following files are required to establish secure OPC UA communication:

- digitaltwincert.der
- key2.pem

2. The industrial data stream used by the **DT_HW_HP_Prototype** is stored in the following file:

- ValueSpace.csv

### Deployment Synchronization Layer Leveraging OPC UA protocol

To enable communication between the Industrial Control System (ICS) and the **DT_HW_HP_Prototype**, an OPC UA server must be hosted on a computer equipped with:
A public IP address with port forwarding enabled; or A VPN providing a dedicated public IP address with port forwarding enabled.

1. Open a PowerShell terminal with administrator privileges.

2. Start the OPC UA server by executing:

```bash
python OPC_UA_StartServer.py
```

### Deployment of the Industrial Control System (ICS)

The ICS application continuously supplies the **DT_HW_HP_Prototype** with industrial process data. It can also simulate control command exchanges in offline mode or transmit real control setpoints when the physical heat pump test bench is connected through the serial interface and the NI-DAQ acquisition hardware.

1. Open the following LabVIEW project nammed: HP_testbench_SCADA_application.vi (file provided on this github)
   Please set the this VI as "trusted" when executing this labview virtual interface in order to launch it properly. 

3. From the LabVIEW menu, select: Window => Show Block Diagram

4. Verify that the configured Python interpreter points to the installed Python 3.9.13 executable as shown on the picture below.
   <img width="1917" height="1007" alt="capture_1" src="https://github.com/user-attachments/assets/2da4dcf8-968d-4e6a-aad9-ccfcfd803a66" />

5. Start the Industrial Control System application by clicking the Run button (=>) in LabVIEW.

### Remarks No.1

- The computer hosting the OPC UA server must remain reachable from the Internet throughout the experiment.
- If no physical heat pump test bench is connected, the ICS application operates with industrial data flow retained inside the file **ValueSpace.csv** while maintaining the complete Digital Twin synchronization workflow.
- When the physical equipment is connected, the same application transparently switches to real-time operation, exchanging industrial measurements and control setpoints with the Digital Twin through the secure OPC UA communication channel.


## REPLICATION OF THE DATA-DRIVEN DIGITAL TWIN (DT) CLOUD PLATFORM NAMED DT_HW_HP_Prototype

### Platform Installation

1. Install Docker 28.4.0 on a remote Server or a remote Virtual Private (VPS) or remote Baremetal Server 

2. Install MicroKubernetes (or Kubernetes) v1.33.13 on this server 

3. On the server firewall (ufw, iptables, or other), open inbound and outbound connections on the following ports:  
    48480 (OPC UA)  
    1880 (Node-RED)  

4. Run the installation script of the Data-Driven Digital Twin prototype named DT_HW_HP_Prototype with root privileges using the command:

```bash
microK8s start
microK8s kubectl apply -f DataDrivenDT_deployement.yaml
```

### How to run and use the DT_HW_HP_Prototype

1. Open the Node-RED flow using the URL: https://yourPublicIP:1880/

2. Imperative Modification inside Node-RED flow:

i. Update the public IP address used in the OPC UA endpoint in the Node-RED flow
ii. Add the MariaDB credentials for industrial data storage and phpmyadmin access (only local acess allowed):
    Login: prototype
    Password: Yannick

3. Access the virtual replica of the heat pump test bench hot water cycle using: https://yourPublicIP:18180/dashboard
    
    Authentication Credentials (All tabs): 
        Login: datadrivendigitaltwin
        Password: datadrivendigitaltwin

### Remark No.2
You may need to bypass SSL certificate verification when opening the web interfaces to access the Human-Machine Interface (HMI).
This is not a security risk; it is due to the SSL certificate being configured only for my specific domain name.
