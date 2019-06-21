# solcbuild
Um utilitário para compilação e deploy de contratos ethereum "from scratch"

Funciona assim: você salva o código na linguagem Solidity de um smart contract(exemplo: MeuContrato) num arquivo MeuContrato.sol.

Esse utilitário irá pegar esse contrato, compilar, gerando o BIN e o ABI, e irá gerar um arquivo MeuContrato.js pronto para ser executado, que irá lançar o contrato a partir de um console geth.

Rode `python3 pythonsolcbuild.py --help` para informações.
