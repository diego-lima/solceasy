var abi = <<abi|O Application Binary Interface (ABI) do seu contrato>>
var bin = <<bin|O BIN do seu contrato>>
var config = {
                from: <<from_address|O endereço que irá lançar o contrato|web3.eth.accounts[0]>>,
                data: bin,
                gas: <<gas|Quanto gas está disposto a pagar pela transação|4700000>>
    };
var callback = function(e, contract){
	console.log(e, contract);
	if (typeof contract.address !== 'undefined') {
         console.log('Contrato minerado! endereço: ' + contract.address);
    }

};

var contract_factory = web3.eth.contract(abi);
var <<nome_contrato|O nome do seu contrato|contract>> = contract_factory.new(config, callback);
