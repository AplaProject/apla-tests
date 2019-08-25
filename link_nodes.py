import time
import json

from libs import actions, tools, loger


log = loger.create_loger(__name__)


if __name__ == '__main__':
    log.info('Start ' + __name__)
    wait = tools.read_config('test')['wait_tx_status']
    conf = tools.read_config('nodes')
    url = conf[0]['url']
    pr_key1 = conf[0]['private_key']
    pr_key2 = conf[1]['private_key']
    pr_key3 = conf[2]['private_key']
    test_config = tools.read_config('test')
    test_config.update({'net_work': 'cn'})
    tools.write_config(test_config)
    data = actions.login(url, pr_key1, 0)
    token1 = data['jwtToken']
    actions.imp_app('system', url, pr_key1, token1, data['account'], pub=True)
    actions.imp_app('conditions', url, pr_key1, token1, data['account'], pub=True)
    actions.imp_app('basic', url, pr_key1, token1, data['account'], pub=True)
    actions.imp_app('lang_res', url, pr_key1, token1, data['account'], pub=True)
    actions.roles_install(url, pr_key1, token1, wait)
    actions.set_apla_consensus(data['account'], url, pr_key1, token1, wait)
    actions.voting_templates_install(url, pr_key1, token1, wait)
    node1 = json.dumps({'tcp_address': conf[0]['tcp_address'],
                        'api_address': conf[0]['api_address'],
                        'key_id': conf[0]['keyID'],
                        'public_key': conf[0]['pubKey']})
    actions.edit_app_param('first_node', node1, url, pr_key1, token1, wait)
    data2 = actions.login(url, pr_key2, 0)
    token2 = data2['jwtToken']
    actions.validator_request(conf[1]['tcp_address'], conf[1]['api_address'],
                              conf[1]['pubKey'],
                              url, pr_key2, token2, wait)
    id_validator = actions.get_count(url, 'cn_connection_requests', token1)
    actions.run_voting(1, url, pr_key1, token1, wait)
    actions.voiting(1, url, pr_key1, token1, wait)
    
    data3 = actions.login(url, pr_key3, 0)
    token3 = data3['jwtToken']
    actions.validator_request(conf[2]['tcp_address'], conf[2]['api_address'],
                              conf[2]['pubKey'],
                              url, pr_key3, token3, wait)
    id_validator2 = actions.get_count(url, 'cn_connection_requests', token1)
    actions.run_voting(id_validator2, url, pr_key1, token1, wait)
    if actions.voiting(id_validator2, url, pr_key1, token1, wait):
        # and actions.voiting(id_validator2, url, pr_key2, token2, wait):
        log.info('Nodes successfully linked')
        exit(0)
    else:
        log.error('Nodes is not linked')
        exit(1)
