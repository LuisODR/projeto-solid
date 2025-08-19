Refatoração com SOLID

Este projeto apresenta a refatoração de um sistema bancário em Python aplicando os princípios do **SOLID**.  
Abaixo estão as classes **originais**, o **princípio aplicado** e a **versão refatorada**.

---
```python
## Cliente

### a) Classe Original

class Cliente:
    def __init__(self, nome: str, cpf: str, endereco: str, telefone: str):
        self.nome = nome
        self.cpf = cpf
        self.endereco = endereco
        self.telefone = telefone

    def getInfo(self) -> str:
        return f"{self.nome} (CPF: {self.cpf}, Tel: {self.telefone})"

b) Princípio SOLID Aplicado
Princípio: SRP - Single Responsibility Principle (Responsabilidade Única)

Explicação:
Apenas mantive como entidade simples pois ja tinha apenas uma responsabilidade

c) Classe Refatorada

class Cliente:
    def __init__(self, nome: str, cpf: str, endereco: str, telefone: str):
        self.nome = nome
        self.cpf = cpf
        self.endereco = endereco
        self.telefone = telefone

    def getInfo(self) -> str:
        return f"{self.nome} (CPF: {self.cpf}, Tel: {self.telefone})"

Conta

a) Classe Original

class Conta(ABC):
    def __init__(self, numero: str, cliente: Cliente, tipo: str, saldo: float = 0.0):
        self.numero = numero
        self.cliente = cliente
        self.tipo = tipo
        self.saldo = saldo
        self.transacoes: List[Transacao] = []

    def depositar(self, valor: float):
        ...

    def sacar(self, valor: float):
        ...

    def transferir(self, destino: "Conta", valor: float):
        ...

    def getSaldo(self) -> float:
        return self.saldo

b) Princípio SOLID Aplicado
Princípios:

OCP - Open/Closed Principle: A classe foi desenhada para permitir extensão (ContaCorrente, ContaPoupanca) sem precisar ser modificada

ISP - Interface Segregation Principle: Foram criadas interfaces (Sacavel, Depositavel, Transferivel) pra separar as responsabilidades

LSP - Liskov Substitution Principle: As subclasses podem substituir Conta sem quebrar o sistema

c) Classe Refatorada

class Conta(ABC, Sacavel, Depositavel, Transferivel):
    def __init__(self, numero: str, cliente: Cliente, tipo: str, saldo: float = 0.0):
        self.numero = numero
        self.cliente = cliente
        self.tipo = tipo
        self.saldo = saldo
        self.transacoes: List["Transacao"] = []

    def depositar(self, valor: float):
        if valor <= 0:
            raise ValueError("Depósito deve ser positivo.")
        self.saldo += valor
        self._registrar_transacao(valor, "Depósito")

    def transferir(self, destino: "Conta", valor: float):
        self.sacar(valor)
        destino.depositar(valor)
        self._registrar_transacao(valor, f"Transferência para {destino.numero}")

    def getSaldo(self) -> float:
        return self.saldo

    def _registrar_transacao(self, valor: float, tipo: str):
        self.transacoes.append(Transacao(len(self.transacoes)+1, datetime.now(), valor, tipo))

    @abstractmethod
    def sacar(self, valor: float):
        pass
ContaCorrente
a) Classe Original

class ContaCorrente(Conta):
    def __init__(self, numero: str, cliente: Cliente, limite: float = 500.0, saldo: float = 0.0):
        super().__init__(numero, cliente, "Corrente", saldo)
        self.limite = limite

    def sacar(self, valor: float):
        if valor <= 0:
            raise ValueError("Saque deve ser positivo.")
        if valor > self.saldo + self.limite:
            raise ValueError("Saldo + limite insuficientes.")
        self.saldo -= valor
        self.transacoes.append(Transacao(len(self.transacoes)+1, datetime.now(), -valor, "Saque (CC)"))
b) Princípio SOLID Aplicado
Princípios:

LSP: ContaCorrente respeita o contrato de Conta.

SRP: A lógica de registrar transações foi movida para _registrar_transacao na classe base, assim evita a repetição

c) Classe Refatorada

class ContaCorrente(Conta):
    def __init__(self, numero: str, cliente: Cliente, limite: float = 500.0, saldo: float = 0.0):
        super().__init__(numero, cliente, "Corrente", saldo)
        self.limite = limite

    def sacar(self, valor: float):
        if valor <= 0:
            raise ValueError("Saque deve ser positivo.")
        if valor > self.saldo + self.limite:
            raise ValueError("Saldo + limite insuficientes.")
        self.saldo -= valor
        self._registrar_transacao(-valor, "Saque (CC)")
ContaPoupanca
a) Classe Original

class ContaPoupanca(Conta):
    def __init__(self, numero: str, cliente: Cliente, rendimento: float = 0.01, saldo: float = 0.0):
        super().__init__(numero, cliente, "Poupança", saldo)
        self.rendimento = rendimento
b) Princípio SOLID Aplicado
Princípios:

OCP: Possibilidade de criar novas contas sem alterar Conta

LSP: Substitui Conta sem quebrar o sistema

c) Classe Refatorada

class ContaPoupanca(Conta):
    def __init__(self, numero: str, cliente: Cliente, rendimento: float = 0.01, saldo: float = 0.0):
        super().__init__(numero, cliente, "Poupança", saldo)
        self.rendimento = rendimento

    def sacar(self, valor: float):
        if valor <= 0:
            raise ValueError("Saque deve ser positivo.")
        if valor > self.saldo:
            raise ValueError("Saldo insuficiente.")
        self.saldo -= valor
        self._registrar_transacao(-valor, "Saque (Poupança)")
Transacao
a) Classe Original

class Transacao:
    def __init__(self, id: int, data: datetime, valor: float, tipo: str):
        self.id = id
        self.data = data
        self.valor = valor
        self.tipo = tipo

    def registrar(self):
        return f"{self.data.strftime('%d/%m/%Y %H:%M')} - {self.tipo}: R$ {self.valor:.2f}"
b) Princípio SOLID Aplicado
Princípio: SRP

Explicação:
Antes, Transacao tinha duas responsabilidades: armazenar dados e formatar o extrato.
Agora, ela guarda apenas dados. A geração do extrato foi movida para ExtratoService

c) Classe Refatorada

class Transacao:
    def __init__(self, id: int, data: datetime, valor: float, tipo: str):
        self.id = id
        self.data = data
        self.valor = valor
        self.tipo = tipo
ExtratoService (Nova Classe)
a) Classe Original
Não existia

b) Princípio SOLID Aplicado
Princípio: SRP

Explicação:
Tirei a responsabilidade de gerar relatórios de Transacao e centralizei em um serviço específico

c) Classe Criada

class ExtratoService:
    @staticmethod
    def gerar(conta: Conta) -> str:
        return "\n".join(
            f"{t.data.strftime('%d/%m/%Y %H:%M')} - {t.tipo}: R$ {t.valor:.2f}"
            for t in conta.transacoes
        )
Banco
a) Classe Original

class Banco:
    def __init__(self, nome: str):
        self.nome = nome
        self.contas: List[Conta] = []

    def criarConta(self, conta: Conta):
        self.contas.append(conta)

    def fecharConta(self, numero: str):
        self.contas = [c for c in self.contas if c.numero != numero]

    def listarContas(self):
        for conta in self.contas:
            print(conta)
b) Princípio SOLID Aplicado
Princípio: DIP - Dependency Inversion Principle

Explicação:
O Banco não pode depender de implementações fixas, mas sim de abstrações, ou seja agora interage com contas polimorficamente

c) Classe Refatorada

class Banco:
    def __init__(self, nome: str):
        self.nome = nome
        self.contas: List[Conta] = []

    def criarConta(self, conta: Conta):
        self.contas.append(conta)

    def fecharConta(self, numero: str):
        self.contas = [c for c in self.contas if c.numero != numero]

    def listarContas(self):
        for conta in self.contas:
            print(conta)
