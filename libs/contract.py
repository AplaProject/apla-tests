import requests

from genesis_blockchain_tools.crypto import get_public_key
from libs import api, tools, actions


def new_contract(url, pr_key, token, source='', name='', app=1, condition='true'):
    if name == '':
        code, name = tools.generate_name_and_code(source)
    else:
        if source == '':
            source = '{data { }    conditions {    }    action {    }    }'
        code = 'contract ' + name + source
    data = {"Value": code, "ApplicationId": app, "Conditions": condition}
    result = {"hash": actions.call_contract(url, pr_key, "NewContract", data, token),
              "name": name, "code": code}
    return result

def new_ecosystem(url, pr_key, token, name=''):
    if name == '':
        name = "Ecosys_" + tools.generate_random_name()
    else:
        name = name
    data = {"Name": "Ecosys_" + tools.generate_random_name()}
    result = {"hash": actions.call_contract(url, pr_key, "NewEcosystem", data, token),
              "name": name}
    return result

def new_application(url, pr_key, token, name='', condition='true'):
    if name == '':
        name = "App" + tools.generate_random_name()
    data = {"Name": name, "Conditions": condition}
    result = {"hash": actions.call_contract(url, pr_key, "NewApplication", data, token),
              "name": name}
    return result

def new_table(url, pr_key, token, name='', columns='', perms='', appId=1):
    if name == '':
        name = "Tab_" + tools.generate_random_name()
    if perms == '':
        perms = """{"insert": "false", "update": "true", "new_column": "true"}"""
    if columns == '':
        columns = """[{"name": "MyName", "type":"varchar", "index": "1", "conditions": "true"}]""" 
    data = {"ApplicationId": appId, "Name": name,
            "Columns": columns, "Permissions": perms}
    result = {"hash": actions.call_contract(url, pr_key, "NewTable", data, token),
              "name": name}
    return result

def new_column(url, pr_key, token, table, name='', type="varchar", up_perm="true",
               read_perm="true"):
    if name == '':
        name = 'col_' + tools.generate_random_name()
    data = {"TableName": table, "Name": name, "Type": type, "UpdatePerm": up_perm,
            "ReadPerm": read_perm}
    result = {"hash": actions.call_contract(url, pr_key, "NewColumn", data, token),
              'name': name}
    return result

def edit_column(url, pr_key, token, table, column, up_perm="true",
               read_perm="true"):
    data_edit = {"TableName": table, "Name": column,
                 "UpdatePerm": "false", "ReadPerm": "false"}
    result = {"hash": actions.call_contract(url, pr_key, "EditColumn", data_edit, token),
              'name': table}
    return result

def edit_ecosystem_name(url, pr_key, token, id=1, name=''):
    if name == '':
        name = "Ecosys_" + tools.generate_random_name()
    data = {"EcosystemID": id, "NewName": name}
    result = {"hash": actions.call_contract(url, pr_key, "EditEcosystemName", data, token),
              'pr_key': pr_key}
    return result

def new_lang(url, pr_key, token, name='', trans=''):
    if name == '':
        name = "Lang_" + tools.generate_random_name()
    if trans == '':
        trans = "{\"en\": \"false\", \"ru\" : \"true\"}"
    data = {"Name": name, "Trans": trans}
    result = {"hash": actions.call_contract(url, pr_key, "NewLang", data, token),
              'name': name}
    return result

def edit_contract(url, pr_key, token, id, new_source='', condition='true', wallet=''):
    if new_source == '':
        new_source = '{data { }    conditions {    }    action {    }    }'
    code = 'contract ' + name + new_source
    if wallet == '':
        wallet = "0005-2070-2000-0006-0200"
    data = {"Id": id, "Value": code, "Conditions": condition, "WalletId": wallet}
    result = {"hash": actions.call_contract(url, pr_key, "EditContract", data, token)}
    return result

def edit_lang(url, pr_key, token, id, trans=''):
    if trans == '':
        trans = "{\"en\": \"false\", \"ru\" : \"true\"}"
    data = {"Id": id, "Trans": trans}
    result = {"hash": actions.call_contract(url, pr_key, "EditLang", data, token)}
    return result

def edit_application(url, pr_key, token, id, condition="true"):
    data = {"ApplicationId": id, "Conditions": condition}
    result = {"hash": actions.call_contract(url, pr_key, "EditApplication", data, token)}
    return result

def del_application(url, pr_key, token, id, val):
    data = {"ApplicationId": id, "Value": val}
    result = {"hash": actions.call_contract(url, pr_key, "DelApplication", data, token)}
    return result

def tokens_send(url, pr_key, token, wall, amount):
    data = {"Recipient": wall, "Amount": amount}
    result = {"hash": actions.call_contract(url, pr_key, "TokensSend", data, token)}
    return result

def bind_wallet(url, pr_key, token, id, wallet=''):
    if wallet == '':
        data = {"Id": id}
    else:
        {"Id": id, "WalletId": wallet}
    result = {"hash": actions.call_contract(url, pr_key, "BindWallet", data, token)}
    return result

def unbind_wallet(url, pr_key, token, id):
    data = {"Id": id}
    result = {"hash": actions.call_contract(url, pr_key, "UnbindWallet", data, token)}
    return result

def new_parameter(url, pr_key, token, name='', val="test", condition="true"):
    if name == '':
        name = "Par_" + tools.generate_random_name()
    data = {"Name": name, "Value": val,"Conditions": condition}
    result = {"hash": actions.call_contract(url, pr_key, "NewParameter", data, token),
              "name": name}
    return result

def edit_parameter(url, pr_key, token, id, value="test_edited", condition="true"):
    data = {"Id": id, "Value": value, "Conditions": condition}
    result = {"hash": actions.call_contract(url, pr_key, "EditParameter", data, token)}
    return result

def new_menu(url, pr_key, token, name='', value="Item1", condition="true"):
    if name == '':
        name = "Menu_" + tools.generate_random_name()
    data = {"Name": name, "Value": value, "Conditions": condition}
    result = {"hash": actions.call_contract(url, pr_key, "NewMenu", data, token),
              "name": name}
    return result

def edit_menu(url, pr_key, token, id, value="ItemEdited", condition="true"):
    data = {"Id": id, "Value": value, "Conditions": condition}
    result = {"hash": actions.call_contract(url, pr_key, "EditMenu", data, token)}
    return result

def append_item(url, pr_key, token, id, value='AppendedItem'):
    data = {"Id": id, "Value": value}
    result = {"hash": actions.call_contract(url, pr_key, "AppendedItem", data, token)}
    return result

def new_page(url, pr_key, token, name='', value='', app_id=1, condition='true', menu='default_menu'):
    if name == '':
        name = "Page_" + tools.generate_random_name() 
    if value == '':
        value = "Hello page!"
    data = {"Name": name, "Value": value, "ApplicationId": app_id,
            "Conditions": condition, "Menu": menu}
    result = {"hash": actions.call_contract(url, pr_key, "NewPage", data, token),
              "name": name}
    return result

def edit_page(url, pr_key, token, id, condition='true', menu='default_menu', value=''):
    if value == '':
        value = "Good by page!"
    data_edit = {"Id": id, "Value": value, "Conditions": condition, "Menu": menu}
    result = {"hash": actions.call_contract(url, pr_key, "EditPage", data, token)}
    return result


