import os
import re
import csv
from itertools import chain

folder_path = "C:/Users/steve/Desktop/text_parsing"
##folder_path = "/path/to/folder/containing/text_files"

fieldnames=['Device Name','Same Login','login block-for','login quiet-mode access-class',\
     'login delay','service tcp-keepalives-in','service tcp-keepalives-out','banner login',\
     'transport input ssh','ip ssh version 2','snmp-server community public','no ip http server',\
     'spanning tree','spanning-tree bpduguard','no ip bootp server','ntp authenticate',\
     'no ip proxy-arp','log buffer','logging host','no logging console','aaa acounting',\
     'ntp source loopback','ip accounting access-violations','ntp status','vtp enabled',\
     'PVST','Unused ports shutdown','SNMP v3']

#compile and store regex
re_dict = {"Device Name": re.compile(r"(?<=hostname\s)(\w*)(?=\s)"),
           "Same Login": re.compile(r"(?<=username\s)(\w*)(?=\s)"),
           "log buffer": re.compile(r"(?<=Log Buffer\s[(])([0-9]*)(?=\sbytes[)])"),
           "aaa acounting": re.compile(r"(?<!no\s)(aaa new-model)(?=\s)"),
           "SNMP v3": re.compile(r"(?<=snmp-server\s)(.*v3.*)"),
           "vtp enabled": re.compile(r"VTP Operating Mode\s*:\s((?!Transparent|Off).)*"),
           "Unused ports shutdown no": re.compile(r"('((?!administratively).)*', 'down', '.*')"),
           "Unused ports shutdown yes": re.compile(r"('administratively', 'down', 'down')")
           }

#create container for file data, set "no" as default value
merged = chain(range(2,7),range(8,12),range(13,17),range(18,20),range(22,23))
file_data = {}
for i in merged:
    file_data[fieldnames[i]]="no"
    
#open and read each .txt file, save data in file_data dictionary
#append dictionaries to data_list
data_list = []
for file in filter(lambda x: x[-4:] == '.txt',os.listdir(folder_path)):
    merged = chain(range(2,7),range(8,12),range(13,17),range(18,20),range(22,23))
    with open("/".join((folder_path,file))) as f:
        file_contents = f.read()

        if re.search(re_dict["Device Name"], file_contents):
            file_data["Device Name"] = re.search(re_dict["Device Name"], file_contents).group()
        else:
            file_data["Device Name"] = "not found"

        if re.findall(re_dict["Same Login"], file_contents):
            file_data["Same Login"] = re.findall(re_dict["Same Login"], file_contents)
        else:
            file_data["Same Login"] = ["username not found"]

        for i in merged:
            if fieldnames[i] in file_contents:
                file_data[fieldnames[i]] = "yes"
    
        if ("banner login" in file_contents) or ("banner motd" in file_contents):
            file_data["banner login"] = "yes"
        else:
            file_data["banner login"] = "no"
        
        if ("spanning-tree guard root" in file_contents) or ("spanning-tree guard loop" in file_contents):
            file_data["spanning tree"] = "yes"
        else:
            file_data["spanning tree"] = "no"
        
        if re.search(re_dict["log buffer"], file_contents):
            file_data["log buffer"] = re.search(re_dict["log buffer"], file_contents).group()
        else:
            file_data["log buffer"] = "not found"
        
        if re.search(re_dict["aaa acounting"], file_contents):
            file_data["aaa acounting"] = "yes"
        else:
            file_data["aaa acounting"] = "no"
            
        if "ntp source interface Loopback" in file_contents:
            file_data["ntp source loopback"] = "yes"
        else:
            file_data["ntp source loopback"] = "no"
            
        if "%NTP is not enabled" in file_contents:
            file_data["ntp status"] = "no"
        else:
            file_data["ntp status"] = "yes"
            
        if ("vtp mode transparent" in file_contents) or ("vtp mode off" in file_contents):
            file_data["vtp enabled"] = "no"
        else:
            if re.search(re_dict["vtp enabled"], file_contents):
                file_data["vtp enabled"] = "yes"
            else:
                file_data["vtp enabled"] = "vtp mode not found"
                
        if "spanning-tree mode rapid-pvst" in file_contents:
            file_data["PVST"] = "yes"
        else:
            file_data["PVST"] = "no"
            
        if re.search(re_dict["SNMP v3"], file_contents):
            file_data["SNMP v3"] = "yes"
        else:
            if "snmp-server" in file_contents:
                file_data["SNMP v3"] = "no"
            else:
                file_data["SNMP v3"] = "snmp-server not found"
                
        if re.search\
           (r"show ip interface brief(.*\n)#*\n(.*\n)*?#########*\n\n",file_contents,flags=re.MULTILINE):
            ip_interface_brief = re.search\
            (r"show ip interface brief(.*\n)#*\n(.*\n)*?#########*\n\n",file_contents,flags=re.MULTILINE).group().split("\n")
            line_data = [tuple(line.split()[-3:]) for line in ip_interface_brief if len(line.split()) > 3]
            line_set = set(line_data)
            if re.search(re_dict["Unused ports shutdown no"],str(line_set)):
                file_data["Unused ports shutdown"] = "no"
            elif re.search(re_dict["Unused ports shutdown yes"],str(line_set)):
                file_data["Unused ports shutdown"] = "yes"
            else:
                file_data["Unused ports shutdown"] = "other"
        else:
            file_data["Unused ports shutdown"] = "ip interface brief not found"
        data_list.append(file_data)
        file_data = {key: "no" for key in file_data}

#identify logins used on more than one device
logins = list(chain(*[item["Same Login"] for item in data_list]))
same_login = list(set([item for item in logins if logins.count(item) > 1]))
for item in data_list:
    new_list = []
    for login in item["Same Login"]:
        if login in same_login:
            new = login    
            new_list.append(new)
    item["Same Login"] = []
    if new_list == []:
        item["Same Login"] = "no"
    else:
        item["Same Login"] = " ".join(new_list)

#create header row
header_row = {}
for fieldname in fieldnames:
    header_row[fieldname] = fieldname

data_list.insert(0,header_row)

#write data to csv    
with open("C:/Users/steve/Desktop/data.csv", "w", newline= "") as csv_file:
    writer = csv.DictWriter(csv_file, delimiter = ',', fieldnames=fieldnames)
    writer.writerows(data_list)            



    

