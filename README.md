# SQL Query Builder

Interface visual escrita em Python para criação de uma query SELECT SQL, aqui chamadas de extrações, sem conexão direta com a base de dados. Utiliza somente bibliotecas nativas, sem a necessidade de instalações adicionais. As tabelas de cada base de dados são documentadas separadamente em um arquivo json.

Desenvolvido no contexto de serviço público, onde frequentemente há restrição de instalação de softwares e utilização de bases de dados de empresas contratadas. Pode ser utilizado quando há somente acesso SELECT à uma base de dados qualquer, bem como consulta das tabelas nela existente. O mapeamento das tabelas, seus campos e conexões é necessário para o funcionamento da interface.

## Funcionalidades

- Possibilidade de utilizar múltiplas bases de dados.
- Suporte para vários idiomas.
- Salva e carrega modelos de extração.
- Visualiza o extrator.
- Configurações individuais por usuário, para uso em pastas compartilhadas.
- Exportar a query como arquivo txt.

## Utilização

#### Idiomas

Para adicionar um idioma, adicione um arquivo json na pasta `lang`, seguindo o padrão dos arquivos `EN.json` ou `PT.json`.

#### Mapeando a Base de Dados

O mapeamento das bases de dados é feita em um arquivo json na pasta `databases` por padrão, embora a interface permita selecionar arquivos em outras patas. O arquivo `template.json` contém um modelo, onde cada chave é uma tabela da base.

```json
{
    "table1":{
		"descricao":"Description.",
		"alias":"aliasSQL",
		"campos":{
			"columnName":"alias (optional)"
		},
		"conexoes":{
			"table2":{"chaveSelf":["selfKey"], "chaveOther":["connectionKey"]}
		}
	},
	"table2":{
		"descricao":"Description.",
		"alias":"aliasSQL",
		"campos":{
			"columnName":"alias (optional)"
		},
		"conexoes":{
			"table1":{"chaveSelf":["selfKey"], "chaveOther":["connectionKey"]}
		}
	}
}
```

Cada tabela utiliza as seguintes chaves:

- **descricao:** descrição da tabela, documentando o que contém.
- **alias:** alias utilizada no extrator para essa tabela.
- **campos:** lista de campos da tabela. Cada campo é um json, onde a chave é nome do campo, e seu valor é o alias. Caso não queira um alias, utilize o valor `""`.
- **conexoes:** lista das outras tabelas que podem se conectar com a tabela atual. Cada tabela é um json, com duas chaves:
    - **chaveSelf:** lista com as possíveis chaves da tabela atual utilizada para a conexão.
    - **chaveOther:** lista com as possíveis chaves da tabela conectada utilizada para a conexão.


#### Configurações

As configurações padrão são definidas no arquivo `settings\settings.json`. Cada usuário que utilizar este script terá uma cópia do arquivo na pasta `settings`, onde terá suas configurações individuais. O nome do arquivo é um hash do usuário.

```json
{
	"joinValores": [
		"JOIN",
		"LEFT JOIN",
		"RIGHT JOIN",
		"FULL JOIN"
	],
	"compararValores": [
		"",
		"=",
		"!=",
		">",
		">=",
		"<",
		"<=",
		"in",
		"not in"
	],
	"base": "databases/tabelasBase.json",
	"lang": "PT",
	"modelo": ""
}
```

As configurações padrão são:
- **joinValores:** lista com os tipos de join permitidos.
- **compararValores:** lista com os comparativos permitidos.
- **base:** base de dados padrão.
- **lang:** idioma padrão. É o nome do arquivo na pasta `lang`, sem a extensão.
- **modelo:** endereço do arquivo com um modelo de extração padrão. Pode ser deixado em branco.

#### Utilizando o extrator

![Legenda do menu do extrator.](readmeAssets\docMenuReference.png?raw=true "Legenda do extrator.")

1. **Novo Modelo:** remove todas as tabelas e campos do extrator.
2. **Abrir Modelo:** carrega um modelo previamente salvo.
3. **Salvar Modelo:** salva a extração atual em um modelo, no formato json.
4. **Exportar Modelo:** exporta o extrator em um arquivo txt.
5. **Sair:** encerra o script.

![Legenda do extrator.](readmeAssets\docReference.png?raw=true "Legenda do extrator.")

1. **Aplicar Alterações:** aplica todas as tabelas, campos, conexões e preferências ao extrator, atualizando o visualizador.
2. **Visualizador:** visualiza a query SQL resultante do extrator.
3. **Adicionar Tabela:** adiciona a tabela selecionada ao extrator.
4. **Adicionar Coluna:** adiciona uma coluna ao extrator.
5. **Remover Tabela:** remove a tabela do extrator.
6. **Descrição:** exibe a descrição da tabela, conforme chave `descricao` configurada no mapeamento da base.
7. **Conexão:** define a conexão desta tabela.
    - **Join:** seleciona o tipo de join da conexão.
    - **Conexão:** seleciona a tabela que servirá de elo na conexão, conforme chave `conexao` configurada no mapeamento da base.
    - **Chave Própria:** chave da tabela atual utilizada para a conexão. Equivale ao operador SQL `ON`.
    - **Chave Conexão:** chave da tabela elo utilizada para a conexão. Equivale ao operador SQL `ON`.
8. Colunas:** as colunas da tabela adicionadas ao extrator.
    - **Coluna:** nome da coluna.
    - **Ordem:** ordem global da coluna no extrator. É a ordem em que a coluna aparecerá após `SELECT`. Deve ser preenchido manualmente.
    - **Filtro:** filtro aplicável à coluna. Equivale ao operador SQL `WHERE`.
    - **Valor:** valor utilizado no filtro da coluna.
    - **Ordenar:** define se a coluna será parâmetro para ordenar o resultado. Equivale ao operador SQL `ORDER BY`.
    - **Remover Coluna:** remove a coluna da tabela.

A primeira tabela, no topo do extrator, sempre terá uma conexão `FROM`. A interface não bloqueia as opções de conexão desta tabela, permitindo a consulta de quais são as conexões possíveis, independente da ordem da tabela no extrator.

Cabe ao usuário customizar o resultado exportado para utilizar outras funções SQL, como `sum()`, `distinct` ou a utilização de sub-queries.