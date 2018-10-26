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
    return actions.call_contract(url, pr_key, "NewContract", data, token)


