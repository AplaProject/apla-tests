import time
import json

from libs import actions, tools, loger, check


log = loger.create_loger(__name__)


if __name__ == '__main__':
    log.info('Start ' + __name__)
    config = tools.read_config('test')
    print('TestConfig: ', config)
    wait = tools.read_config('test')['wait_tx_status']
    conf = tools.read_config('nodes')
    url = conf[0]['url']
    pr_key1 = conf[0]['private_key']
    pr_key2 = conf[1]['private_key']
    pr_key3 = conf[2]['private_key']
    data = actions.login(url, pr_key1, 0)
    token1 = data['jwtToken']
    actions.imp_app('system', url, pr_key1, token1, data['account'])
    actions.imp_app('lang_res', url, pr_key1, token1, data['account'])
    actions.imp_app('conditions', url, pr_key1, token1, data['account'])
    actions.imp_app('companies_registry', url, pr_key1, token1, data['account'])
    full_nodes = json.dumps([{'tcp_address': conf[0]['tcp_address'],
                        'api_address': conf[0]['api_address'],
                        'public_key': conf[0]['node_pub_key']}, {'tcp_address': conf[1]['tcp_address'],
                        'api_address': conf[1]['api_address'],
                        'public_key': conf[1]['node_pub_key']}, {'tcp_address': conf[2]['tcp_address'],
                        'api_address': conf[2]['api_address'],
                        'public_key': conf[2]['node_pub_key']}])
    print("Strt update full_nodes")
    data = {'Name': 'full_nodes', 'Value': full_nodes}
    res = actions.call_contract(url, pr_key1, 'UpdateSysParam', data, token1)
    print('here')
    if check.is_tx_in_block(url, wait, {'hash': res}, token1):
        log.info('Nodes successfully linked')
    else:
        log.error('Nodes is not linked')
        exit(1)
    data = {'Name': 'max_block_generation_time', 'Value': '10000'}
    res = actions.call_contract(url, pr_key1, 'UpdateSysParam', data, token1)
    check.is_tx_in_block(url, wait, {'hash': res}, token1)
    
    call_dep = actions.call_contract(url, pr_key1, 'Deploy',
                                 {}, token1)
    if check.is_tx_in_block(url, wait, {'hash': call_dep}, token1):
        log.info('X_reg successfully deployed')
    else:
        log.error('X_reg is not deployed')
        exit(1)
    data = {'Name': 'max_block_generation_time', 'Value': '2000'}
    res = actions.call_contract(url, pr_key1, 'UpdateSysParam', data, token1)
    if check.is_tx_in_block(url, wait, {'hash': res}, token1):
        log.info('Limits are returned')
        exit(0)
    else:
        log.error('Limits arent returned')
        exit(1)