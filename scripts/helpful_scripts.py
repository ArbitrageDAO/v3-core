from brownie import (
    network,
    accounts,
    config,
    Contract,
    web3
)
import time

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]
# Etherscan usually takes a few blocks to register the contract has been deployed
BLOCK_CONFIRMATIONS_FOR_VERIFICATION = 6
DECIMALS = 18
INITIAL_VALUE = web3.toWei(2000, "ether")


def get_account(index=None, id=None):
    #if index:
    #    return accounts[index]
    #if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    #    return accounts[0]
    #if id:
    #    return accounts.load(id)
    return accounts.add(config["networks"][network.show_active()]["from_key"])

def get_wallet(wallet_name):
    return accounts.add(config["networks"][network.show_active()][wallet_name])

def get_wallet_account(account_name):
    import json
    import os
    wallet_file = "wallet/" +network.show_active() + ".json"
    file_exists =  os.path.exists(wallet_file)
    if file_exists: 
        with open( wallet_file) as fr:
            json_abi = json.load(fr)
            privkey = json_abi[account_name]
            return accounts.add(privkey)
    return None

def get_contract_address(contract_name):
    contract_address = config["networks"][network.show_active()][contract_name]
    return contract_address

def get_params(param_name):
    param_value = config["networks"][network.show_active()][param_name]
    return param_value

def find_contract(contract_name, use_config = False):
    import json
    import os
    address = ""
    if use_config == False:
        address_file = config["networks"][network.show_active()]["save"]
        if os.path.exists(address_file) == False:
            return False,None
        
        f = open(address_file)
        json_address = json.load(f)
        address = json_address[contract_name]
    else :
        address =  config["networks"][network.show_active()][contract_name]
    abi_file = "build/contracts/" + contract_name + ".json"
    project =  os.path.exists(abi_file)
    if project == True:
        with open( abi_file) as fr:
            json_abi = json.load(fr)
            contract = Contract.from_abi(contract_name, 
            address, json_abi["abi"]
            )
            return True, contract 
    else :
        abi_file = "abi/" + contract_name + ".json"
        extern = os.path.exists(abi_file)
        if extern == True:
            with open( abi_file) as fr:
                json_abi = json.load(fr)
                contract = Contract.from_abi(contract_name, 
                address, json_abi
                )
            return True, contract 
    return False, None

def contract_from_abi(abi_name, address):
    import json
    import os
    abi_file = "build/contracts/" + abi_name + ".json"
    project =  os.path.exists(abi_file)
    if project == True:
        with open( abi_file) as fr:
            json_abi = json.load(fr)
            contract = Contract.from_abi(abi_name, 
            address, json_abi["abi"]
            )
            return True, contract 
    else :
        abi_file = "abi/" + abi_name + ".json"
        extern = os.path.exists(abi_file)
        if extern == True:
            with open( abi_file) as fr:
                json_abi = json.load(fr)
                contract = Contract.from_abi(abi_name, 
                address, json_abi
                )
            return True, contract 
    return False, None


def get_contract(contract_name):
    try:
        find,contract = find_contract(contract_name, False)
        if find == False :
            print("not find %s"%contract_name)
            assert False
    except KeyError:
        print(
            f"{network.show_active()} address not found, perhaps you should add it to the config or deploy mocks?"
        )
        print(
            f"brownie run scripts/deploy_mocks.py --network {network.show_active()}"
        )
    return contract

def filter_event_log(contract, event, from_block, to_block):
    event_filter = contract.events[event].createFilter(fromBlock=from_block, toBlock=to_block)
    for event_response in event_filter.get_all_entries():
        #if event in event_response.event:
        print(event_response)
    
def listen_for_event(brownie_contract, event, timeout=200, poll_interval=2):
    """Listen for an event to be fired from a contract.
    We are waiting for the event to return, so this function is blocking.

    Args:
        brownie_contract ([brownie.network.contract.ProjectContract]):
        A brownie contract of some kind.

        event ([string]): The event you'd like to listen for.

        timeout (int, optional): The max amount in seconds you'd like to
        wait for that event to fire. Defaults to 200 seconds.

        poll_interval ([int]): How often to call your node to check for events.
        Defaults to 2 seconds.
    """
    web3_contract = web3.eth.contract(
        address=brownie_contract.address, abi=brownie_contract.abi
    )
    start_time = time.time()
    current_time = time.time()
    event_filter = web3_contract.events[event].createFilter(fromBlock="latest")
    while current_time - start_time < timeout:
        for event_response in event_filter.get_new_entries():
            if event in event_response.event:
                print("Found event!")
                return event_response
        time.sleep(poll_interval)
        current_time = time.time()
    print("Timeout reached, no event found.")
    return { "event": None }
