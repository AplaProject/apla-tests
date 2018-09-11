import pytest
import os



def pytest_addoption(parser):
    curDir = os.path.dirname(os.path.abspath(__file__))

    parser.addoption("--binary", action = "store", default = [])
    
    parser.addoption('--workDir', action = "store", default=os.path.join(curDir, 'data'))
    
    parser.addoption("--centrifugo", action = "store", default = [])
    
    
    parser.addoption('--dbHost', action="store", default='localhost')
    parser.addoption('--dbPort', action="store", default='5432')
    parser.addoption('--dbUser', action="store", default='postgres')
    parser.addoption('--dbPassword', action="store", default='postgres')
    
    parser.addoption('--tcpPort1', action="store", default='7078')
    parser.addoption('--httpPort1', action="store", default='7079')
    parser.addoption('--dbName1', action="store", default='gen1')
    
    parser.addoption('--tcpPort2', action="store", default='7081')
    parser.addoption('--httpPort2', action="store", default='7018')
    parser.addoption('--dbName2', action="store", default='gen2')
    
    parser.addoption('--tcpPort3', action="store", default='7080')
    parser.addoption('--httpPort3', action="store", default='7082')
    parser.addoption('--dbName3', action="store", default='gen3')
    
    parser.addoption('--gapBetweenBlocks', action="store", default='2')

    # Arguments for gemaxblockid
    parser.addoption('--type1', action="store", default='http')
    parser.addoption('--type2', action="store", default='http')
    parser.addoption('--type3', action="store", default='http')
    parser.addoption('--httpHost1', action="store", default='localhost')
    parser.addoption('--httpHost2', action="store", default='localhost')
    parser.addoption('--httpHost3', action="store", default='localhost')

    # Arguments for quickStarterMonitoring
    parser.addoption('--dbName', action="store", default='genesis')
    parser.addoption('--logAll', action="store", default='1')
    parser.addoption('--nodesCount', action="store", default='2')
    parser.addoption('--timeout', action="store", default='2')

    # Arguments for updatePrivateKeyForRollback and RunTests
    parser.addoption('--privateKeyPath', action="store", default='D:\\genesis-go')
    parser.addoption('--configPath', action="store", default='D:\\GitHub\\GenesisKernel\\genesis-tests\\')

    # Arguments for test_update_sys_param
    parser.addoption('--privKey', action="store", default='')
    parser.addoption('--name', action="store", default='')
    parser.addoption('--value', action="store", default='')

