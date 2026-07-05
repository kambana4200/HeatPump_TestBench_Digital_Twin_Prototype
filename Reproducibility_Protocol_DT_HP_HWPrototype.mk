# REPLICATION OF THE DATA-DRIVEN DIGITAL TWIN (DT) CLOUD PLATFORM NAMED DT_HW_HP_Prototype

## 1) Platform Installation

1) Install Docker 28.4.0  

2) Install MicroKubernetes (or Kubernetes) v1.33.13  

3) On the server firewall (ufw, iptables, or other), open inbound and outbound connections on the following ports:  
    48480 (OPC UA)  
    1880 (Node-RED)  

4) Run the installation script of the Data-Driven Digital Twin prototype named DT_HW_HP_Prototype with root privileges using the command:

microK8s start
microK8s kubectl apply -f DataDrivenDT_deployement.yaml

## How to run and use the DT_HW_HP_Prototype

1) Open the Node-RED flow using the URL: https://yourPublicIP:1880/

2) Imperative Modification inside Node-RED flow:

i) Update the public IP address used in the OPC UA endpoint in the Node-RED flow
ii) Add the MariaDB credentials for industrial data storage and phpmyadmin access (only local acess allowed):
    Login: prototype
    Password: Yannick

3) Access the virtual replica of the heat pump test bench hot water cycle using: https://yourPublicIP:18180/dashboard
    
    Authentication Credentials (All tabs): 
        Login: datadrivendigitaltwin
        Password: datadrivendigitaltwin

## Remark
You may need to bypass SSL certificate verification when opening the web interfaces to access the Human-Machine Interface (HMI).
This is not a security risk; it is due to the SSL certificate being configured only for my specific domain name.