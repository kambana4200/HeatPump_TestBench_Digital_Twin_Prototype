# Reproducibility Protocol for DT_HP_HWPrototype

## FEEDING REAL INDUSTRIAL DATA RETAINED FROM THE INDUSTRIAL CONTROL SYSTEM (ICS) OF THE HOT WATER CYCLE OF A HEAT PUMP TEST BENCH

### Software Requirements

1. Install Python 3.x (32-bit or 64-bit).

2. Install the required Python packages using the following commands:

```bash
pip install opcua
pip install crypto
pip install keyboard
pip install cryptography
```

### Required Files

The following files are required to reproduce the experiment.

#### 1. Secure OPC UA Communication

The following certificate and private key are required to establish a secure OPC UA communication channel:

- `digitaltwincert.der`
- `key2.pem`

#### 2. Industrial Data Stream

The industrial data stream acquired from the ICS of the hot water cycle of the heat pump test bench is stored in:

- `ValueSpace.csv`

This dataset is used by the **DT_HW_HP_Prototype** to emulate the behaviour of the physical system.


### Deployment of the Simulated Physical Layer Using Recorded ICS Data

The physical layer of the **DT_HW_HP_Prototype** is simulated by replaying the recorded industrial data while exposing it through an OPC UA server acting as the Synchronisation Layer.

To deploy this configuration, the computer hosting the OPC UA server must provide one of the following:

- a public IP address with the required port forwarding enabled; or
- a VPN service providing a dedicated public IP address with port forwarding enabled.

#### Deployment Procedure

1. Open a PowerShell terminal with administrator privileges.

2. Start the OPC UA server by executing:

```bash
python OPC_UA_Server_Data_Synchroniser_Simulator.py
```

### Remarks

- The computer hosting the OPC UA server must remain accessible from the Internet throughout the entire experiment.

- In this replication scenario, the physical heat pump test bench is not directly available. Consequently, the Industrial Control System (ICS) is emulated by replaying the recorded industrial data contained in `ValueSpace.csv`. The simulator publishes the process variables every **1 second (t = 1 s)** through the OPC UA server, thereby reproducing the behaviour of the Synchronisation Layer of the Digital Twin prototype.

- When the physical heat pump test bench is available, the recorded-data simulator is replaced by the actual ICS. In this configuration, a LabVIEW application interfaces with the physical equipment, while a Python application hosts and manages the OPC UA server. Together, they enable bidirectional communication with the Digital Twin, supporting both real-time data acquisition from the physical system and transmission of control commands through a secure OPC UA communication channel.


## REPLICATION OF THE DATA-DRIVEN DIGITAL TWIN (DT) CLOUD PLATFORM NAMED **DT_HW_HP_Prototype**

### Platform Requirements

The **DT_HW_HP_Prototype** is deployed as a containerised cloud platform orchestrated with Kubernetes.

The target deployment server can be:

- a remote Virtual Private Server (VPS);
- a remote bare-metal server; or
- any remote server running a Linux operating system.

Install the following software components:

1. Docker **v28.4.0** (or a compatible version).

2. MicroKubernetes (**MicroK8s**) **v1.33.13** (or an equivalent Kubernetes distribution).

3. Configure the server firewall (e.g., ufw, iptables, or any equivalent firewall) to allow inbound and outbound traffic on the following ports:

48480 : Secure OPC UA communication
1880 : Node-RED Web Interface and Dashboard 


### Platform Deployment

1. Start the MicroKubernetes cluster:

```bash
microk8s start
```

2. Deploy the **DT_HW_HP_Prototype** by applying the Kubernetes deployment file:

```bash
microk8s kubectl apply -f DataDrivenDT_deployement.yaml
```

### Platform Configuration

After deployment, several configuration parameters must be updated before using the Digital Twin.

#### 1. Node-RED Access

Open the Node-RED editor using:

```text
https://<Your_Public_IP>:1880/
```

#### 2. Required Configuration

Within the Node-RED flow:

- update the OPC UA endpoint from the "connector" input field by replacing the default IP address with the public IP address of the OPC UA server hosting the simulated ICS i.e the PC which you launched the OPC_UA_Server_Data_Synchroniser_Simulator.py as shown in the figure below:
  <img width="868" height="815" alt="capture_3" src="https://github.com/user-attachments/assets/9b664491-e775-4852-9b05-098756bb9222" />

- configure the MariaDB connection by providing the database credentials used for industrial data storage.

Database credentials:

```text
Username: prototype
Password: Yannick
```

> **Note:** Database administration through phpMyAdmin is intended for local access only.


### Accessing the Digital Twin Human-Machine Interface (HMI)

The virtual replica of the hot water cycle of the heat pump test bench is available through the Node-RED Dashboard:

```text
https://<Your_Public_IP>:1880/dashboard
```

Authentication credentials (valid for all dashboard pages):

```text
Username: datadrivendigitaltwin
Password: datadrivendigitaltwin
```

### Remarks

- During the first connection, your web browser may display a warning related to the SSL/TLS certificate.

- This warning is expected because the SSL certificate included with the prototype was issued for the original deployment domain and not for your server's public IP address or hostname.

- For the purpose of replicating the experiment, this warning can be safely bypassed to access the Human-Machine Interface (HMI). In a production deployment, the certificate should be replaced with one issued for the target domain or IP address.
