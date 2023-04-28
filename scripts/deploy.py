from brownie import UniswapV3Factory,SuperCall, accounts, config, network
from scripts.helpful_scripts import (
    get_account,
    get_contract_address,
    get_params,
    find_contract,
    contract_from_abi
)
import time,json
from brownie.network import priority_fee
priority_fee("2 gwei")
json_contract = {}
def deploy_All():
    account = get_account()
    print("deploy UniswapV3Factory")

    factory = UniswapV3Factory.deploy(
        {"from": account},
    )
    
    if (config["networks"][network.show_active()].get("verify", False)):
        factory.tx.wait(BLOCK_CONFIRMATIONS_FOR_VERIFICATION)
        UniswapV3Factory.publish_source(factory)
    else: 
        factory.tx.wait(1)
    json_contract["UniswapV3Factory"] = factory.address


    print("deploy pool")
    BTC = get_contract_address("btc")
    USDC = get_contract_address("usdc")
    fee = get_params("fee")

    tx = factory.createPool(BTC, USDC, fee, {"from": account})
    tx.wait(1)
    btc_usdc = factory.getPool(BTC, USDC, fee)
    
    super_call = SuperCall.deploy(
        {"from": account},
    )

    if (config["networks"][network.show_active()].get("verify", False)):
        super_call.tx.wait(BLOCK_CONFIRMATIONS_FOR_VERIFICATION)
        SuperCall.publish_source(super_call)
    else: 
        super_call.tx.wait(1)
    json_contract["SuperCall"] = super_call.address

    btc_usdcl = super_call.getpoolAdress(factory.address, BTC, USDC, fee, factory.getPoolHash())
    #btc_usdcr = super_call.getpoolAdress(factory.address, USDC, BTC, fee)
    find, pool = contract_from_abi("UniswapV3Pool",btc_usdc)
    sqrtPriceX96 = get_params("sqrtPriceX96")
    json_contract["pool"] = btc_usdc
    json_contract["pooll"] = btc_usdcl
    json_contract["inithash"] = str(factory.getPoolHash())
    #json_contract["poolr"] = btc_usdcr

    tx = pool.initialize(sqrtPriceX96, {"from": account})
    tx.wait(1)
    '''find, btc_token =  contract_from_abi("IERC20Minimal", BTC);
    btc_token.transfer(btc_usdc, 100000000, {"from": account})
    find, usdc_token =  contract_from_abi("IERC20Minimal", USDC);
    usdc_token.transfer(btc_usdc, 100000000, {"from": account})
    '''
    '''tickLower = get_params("tickLower")
    tickUpper = get_params("tickUpper")
    amount = get_params("amount")
    data = b""
    tx = pool.mint(account, tickLower, tickUpper, amount, data, {"from": account})
    tx.wait(1)'''
        


def main():
    deploy_All()
    save_file = get_params("save")
    with open(save_file, "w") as f:
        json.dump(json_contract, f, indent=4)
    return 0
