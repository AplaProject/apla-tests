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
    actions.imp_app('companies_registry', url, pr_key, token)
    
    h_rol_install = actions.call_contract(url, pr_key, 'RolesInstall',
                                 {}, token)
    check.is_tx_in_block(url, wait, {'hash': h_rol_install}, token)
    data_roles = {'RoleLawFirmJunior': 8, 'RoleLawFirmPartner': 9}
    roles_h = actions.call_contract(url, pr_key, 'CompaniesRegistrySettingsRoles',
                                       data_roles, token)
    data = {'MemberId': conf[0]['keyID'], 'Rid': 8}
    call = actions.call_contract(url, pr_key, 'RolesAssign',
                                 data, token)
    check.is_tx_in_block(url, wait, {'hash': call}, token)
    data_l = actions.login(url, pr_key, 8)
    token_l = data_l['jwtToken']
    c_id = 1

    while c_id < 1000:
        c_name = "com" + tools.generate_random_name_ch()
        print('name ', c_name)
        c_data_1 = {"Step": 1, "Id": 0,
                    "Name": c_name,
                    "TraderName": "T" + c_name}
        print('c_data_1', c_data_1)
        c_data_2 = {"Step": 2, "Id": c_id,
                    "LegalForm": "Joint-Stock Company"}
        c_data_3 = {"Step": 3, "Id": c_id,
                    "AddressCountry": "France",
                    "AddressStreet": "Sharlya",
                    "AddressHouseNumber": "10",
                    "AddressCity": "Paris",
                    "AddressPostalCode": "108813"}
        c_data_4 = {"Step": 4, "Id": c_id,
                    "RegistrationAuthority": "Tryam",
                    "RegistrationNumber": "10000",
                    "RegistrationDate": "13-Jun-2018",
                    "FlagUnlimited": "true"}
        c_data_5 = {"Step": 5, "Id": c_id,
                    "FlagLicense": "false"}
        hash1 = actions.call_contract(url, pr_key, '@1CompanyEdit', c_data_1,  token_l)
        check.is_tx_in_block(url, wait, {"hash": hash1}, token)
        hash2 = actions.call_contract(url, pr_key, '@1CompanyEdit', c_data_2,  token_l)
        check.is_tx_in_block(url, wait, {"hash": hash2}, token)
        hash3 = actions.call_contract(url, pr_key, '@1CompanyEdit', c_data_3,  token_l)
        check.is_tx_in_block(url, wait, {"hash": hash3}, token)
        hash4 = actions.call_contract(url, pr_key, '@1CompanyEdit', c_data_4,  token_l)
        check.is_tx_in_block(url, wait, {"hash": hash4}, token)
        hash5 = actions.call_contract(url, pr_key, '@1CompanyEdit', c_data_5,  token_l)
        check.is_tx_in_block(url, wait, {"hash": hash5}, token)
        print("Company " + c_name + "created." + str(c_id))
        c_id += 1
    user = 1
    while user < 10000:
        tx_cont = contract.new_user(url, pr_key, token_e)
        check.is_tx_in_block(url, wait, tx_cont, token_e)
        user += 1
    print("finish")
