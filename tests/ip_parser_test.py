import unittest, sys, os
from IP_Parser import IP_Parser

class IP_Parser_Tests (unittest.TestCase):
    
    def test_loadConfig(self):
        parser = IP_Parser('./tests/test_config.json')
        parser.loadConfigFromFile()
        self.assertEqual(parser.getConfigObject()["name"], "IP Config Test")

    def test_getIpList(self):
        parser = IP_Parser('./tests/test_config.json')
        parser.loadConfigFromFile()
        parser.generateIPList()

        ipList = parser.getIpList()
        self.assertEqual(ipList, ["10.0.1.6", "10.0.1.1", '10.0.1.2', '10.0.1.3'])

    def test_getExclusionList(self):
        parser = IP_Parser('./tests/test_config.json')
        parser.loadConfigFromFile()
        parser.generateIPList()

        ipList = parser.getIpExclusionList()
        self.assertEqual(ipList, ["10.0.1.0"])

if __name__ == '__main__':
    unittest.main()