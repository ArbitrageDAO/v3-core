pragma solidity =0.7.6;
import './libraries/PoolAddress.sol';
import './UniswapV3Pool.sol';

contract SuperCall{
    constructor()
    {}

    function doCall(
        address tigger,
        bytes calldata data
    ) external {
        (bool success, bytes memory ret) = tigger.call(data);
        require(success && (ret.length == 0 || abi.decode(ret, (bool))), 'TF');
    }
    mapping (int => bytes) delcount_data;
    function doDelCall(
        address tigger,
        address to,
        uint256 amount
    ) external {
        //(bool success, bytes memory ret) = tigger.delegatecall(abi.encodeWithSignature("transfer(address,uint256)", to, amount));
       // require(success && (ret.length == 0 || abi.decode(ret, (bool))), 'TF');
        bytes memory data = abi.encodeWithSignature("transfer(address,uint256)", to, amount);
        uint256 tx_gas = gasleft();
        bool success =false;
        assembly {
                success := delegatecall(tx_gas, tigger, add(data, 0x20), mload(data), 0, 0)
            }
        require(success, 'TF');
    }

    function viewTransfer(address to, uint256 amount)  public view  returns (bytes memory){
        bytes memory callData = abi.encodeWithSignature("transfer(address,uint256)", to, amount);
        return  callData;
    }
    function getpoolAdress(address factory, address token0, address token1, uint24 fee, bytes32 init_hash) view public returns (address pool)
    {
        pool = PoolAddress.computeAddress(
                        factory,
                        PoolAddress.PoolKey({token0: token0, token1: token1, fee: fee}),
                        init_hash
                    );
        return pool;
    }

   

}