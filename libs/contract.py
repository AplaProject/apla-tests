import requests


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
    result = {"hash": actions.call_contract(url, pr_key, "EditColumn", data, token),
              'name': name}
    return result

def new_user(url, pr_key, token, pub_key='', pr_key=''):
    if pr_key == '':
        pr_key = tools.generate_pr_key()
    if pub_key == '':
        pub_key = get_public_key(pr_key)
    data = {"NewPubkey": pub_key}
    result = {"hash": actions.call_contract(url, pr_key, "NewUser", data, token),
              'pr_key': pr_key}
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

def edit_contract(url, pr_key, token, name, new_source='', condition='true', wallet=''):
    if new_source == '':
        new_source = '{data { }    conditions {    }    action {    }    }'
    code = 'contract ' + name + source
    if wallet == '':
        wallet = "0005-2070-2000-0006-0200"
    data = {"Id": actions.get_contract_id(url, name, token),
             "Value": code, "Conditions": condition, "WalletId": wallet}
    result = {"hash": actions.call_contract(url, pr_key, "EditContract", data, token)}
    return result

def edit_lang(url, pr_key, token, name, trans=''):
    if trans == '':
        trans = "{\"en\": \"false\", \"ru\" : \"true\"}"
    id = actions.get_object_id(url, name, "languages", token)
    data = {"Id": id, "Trans": trans}
    result = {"hash": actions.call_contract(url, pr_key, "EditLang", data, token)}
    return result

  
    
        




