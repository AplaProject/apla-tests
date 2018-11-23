import time
import json

from libs import actions, tools, loger


log = loger.create_loger(__name__, 'environment.log')


if __name__ == '__main__':
    log.info('Start ' + __name__)
    wait = tools.read_config('test')['wait_tx_status']
    conf = tools.read_config('nodes')
    url = conf[0]['url']
    pr_key1 = conf[0]['private_key']
    pr_key2 = conf[1]['private_key']
    pr_key3 = conf[2]['private_key']
    data = actions.login(url, pr_key1, 0)
    token1 = data['jwtToken']
    actions.imp_app('system', url, pr_key1, token1)
    actions.imp_app('conditions', url, pr_key1, token1)
    actions.imp_app('basic', url, pr_key1, token1)
    actions.imp_app('lang_res', url, pr_key1, token1)

    actions.roles_install(url, pr_key1, token1, wait)

    actions.voting_templates_install(url, pr_key1, token1, wait)
    actions.edit_app_param('voting_sysparams_template_id', 2, url, pr_key1, token1, wait)
    node1 = json.dumps({'tcp_address': conf[0]['tcp_address'],
                        'api_address': conf[0]['api_address'],
                        'key_id': conf[0]['keyID'],
                        'public_key': conf[0]['pubKey']})
    actions.edit_app_param('first_node', node1, url, pr_key1, token1, wait)

    data2 = actions.login(url, pr_key2, 0)
    token2 = data2['jwtToken']
    actions.update_profile('nodeowner1', url, pr_key2, token2, wait)
    data3 = actions.login(url, pr_key3, 0)
    token3 = data3['jwtToken']
    actions.update_profile('nodeowner2', url, pr_key3, token3, wait)

    data = actions.login(url, pr_key1, 1)
    token1 = data['jwtToken']

    actions.set_apla_consensus(conf[1]['keyID'], url, pr_key1, token1, wait)
    actions.set_apla_consensus(conf[2]['keyID'], url, pr_key1, token1, wait)
    actions.set_apla_consensus(conf[0]['keyID'], url, pr_key1, token1, wait)

    log.info('Start create voting 1')
    data = actions.login(url, pr_key2, 3)
    token2 = data['jwtToken']
    actions.create_voiting(conf[1]['tcp_address'], conf[1]['api_address'],
                   conf[1]['keyID'], conf[1]['pubKey'],
                   url, pr_key2, token2, wait)
    actions.voting_status_update(url, pr_key1, token1, wait)

    data = actions.login(url, pr_key3, 3)
    token3 = data['jwtToken']
    actions.voiting(1, url, pr_key3, token3, wait)
    data = actions.login(url, pr_key1, 3)
    token1 = data['jwtToken']
    actions.voiting(1, url, pr_key1, token1, wait)
    data = actions.login(url, pr_key2, 3)
    token2 = data['jwtToken']
    actions.voiting(1, url, pr_key2, token2, wait)

    log.info('Start create voting 2')
    data = actions.login(url, pr_key3, 3)
    token3 = data['jwtToken']
    actions.create_voiting(conf[2]['tcp_address'], conf[2]['api_address'],
                   conf[2]['keyID'], conf[2]['pubKey'],
                   url, pr_key3, token3, wait)
    actions.voting_status_update(url, pr_key1, token1, wait)

    data = actions.login(url, pr_key3, 3)
    token3 = data['jwtToken']
    actions.voiting(2, url, pr_key3, token3, wait)
    data = actions.login(url, pr_key1, 3)
    token1 = data['jwtToken']
    actions.voiting(2, url, pr_key1, token1, wait)
    data = actions.login(url, pr_key2, 3)
    token2 = data['jwtToken']
    if actions.voiting(2, url, pr_key2, token2, wait):
        log.info('Nodes successfully linked')
        exit(0)
    else:
        log.error('Nodes is not linked')
        exit(1)
