import time
import json

from libs import actions, tools, loger, contract, check


log = loger.create_loger(__name__)


if __name__ == '__main__':
    log.info('Start ' + __name__)
    conf = tools.read_config('nodes')
    url = conf[0]['url']
    pr_key = conf[0]['private_key']
    wait = tools.read_config('test')['wait_tx_status']
    data = actions.login(url, pr_key, 0)
    token = data['jwtToken']
    
    h_rol_install = actions.call_contract(url, pr_key, 'RolesInstall',
                                 {}, token)
    check.is_tx_in_block(url, wait, {'hash': h_rol_install}, token)
    data_roles = {'RoleLawFirmJunior': 3, 'RoleLawFirmPartner': 4}
    roles_h = actions.call_contract(url, pr_key, 'CompaniesRegistrySettingsRoles',
                                       data_roles, token)
    data = {'MemberId': conf[0]['keyID'], 'Rid': 3}
    call = actions.call_contract(url, pr_key, 'RolesAssign',
                                 data, token)
    check.is_tx_in_block(url, wait, {'hash': call}, token)
    data_l = actions.login(url, pr_key, 3)
    token_l = data_l['jwtToken']
    tr = 0
    while tr < 1:
        hash1 = actions.call_contract(url, pr_key, '@1BDMeetingStatusUpdate', {},  token_l)
        time.sleep(5)
    print("finish")
