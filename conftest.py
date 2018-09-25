import pytest
import os

from libs import tools, actions, db


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

@pytest.fixture(scope="class")
def setup_vars():
    wait = tools.read_config("test")["wait_tx_status"]
    conf = tools.read_config("nodes")
    keys = tools.read_fixtures("keys")
    url = conf["2"]["url"]
    url1 = conf["1"]["url"]
    prKey = conf["1"]['private_key']
    data = actions.login(url, prKey, 0)
    token = data["jwtToken"]
    data_limits = actions.login(conf["2"]["url"],
                                conf["1"]['private_key'], 0)
    token_limits = data_limits["jwtToken"]
    data_sys_con = actions.login(url1, prKey, 0)
    token_sys_con = data_sys_con["jwtToken"]
    db1 = conf["1"]["db"]
    db2 = conf["2"]["db"]
    contract = tools.read_fixtures("contracts")
    vars = {"wait": wait, "conf": conf, "keys": keys, "url": url, "url1": url1, "contract": contract, "data": data,
            "token": token, "private_key": prKey, "db1": db1, "db2": db2, "data_limits": data_limits,
            "token_limits": token_limits, "token_sys_con": token_sys_con}
    return vars
