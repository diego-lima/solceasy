import argparse
import pathlib
import re
from os import path
from os.path import isfile
from subprocess import CalledProcessError
from subprocess import check_output as terminal

# Serve para poder testar se um objeto é do tipo match
SRE_MATCH_TYPE = type(re.match("", ""))

#
BASE_DIR = str(pathlib.Path(__file__).resolve().parent)
DEFAULT_TEMPLATE = path.join(BASE_DIR, "templates/template.js")
#
SOLC = terminal('which solc'.split()).strip().decode()

assert isfile(DEFAULT_TEMPLATE), f'{DEFAULT_TEMPLATE} não encontrado'
assert isfile(SOLC), f'{SOLC} não encontrado'


class JSTemplate:
    """
    Serve para utilizar arquivos de texto como template para gerar um arquivo válido *.js
    que instancia um contrato no console geth automaticamente.

    Os templates contêm código JS válido, exceto pelo fato de terem "placeholders" que irão
    ser removidos para serem substituídos por alguma informação fornecida pelo usuário.

    Exemplo:
    var minha_variavel = <<nome_da_variavel|descrição da variável|valor_default>>

    Os placeholders são identificados pela região entre << >>
    Seu conteúdo é separado por barras verticais.
    O primeiro valor é o nome da variável do ponto de vista do template.
    O segundo valor é a descrição daquela variável
    O terceiro valor é um valor padrão, que será colocado em caso default.
    """

    # O conteúdo lido do template
    template_string = None
    # Lista de variáveis encontradas no template
    variaveis = None

    def __init__(self, template):
        with open(template) as arquivo:
            self.template_string = arquivo.read()

        self.carregar_dados(self.template_string)

    def carregar_dados(self, template_string):
        """
        Lê o conteúdo da string template_string, procurando por variáveis.
        """
        self.variaveis = list()

        # Vamos pegar qualquer texto entre << >>
        regex = re.compile("<<.+>>")

        for variavel in regex.finditer(template_string):
            self.variaveis.append(Variavel(variavel))

    def find(self, nome):
        """
        Procura por uma variável a partir do seu nome.
        """
        if self.variaveis:
            for var in self.variaveis:
                if var.nome == nome:
                    return var

        return None

    @property
    def pendencias(self):
        """
        Retorna uma lista de variáveis com configuração pendente
        """
        pendencias = []
        for variavel in self.variaveis:
            if not variavel.status:
                pendencias.append(variavel)
        return pendencias

    def compilar(self):
        """
        Retorna a string do arquivo compilado, ou seja, com as variáveis substituídas por seus valores.
        """
        pendencias = self.pendencias
        if pendencias:
            raise Exception(
                "Existem variáveis mal configuradas: %s\n Veja se todas variáveis do template tem valores" % pendencias
            )

        template_out = self.template_string

        for var in self.variaveis:
            template_out = template_out.replace(
                var.match.group(), var.valor, 1)

        return template_out

    def __getattr__(self, key):
        """
        Serve para eu poder pegar uma variável fazendo
        > jst = JSTemplate(templates/template.js)
        > jst.bin
        onde bin é uma das variáveis dentro de jst.variaveis.
        """
        variavel = self.find(key)
        if variavel:
            return variavel
        else:
            return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        """
        Serve para eu poder setar uma variável fazendo
        > jst = JSTemplate(templates/template.js)
        > jst.bin = "foo"
        onde bin é uma das variáveis dentro de jst.variaveis.
        """
        variavel = self.find(key)
        if variavel:
            variavel.valor = value
        else:
            super().__setattr__(key, value)

    def __dir__(self):
        """
        Serve para fazer os nomes das variáveis aparecerem se alguem fizer
        > dir(jst)
        """
        return [var.nome for var in self.variaveis] + [x for x in super().__dir__()]


class Variavel:
    """
    Serve para abstrair a funcionalidade da variável encontrada no template.

    Vai receber uma string no formato da expressão regular "<<.+>>", e irá ler seu nome, descrição e valor padrão.
    """

    # O nome da variavel
    nome_contrato = None
    # O valor padrão da variável
    default = None
    # A descrição da variável
    descricao = None
    # O objeto SRE_MATCH_TYPE que foi passado
    match = None

    # O valor atual da variável
    _value = None

    def __init__(self, variavel):

        if not isinstance(variavel, SRE_MATCH_TYPE):
            raise Exception("Variável '%s' precisa ser _sre.SRE_Match, e não %s" % (
                variavel, type(variavel)))

        self.match = variavel
        # Tirando os << >> e dando split
        valor = variavel.group()[2:-2].split("|")

        try:
            self.nome = valor[0]
        except IndexError:
            raise Exception("Toda variavel precisa de um nome!")

        if len(valor) >= 2:
            self.descricao = valor[1]

        if len(valor) >= 3:
            self.default = valor[2]

    @property
    def valor(self):
        """
        Se não houver valor, eu retornarei o valor default.
        """

        return self.default if self._value is None else self._value

    @valor.setter
    def valor(self, value):
        """
        Setter da property valor
        """
        self._value = value

    @property
    def status(self):
        """
        Avisa se a variável foi configurada corretamente
        """
        return self.valor is not None

    def __repr__(self):
        return self.nome


def main():
    """
    Script de compilação e lançamento de contratos em arquivos *.sol
    """
    parser = argparse.ArgumentParser(
        description='Script de compilação e lançamento de contratos em arquivos *.sol')
    parser.add_argument("contrato", help="O arquivo *.sol que será compilado")
    parser.add_argument("-t", "--template", help="O arquivo de template *.js que será usado como base para lançamento",
                        default=DEFAULT_TEMPLATE)
    parser.add_argument("-m", "--manter", help="Se os arquivos *.bin e *.abi devem ser mantidos ou não",
                        action="store_true")

    args = parser.parse_args()

    if not isfile(args.contrato):
        raise Exception("Arquivo %s não enontrado." % args.contrato)

    filepath = pathlib.PurePath(args.contrato)
    base_dir = filepath.parent

    # Comando de disparar o compilador passando o arquivo
    comando = f"{SOLC} -o {base_dir} --bin --abi {filepath} --overwrite"

    try:
        terminal(comando.split(" "))
    except CalledProcessError:
        print('Verifique erros de saída.')
        exit()

    name = filepath.name.split('.')[0]
    abi = path.join(base_dir, f"{name}.abi")
    bin = path.join(base_dir, f"{name}.bin")
    js = path.join(base_dir, f"{name}.js")

    if not isfile(abi):
        print("Verifique se o nome do arquivo é igual ao nome do contrato declarado dentro dele.")
        exit()

    conteudo_abi = open(abi)
    conteudo_bin = open(bin)

    jst = JSTemplate(args.template)

    jst.abi = conteudo_abi.read()
    jst.bin = '"0x%s"' % conteudo_bin.read()

    conteudo_abi.close()
    conteudo_bin.close()

    conteudo_js = open(js, "w")

    conteudo_js.write(jst.compilar())

    conteudo_js.close()

    if not args.manter:
        # Apagar os arquivos *.abi e *.bin
        comando = f"rm {abi} {bin}"
        terminal(comando.split(" "))


if __name__ == "__main__":
    main()
