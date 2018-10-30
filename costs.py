import argparse

from libs import actions

def get_contract(func):
    dict = {'CreateColumn': 'NewColumn',
            'CompileContract': 'NewContract',
            'CreateEcosystem': 'NewEcosystem',
            'FlushContract': 'NewContract',
            'CreateTable': 'NewTable',
            'ColumnCondition': 'NewColumn',
            'PermColumn': 'EditColumn',
            'TableConditions': 'NewTable',
            'PermTable': 'EditTable',
            'NewMoney': 'NewUser',
            'EditEcosysName': 'EditEcosystemName',
            'CreateContract': 'NewContract',
            'EditLanguage': 'EditLang',
            'CreateLanguage': 'NewLang',
            'UpdateContract': 'EditContract',
            'SetPubKey': 'NewUser'}
    return dict.get(func)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', default='http://localhost:7079/api/v2')
    parser.add_argument('-prKey', required=True)
    parser.add_argument('-firstBoot', default=False)
    parser.add_argument('-function', required=False)
    parser.add_argument('-n', required=False)
    parser.add_argument('-threads', required=False)
    
    args = parser.parse_args()
    data = actions.login(args.url, args.prKey, 0)
    token = data["jwtToken"]
    
    if args.firstBoot == True:
        actions.imp_app("system", args.url, args.prKey, token)
        actions.imp_app("bench", args.url, args.prKey, token)
    else:
        is_present = actions.is_contract_present(args.url, token, 'bench_' + name)
        if is_present == True:
            cont_data = [{"contract": args.function,
                          "params": {"n": args.n}} for _ in range(args.threads)]
            actions.call_multi_contract(args.url, args.prKey, args.function, cont_data, token, False)
        else:
            contract = get_contract(func)
            if contract == None:
                print("Contract for the function isn't present")
                exit(1)
            if contract == "NewContract":
                i = 0
                while i < args.n:
                    code = 'contract ' + name + source
                    data = [{"contract": contract,
                            "params": {"Value": 'contract ' + "cont_" + tools.generate_random_name() + '{data { }    conditions {    }    action {    }    }',
                                    "ApplicationId": 1, "Conditions": 'true'}} for _ in range(args.threads)]
                    actions.call_multi_contract(args.url, args.prKey, contract, data, token, False)
                    i +=1
            if contract == "NewTable":
                perms = """{"insert": "false", "update": "true", "new_column": "true"}"""
                columns = """[{"name": "MyName", "type":"varchar", "index": "1", "conditions": "true"}]""" 
                i = 0
                while i < args.n:
                    name = "Tab_" + tools.generate_random_name()
                    data = [{"contract": contract,
                         "params": {"ApplicationId": 1, "Name": name,
                                    "Columns": columns, "Permissions": perms}} for _ in range(args.threads)]
                    actions.call_multi_contract(args.url, args.prKey, contract, data, token, False)
                    i +=1