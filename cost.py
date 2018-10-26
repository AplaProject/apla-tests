import argparse

from libs import actions


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', default='http://localhost:7079/api/v2')
    parser.add_argument('-prKey', required=True)
    parser.add_argument('-contract', required=True)
    parser.add_argument('-n', required=True)
    parser.add_argument('-threads', required=True)
    
    args = parser.parse_args()
    data = actions.login(args.url, args.prKey, 0)
    token = data["jwtToken"] 
    
    cont_data = [{"contract": args.contract,
                 "params": {"n": args.n}} for _ in range(args.threads)]
    actions.call_multi_contract(args.url, args.prKey, args.contract, cont_data, token, False)