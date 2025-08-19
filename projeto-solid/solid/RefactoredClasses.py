from datetime import datetime
from typing import List, Protocol
from abc import ABC, abstractmethod


# SRP: Cliente só representa dados
class Cliente:
    def __init__(self, nome: str, cpf: str, endereco: str, telefone: str):
        self.nome = nome
        self.cpf = cpf
        self.endereco = endereco
        self.telefone = telefone

    def getInfo(self) -> str:
        return f"{self.nome} (CPF: {self.cpf}, Tel: {self.telefone})"


# ISP: Interfaces separadas
class Sacavel(Protocol):
    def sacar(self, valor: float): ...


class Depositavel(Protocol):
    def depositar(self, valor: float): ...


class Transferivel(Protocol):
    def transferir(self, destino: "Conta", valor: float): ...


# OCP e LSP: Conta é a base do programa
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

    def __str__(self):
        return f"Conta {self.numero} ({self.tipo}) - Cliente: {self.cliente.nome} - Saldo: R$ {self.saldo:.2f}"


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


# SRP: Transação só guarda dados
class Transacao:
    def __init__(self, id: int, data: datetime, valor: float, tipo: str):
        self.id = id
        self.data = data
        self.valor = valor
        self.tipo = tipo


# SRP: Serviço de extrato separado ----------------
class ExtratoService:
    @staticmethod
    def gerar(conta: Conta) -> str:
        return "\n".join(
            f"{t.data.strftime('%d/%m/%Y %H:%M')} - {t.tipo}: R$ {t.valor:.2f}"
            for t in conta.transacoes
        )


# Banco depende de abstração
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


def criar_dados_mock():
    banco = Banco("Banco")

    cliente1 = Cliente("João Silva", "12345678900", "Rua A", "9999-9999")
    cliente2 = Cliente("Maria Oliveira", "98765432100", "Rua B", "8888-8888")

    conta1 = ContaCorrente("001", cliente1, limite=1000, saldo=500)
    conta2 = ContaPoupanca("002", cliente2, rendimento=0.02, saldo=1500)

    banco.criarConta(conta1)
    banco.criarConta(conta2)

    return banco, [cliente1, cliente2]


if __name__ == "__main__":
    banco, clientes = criar_dados_mock()
    banco.listarContas()

    banco.contas[0].depositar(300)
    banco.contas[1].sacar(200)
    banco.contas[0].transferir(banco.contas[1], 150)

    banco.listarContas()

    print("\nExtrato da conta 001:")
    print(ExtratoService.gerar(banco.contas[0]))
