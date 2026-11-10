"""Modelo de uma orientação do Citizen Assist AI"""


class Orientacao:
    CAMPOS = (
        "id", "categoria", "titulo", "palavras_chave", "resposta",
        "documentos", "onde", "fonte", "verificado_em"
    )

    def __init__(self, dados):
        faltando = [campo for campo in self.CAMPOS if campo not in dados]
        if faltando:
            raise ValueError(f"Campos ausentes: {', '.join(faltando)}")

        self.id = dados["id"]
        self.categoria = dados["categoria"]
        self.titulo = dados["titulo"]
        self.palavras_chave = dados["palavras_chave"]
        self.resposta = dados["resposta"]
        self.documentos = dados["documentos"]
        self.onde = dados["onde"]
        self.fonte = dados["fonte"]
        self.verificado_em = dados["verificado_em"]

        if not isinstance(self.id, int):
            raise ValueError("O id deve ser inteiro")
        if not isinstance(self.palavras_chave, list) or len(self.palavras_chave) < 3:
            raise ValueError("Cada orientação precisa de pelo menos 3 palavras-chave")
        if not isinstance(self.documentos, list):
            raise ValueError("O campo documentos deve ser uma lista")
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em"):
            if not isinstance(getattr(self, campo), str) or not getattr(self, campo).strip():
                raise ValueError(f"Campo inválido: {campo}")
        if not all(isinstance(p, str) and p.strip() for p in self.palavras_chave):
            raise ValueError("Palavras-chave inválidas")
        if not all(isinstance(p, str) and p.strip() for p in self.documentos):
            raise ValueError("Documentos inválidos")

    def exibir(self):
        print(f"\n=== {self.titulo} [{self.categoria}] ===")
        print(self.resposta)
        print("\nDocumentos / requisitos informados:")
        if self.documentos:
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("  - Nenhum documento informado na orientação")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte}")
        print(f"Verificado em: {self.verificado_em}")
        print("Aviso: este assistente NÃO é um canal oficial e não garante benefícios ou direitos\n")


