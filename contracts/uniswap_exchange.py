OntCversion = '2.0.0'
"""
This is the uniswap_exchange smart contract on Ontology
"""
from ontology.libont import byte2int, hexstring2bytes, hexstring2address, bytes2hexstring
from ontology.interop.Ontology.Native import Invoke
from ontology.interop.Ontology.Contract import Migrate, Create, GetScript
from ontology.interop.System.Action import RegisterAction
from ontology.interop.Ontology.Runtime import Base58ToAddress, GetCurrentBlockHash
from ontology.interop.System.Storage import Put, GetContext, Get, Delete
from ontology.interop.System.ExecutionEngine import  GetExecutingScriptHash, GetCallingScriptHash, GetEntryScriptHash
from ontology.interop.System.Runtime import CheckWitness, Notify, Serialize, Deserialize, GetTime
from ontology.builtins import concat, state
from ontology.libont import bytearray_reverse, AddressFromVmCode
from ontology.interop.System.App import RegisterAppCall, DynamicAppCall

ZERO_ADDRESS = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

# TODO: change this contract hash when on mainnet
ONTD_ADDRESS = hexstring2address('2e0de81023ea6d32460244f29c57c84ce569e7b7')

NAME = "Uniswap V1"
SYMBOL= "UNI-V1"
DECIMALS= 9
TOTAL_SUPPLY_KEY = "totalSupply"
BALANCE_PREFIX = "balance"
APPROVE_PREFIX = "allowance"

TOKEN_KEY = "token"
FACTORY_KEY = "factory"

# Event format
SetupEvent = RegisterAction("setup", "token_addr", "factory_addr")
TokenPurchaseEvent = RegisterAction("tokenPurchase", "buyer", "ont_sold", "tokens_bought")
OntPurchaseEvent = RegisterAction("ontPurchase", "buyer", "tokens_sold", "ont_bought")
AddLiquidityEvent = RegisterAction("addLiquidity", "provider", "ont_amount", "token_amount")
RemoveLiquidityEvent = RegisterAction("removeLiquidity", "provider", "ont_amount", "token_amount")
TransferEvent = RegisterAction("transfer", "from", "to", "amount")
ApprovalEvent = RegisterAction("approval", "owner", "spender", "amount")

# Method name used for Invoke or DynamicAppCall
Transfer_MethodName = "transfer"
Approve_MethodName = "approve"
TransferFrom_MethodName = "transferFrom"
BalanceOf_MethodName = "balanceOf"
GetExchange_MethodName = "getExchange"
OntToTokenTransferInput_MethodName = "ontToTokenTransferInput"
GetOntToTokenOutputPrice_MethodName = "getOntToTokenOutputPrice"
OntToTokenTransferOutput_MethodName = "ontToTokenTransferOutput"

def Main(operation, args):
    if operation == "setup":
        assert (len(args) == 2)
        token_addr = args[0]
        factory_addr = args[1]
        return setup(token_addr, factory_addr)
    if operation == "addLiquidity":
        assert (len(args) == 5)
        min_liquidity = args[0]
        max_tokens = args[1]
        deadline = args[2]
        depositer = args[3]
        deposit_ontd_amt = args[4]
        return addLiquidity(min_liquidity, max_tokens, deadline, depositer, deposit_ontd_amt)
    if operation == "removeLiquidity":
        assert (len(args) == 5)
        amount = args[0]
        min_ontd = args[1]
        min_tokens = args[2]
        deadline = args[3]
        withdrawer = args[4]
        return removeLiquidity(amount, min_ontd, min_tokens, deadline, withdrawer)
    if operation == "ontToTokenSwapInput":
        assert (len(args) == 4)
        min_tokens = args[0]
        deadline = args[1]
        invoker = args[2]
        ontd_amount = args[3]
        return ontToTokenSwapInput(min_tokens, deadline, invoker, ontd_amount)
    if operation == "ontToTokenTransferInput":
        assert (len(args) == 5)
        min_tokens = args[0]
        deadline = args[1]
        recipient = args[2]
        invoker = args[3]
        ontd_amount = args[4]
        return ontToTokenTransferInput(min_tokens, deadline, recipient, invoker, ontd_amount)
    if operation == "ontToTokenSwapOutput":
        assert (len(args) == 4)
        tokens_bought = args[0]
        deadline = args[1]
        invoker = args[2]
        ontd_amount = args[3]
        return ontToTokenSwapOutput(tokens_bought, deadline, invoker, ontd_amount)
    if operation == "ontToTokenTransferOutput":
        assert (len(args) == 5)
        tokens_bought = args[0]
        deadline = args[1]
        recipient = args[2]
        invoker = args[3]
        ontd_amount = args[4]
        return ontToTokenTransferOutput(tokens_bought, deadline, recipient, invoker, ontd_amount)
    if operation == "tokenToOntSwapInput":
        assert (len(args) == 4)
        tokens_sold = args[0]
        min_ontd = args[1]
        deadline = args[2]
        tokens_seller = args[3]
        return tokenToOntSwapInput(tokens_sold, min_ontd, deadline, tokens_seller)
    if operation == "tokenToOntTransferInput":
        assert (len(args) == 5)
        tokens_sold = args[0]
        min_ontd = args[1]
        deadline = args[2]
        tokens_seller = args[3]
        recipient = args[4]
        return tokenToOntTransferInput(tokens_sold, min_ontd, deadline, tokens_seller, recipient)
    if operation == "tokenToOntSwapOutput":
        assert (len(args) == 4)
        ontd_bought = args[0]
        max_tokens = args[1]
        deadline = args[2]
        invoker = args[3]
        return tokenToOntSwapOutput(ontd_bought, max_tokens, deadline, invoker)
    if operation == "tokenToOntTransferOutput":
        assert (len(args) == 5)
        ontd_bought = args[0]
        max_tokens = args[1]
        deadline = args[2]
        recipient = args[3]
        invoker = args[4]
        return tokenToOntTransferOutput(ontd_bought, max_tokens, deadline, recipient, invoker)
    if operation == "tokenToTokenSwapInput":
        assert (len(args) == 6)
        tokens_sold = args[0]
        min_tokens_bought = args[1]
        min_ontd_bought = args[2]
        deadline = args[3]
        token_addr = args[4]
        invoker = args[5]
        return tokenToTokenSwapInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, token_addr, invoker)
    if operation == "tokenToTokenTransferInput":
        assert (len(args) == 7)
        tokens_sold = args[0]
        min_tokens_bought = args[1]
        min_ontd_bought = args[2]
        deadline = args[3]
        recipient = args[4]
        token_addr = args[5]
        invoker = args[6]
        return tokenToTokenTransferInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, recipient, token_addr, invoker)
    if operation == "tokenToTokenSwapOutput":
        assert (len(args) == 6)
        tokens_bought = args[0]
        max_tokens_sold = args[1]
        max_ontd_sold = args[2]
        deadline = args[3]
        token_hash = args[4]
        invoker = args[5]
        return tokenToTokenSwapOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, token_hash, invoker)
    if operation == "tokenToTokenTransferOutput":
        assert (len(args) == 7)
        tokens_bought = args[0]
        max_tokens_sold = args[1]
        max_ontd_sold = args[2]
        deadline = args[3]
        recipient = args[4]
        token_hash = args[5]
        invoker = args[6]
        return tokenToTokenTransferOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, recipient, token_hash, invoker)
    if operation == "tokenToExchangeSwapInput":
        assert (len(args) == 6)
        tokens_sold = args[0]
        min_tokens_bought = args[1]
        min_ontd_bought = args[2]
        deadline = args[3]
        exchange_hash = args[4]
        invoker = args[5]
        return tokenToExchangeSwapInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, exchange_hash, invoker)
    if operation == "tokenToExchangeTransferInput":
        assert (len(args) == 7)
        tokens_sold = args[0]
        min_tokens_bought = args[1]
        min_ontd_bought = args[2]
        deadline = args[3]
        recipient = args[4]
        exchange_hash = args[5]
        invoker = args[6]
        return tokenToExchangeTransferInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, recipient, exchange_hash, invoker)
    if operation == "tokenToExchangeSwapOutput":
        assert (len(args) == 6)
        tokens_bought = args[0]
        max_tokens_sold = args[1]
        max_ontd_sold = args[2]
        deadline = args[3]
        exchange_hash = args[4]
        invoker = args[5]
        return tokenToExchangeSwapOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, exchange_hash, invoker)
    if operation == "tokenToExchangeTransferOutput":
        assert (len(args) == 7)
        tokens_bought = args[0]
        max_tokens_sold = args[1]
        max_ontd_sold = args[2]
        deadline = args[3]
        recipient = args[4]
        exchange_hash = args[5]
        invoker = args[6]
        return tokenToExchangeTransferOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, recipient, exchange_hash, invoker)
    if operation == "getOntToTokenInputPrice":
        assert (len(args) == 1)
        ontd_sold = args[0]
        return getOntToTokenInputPrice(ontd_sold)
    if operation == "getOntToTokenOutputPrice":
        assert (len(args) == 1)
        tokens_bought = args[0]
        return getOntToTokenOutputPrice(tokens_bought)
    if operation == "getTokenToOntInputPrice":
        assert (len(args) == 1)
        tokens_sold = args[0]
        return getTokenToOntInputPrice(tokens_sold)
    if operation == "getTokenToOntOutputPrice":
        assert (len(args) == 1)
        ontd_bought = args[0]
        return getTokenToOntOutputPrice(ontd_bought)
    if operation == "tokenAddress":
        return tokenAddress()
    if operation == "factoryAddress":
        return factoryAddress()

    if operation == "name":
        return name()
    if operation == "symbol":
        return symbol()
    if operation == "decimals":
        return decimals()
    if operation == "totalSupply":
        return totalSupply()
    if operation == "balanceOf":
        assert (len(args) == 1)
        owner = args[0]
        return balanceOf(owner)
    if operation == "transfer":
        assert (len(args) == 3)
        from_acct = args[0]
        to_acct = args[1]
        amount = args[2]
        return transfer(from_acct, to_acct, amount)
    if operation == "transferMulti":
        return transferMulti(args)
    if operation == "transferFrom":
        assert (len(args) == 4)
        spender = args[0]
        from_acct = args[1]
        to_acct = args[2]
        amount = args[3]
        return transferFrom(spender, from_acct, to_acct, amount)
    if operation == "approve":
        assert (len(args) == 3)
        owner = args[0]
        spender = args[1]
        amount = args[2]
        return approve(owner, spender, amount)
    if operation == "allowance":
        assert (len(args) == 2)
        owner = args[0]
        spender = args[1]
        return allowance(owner, spender)
    assert (False)


def setup(token_addr, factory_addr):
    """
    This function is called once by the factory contract during contract creation.
    :param token_addr: Indicate which token is supported by current exchange contract, token_addr -> reversed token contract hash
    :param factory_addr: Indicate contract address which is invoking `setup` method, factory_addr -> reversed factory contract hash
    :return:
    """
    # Make sure the stored factory and token are empty and passed token_addr is not empty
    factory = Get(GetContext(), FACTORY_KEY)
    token = Get(GetContext(), TOKEN_KEY)
    assert (len(factory) == 0 and len(token) == 0 and len(token_addr) == 20 and len(factory_addr) == 20)
    # Ensure being invoked by the contract with hash of factory_addr
    assert (CheckWitness(factory_addr))
    # token_addr cannot be self
    assert (token_addr != GetExecutingScriptHash())
    # token_addr cannot be ontd contract address
    assert (token_addr != ONTD_ADDRESS)
    # Store the token_addr
    Put(GetContext(), TOKEN_KEY, token_addr)
    Put(GetContext(), FACTORY_KEY, factory_addr)

    # Fire event
    SetupEvent(token_addr, factory_addr)
    return True


def addLiquidity(min_liquidity, max_tokens, deadline, depositer, deposit_ontd_amt):
    """
    Deposit ONT and Tokens at current ratio to mint UNI tokens

    :param min_liquidity: Condition check to help depositer define minimum share minted to himself
    :param max_tokens: Maximum number of tokens deposited. Deposits max amount if total UNI supply is 0
    :param deadline: Time after which this transaction can no longer be executed.
    :param depositer: Account address depositing Ont and tokens into contract to add liquidity
    :param deposit_ontd_amt: Amount of ont that will be deposited
    :return: The amount of UNI minted
    """
    # Ensure the validity of parameters
    assert (deposit_ontd_amt > 0 and deadline > GetTime() and max_tokens > 0)
    # Check depositer's signature
    assert (CheckWitness(depositer))
    self = GetExecutingScriptHash()

    curSupply= totalSupply()
    tokenAddr = tokenAddress()
    liquidityMinted = 0
    if curSupply > 0:
        assert (min_liquidity > 0)
        # Get ontd balance of current contract
        ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
        # Get OEP4 asset balance of current contract
        tokenReserve = DynamicAppCall(tokenAddr, BalanceOf_MethodName, [self])
        # Calculate the token increment correlated with deposit_ont_amt
        # Optimize here, ethereum version: tokenAmount = deposit_ontd_amt * tokenReserve / ontdReserve + 1
        tokenAmount = (deposit_ontd_amt * tokenReserve + ontdReserve - 1) / ontdReserve
        # Calculate how many token should be minted as shares for the provider
        liquidityMinted = deposit_ontd_amt * curSupply / ontdReserve
        # Check if conditions are met
        assert (max_tokens >= tokenAmount and liquidityMinted >= min_liquidity)
        # Update the depositer's share balance and the total supply (or share)
        Put(GetContext(), concat(BALANCE_PREFIX, depositer), liquidityMinted + balanceOf(depositer))
        Put(GetContext(), TOTAL_SUPPLY_KEY, curSupply + liquidityMinted)
    else:
        # Make sure the factory and token address are not empty, make sure initial depositing amount is greater than 0
        factory = factoryAddress()
        assert (len(factory) > 0 and len(tokenAddr) > 0 and deposit_ontd_amt > 0)
        # Obtain the exchange hash correlated with tokenHash and ensure it equals current contract hash
        exchange = DynamicAppCall(factory, GetExchange_MethodName, [bytearray_reverse(tokenAddr)])
        assert (exchange == self)
        # Update the depositer's share balance and the total supply
        tokenAmount = max_tokens
        initialLiquidity = deposit_ontd_amt
        Put(GetContext(), concat(BALANCE_PREFIX, depositer), initialLiquidity)
        Put(GetContext(), TOTAL_SUPPLY_KEY, initialLiquidity)
    # Transfer deposit_amt amount of ontd into this contract
    assert (DynamicAppCall(ONTD_ADDRESS, Transfer_MethodName, [depositer, self, deposit_ontd_amt]))
    # Transfer token from depositer to current contract
    assert (DynamicAppCall(tokenAddr, TransferFrom_MethodName, [self, depositer, self, tokenAmount]))
    # Fire event
    AddLiquidityEvent(depositer, deposit_ontd_amt, tokenAmount)
    TransferEvent(ZERO_ADDRESS, depositer, liquidityMinted)
    # return minted liquidity or minted shares
    return liquidityMinted


def removeLiquidity(amount, min_ontd, min_tokens, deadline, withdrawer):
    """
    Burn UNI tokens to withdraw ETH and Tokens at current ratio

    :param amount: Amount of UNI burned
    :param min_ontd: Minimum Ontd withdrawn
    :param min_tokens: Minimum tokens withdrawn
    :param deadline: Time after which this transaction can no longer be executed
    :param withdrawer: Account address who wants to remove his shares of Ont and tokens from liquidity pool
    :return: The amount of Ont and tokens withdrawn
    """
    # Ensure conditions are met
    assert (amount > 0 and deadline > GetTime() and min_ontd > 0 and min_tokens > 0)
    assert (CheckWitness(withdrawer))
    curSupply = totalSupply()
    assert (curSupply > 0)
    # Obtain token balance of current contract
    self = GetExecutingScriptHash()
    tokenAddr = tokenAddress()
    tokenReserve = DynamicAppCall(tokenAddr, BalanceOf_MethodName, [self])
    # Obtain native asset reserve balance of current contract
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    # Calculate how many OEP4 tokens should be withdrawn by the withdrawer
    tokenAmount = amount * tokenReserve / curSupply
    # Calculate how much native asset should be withdrawn by the withdrawer
    ontdAmount = amount * ontdReserve / curSupply
    # Ensure the calculated withdrawn amounts are no less than required, otherwise, roll back this tx
    assert (ontdAmount >= min_ontd and tokenAmount >= min_tokens)
    # Update withdrawer's balance and total supply
    oldBalance = balanceOf(withdrawer)
    assert (amount <= oldBalance and amount <= curSupply)

    newBalance = oldBalance - amount
    newSupply = curSupply - amount
    if newBalance == 0:
        Delete(GetContext(), concat(BALANCE_PREFIX, withdrawer))
    else:
        Put(GetContext(), concat(BALANCE_PREFIX, withdrawer), oldBalance - amount)
    if newSupply == 0:
        Delete(GetContext(), TOTAL_SUPPLY_KEY)
    else:
        Put(GetContext(), TOTAL_SUPPLY_KEY, curSupply - amount)

    # Transfer ontdAmount of native asset to withdrawer
    assert (DynamicAppCall(ONTD_ADDRESS, Transfer_MethodName, [self, withdrawer, ontdAmount]))
    # Transfer tokenAmount of token to withdrawer
    assert (DynamicAppCall(tokenAddr, Transfer_MethodName, [self, withdrawer, tokenAmount]))
    # Fire event
    RemoveLiquidityEvent(withdrawer, ontdAmount, tokenAmount)
    TransferEvent(withdrawer, ZERO_ADDRESS, amount)
    return [ontdAmount, tokenAmount]



def _ontToTokenInput(ontd_sold, min_tokens, deadline, buyer, recipient):
    # Check signature of buyer
    assert (CheckWitness(buyer))
    assert (deadline >= GetTime() and ontd_sold > 0 and min_tokens > 0)
    # Obtain the token balance and native asset balance
    tokenHash = tokenAddress()
    self = GetExecutingScriptHash()
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    # Calculate how many tokens should be transferred to recipient considering buyer provide ont_sold amount of native asset ont
    tokenBought = _getInputPrice(ontd_sold, ontdReserve, tokenReserve)
    # Ensure the calculated amount of token bought is no less than min_tokens required
    assert (tokenBought >= min_tokens)
    # Transfer ontd_sold amount of ontd from buyer to self contract address
    assert (DynamicAppCall(ONTD_ADDRESS, TransferFrom_MethodName, [self, buyer, self, ontd_sold]))
    # Transfer tokenBought amount of tokens directly from this exchange to recipient
    assert (DynamicAppCall(tokenHash, Transfer_MethodName, [self, recipient, tokenBought]))
    # Fire event
    TokenPurchaseEvent(buyer, ontd_sold, tokenBought)
    return tokenBought


def ontToTokenSwapInput(min_tokens, deadline, invoker, ontd_amount):
    """
    Convert ont_amount of Ont to tokens and transfer tokens to invoker with conditions:
    1. tokens bought no less than min_tokens
    2. tx executed no late than deadline

    :param min_tokens: min_tokens invoker expects providing ont_amount of ont
    :param deadline: Time after which this transaction can no longer be executed
    :param invoker: The user's account address
    :param ontd_amount: The amount of ont user provides
    :return: Amount of tokens bought
    """
    return _ontToTokenInput(ontd_amount, min_tokens, deadline, invoker, invoker)

def ontToTokenTransferInput(min_tokens, deadline, recipient, invoker, ontd_amount):
    """
    Convert Ont to tokens and transfer tokens to recipient with conditions:
    1. tokens bought no less than min_tokens
    2. tx executed no late than deadline

    :param min_tokens: Minimum token bought expected
    :param deadline: Time after which this tx will not be executed
    :param recipient: Address that will receive output tokens
    :param invoker: msg sender of this tx, account address wishing exchange ont for tokens
    :param ontd_amount: Amount of Ont invoker provides to buy tokens
    :return:
    """
    assert (recipient != GetExecutingScriptHash() and len(recipient) == 20 and recipient != ZERO_ADDRESS)
    return _ontToTokenInput(ontd_amount, min_tokens, deadline, invoker, recipient)


def _ontToTokenOutput(tokens_bought, max_ontd, deadline, buyer, recipient):
    # Check signature of buyer
    assert (CheckWitness(buyer))
    # Legal check
    assert (deadline >= GetTime() and tokens_bought > 0 and max_ontd > 0)
    # Obtain the token balance and native asset balance of contract
    tokenHash = tokenAddress()
    self = GetExecutingScriptHash()
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    # Calculate how much native asset we have to provide to acquire tokens_bought amount of token
    ontdSold = _getOutputPrice(tokens_bought, ontdReserve, tokenReserve)
    # Condition check: make sure ontdSold that will be deducted from buyer is no more than max_ont
    assert (ontdSold <= max_ontd)
    # Transfer ontdSold amount of native asset directly from buyer account to this contract
    assert (DynamicAppCall(ONTD_ADDRESS, TransferFrom_MethodName, [self, buyer, self, ontdSold]))
    # Transfer tokens_bought amount of token from contract to recipient account address
    assert (DynamicAppCall(tokenHash, Transfer_MethodName, [self, recipient, tokens_bought]))
    # Fire event
    TokenPurchaseEvent(buyer, ontdSold, tokens_bought)
    return ontdSold

def ontToTokenSwapOutput(tokens_bought, deadline, invoker, ontd_amount):
    """
    Convert some Ont, yet less than ont_amount, to tokens_bought amount of tokens and transfer tokens to invoker with conditions:
    1. the spent ont amount should be no greater than ont_amount
    2. tx should not be executable after deadline

    :param tokens_bought: Exact amount of tokens bought
    :param deadline: Time after which this tx can no longer be executed
    :param invoker: User expecting to exchange with ont for tokens
    :param ontd_amount: Amount of Maximum ont invoker provides for acquiring tokens_bought tokens
    :return: Amount of ont sold for obtaining tokens_bought amount of tokens
    """
    return _ontToTokenOutput(tokens_bought, ontd_amount, deadline, invoker, invoker)

def ontToTokenTransferOutput(tokens_bought, deadline, recipient, invoker, ontd_amount):
    """
    Convert some Ont, yet less than ont_amount, to tokens_bought amount of tokens and transfer tokens to recipient with conditions:
    1. the spent ont amount should be no greater than ont_amount
    2. tx should not be executable after deadline

    :param tokens_bought: Exact amount of tokens bought
    :param deadline: Time after which this tx can no longer be executed
    :param recipient: Address that receives output Tokens.
    :param invoker: User expecting to exchange with ont for tokens
    :param ont_amount: Amount of Maximum ont invoker provides for acquiring tokens_bought tokens
    :return: Amount of ont sold for obtaining tokens_bought amount of tokens
    """
    return _ontToTokenOutput(tokens_bought, ontd_amount, deadline, invoker, recipient)


def _tokenToOntInput(tokens_sold, min_ontd, deadline, buyer, recipient):
    # Check the signature of buyer
    assert (CheckWitness(buyer))
    assert (deadline >= GetTime() and tokens_sold > 0 and min_ontd > 0)
    # Obtain the current token balance and native asset balance
    tokenHash = tokenAddress()
    self = GetExecutingScriptHash()
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    # Calculate how much native asset should be deducted from the pool if tokens_sold amount of token are added
    ontdBought = _getInputPrice(tokens_sold, tokenReserve, ontdReserve)
    # Ensure the ontdBought is no less than the expected minimum native asset ont amount
    assert (ontdBought >= min_ontd)
    # Transfer directly tokens_sold amount of token from buyer account to current contract
    assert (DynamicAppCall(tokenHash, TransferFrom_MethodName, [self, buyer, self, tokens_sold]))
    # Transfer native asset directly to the recipient
    assert (DynamicAppCall(ONTD_ADDRESS, Transfer_MethodName, [self, recipient, ontdBought]))
    # Fire event
    OntPurchaseEvent(buyer, tokens_sold, ontdBought)
    return ontdBought


def tokenToOntSwapInput(tokens_sold, min_ontd, deadline, tokens_seller):
    """
    Convert tokens_sold amount of tokens to Ont and transfer ont to tokens_seller with conditions:
    1. the converted ont should be no less than min_ont
    2. tx can no long be executed after deadline

    :param tokens_sold: Amount of tokens sold
    :param min_ontd: Minimum Ont after converted
    :param deadline: Time after which this tx can no longer be executed
    :param tokens_seller: Account address who wishes convert tokens_sold amount token to some ont no less than min_ont
    :return: Amount of ont converted
    """
    return _tokenToOntInput(tokens_sold, min_ontd, deadline, tokens_seller, tokens_seller)

def tokenToOntTransferInput(tokens_sold, min_ontd, deadline, tokens_seller, recipient):
    """
    Convert tokens_sold amount of tokens to Ont and transfer ont to recipient with conditions:
    1. the converted ont should be no less than min_ont
    2. tx can no long be executed after deadline

    :param tokens_sold: Amount of tokens sold
    :param min_ontd: Minimum Ont after converted
    :param deadline: Time after which this tx can no longer be executed
    :param tokens_seller: Account address who wishes convert tokens_sold amount token to some ont no less than min_ont
    :param recipient: Address that receives output Ont
    :return:
    """
    assert (recipient != GetExecutingScriptHash() and len(recipient) == 20 and recipient != ZERO_ADDRESS)
    return _tokenToOntInput(tokens_sold, min_ontd, deadline, tokens_seller, recipient)

def _tokenToOntOutput(ontd_bought, max_tokens, deadline, buyer, recipient):
    # Check signature of buyer
    assert (CheckWitness(buyer))
    assert (deadline > GetTime() and ontd_bought > 0)
    # Obtain the current balance of token and native asset
    tokenHash = tokenAddress()
    self = GetExecutingScriptHash()
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    # Calculate how much token will be added into the pool providing the amount of token should be worth of ont_bought native asset
    tokensSold = _getOutputPrice(ontd_bought, tokenReserve, ontdReserve)
    # Make sure the sold token will be no greater than max_token if he wants ont_bought amount of native asset
    assert (max_tokens >= tokensSold)
    # Transfer na_bought native asset directly to the recipient address
    assert (DynamicAppCall(ONTD_ADDRESS, Transfer_MethodName, [self, recipient, ontd_bought]))
    # Transfer tokensSold amount of token from buyer to contract
    assert (DynamicAppCall(tokenHash, TransferFrom_MethodName, [self, buyer, self, tokensSold]))
    # Fire event
    OntPurchaseEvent(buyer, tokensSold, ontd_bought)
    return tokensSold

def tokenToOntSwapOutput(ontd_bought, max_tokens, deadline, invoker):
    """
    Convert some tokens to specific ont_bought amount of ont and transfer ont to invoker with conditions
    1. the required amount of tokens equal to ont_bought should be no more than max_tokens
    2. tx can no long be executed after deadline

    :param ontd_bought: Amount of ont converted from some unknown amount of tokens
    :param max_tokens:  Maximum amount of tokens that will be sold to obtain ont_bought amount of ont
    :param deadline: Time after which this tx can no longer be executed
    :param invoker: Account address who wishes to convert some amount of tokens (no more than max_tokens) to ont_bought amount of ont
    :return: Amount of tokens invoker should sell to acquire ont_bought amount of ont
    """
    return _tokenToOntOutput(ontd_bought, max_tokens, deadline, invoker, invoker)

def tokenToOntTransferOutput(ontd_bought, max_tokens, deadline, recipient, invoker):
    """
    Convert some tokens to specific ont_bought amount of ont and transfer ont to recipient with conditions
    1. the required amount of tokens equal to ont_bought should be no more than max_tokens
    2. tx can no long be executed after deadline

    :param ontd_bought: Amount of ont converted from some unknown amount of tokens
    :param max_tokens:  Maximum amount of tokens that will be sold to obtain ont_bought amount of ont
    :param deadline: Time after which this tx can no longer be executed
    :param recipient: Address that will receive ont
    :param invoker: Account address who wishes to convert some amount of tokens (no more than max_tokens) to ont_bought amount of ont
    :return:
    """
    assert (recipient != GetExecutingScriptHash() and len(recipient) == 20 and recipient != ZERO_ADDRESS)
    return _tokenToOntOutput(ontd_bought, max_tokens, deadline, invoker, recipient)

def _tokenToTokenInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, buyer, recipient, exchange_addr):
    # Check the signature of buyer
    assert (CheckWitness(buyer))
    # Legal check
    assert (deadline >= GetTime() and tokens_sold > 0 and min_tokens_bought > 0 and min_ontd_bought > 0)
    self = GetExecutingScriptHash()
    assert (exchange_addr != self and exchange_addr != ZERO_ADDRESS and len(exchange_addr) == 20)
    tokenHash = tokenAddress()
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    ontdBought = _getInputPrice(tokens_sold, tokenReserve, ontReserve)
    # Make sure tokens_sold amount of tokenHash can be exchanged for at least min_ont_bought amount of native asset
    assert (ontdBought >= min_ontd_bought)
    # Transfer tokens_sold amount of tokenHash to current contract
    assert (DynamicAppCall(tokenHash, TransferFrom_MethodName, [self, buyer, self, tokens_sold]))

    # Before we invoke another exchange's "ontTokenTransferOutput" method, we need to approve ontdBought amount of ontd to another exchange
    # so that another exchange can do ontd.transferFrom(exchange2, exchange1, exchange2, ontdBought)
    assert (DynamicAppCall(ONTD_ADDRESS, Approve_MethodName, [self, exchange_addr, ontdBought]))

    # Invoke another exchange contract to sell ontdBought amount of native asset and buy at least
    # min_tokens_bought amount of another token and transfer the bought token to recipient directly
    tokensBought = DynamicAppCall(exchange_addr, OntToTokenTransferInput_MethodName, [min_tokens_bought, deadline, recipient, self, ontdBought])
    assert (tokensBought > 0)

    # Fire event
    OntPurchaseEvent(buyer, tokens_sold, ontdBought)
    return

def tokenToTokenSwapInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, token_hash, invoker):
    """
    Convert token1 within current exchange to another token2 of token_addr and transfer token_addr to recipient with conditions:
    1. tokens_sold amount of token1 will be sold out
    2. both exchanges supporting token1 and token2 were created by the same factory
    3. the bought amount of token2 should be no less than min_tokens_bought
    4. the converted ont amount from selling tokens_sold amount of token1 should be no less than min_ont_bought
        min_ont_bought means how many ont at minimum we expect to use to purchase token2
    5. tx can no long be executed after deadline

    :param tokens_sold: Amount of token sold
    :param min_tokens_bought: Minimum tokens of token_addr purchased
    :param min_ontd_bought: Minimum ont purchased as intermediary
    :param deadline: Time after which this tx can no longer be executed
    :param token_addr: Address of token being purchased
    :param invoker: Account address expecting to convert his tokens to token_addr
    :return: Amount of tokens (token_addr) bought
    """
    exchangeAddr = DynamicAppCall(factoryAddress(), GetExchange_MethodName, [token_hash])
    return _tokenToTokenInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, invoker, invoker, exchangeAddr)

def tokenToTokenTransferInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, recipient, token_addr, invoker):
    """
    Convert tokens_sold amount of token1 within current exchange to another token2 of token_addr and transfer token_addr to recipient with conditions:
    1. tokens_sold amount of token1 will be sold out
    2. both exchanges supporting token1 and token2 were created by the same factory
    3. the bought amount of token2 should be no less than min_tokens_bought
    4. the converted ont amount from selling tokens_sold amount of token1 should be no less than min_ont_bought
        min_ont_bought means how many ont at minimum we expect to use to purchase token2
    5. tx can no long be executed after deadline

    :param tokens_sold: Amount of token sold
    :param min_tokens_bought: Minimum tokens of token_addr purchased
    :param min_ontd_bought: Minimum ont purchased as intermediary
    :param deadline: Time after which this tx can no longer be executed
    :param recipient: Address that receives output token_addr
    :param token_addr: Address of token being purchased
    ::param invoker: Account address expecting to convert his tokens to token_addr
    :return: Amount of tokens (token_addr) bought
    """
    exchangeAddr = DynamicAppCall(factoryAddress(), GetExchange_MethodName, [token_addr])
    return _tokenToTokenInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, invoker, recipient, exchangeAddr)


def _tokenToTokenOutput(tokens_bought, max_tokens_sold, max_ont_sold, deadline, buyer, recipient, exchange_addr):
    # Check signature of buyer
    assert (CheckWitness(buyer))
    # Legal check
    assert (deadline >= GetTime() and tokens_bought > 0 and max_ont_sold > 0)
    self = GetExecutingScriptHash()
    assert (exchange_addr != self and exchange_addr != ZERO_ADDRESS and len(exchange_addr) == 20)
    # Calculate how much native asset should we provide to buy tokens_bought amount token in exchange_addr platform
    ontdBought = DynamicAppCall(exchange_addr, GetOntToTokenOutputPrice_MethodName, [tokens_bought])
    tokenHash = tokenAddress()
    # Obtain current token and native asset balance of current contract
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    # Calculate how much tokens we have to sell to obtain ontdBought amount of native asset in current exchange
    tokensSold = _getOutputPrice(ontdBought, tokenReserve, ontdReserve)
    # Condition check
    # 1. The tokens sold to obtain tokens_bought amount of another token is at most max_token_sold
    # 2. To acquire tokens_bought amount of another token, we expect to provide at most max_ont_sold amount of native asset
    assert (max_tokens_sold >= tokensSold and max_ont_sold >= ontdBought)
    # Transfer tokensSold amount of token to current contract
    assert (DynamicAppCall(tokenHash, TransferFrom_MethodName, [self, buyer, self, tokensSold]))

    # Before we invoke another exchange's "ontTokenTransferOutput" method, we need to approve ontdBought amount of ontd to another exchange
    # so that another exchange can do ontd.transferFrom(exchange2, exchange1, exchange2, ontdBought)
    assert (DynamicAppCall(ONTD_ADDRESS, Approve_MethodName, [self, exchange_addr, ontdBought]))

    # Invoke another exchange to convert ontdBought amount native asset to tokens_bought amount of another token
    assert (DynamicAppCall(exchange_addr, OntToTokenTransferOutput_MethodName, [tokens_bought, deadline, recipient, self, ontdBought]))

    # Fire event
    OntPurchaseEvent(buyer, tokensSold, ontdBought)
    return tokensSold


def tokenToTokenSwapOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, token_hash, invoker):
    """
    Convert some token1 within current exchange to tokens_bought amount of another token2 of token_addr and transfer token_addr to invoker with conditions:
    1. tokens_bought amount of token2 should be bought
    2. both exchanges supporting token1 and token2 were created by the same factory
    3. the sold amount of token1 should be no more than max_token_sold
    4. the converted ont amount from purchasing tokens_bought amount of token2 should be no more than max_ont_sold
        max_ont_sold means how many ont at maximum from selling token1 we expect to use to purchase token2
    5. tx can no long be executed after deadline

    :param tokens_bought: Amount of tokens (token_addr) bought
    :param max_tokens_sold: Maximum tokens (within current exchange) sold
    :param max_ontd_sold: Maximum Ont purchased as intermediary
    :param deadline: Time after which this tx can no longer be executed
    :param token_hash: Contract hash of token being purchased
    :param invoker: Account address expecting to convert his tokens to token_addr
    :return: Amount of tokens (within current exchange) sold
    """
    exchangeAddr = DynamicAppCall(factoryAddress(), GetExchange_MethodName, [token_hash])
    return _tokenToTokenOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, invoker, invoker, exchangeAddr)

def tokenToTokenTransferOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, recipient, token_hash, invoker):
    """
    Convert some token1 within current exchange to tokens_bought amount of another token2 of token_addr and transfer token_addr to recipient with conditions:
    1. tokens_bought amount of token2 should be bought
    2. both exchanges supporting token1 and token2 were created by the same factory
    3. the sold amount of token1 should be no more than max_token_sold
    4. the converted ont amount from purchasing tokens_bought amount of token2 should be no more than max_ont_sold
        max_ont_sold means how many ont at maximum from selling token1 we expect to use to purchase token2
    5. tx can no long be executed after deadline

    :param tokens_bought: Amount of tokens (token_addr) bought
    :param max_tokens_sold: Maximum tokens (within current exchange) sold
    :param max_ontd_sold: Maximum Ont purchased as intermediary
    :param deadline: Time after which this tx can no longer be executed
    :param recipient: Address that receives output token_addr
    :param token_hash: Contract hash of token being purchased
    :param invoker: Account address expecting to convert his tokens to token_addr
    :return: Amount of tokens (within current exchange) sold
    """
    exchangeAddr = DynamicAppCall(factoryAddress(), GetExchange_MethodName, [token_hash])
    return _tokenToTokenOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, invoker, recipient, exchangeAddr)


def tokenToExchangeSwapInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, exchange_hash, invoker):
    """
    Convert token1 within current exchange to another token2 supported within exchange_addr and transfer token2 to invoker with conditions:
    1. tokens_sold amount of token1 will be sold out
    2. both exchanges supporting token1 and token2 were created by the same factory
    3. the bought amount of token2 should be no less than min_tokens_bought
    4. the converted ont amount from selling tokens_sold amount of token1 should be no less than min_ont_bought
        min_ont_bought means how many ont at minimum we expect to use to purchase token2
    5. tx can no long be executed after deadline

    :param tokens_sold: Amount of token sold
    :param min_tokens_bought: Minimum tokens of token_addr purchased
    :param min_ontd_bought: Minimum ont purchased as intermediary
    :param deadline: Time after which this tx can no longer be executed
    :param exchange_hash: Contract hash of exchange for the token being purchased
    :param invoker: Account address expecting to convert his tokens to exchange_addr.token
    :return: Amount of tokens (exchange_addr.token) bought
    """
    return _tokenToTokenInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, invoker, invoker, bytearray_reverse(exchange_hash))

def tokenToExchangeTransferInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, recipient, exchange_hash, invoker):
    """
    Convert token1 within current exchange to another token2 supported within exchange_addr and transfer token2 to recipient with conditions:
    1. tokens_sold amount of token1 will be sold out
    2. both exchanges supporting token1 and token2 were created by the same factory
    3. the bought amount of token2 should be no less than min_tokens_bought
    4. the converted ont amount from selling tokens_sold amount of token1 should be no less than min_ont_bought
        min_ont_bought means how many ont at minimum user expects to use to purchase token2
    5. tx can no long be executed after deadline

    :param tokens_sold: Amount of token sold
    :param min_tokens_bought: Minimum tokens of token_addr purchased
    :param min_ont_bought: Minimum ont purchased as intermediary
    :param deadline: Time after which this tx can no longer be executed
    :param recipient: Address that receive output token_addr
    :param exchange_hash: Contract hash of exchange for the token being purchased
    :param invoker: Account address expecting to convert his tokens to exchange_addr.token
    :return: Amount of tokens (exchange_addr.token) bought
    """
    assert (recipient != GetExecutingScriptHash())
    return _tokenToTokenInput(tokens_sold, min_tokens_bought, min_ontd_bought, deadline, invoker, recipient, bytearray_reverse(exchange_hash))


def tokenToExchangeSwapOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, exchange_hash, invoker):
    """
    Convert some token1 within current exchange to tokens_bought of another token2 supported within exchange_addr
    and transfer tokens_bought amount of token2 to invoker with conditions:
    1. user expects to purchase and acquire tokens_bought amount of token2
    2. both exchanges supporting token1 and token2 were created by the same factory
    3. the sold amount of token1 should be no more than max_tokens_sold
    4. the converted ont amount from purchasing tokens_sold amount of token2 should be no more than max_ont_sold
        max_ont_sold means how many ont at maximum user bears to use to purchase token2
    5. tx can no long be executed after deadline

    :param tokens_bought: Exact amount of tokens (exchange_addr.token) bought user expects to purchase
    :param max_tokens_sold: Maximum tokens (self.token) sold
    :param max_ont_sold: Maximum ont purchased as intermediary
    :param deadline: Time after which this tx can no longer be executed
    :param exchange_hash: Contract hash of exchange for the token being purchased
    :param invoker: Account address expecting to convert his tokens to exchange_addr.token
    :return: Amount of tokens (self.token) sold
    """
    return _tokenToTokenOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, invoker, invoker, bytearray_reverse(exchange_hash))

def tokenToExchangeTransferOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, recipient, exchange_hash, invoker):
    """
    Convert some token1 within current exchange to tokens_bought of another token2 supported within exchange_addr
    and transfer tokens_bought amount of token2 to invoker with conditions:
    1. user expects to purchase and acquire tokens_bought amount of token2
    2. both exchanges supporting token1 and token2 were created by the same factory
    3. the sold amount of token1 should be no more than max_tokens_sold
    4. the converted ont amount from purchasing tokens_sold amount of token2 should be no more than max_ont_sold
        max_ont_sold means how many ont at maximum user bears to use to purchase token2
    5. tx can no long be executed after deadline

    :param tokens_bought: Exact amount of tokens (exchange_addr.token) bought user expects to purchase
    :param max_tokens_sold: Maximum tokens (self.token) sold
    :param max_ont_sold: Maximum ont purchased as intermediary
    :param deadline: Time after which this tx can no longer be executed
    :param recipient: The address receives tokens_bought amount of exchange_addr.token
    :param exchange_hash: Address of exchange for the token being purchased
    :param invoker: Account address expecting to convert his tokens to exchange_addr.token
    :return: Amount of tokens (self.token) sold
    """
    assert (recipient != GetExecutingScriptHash())
    return _tokenToTokenOutput(tokens_bought, max_tokens_sold, max_ontd_sold, deadline, invoker, recipient, bytearray_reverse(exchange_hash))


def getOntToTokenInputPrice(ontd_sold):
    """
    Calculate how many tokens user can get if he provides an exact input ont
    :param ont_sold: Amount of ont sold
    :return: Amount of tokens that can be bought with ont_sold amount of ont
    """
    assert (ontd_sold > 0)
    # Obtain the token and native asset balance of contract
    tokenHash = tokenAddress()
    self = GetExecutingScriptHash()
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    # Calculate how many token we will get if we provide ont_sold amount of native asset
    return _getInputPrice(ontd_sold, ontdReserve, tokenReserve)

def getOntToTokenOutputPrice(tokens_bought):
    """
    Calculate how many ont user should provide to get tokens_bought amount of tokens
    :param tokens_bought: Amount of tokens bought
    :return: Amount of ont needed to buy output tokens
    """
    assert (tokens_bought > 0)
    # Obtain the token and native asset balance of contract
    tokenHash = tokenAddress()
    self = GetExecutingScriptHash()
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    # Calculate how many native asset we have to pay to acquire tokens_bought amount of tokens
    return _getOutputPrice(tokens_bought, ontdReserve, tokenReserve)

def getTokenToOntInputPrice(tokens_sold):
    """
    Calculate how many ont user can get if he sells tokens_sold amount of tokens
    :param tokens_sold: Amount of tokens sold
    :return: Amount of ont that can be used to purchase tokens_sold amount of tokens
    """
    assert (tokens_sold > 0)
    # Obtain the token and native asset balance of contract
    tokenHash = tokenAddress()
    self = GetExecutingScriptHash()
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    return _getInputPrice(tokens_sold, tokenReserve, ontdReserve)

def getTokenToOntOutputPrice(ont_bought):
    """
    Calculate how many tokens use should provide to get ont_bought amount of ont
    :param ont_bought: Amount of output ont
    :return: Amount of tokens needed to buy output ont
    """
    assert (ont_bought > 0)
    # Obtain the token and native asset balance of contract
    tokenHash = tokenAddress()
    self = GetExecutingScriptHash()
    tokenReserve = DynamicAppCall(tokenHash, BalanceOf_MethodName, [self])
    ontdReserve = DynamicAppCall(ONTD_ADDRESS, BalanceOf_MethodName, [self])
    return _getOutputPrice(ont_bought, tokenReserve, ontdReserve)


def _getInputPrice(input_amount, input_reserve, output_reserve):
    """
    Suppose, we want to use input_amount of token1 to exchange for token2 considering current contract balances:
    token1 -> input_reserve, token2 -> output_reserve, and this function calculates how many token2 we will
    get.
    1. Parameter definition: input_amount -> ia, input_reserve -> ir, output_reserve -> or, returned value -> oa
    2. The logic gives us the constrain:
            ir * or = [ir + ia * (1 - fee)] * (or - oa)
    3. Conclusion:
            oa = ia * (1 - fee) * or / [ir + ia * (1 - fee)]
    :param input_amount:
    :param input_reserve:
    :param output_reserve:
    :return:
    """
    assert (input_reserve > 0 and output_reserve > 0)
    inputAmountWithFee = input_amount * 9975
    numerator = inputAmountWithFee * output_reserve
    denominator = input_reserve * 10000 + inputAmountWithFee
    return numerator / denominator

def _getOutputPrice(output_amount, input_reserve, output_reserve):
    """
    Suppose, we want to obtain output_amount of token2 considering current contract balances:
    token1 -> input_reserve, token2 -> output_reserve, and this function calculates how many
    token1 we need to provide for exchanging in order to get exact output_amount of token2 finally.
    1. Parameter definition: output_amount -> oa, input_reserve -> ir, output_reserve -> or, returned value -> ia
    2. The logic gives us the constrain:
            ir * or = [ir + ia * (1 - fee)] * (or - oa)
    3. Conclusion:
            ia = ir * oa / [(or - oa) * (1 - fee)] + 1
    4. optimal conclusion:
            ia = [ir * oa + (or - oa) * (1 - fee) -1 ] / [(or - oa) * (1 - fee)]
    :param input_amount:
    :param input_reserve:
    :param output_reserve:
    :return:
    """
    assert (input_reserve > 0 and output_reserve > 0 and output_reserve > output_amount)
    numerator = input_reserve * output_amount * 10000
    denominator = (output_reserve - output_amount) * 9975
    return (numerator + denominator - 1) / denominator



def tokenAddress():
    return Get(GetContext(), TOKEN_KEY)


def factoryAddress():
    return Get(GetContext(), FACTORY_KEY)


# The below implementation follows OEP4 Protocol
# https://github.com/ontio/OEPs/blob/master/OEPS/OEP-4.mediawiki
def name():
    """
    :return: name of the token
    """
    return NAME


def symbol():
    """
    :return: symbol of the token
    """
    return SYMBOL


def decimals():
    """
    :return: the decimals of the token
    """
    return DECIMALS


def totalSupply():
    """
    :return: the total supply of the token
    """
    return Get(GetContext(), TOTAL_SUPPLY_KEY)

def balanceOf(owner):
    return Get(GetContext(), concat(BALANCE_PREFIX, owner))


def transfer(from_acct, to_acct, amount):
    """
    Transfer amount of tokens from from_acct to to_acct
    :param from_acct: the account from which the amount of tokens will be transferred
    :param to_acct: the account to which the amount of tokens will be transferred
    :param amount: the amount of the tokens to be transferred, >= 0
    :return: True means success, False or raising exception means failure.
    """
    assert (len(to_acct) == 20 and len(from_acct) == 20)
    if CheckWitness(from_acct) == False or amount < 0:
        return False
    fromKey = concat(BALANCE_PREFIX,from_acct)
    fromBalance = Get(GetContext(),fromKey)
    if amount > fromBalance:
        return False
    if amount == fromBalance:
        Delete(GetContext(),fromKey)
    else:
        Put(GetContext(), fromKey, fromBalance - amount)
    toKey = concat(BALANCE_PREFIX, to_acct)
    toBalance = Get(GetContext(), toKey)
    Put(GetContext(),toKey, toBalance + amount)

    # Fire event
    TransferEvent(from_acct, to_acct, amount)
    return True


def transferMulti(args):
    """
    :param args: the parameter is an array, containing element like [from, to, amount]
    :return: True means success, False or raising exception means failure.
    """
    for p in args:
        assert (len(p) == 3)
        assert (transfer(p[0], p[1], p[2]))
    return True


def transferFrom(spender, from_acct, to_acct, amount):
    """
    spender spends amount of tokens on the behalf of from_acct, spender makes a transaction of amount of tokens
    from from_acct to to_acct
    :param spender:
    :param from_acct:
    :param to_acct:
    :param amount:
    :return:
    """
    assert (len(spender) == 20 and len(from_acct) == 20 and len(to_acct) == 20)

    if CheckWitness(spender) == False:
        return False

    fromKey = concat(BALANCE_PREFIX, from_acct)
    fromBalance = Get(GetContext(), fromKey)
    if amount > fromBalance or amount < 0:
        return False

    approveKey = concat(concat(APPROVE_PREFIX, from_acct), spender)
    approvedAmount = Get(GetContext(), approveKey)
    toKey = concat(BALANCE_PREFIX,to_acct)

    if amount > approvedAmount:
        return False
    elif amount == approvedAmount:
        Delete(GetContext(), approveKey)
        Put(GetContext(), fromKey, fromBalance - amount)
    else:
        Put(GetContext(), approveKey, approvedAmount - amount)
        Put(GetContext(), fromKey, fromBalance - amount)

    toBalance = Get(GetContext(), toKey)
    Put(GetContext(), toKey, toBalance + amount)
    # Fire event
    TransferEvent(from_acct, to_acct, amount)
    return True


def approve(owner, spender, amount):
    """
    owner allow spender to spend amount of token from owner account
    Note here, the amount should be less than the balance of owner right now.
    :param owner:
    :param spender:
    :param amount: amount>=0
    :return: True means success, False or raising exception means failure.
    """
    assert (len(spender) == 20 and len(owner) == 20)
    if CheckWitness(owner) == False:
        return False
    if amount > balanceOf(owner) or amount < 0:
        return False

    key = concat(concat(APPROVE_PREFIX, owner), spender)
    Put(GetContext(), key, amount)
    # Fire event
    ApprovalEvent(owner, spender, amount)
    return True


def allowance(owner, spender):
    """
    check how many token the spender is allowed to spend from owner account
    :param owner: token owner
    :param spender:  token spender
    :return: the allowed amount of tokens
    """
    return Get(GetContext(), concat(concat(APPROVE_PREFIX, owner), spender))