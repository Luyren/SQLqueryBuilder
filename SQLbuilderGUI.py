import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import json
import os
import classes.extractorClasses as eb
import hashlib


#Carregar configurações
	#os.getlogin para utilizar o usuário e salvar configurações específicas
	#hashlib para hash o usuário
	#Usuário e hash para uso compartilhado
currUser = hashlib.sha256(bytes(os.getlogin(), encoding='utf-8')).hexdigest()
arquivoSettings = dict()
settings = dict()
idiomaPadrao = 'PT'

def salvarConfig(base=arquivoSettings):
	"""Salva alterações nas configurações."""
	with open(arquivoSettings, "w", encoding="utf-8") as file:
		file.write(json.dumps(settings, indent=4))

	#buscar configurações de usuários
listaSettings = list()
for root, dir, file in os.walk("settings"):
	for i in file:
		#somente o usuário, sem extensão
		listaSettings.append(i.split(".")[0])
arquivoSettings = f"settings/{currUser}.json"
if currUser in listaSettings:
	with open(arquivoSettings, "r", encoding="utf-8") as file:
		settings = json.loads(file.read())
else:
	with open("settings/settings.json", "r", encoding="utf-8") as file:
		settings = json.loads(file.read())
		salvarConfig()

#Carregar texto
textoGUI = dict()
def aplicarIdioma(texto=textoGUI):
	"""Atualiza o texto da GUI por idioma."""
	def selecionarIdioma(arquivo:str):
		"""Carrega arquivo com os textos da GUI por idioma, na pasta lang."""
		with open(f'lang/{arquivo}.json', "r", encoding="utf-8") as file:
			return json.loads(file.read())
	#read only global settings
	if "lang" in settings:
		base = selecionarIdioma(settings["lang"])
	else:
		base = selecionarIdioma(idiomaPadrao)
	for i, j in base.items():
		texto[i] = j
aplicarIdioma()
#listar idiomas para alteração
listaIdiomas = list()
for root, dir, file in os.walk("lang"):
	for i in file:
		listaIdiomas.append(i.split(".")[0])
#Inicializar extrator
extracao = eb.extrator()
def carregarExtrator(base=extracao, settings=settings, add=False):
	"""Carregar modelo de extrator e salva como último modelo trabalhado."""
	base.carregarExtrator()
	carregarGUI(add=add)
	if not add:
		settings["modelo"] = base.modelo
		salvarConfig()
def salvarExtrator(base=extracao, settings=settings):
	"""Salva modelo de extrator e salva como último modelo trabalhado"""
	atualizarExtrator()
	base.salvarExtrator()
	settings["modelo"] = base.modelo
	salvarConfig()
#Carregar base de tabelas
baseTabelas = dict()
def carregarBase(extrator=extracao, base=baseTabelas, settings=settings, inputBase=""):
	"""Inicializa a base de tabelas."""
	if inputBase != "":
		arquivo = inputBase
	else:
		arquivo = filedialog.askopenfilename(title="Escolha a base de tabelas.", defaultextension=".json", filetypes=[("JSON files", "*.json")])
		settings["base"] = arquivo
		salvarConfig()
	with open(arquivo, "r", encoding="utf-8") as file:
		tabelas = json.loads(file.read())
	for i, j in tabelas.items():
		base[i] = (eb.tabelaSQL(i, j))
	extrator.database = base
carregarBase(inputBase=settings["base"])
#Carregar último modelo
if "modelo" in settings and settings["modelo"] != "":
	extracao.carregarExtrator(data=settings["modelo"])

def atualizarExtrator(base=extracao):
	"""Aplica todas as alterações da GUI ao extrator."""
	base.clear()
	for i in guiTabelas: #read only
		idTabela = i["id"]
		count = i["count"]
		tipoJoin = i["valorJoin"].get()
		conexaoUsada = i["valorConexao"].get()
		conexaoChaveSelf = i["chaveSelf"].get()
		conexaoChaveOther = i["chaveOther"].get()
		tabelaUsada = base.database[idTabela]
		idUsado = f"{idTabela}.{count}"
		tabelaNova = eb.instanceTabela(tabelaUsada, count)
		tabelaNova.join = tipoJoin
		tabelaNova.conexao = conexaoUsada
		base.tabelas[idUsado] = tabelaNova
		#conexão
		if len(base.tabelas) == 1:
			tabelaNova.conexaoAtiva = f"FROM {tabelaNova.getAlias()}"
		else:
			tabelaNova.conexaoChaveSelf = conexaoChaveSelf
			tabelaNova.conexaoChaveOther = conexaoChaveOther
			tabelaNova.conexaoAtiva = f"{tipoJoin} {tabelaNova.getAlias()} ON {tabelaNova.alias}.{conexaoChaveSelf} = {base.database[conexaoUsada].alias}.{conexaoChaveOther}"
		#adicionar campos
		for j in i["campos"]:
			valorCampo = j["valor"].get()
			novoCampo = eb.instanceCampo(tabelaNova.campos[valorCampo])
			novoCampo.prioridade = j["prioridade"].get()
			ordenar = j["valorOrdenar"].get()
			novoCampo.ordenar = ordenar
			filtro = j["valorFiltro"].get()
			novoCampo.filtro = filtro
			novoCampo.filtroAlvo = j["valorFiltroAlvo"].get()
			tabelaNova.camposAtivos[valorCampo] = novoCampo
			#Adicionar novo campo à lista de campos do extrator, para ordenar, filtrar e agrupar
			base.extratorCampos.append(novoCampo)
			if bool(ordenar):
				base.extratorOrderBy.append(novoCampo)
			if bool(filtro):
				base.extratorFiltros.append(novoCampo)
		base.extratorCampos.sort(key=lambda x:x.prioridade)
		base.extratorOrderBy.sort(key=lambda x:x.prioridade)
		base.extratorFiltros.sort(key=lambda x:x.prioridade)
	updateExtractorDisplay()
##########################
#Graphics User Interface
##########################
#lista contendo as tabelas adicionadas
guiTabelas = list()
def limparGUI(clear=False):
	for i in guiTabelas:
		i["frame"].destroy()
	if clear:
		extracao.clear()
		guiTabelas.clear()
		atualizarExtrator()
def carregarGUI(add=False):
	if not add:
		limparGUI()
		guiTabelas.clear()
	for j in extracao.tabelas.values():
		guiAddTabela(nomeTabela=j.id, loadData=j)
	atualizarExtrator()
#Main window
root = tk.Tk()
root.title(textoGUI["titulo"])
root.geometry("780x600")
root.resizable(False, False)
#Menu
menu = tk.Menu(root, tearoff=0)
root.config(menu=menu)
	#Menu arquivo
fileMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label=textoGUI["arquivo"], menu=fileMenu)
fileMenu.add_command(label=textoGUI["novoModelo"], command=lambda: limparGUI(clear=True))
fileMenu.add_command(label=textoGUI["abrirModelo"], command=carregarExtrator)
fileMenu.add_command(label=textoGUI["adicionarModelo"], command=lambda:carregarExtrator(add=True))
fileMenu.add_command(label=textoGUI["salvarModelo"], command=salvarExtrator)
fileMenu.add_command(label=textoGUI["exportarModelo"], command=extracao.exportarExtrator)
fileMenu.add_command(label=textoGUI["sairExtrator"], command=root.quit)
	#Menu configurações
settingsMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label=textoGUI["config"], menu=settingsMenu)
idiomaGUI = tk.StringVar(value=settings["lang"])
def atualizarIdioma(settings=settings, idioma=idiomaGUI):
	"""Aplica o novo idioma às configurações."""
	settings["lang"] = idioma.get()
	salvarConfig()
idiomaMenu = tk.Menu(settingsMenu, tearoff=0)
settingsMenu.add_cascade(label=textoGUI["idioma"], menu=idiomaMenu)
	#Adicionando um botão por idioma.
for i in listaIdiomas:
	idiomaMenu.add_radiobutton(label=i, variable=idiomaGUI, value=i, command=atualizarIdioma)
settingsMenu.add_command(label=textoGUI["alteraBase"], command=carregarBase)
#Botão de atualizar extrator
botaoAplicar = tk.Button(root, text=textoGUI["aplicar"], command=atualizarExtrator)
botaoAplicar.pack()

#Frame com display do extrator e scrollbar
extratorFrame = tk.Frame(root)
extratorFrame.pack()
text = tk.Text(extratorFrame, height=12, bd=2)
def updateExtractorDisplay():
	"""Atualiza o display do extrator."""
	text.config(state=tk.NORMAL)
	text.delete(1.0, 'end')
	text.insert('end', str(extracao))
	text.config(state=tk.DISABLED)
text.pack(side=tk.LEFT, expand=True, fill=tk.Y)
extratorScrollV = tk.Scrollbar(extratorFrame, cursor="arrow", orient="vertical")
extratorScrollV.config(command=text.yview)
text.config(yscrollcommand=extratorScrollV.set)
extratorScrollV.pack(side=tk.RIGHT, expand=True, fill=tk.Y)

#Adicionar Tabela
frameAddTabela = tk.Frame(root)
frameAddTabela.pack()
nomeTabela = tk.Label(frameAddTabela, text=textoGUI["nomeTabela"])
nomeTabela.grid(row=0, column=0, padx=2, pady=2)

def guiAddTabela(texto=textoGUI, save=guiTabelas, nomeTabela="", loadData={}):
	"""Adiciona um frame de tabela à GUI"""
	frame = tk.Frame(canvasFrame) #canvasFrame readonly
	if bool(nomeTabela):
		nome = nomeTabela
	else:
		nome = nomeTabelaVar.get()
	output = {"id":nome, "campoId":0, "count":0, "rowCount":0, "frame":frame, "valorJoin":tk.StringVar(), "valorConexao":tk.StringVar(), "chaveSelf":tk.StringVar(), "chaveOther":tk.StringVar(),"campos":list()}
	#Contagem de ids, para tabelas repetidas
	count = 0
	for i in save:
		if i["id"] == nome:
			count += 1
	output["count"] = count
	nomeTabela = tk.Label(frame, text=nome)
	nomeTabela.grid(row=0, column=0, padx=2, pady=2)
	#Botão adicionar campo
	addCampo = tk.Button(frame, text=texto["addCampo"], padx=2)
	addCampo.grid(row=0, column=1)
	#Botão para remover tabela
	removeTabela = tk.Button(frame, text=texto["removeTabela"], padx=2, command=lambda:guiRemoveTabela(nome, count))
	removeTabela.grid(row=0, column=2)
	#Botão para mostrar descrição da tabela
	descTabela = tk.Button(frame, text=texto["descricaoTabela"], padx=2, command=lambda:messagebox.showinfo(nome, baseTabelas[nome].descricao))
	descTabela.grid(row=0, column=3)
	baseRow = 1
	def addConexao():
		nomeConexao = tk.Label(frame, text=texto["conexao"])
		nomeConexao.grid(row=baseRow, column=0, padx=2, pady=2)
		#lista de conexões
		conexaoValores = list()
		for i in baseTabelas[nome].conexoes: #readonly baseTabelas
			conexaoValores.append(i)
		conexaoBox = ttk.Combobox(frame, values=conexaoValores, textvariable=output["valorConexao"], state="readonly")
		conexaoBox.grid(row=baseRow, column=1, padx=2, pady=2)
		conexaoBox.current(0)
		#chaves da conexão
		#chave self
		chaveSelfConexao = tk.Label(frame, text=texto["chaveSelf"])
		chaveSelfConexao.grid(row=baseRow-1, column=2, padx=2, pady=2)
		chaveSelfValores = list()
		for i in baseTabelas[nome].conexoes[output["valorConexao"].get()]["chaveSelf"]:
			chaveSelfValores.append(i)
		chaveSelfBox = ttk.Combobox(frame, values=chaveSelfValores, textvariable=output["chaveSelf"], state="readonly")
		chaveSelfBox.grid(row=baseRow-1, column=3, padx=2, pady=2)
		chaveSelfBox.current(0)
		#chaveOther
		chaveOtherConexao = tk.Label(frame, text=texto["chaveOther"])
		chaveOtherConexao.grid(row=baseRow, column=2, padx=2, pady=2)
		chaveOtherValores = list()
		for i in baseTabelas[nome].conexoes[output["valorConexao"].get()]["chaveOther"]:
			chaveOtherValores.append(i)
		chaveOtherBox = ttk.Combobox(frame, values=chaveOtherValores, textvariable=output["chaveOther"], state="readonly")
		chaveOtherBox.grid(row=baseRow, column=3, padx=2, pady=2)
		chaveOtherBox.current(0)
		#bind conexaoBox em "<<ComboboxSelected>>" para alterar os valores das chaves
		def atualizarConexoes(*args):
			chaveSelfBox.configure(values=baseTabelas[nome].conexoes[output["valorConexao"].get()]["chaveSelf"].copy())
			chaveSelfBox.current(0)
			chaveOtherBox.configure(values=baseTabelas[nome].conexoes[output["valorConexao"].get()]["chaveOther"].copy())
			chaveOtherBox.current(0)
		conexaoBox.bind("<<ComboboxSelected>>", atualizarConexoes)
		return conexaoValores, conexaoBox, chaveSelfValores, chaveSelfBox, chaveOtherValores, chaveOtherBox
	#Label do combobox de join
	nomeJoin = tk.Label(frame, text=texto["tipoJoin"])
	nomeJoin.grid(row=baseRow, column=0, padx=2, pady=2)
	#Combobox para o tipo de join
	#filtro, por lista
	joinValores = settings["joinValores"]
	joinBox = ttk.Combobox(frame, values=joinValores, textvariable=output["valorJoin"], state="readonly")
	joinBox.current(0)
	joinBox.grid(row=baseRow, column=1, padx=2, pady=2)
	baseRow += 1
	#conexão: label e combobox
	conexaoBoxValores, conexaoBoxGerado, chaveSelfValores, conexaoChaveSelf, chaveOtherValores, conexaoChaveOther = addConexao()
	baseRow += 1
	#Cabeçalho dos campos
	headerSpace = " " * 40
	headerCampos = tk.Label(frame, text=f"{texto["campo"]}{headerSpace}{texto["ordem"]}{headerSpace}{texto["filtro"]}{headerSpace}{texto["valor"]}")
	headerCampos.grid(row=baseRow, column=0, padx=2, pady=2, columnspan=4, sticky="nw")
	output["rowCount"] = baseRow + 1
	frame.grid(row=len(save), column=0)
	#configura o botão para adicionar novo campo
	addCampo.configure(command=lambda:output["campos"].append(guiAddCampo(output, baseTabelas[nome].campos)))
	if bool(loadData):
		output["valorJoin"].set(loadData.join)
		if bool(joinBox) and loadData.join in joinValores:
			joinBox.current(joinValores.index(loadData.join))
		output["valorConexao"].set(loadData.conexao)
		if bool(loadData.conexao):
			conexaoBoxGerado.current(conexaoBoxValores.index(loadData.conexao))
			chaveSelfValores = baseTabelas[nome].conexoes[output["valorConexao"].get()]["chaveSelf"]
			conexaoChaveSelf.configure(values=chaveSelfValores.copy())
			chaveOtherValores = baseTabelas[nome].conexoes[output["valorConexao"].get()]["chaveOther"]
			conexaoChaveOther.configure(values=chaveOtherValores.copy())
		if bool(loadData.conexaoChaveSelf):
			conexaoChaveSelf.current(chaveSelfValores.index(loadData.conexaoChaveSelf))
		if bool(loadData.conexaoChaveOther):
			conexaoChaveOther.current(chaveOtherValores.index(loadData.conexaoChaveOther))
		for i, j in loadData.camposAtivos.items():
			output["campos"].append(guiAddCampo(output, baseTabelas[nome].campos, loadData=j))
	updateCanvasScrollRegion()
	save.append(output)

def guiAddCampo(parent, campos, loadData={}):
	"""Adiciona um campo ao frame de uma tabela da GUI."""
	frame = tk.Frame(parent["frame"])
	output = {"id":parent["campoId"],"frame":frame, "valor":tk.StringVar(), "prioridade":tk.IntVar(), "valorFiltro":tk.StringVar(), "valorFiltroAlvo":tk.StringVar(), "valorOrdenar":tk.IntVar()}
	#Combobox com os campos da tabela
	listaCampos = list()
	for i in campos:
		listaCampos.append(i)
	campoBox = ttk.Combobox(frame, values=listaCampos, textvariable=output["valor"], state="readonly")
	campoBox.current(0)
	campoBox.grid(row=0, column=0, padx=2, pady=2)
	#Ordem
	ordemEntry = tk.Entry(frame, textvariable=output["prioridade"])
	ordemEntry.grid(row=0, column=1, padx=2, pady=2)
	#Filtro
	listaValores = settings["compararValores"]
	filtroBox = ttk.Combobox(frame, values=listaValores, textvariable=output["valorFiltro"], state="readonly")
	filtroBox.grid(row=0, column=2, padx=2, pady=2)
	#valor alvo do filtro
	filtroEntry = tk.Entry(frame, textvariable=output["valorFiltroAlvo"])
	filtroEntry.grid(row=0, column=3, padx=2, pady=2)
	#Botão de ordenar
	botaoOrdenar = tk.Checkbutton(frame, text=textoGUI["ordenar"], variable=output["valorOrdenar"])
	botaoOrdenar.grid(row=0, column=4)
	#Botão remover campo
	removeCampo = tk.Button(frame, text=textoGUI["removeCampo"], padx=16, command=lambda:guiRemoveCampo(output["id"], parent))
	removeCampo.grid(row=0, column=5)
	#Grid frame
	frame.grid(row = parent["rowCount"], column=0, columnspan = 4)
	parent["rowCount"] += 1
	parent["campoId"] += 1
	if bool(loadData):
		output["valor"].set(loadData.id)
		campoBox.current(listaCampos.index(loadData.id))
		output["prioridade"].set(loadData.prioridade)
		ordemEntry.config(text=loadData.prioridade)
		output["valorFiltro"].set(loadData.filtro)
		filtroBox.current(listaValores.index(loadData.filtro))
		output["valorFiltroAlvo"].set(loadData.filtroAlvo)
		output["valorOrdenar"].set(loadData.ordenar)
		if bool(loadData.ordenar):
			botaoOrdenar.select()
	updateCanvasScrollRegion()
	return output
def guiRemoveCampo(id, base):
	index = 0
	campos = base["campos"]
	for i in range(len(campos)):
		item = campos[i]
		if item["id"] == id:
			index = i
			break
	campos[index]["frame"].destroy()
	campos.pop(index)
	base["campoId"] -= 1
	updateCanvasScrollRegion()

def guiRemoveTabela(nome, count, base=guiTabelas):
	"""Remove um frame de tabela da GUI"""
	index = 0
	for i in range(len(base)):
		item = base[i]
		if item["id"] == nome:
			currCount = item["count"]
			if currCount == count:
				index = i
	base[index]["frame"].destroy()
	base.pop(index)
	updateCanvasScrollRegion()

	#listando tabelas para a combo box
listaTabelas = list()
for i in baseTabelas:
	listaTabelas.append(i)
nomeTabelaVar = tk.StringVar()
tabelasBox = ttk.Combobox(frameAddTabela, values=listaTabelas, textvariable=nomeTabelaVar, width=64, state="readonly")
tabelasBox.current(0)
tabelasBox.grid(row=0, column=1, padx=2, pady=2)
	#Botão de adicionar tabela
addTabela = tk.Button(frameAddTabela, text=textoGUI["addTabela"], padx=2, command=guiAddTabela)
addTabela.grid(row=0, column=2, columnspan=32)

#Inicializar valores para o canvas das tabelas
localTabela = tk.Canvas(root, width=800, height=400, relief='sunken', scrollregion=(0,0,256,256))
canvasFrame = tk.Frame(localTabela)
	#Scroll da lista de tabelas
canvasScroll = tk.Scrollbar(root, cursor="arrow", orient="vertical")
#canvasScroll.bind("<Configure>", lambda e: localTabela.configure(scrollregion=canvasFrame.bbox("all")))
localTabela.config(yscrollcommand=canvasScroll.set)
canvasScroll.config(command=localTabela.yview)
canvasScroll.pack(side=tk.RIGHT, expand=True, fill=tk.Y)
localTabela.pack()
localTabela.create_window(0, 0, window=canvasFrame, anchor=tk.NW)
def updateCanvasScrollRegion():
	"""Atualiza a scrollable area do canvas de tabelas"""
	localTabela.update_idletasks()
	localTabela.config(scrollregion=canvasFrame.bbox())
#Carregar GUI com base nos dados carregados do modelo
carregarGUI()
#Atualizar display do extrator
#run
root.mainloop()