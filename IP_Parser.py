import json
import ipaddress
import datetime
import time

class IP_Parser:
    def __init__(self, iConfig="config.json"):
        self.config_file = iConfig
        self.config = {}
        self.ip_list = []
        self.ip_exclusion = []

    def getIpList(self):
        return self.ip_list

    def getIpExclusionList(self):
        return self.ip_exclusion

    def getConfigObject(self):
        return self.config

    def updateConfigFile(self, iConfigFile):
        self.config_file = iConfigFile

    def loadConfigFromObject(self, iConfigObject):
        self.config = iConfigObject

    def loadConfigFromFile(self):
        try:
            with open(self.config_file) as json_config_file:
                data = json.load(json_config_file)
                self.config = data
        except:
            print ("Failed to parse config file")

    def getTimeStamp(self, iIncludeTime=False):
        timeStr = ""
        theTime = time.time()
        if (iIncludeTime):
            timeStr = datetime.datetime.fromtimestamp(theTime).strftime('%Y_%m_%d_%H_%M_%S')
        else:
            timeStr = datetime.datetime.fromtimestamp(theTime).strftime('%Y_%m_%d')

        return timeStr

    def parseIpFile(self, iIpFileName):
        print ("Parsing IP range from file...")
        output = []

        with open(iIpFileName) as f:
            output = f.readlines()
            output = [entry.strip() for entry in output]

        subnets = [self.parseIpRange(output[i]) for i in range(len(output)) if (output[i].find('/') > -1)]
        subnets = [entry for subnet in subnets for entry in subnet] #flatten list of subnets (lists)
        output = [output[i] for i in range(len(output)) if (str(output[i]).find('/') == -1)]

        return output + subnets

    def parseIpRange(self, iIpRange):
        if iIpRange.find('/') == -1:
            return [iIpRange]
        try:
            ipAddresses = [str(ip) for ip in ipaddress.IPv4Network(iIpRange)]
            return ipAddresses
        except:
            return []

    def generateIPList(self):
        print ("Generating IP List...")
        ipList = []
        for range in self.config['ranges']:
            if "target" in range:
                ipList = ipList + self.parseIpRange(range['target'])
            if "target_file" in range:
                ipList = ipList + self.parseIpFile(range['target_file'])

        # Filter out exclusions
        self.generateExclusionList()
        ipList = [ip for ip in ipList if ip not in self.ip_exclusion]

        ipSet = set(ipList)
        ipList = list(ipSet).sort()
        self.ip_list = ipList

    def generateExclusionList(self):
        print ("Generating IP Exclusion List...")
        ipExList = []
        for entries in self.config['exclusions']:
            if "exclusion" in entries:
                ipExList = ipExList + self.parseIpRange(entries['exclusion'])
            if "exclusion_file" in entries:
                ipExList = ipExList + self.parseIpFile(entries['exclusion_file'])

        ipExSet = set(ipExList)
        self.ip_exclusion = list(ipExSet)

    def exportBySubnet(self, cidrMask):
        print ("Segmenting IP List by Subnet")

        cidrValue = 0
        if (cidrMask.find('/') == 0):
            cidrValue = int(cidrMask[1:])
        else:
            cidrValue = int(cidrMask)

        if (cidrValue % 8 != 0 and cidrValue != 0):
            print("Cidr Mask was not valid... Defaulting to one file")
            return [self.ip_list]
        elif (cidrValue == 0):
            return [self.ip_list]
        else:
            netAddrSize = int(cidrValue/8)
            segmentObj = {}

            for ip in self.ip_list:
                splitIp = ip.split('.')
                subnet = splitIp[0:netAddrSize]
                host = ".".join(splitIp[netAddrSize:])
                subnetStr = ".".join(subnet)
                if (subnetStr in segmentObj):
                    segmentObj[subnetStr].append(host)
                else:
                    segmentObj[subnetStr] = [host]

            for subnet in segmentObj:
                lFileName = "./output/ips_" + str(subnet) + "_" + self.getTimeStamp() + ".txt"
                with open (lFileName, 'w') as outputFile:
                    for host in segmentObj[subnet]:
                        outputFile.write("%s\n" % str(subnet + "." + host))

    def exportIpList(self):
        print("Exporting IP List..")
        lOutputFile = str(self.config['export']['filename'])

        if (lOutputFile == ""):
            lOutputFile = "./output/ip_output_" + self.getTimeStamp() + ".txt"

        if (str(self.config['export']['export_by_subnet'])):
            try:
                self.breakUpIpList(cidrMask)
            except:
                print("Failed to write to file...")
        else:
            try:
                with open (lOutputFile, 'w') as outputFile:
                    for ip in self.ip_list:
                        outputFile.write("%s\n" % ip)
            except:
                print("Failed to write to file...")

if __name__ == '__main__':
    parser = IP_Parser()
    parser.loadConfigFromFile()
    parser.generateIPList()
    parser.exportBySubnet("/16")
    print("\nComplete!")
