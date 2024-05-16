from abc import ABC, abstractclassmethod, abstractproperty

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_contas(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "001"
        self._cliente = cliente
        self._historico = Historico()
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if (valor > self.saldo):
            print("Operação falhou! Você não tem saldo suficiente.")
            return False
        
        elif (valor > 0):
            self._saldo -= valor
            print("Operação concluída com sucesso!")
            return True
        
        else:
            print("Operação falhou! O valor informado é inválido.")
            return False

    def depositar(self, valor):
        if (valor > 0):
            self._saldo += valor
            print("Operação concluída com sucesso!")
            return True
        
        else:
            print("Operação falhou! O valor informado é inválido.")
            return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

        if (valor > self.limite):
            print("Operação falhou! O valor de saque excede o limite.")
            return False
        
        elif (numero_saques >= self.limite_saques):
            print("Operação falhou! Número máximo de saques excedido..")
            return False
        
        else:
            return super().sacar(valor)
    
    def __str__(self):
        return f"""
Agência: {self.agencia}
C/C: {self.numero}
Titular: {self.cliente.nome}
"""

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @property
    @abstractclassmethod
    def registrar(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if (conta.depositar(self.valor)):
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        if (conta.sacar(self.valor)):
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """\n
-------------------- MENU --------------------
    [1] Depositar
    [2] Sacar
    [3] Extrato
    [4] Novo Usuário
    [5] Nova Conta
    [6] Listar Contas
    [0] Sair
    => """
    opcao = input(menu)
    print("----------------------------------------------")
    return opcao

def filtrar_cliente(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui conta!")
        return
    
    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]

def depositar(usuarios):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, usuarios)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def sacar(usuarios):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, usuarios)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(usuarios):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, usuarios)

    if not cliente:
        print("Cliente não encontrado!")
        return
    
    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return
    
    print("\n---------------- EXTRATO ----------------")
    transacoes = conta.historico.transacoes
    extrato = ""

    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\nR${transacao['valor']:.2f}"
    print(extrato)
    print(f"\nSaldo: R$ {conta.saldo:.2f}")
    print("-------------------------------------------")

def criar_usuario(usuarios):
    cpf = input("Informe o CPF: ")
    cliente = filtrar_cliente(cpf, usuarios)

    if cliente:
        print("Já existe cliente com esse CPF!")
        return
    
    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nº - bairro - cidade/sigla estado): ")
    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    usuarios.append(cliente)

    print("Usuário criando com sucesso!")

def criar_conta(numero_conta, usuarios, contas):
    cpf = input("Informe o CPF do Usuário: ")
    cliente = filtrar_cliente(cpf, usuarios)

    if not cliente:
        print("Cliente não encontrado, fluxo de criação de conta encerrado!!")
        return
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("Conta criada com sucesso!")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(str(conta))

def principal():
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1": #Depositar
            depositar(usuarios)

        elif opcao == "2": #Sacar
            sacar(usuarios)
        
        elif opcao == "3": #Extrato
            exibir_extrato(usuarios)
        
        elif opcao == "4": #Novo Usuário
            criar_usuario(usuarios)
        
        elif opcao == "5": #Nova Conta
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, usuarios, contas)
        
        elif opcao == "6": #Listar Contas
            listar_contas(contas)

        elif opcao == "0": #Sair
            break
        
        else:
            print("Operação inválida, por favor selecione a operação desejada.")

principal()