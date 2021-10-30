import setuptools

long_description = """
Funciona assim: você salva o código na linguagem Solidity de um smart
contract(exemplo: MeuContrato) num arquivo MeuContrato.sol.

Esse utilitário irá pegar esse contrato, compilar, gerando o BIN e o ABI, e
irá gerar um arquivo MeuContrato.js pronto para ser executado, que irá lançar
o contrato a partir de um console geth.

Rode python3 pythonsolcbuild.py --help para informações.
"""

setuptools.setup(
    name='solceasy',
    version='0.2',
    author="Diego Lima",
    author_email="ddddiegolima@gmail.com",
    description="Um utilitário para compilação e deploy de contratos ethereum",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/diego-lima/solceasy",
    scripts=['bin/solceasy'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
    ],
)
