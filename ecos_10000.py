import time
import json

from libs import actions, tools, loger, contract, check


log = loger.create_loger(__name__, 'environment.log')


if __name__ == '__main__':
    log.info('Start ' + __name__)
    conf = tools.read_config('nodes')
    url = conf[0]['url']
    pr_key = conf[0]['private_key']
    wait = tools.read_config('test')['wait_tx_status']
    data = actions.login(url, pr_key, 0)
    token = data['jwtToken']
    ecos = 0
    while ecos < 3:
        tx = contract.new_ecosystem(url, pr_key, token)
        check.is_tx_in_block(url, wait, tx, token)
        ecos_id = actions.get_object_id(url, tx['name'], "ecosystems", token, ecosystem=0)
        data_e = actions.login(url, pr_key, ecosystem=ecos_id)
        token_e = data_e['jwtToken']
        tx_app = contract.platform_apps_install(url, pr_key, token_e, ecosystem=ecos_id)
        print(tx_app)
        check.is_tx_in_block(url, wait, tx_app, token_e)
        cont = 0
        while cont < 3:
            print(cont)
            tx_cont = contract.new_contract(url, pr_key, token_e, ecosystem=ecos_id)
            print(tx_cont)
            check.is_tx_in_block(url, wait, tx_cont, token_e)
            cont += 1
        ecos += 1
    print("finish")
