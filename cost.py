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

    if args.firstBoot:
        actions.imp_app("system", args.url, args.prKey, token)
        actions.imp_app("bench", args.url, args.prKey, token)
    else:
        is_present = actions.is_contract_present(
            args.url, token, "Bench_" + str(args.function))
        if is_present:
            cont_data = [{"contract": "Bench_" + str(args.function),
                          "params": {"n": int(args.n)}} for _ in range(int(args.threads))]
            actions.call_multi_contract(args.url, args.prKey, "Bench_" + str(args.function),
                                        cont_data, token, False)
        else:
            print("Contract for the function isn't present")
            exit(1)
        print("Contract successfully run")
        exit(0)
