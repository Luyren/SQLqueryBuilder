from tkinter import filedialog
import json

class tabelaSQL:
	"""Classe contendo as tabelas documentadas."""
	def __init__(self, id, source):
		self.id = id
		self.source = source
		self.display = source["nomeDisplay"]
		self.alias = source["alias"]
		self.descricao = source["descricao"]
		self.conexoes = source["conexoes"]#ao verificar, usar isinstance(x, List)
		self.campos = dict()
		for i, j in source["campos"].items(): 
			self.campos[i] = campo(self, i, j)
	def __str__(self):
		"""Print a tabela, seus campos e conexões."""
		output = f"====\nNome:{self.display}\nid:{self.id}\nDescrição:{self.descricao}\nCampos:"
		newLine = ""
		for i in self.campos:
			if bool(newLine):
				newLine += ","
			newLine += f"- {i.id}"
		output += f"{newLine}\nConexões:\n"
		newLine = ""
		for i in self.conexoes:
			if bool(newLine):
				newLine += ","
			newLine += f"- {i}"
		output += newLine
		return output
	def getAlias(self):
		"""Retorna 'nome AS alias'."""
		return f"{self.id} AS {self.alias}"
class instanceTabela(tabelaSQL):
	"""Instância de uma tabela quando incluída no extrator."""
	def __init__(self, parent, count):
		super().__init__(parent.id, parent.source)
		self.camposAtivos = dict()
		self.join = ""
		self.conexao = ""
		self.conexaoAtiva = ""
		self.conexaoChaveSelf = ""
		self.conexaoChaveOther = ""
		self.count = count
		if count > 0:
			self.alias += str(count)
	def getAlias(self):
		"""Retorna 'nome AS alias' com o count."""
		if self.count > 0:
			return f"{self.id} AS {self.alias}{self.count}"
		else:
			return f"{self.id} AS {self.alias}"
	def salvarTabela(self):
		"""Retorna os dados da tabela para o modelo de extração."""
		output = dict()
		output["id"] = self.id
		output["count"] = self.count
		output["join"] = self.join
		output["conexao"] = self.conexao
		output["conexaoAtiva"] = self.conexaoAtiva
		output["conexaoChaveSelf"] = self.conexaoChaveSelf
		output["conexaoChaveOther"] = self.conexaoChaveOther
		output["camposAtivos"] = dict()
		for i, j in self.camposAtivos.items():
			#i é o ID da tabela
			output["camposAtivos"][i] = j.salvarCampo()
		return output
class campo:
	"""Campo de uma tabela SQL."""
	def __init__(self, parent: tabelaSQL, id, alias):
		self.parent = parent #tabela de origem
		self.id = id
		self.alias = alias
		self.parentTable = parent
		self.parentAlias = parent.alias
	def __str__(self):
		return f"{self.parentAlias}.{self.id}"
	def getUsedName(self):
		if self.alias == "":
			return f"{self.parent.alias}.{self.id}"
		else:
			return f"{self.alias}"
	def getSelect(self):
		"Retorna o campo e formata para SELECT SQL, com tabela de origem e alias."
		output = str(self)
		if not self.alias == "":
			output += f" AS '{self.alias}'"
		return output
class instanceCampo(campo):
	"""Instância de um campo de tabela Benner, para receber valor de prioridade e group by"""
	def __init__(self, origem):
		super().__init__(origem.parent, origem.id, origem.alias)
		self.prioridade = 0
		self.ordenar = 0
		self.filtro = ""
		self.filtroAlvo = ""
	def getFiltro(self):
		return f"{self.getUsedName()} {self.filtro} {self.filtroAlvo}"
	def salvarCampo(self):
		output = dict()
		output["id"] = self.id
		output["prioridade"] = self.prioridade
		output["ordenar"] = self.ordenar
		output["filtro"] = self.filtro
		output["filtroAlvo"] = self.filtroAlvo
		return output	
class extrator:
	"""Classe contendo dados para montar um extrator SQL."""
	def __init__(self):
		self.tabelas = dict() #Cada item é o objeto tabelaBenner, chave é o id
		self.extratorCampos = list() #lista de campos para ordenar
		self.extratorFiltros = list()
		self.extratorOrderBy = list()
		self.modelo = ""
	def __contains__(self, a):
		"""Verifica se o ID de uma tabela está contida no extrator."""
		return a in self.tabelas
	def __str__(self):
		"""Para expotar o extrator como SQL query."""
		#Adicionando campos SELECT
		output = "SELECT "
		#Campos
		if len(self.extratorCampos) > 0:
			for i in self.extratorCampos:
				output += f"{i.getSelect()}, "
			else:
				output = f"{output[:-2]}\n"
		#Adicionar tabelas
		for i in self.tabelas.values():
			output += f"{i.conexaoAtiva}\n"
		#Adicionar filtros
		if bool(self.extratorFiltros):
			output += "WHERE "
			for i in self.extratorFiltros:
				output += f"{i.getFiltro()}, "
			else:
				output = f"{output[:-2]}\n"
		#Adicionar ordem
		if bool(self.extratorOrderBy):
			output += "ORDER BY "
			for i in self.extratorOrderBy:
				output += f"{i.getUsedName()}, "
			else:
				output = f"{output[:-2]}\n"
		return output
	def clear(self):
		"""Reseta o extrator"""
		self.tabelas = dict()
		self.extratorCampos = list()
		self.extratorFiltros = list()
		self.extratorOrderBy = list()
	def salvarExtrator(self):
		"""Exporta o extrator como um dicionário, para salvar um modelo."""
		arquivo = filedialog.asksaveasfilename(title="Salvar modelo.", defaultextension=".json", filetypes=[("JSON files", "*.json")])
		self.modelo = arquivo
		output = dict()
		output["tabelas"] = dict()
		for i,j in self.tabelas.items():
			output["tabelas"][i] = j.salvarTabela()
		data = json.dumps(output, indent=4)
		try:
			with open(arquivo, 'w') as file:
				file.write(data)
		except:
			print("Operação cancelada.")

	def carregarExtrator(self, data=""):
		"""Para carregar um modelo de extração."""
		baseTabelas = self.database
		if data == "":
			arquivo = filedialog.askopenfilename(title="Carregar modelo", filetypes=[("JSON files", "*.json")])
		else:
			arquivo = data
		try:
			with open(arquivo, 'r') as file:
				data = json.load(file)
			self.modelo = arquivo
			self.tabelas = dict()
			for i, j in data["tabelas"].items():
				self.tabelas[i] = instanceTabela(baseTabelas[j["id"]], j["count"])
				self.tabelas[i].join = j["join"]
				self.tabelas[i].conexao = j["conexao"]
				self.tabelas[i].conexaoAtiva = j["conexaoAtiva"]
				self.tabelas[i].conexaoChaveSelf = j["conexaoChaveSelf"]
				self.tabelas[i].conexaoChaveOther = j["conexaoChaveOther"]
				tabelaUsada = self.tabelas[i]
				for k, l in j["camposAtivos"].items():
					campoCarregado = instanceCampo(baseTabelas[j["id"]].campos[k])
					tabelaUsada.camposAtivos[k] = campoCarregado
					campoCarregado.prioridade = l["prioridade"]
					campoCarregado.ordenar = l["ordenar"]
					campoCarregado.filtro = l["filtro"]
					campoCarregado.filtroAlvo = l["filtroAlvo"]
		except:
			print(f"Modelo inexistente: {arquivo}")

	def exportarExtrator(self):
		"""Exporta a extração em um arquivo .txt."""
		arquivo = filedialog.asksaveasfilename(title="Escolha o local e nome do arquivo.", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
		with open(arquivo, 'w') as file:
			file.write(str(self))