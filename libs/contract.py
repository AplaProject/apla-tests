import requests
from genesis_blockchain_tools.crypto import get_public_key
from libs import api, tools, actions


def new_contract(url, pr_key, token, source='',
                 name='', app=1, condition='true', ecosystem=1):
    if not name:
        code, name = tools.generate_name_and_code(source)
    else:
        if not source:
            source = '{ data {} conditions {} action {} }'
        code = 'contract ' + name + source
    data = {"Value": code,
            "ApplicationId": app,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1NewContract",
                                data,  token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name,
            "code": source}


def new_ecosystem(url, pr_key, token, name='', ecosystem=1):
    if not name:
        name = "Ecosys_" + tools.generate_random_name()
    data = {"Name": name}
    res = actions.call_contract(url, pr_key, "@1NewEcosystem",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def new_application(url, pr_key, token, name='', condition='true', ecosystem=1):
    if not name:
        name = "App" + tools.generate_random_name()
    data = {"Name": name,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1NewApplication",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def new_table(url, pr_key, token, name='', columns='',
              perms='', appId=1, ecosystem=1):
    if not name:
        name = "Tab_" + tools.generate_random_name()
    if not perms:
        perms = '{"insert": "false", "update": "true", "new_column": "true"}'
    if not columns:
        columns = '[{"name": "MyName", "type":"varchar", "index": "1", "conditions": "true"}]'
    data = {"ApplicationId": appId,
            "Name": name,
            "Columns": columns,
            "Permissions": perms}
    res = actions.call_contract(url, pr_key, "@1NewTable",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def new_column(url, pr_key, token, table, name='', type="varchar",
               up_perm="true", read_perm="true", ecosystem=1):
    if not name:
        name = 'col_' + tools.generate_random_name()
    data = {"TableName": table,
            "Name": name,
            "Type": type,
            "UpdatePerm": up_perm,
            "ReadPerm": read_perm}
    res = actions.call_contract(url, pr_key, "@1NewColumn",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            'name': name}


def edit_column(url, pr_key, token, table, column,
                update_perm="true", read_perm="true", ecosystem=1):
    data_edit = {"TableName": table,
                 "Name": column,
                 "UpdatePerm": update_perm,
                 "ReadPerm": read_perm}
    res = actions.call_contract(url, pr_key, "@1EditColumn",
                                data_edit, token, ecosystem=ecosystem)
    return {"hash": res,
            'name': table}


def edit_ecosystem_name(url, pr_key, token, id=1, name='', ecosystem=1):
    if not name:
        name = "Ecosys_" + tools.generate_random_name()
    data = {"EcosystemID": id,
            "NewName": name}
    res = actions.call_contract(url, pr_key, "@1EditEcosystemName",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            'name': name}


def new_lang(url, pr_key, token, name='', trans='', ecosystem=1):
    if not name:
        name = "Lang_" + tools.generate_random_name()
    if not trans:
        trans = '{"en": "false", "ru" : "true"}'
    data = {"Name": name,
            "Trans": trans}
    res = actions.call_contract(url, pr_key, "@1NewLang",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            'name': name}


def new_lang_joint(url, pr_key, token, name='',
                   value=["en", "ru"], local=["Hi", "Привет"], ecosystem=1):
    if not name:
        name = "Lang_" + tools.generate_random_name()
    data = {"Name": name,
            "ValueArr": value,
            "LocaleArr": local}
    res = actions.call_contract(url, pr_key, "@1NewLangJoint",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def edit_contract(url, pr_key, token, id, new_source='', name='',
                  condition='true', ecosystem=1):
    if name == '':
        name = actions.get_object_name(url, id, "contracts", token)
    if not new_source:
        new_source = '{ data {} conditions {} action {} }'
    code = 'contract ' + name + new_source
    data = {"Id": id,
            "Value": code,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1EditContract",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def edit_lang(url, pr_key, token, id, trans='', ecosystem=1):
    if not trans:
        trans = '{"en": "false", "ru": "true"}'
    data = {"Id": id,
            "Trans": trans}
    res = actions.call_contract(url, pr_key, "@1EditLang",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def edit_lang_joint(url, pr_key, token, id,
                    value=["en", "de"], local=["Hi", "Hallo"], ecosystem=1):
    data = {"Id": id,
            "ValueArr": value,
            "LocaleArr": local}
    res = actions.call_contract(url, pr_key, "@1EditLangJoint",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def edit_application(url, pr_key, token, id, condition="true", ecosystem=1):
    data = {"ApplicationId": id,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1EditApplication",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def del_application(url, pr_key, token, id, val, ecosystem=1):
    data = {"ApplicationId": id,
            "Value": val}
    res =  actions.call_contract(url, pr_key, "@1DelApplication",
                                 data, token, ecosystem=ecosystem)
    return {"hash": res}


def tokens_send(url, pr_key, token, wall, amount, comment='', ecosystem=1):
    data = {"Recipient": wall,
            "Amount": amount,
            "Comment": comment}
    res = actions.call_contract(url, pr_key, "@1TokensSend",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def bind_wallet(url, pr_key, token, id, wallet='', ecosystem=1):
    if not wallet:
        data = {"Id": id}
    else:
        data = {"Id": id,
                "WalletId": wallet}
    res = actions.call_contract(url, pr_key, "@1BindWallet",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def unbind_wallet(url, pr_key, token, id, ecosystem=1):
    data = {"Id": id}
    res = actions.call_contract(url, pr_key, "@1UnbindWallet",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def new_parameter(url, pr_key, token, name='', val="test",
                  condition="true", ecosystem=1):
    if not name:
        name = "Par_" + tools.generate_random_name()
    data = {"Name": name,
            "Value": val,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1NewParameter",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def edit_parameter(url, pr_key, token, id, value="test_edited",
                   condition="true", ecosystem=1):
    data = {"Id": id,
            "Value": value,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1EditParameter",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def new_menu(url, pr_key, token, name='', value="Item1",
             condition="true", ecosystem=1):
    if not name:
        name = "Menu_" + tools.generate_random_name()
    data = {"Name": name,
            "Value": value,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1NewMenu",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def edit_menu(url, pr_key, token, id, value="ItemEdited",
              condition="true", title="true", ecosystem=1):
    data = {"Id": id,
            "Value": value,
            "Title": title,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1EditMenu",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def append_item(url, pr_key, token, id, value='AppendedItem', ecosystem=1):
    data = {"Id": id,
            "Value": value}
    res = actions.call_contract(url, pr_key, "@1AppendMenu",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def new_page(url, pr_key, token, name='', value='', app_id=1,
             condition='true', validate_count=1, menu='default_menu', ecosystem=1):
    if not name:
        name = "Page_" + tools.generate_random_name() 
    if not value:
        value = "Hello page!"
    data = {"Name": name,
            "Value": value,
            "ApplicationId": app_id,
            "Conditions": condition,
            "Menu": menu,
            "ValidateCount": validate_count}
    res = actions.call_contract(url, pr_key, "@1NewPage",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def edit_page(url, pr_key, token, id, condition='true',
              menu='default_menu', value='', validate_count=1, ecosystem=1):
    if not value:
        value = "Good by page!"
    data = {"Id": id,
            "Value": value,
            "Conditions": condition,
            "Menu": menu,
            "ValidateCount": validate_count}
    res = actions.call_contract(url, pr_key, "@1EditPage",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def append_page(url, pr_key, token, id, value="Good by!", ecosystem=1):
    data = {"Id": id,
            "Value": value}
    res = actions.call_contract(url, pr_key, "@1AppendPage",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def new_block(url, pr_key, token, name='', value="Hello block!",
              app_id=1, condition="true", ecosystem=1):
    if not name:
        name = "Block_" + tools.generate_random_name()
    data = {"Name": name,
            "Value": value,
            "ApplicationId": app_id,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1NewBlock",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def edit_block(url, pr_key, token, id, value="Good by!",
               condition="true", ecosystem=1):
    data = {"Id": id,
            "Value": value,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1EditBlock", data, token, ecosystem=ecosystem)
    return {"hash": res}


def edit_table(url, pr_key, token, name, insert="true",
               update="true", read="true", column="true", ecosystem=1):
    data = {"Name": name,
            "InsertPerm": insert,
            "UpdatePerm": update,
            "ReadPerm": read,
            "NewColumnPerm": column}
    res = actions.call_contract(url, pr_key, "@1EditTable",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def new_app_param(url, pr_key, token, name='', app_id=1,
                  val="myParam", condition="true", ecosystem=1):
    if not name:
        name = "param_" + tools.generate_random_name()
    data = {"ApplicationId": app_id,
            "Name": name,
            "Value": val,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1EditTable",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}
    
    
def edit_app_param(url, pr_key, token, id,
                   value="myParamEdited", condition="true", ecosystem=1):
    data = {"Id": id,
            "Value": value,
            "Conditions": condition}
    res = actions.call_contract(url, pr_key, "@1EditAppParam",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def new_delayed_contract(url, pr_key, token, name='',
                         block=1, condition="true", limit=1, ecosystem=1):
    if not name:
        name = "DelayedContr_" + tools.generate_random_name()
    data = {"Contract": name,
            "EveryBlock": block,
            "Conditions": condition,
            "Limit": limit}
    res = actions.call_contract(url, pr_key, "@1NewDelayedContract",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def edit_delayed_contract(url, pr_key, token, id, name, block=1,
                          condition="true", limit=1, ecosystem=1):
    data = {"Id": id,
            "Contract": name,
            "EveryBlock": block,
            "Conditions": condition,
            "Limit": limit}
    res = actions.call_contract(url, pr_key, "@1EditDelayedContract",
                                data, token, ecosystem=ecosystem)
    result = {"hash": res}
    return result


def upload_binary(url, pr_key, token, path, name, app_id='1', ecosystem=1):
    if not name:
        name = "bin_" + tools.generate_random_name()
    with open(path, 'rb') as f:
            file = f.read()
    data = {'Name': name,
            'ApplicationId': app_id,
            'Data': file}
    res = actions.call_contract(url, pr_key, "@1UploadBinary",
                                data, token, ecosystem=ecosystem)
    return {"hash": res,
            "name": name}


def import_upload(url, pr_key, token, path, ecosystem=1):
    data = {'input_file': {'Path': path}}
    res = actions.call_contract(url, pr_key, "@1ImportUpload",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}


def export_new_app(url, pr_key, token, app_id=1, ecosystem=1):
    data = {"ApplicationId": app_id}
    res = actions.call_contract(url, pr_key, "@1ExportNewApp",
                                data, token, ecosystem=ecosystem)
    return {"hash": res}
