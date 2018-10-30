import argparse

from libs import actions

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
            print("Contract for the function isn't present")
            exit(1)
