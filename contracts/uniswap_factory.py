OntCversion = '2.0.0'
"""
This is the factory contract for creating standard uniswap exchange smart contract on Ontology
"""
from ontology.libont import byte2int, hexstring2bytes, hexstring2address, bytes2hexstring
from ontology.interop.Ontology.Native import Invoke
from ontology.interop.Ontology.Contract import Migrate, Create, GetScript
from ontology.interop.System.Action import RegisterAction
from ontology.interop.Ontology.Runtime import Base58ToAddress, GetCurrentBlockHash
from ontology.interop.System.Storage import Put, GetContext, Get, Delete
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash
from ontology.interop.System.Runtime import CheckWitness, Notify, Serialize, Deserialize, GetTime
from ontology.builtins import concat, state
from ontology.libont import bytearray_reverse, AddressFromVmCode
from ontology.interop.System.App import RegisterAppCall, DynamicAppCall

ZERO_ADDRESS = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
BALANCE_PREFIX = bytearray(b'\x01')
APPROVE_PREFIX = b'\x02'

EXCHANGE_TEMPLATE_KEY = 'template'
TOKEN_COUNT_KEY = "count"
TOKEN_TO_EXCHANGE_PREFIX = "tokenToEx"
EXCHANGE_TO_TOKEN_PREFIX = "ExToToken"
ID_TO_TOKEN_PREFIX = "IdToToken"

IntitializeFactoryEvent = RegisterAction("InitializeFactory", "templateScriptHash")
NewExchangeEvent = RegisterAction("NewExchange", "token_addr", "exchange_addr")

def Main(operation, args):
    if operation == "intitializeFactory":
        assert (len(args) == 1)
        template = args[0]
        return intitializeFactory(template)
    if operation == "createExchange":
        assert (len(args) == 1)
        token = args[0]
        return createExchange(token)
    if operation == "getExchange":
        assert (len(args) == 1)
        token = args[0]
        return getExchange(token)
    if operation == "getToken":
        assert (len(args) == 1)
        exchange = args[0]
        return getToken(exchange)
    if operation == "getTokenWithId":
        assert (len(args) == 1)
        token_id = args[0]
        return getTokenWithId(token_id)
    assert (False)


def intitializeFactory(template):
    assert (len(Get(GetContext(), EXCHANGE_TEMPLATE_KEY)) == 0)
    Put(GetContext(), EXCHANGE_TEMPLATE_KEY, template)
    # Fire template hash
    IntitializeFactoryEvent(AddressFromVmCode(template))
    return True


def createExchange(token_hash):
    # Ensure token is a contract with nonzero contract hash
    assert (token_hash != ZERO_ADDRESS and len(token_hash) == 20)

    # Ensure templateCode existgetExchange
    templateScript = Get(GetContext(), EXCHANGE_TEMPLATE_KEY)
    assert (len(templateScript) > 0)
    # Make sure the token_hash has not been used to create exchange before
    assert (len(getExchange(token_hash)) == 0)

    tokenCount = Get(GetContext(), TOKEN_COUNT_KEY)

    # Append unused byte code to avm code to produce different contract hash, yet same executable opcode
    newTokenCount = tokenCount + 1
    templateScript = concat(templateScript, concat(concat(concat(GetExecutingScriptHash(), GetCurrentBlockHash()), GetTime()), newTokenCount))

    # Deploy replica contract
    assert (Create(templateScript, True, "uniswap_exchange", "1.0", "uniswap_factory", "email", "uniswap_exchange contract created by uniswap_factory contract"))

    # Invoke the newly deployed contract to set up the token exchange pair
    exchangeHash = AddressFromVmCode(templateScript)
    exchangeAddr = bytearray_reverse(exchangeHash)
    tokenAddr = bytearray_reverse(token_hash)
    assert (DynamicAppCall(exchangeAddr, "setup", [tokenAddr, GetExecutingScriptHash()]))

    # Store the map between token and exchange contract hash
    Put(GetContext(), concat(TOKEN_TO_EXCHANGE_PREFIX, token_hash), exchangeAddr)
    Put(GetContext(), concat(EXCHANGE_TO_TOKEN_PREFIX, exchangeHash), tokenAddr)

    # Add the token count
    Put(GetContext(), TOKEN_COUNT_KEY, newTokenCount)

    # Map token with token id
    Put(GetContext(), concat(ID_TO_TOKEN_PREFIX, newTokenCount), tokenAddr)

    # Fire the event
    NewExchangeEvent(tokenAddr, exchangeAddr)
    return True


def getExchange(token_hash):
    return Get(GetContext(), concat(TOKEN_TO_EXCHANGE_PREFIX, token_hash))


def getToken(exchange_hash):
    return Get(GetContext(), concat(EXCHANGE_TO_TOKEN_PREFIX, exchange_hash))

def getTokenWithId(token_id):
    return Get(GetContext(), concat(ID_TO_TOKEN_PREFIX, token_id))