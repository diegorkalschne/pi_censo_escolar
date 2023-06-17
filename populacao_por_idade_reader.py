import pandas as pd


def code_to_name_region(row):
    try:
        code = int(row['Código Estado'])
    except:
        return ''

    if code == 12:
        return 'Acre'
    elif code == 27:
        return 'Alagoas'
    elif code == 16:
        return 'Amapá'
    elif code == 13:
        return 'Amazonas'
    elif code == 29:
        return 'Bahia'
    elif code == 23:
        return 'Ceará'
    elif code == 53:
        return 'Distrito Federal'
    elif code == 32:
        return 'Espírito Santo'
    elif code == 52:
        return 'Goiás'
    elif code == 21:
        return 'Maranhão'
    elif code == 51:
        return 'Mato Grosso'
    elif code == 50:
        return 'Mato Grosso do Sul'
    elif code == 31:
        return 'Minas Gerais'
    elif code == 15:
        return 'Pará'
    elif code == 25:
        return 'Paraíba'
    elif code == 41:
        return 'Paraná'
    elif code == 26:
        return 'Pernambuco'
    elif code == 22:
        return 'Piauí'
    elif code == 24:
        return 'Rio Grande do Norte'
    elif code == 43:
        return 'Rio Grande do Sul'
    elif code == 33:
        return 'Rio de Janeiro'
    elif code == 11:
        return 'Rondônia'
    elif code == 14:
        return 'Roraima'
    elif code == 42:
        return 'Santa Catarina'
    elif code == 35:
        return 'São Paulo'
    elif code == 28:
        return 'Sergipe'
    elif code == 17:
        return 'Tocantins'
    else:
        return ''


def read_file(year, read_path):
    if str(read_path).endswith('/'):
        read_path = read_path[0:-1]

    file_path = f'{read_path}/idade{str(year)}.csv'
    # Importa os dados
    df = pd.read_csv(file_path, encoding='Latin-1', delimiter=';')

    # Dropa colunas que não serão utilizadas
    df = df.drop(['Menos que 1 ano de idade', '1  ano', '2  anos', '3  anos', '4  anos', '5  anos'], axis=1)

    # Dropa as colunas em um intervalo
    df = df.drop(df.columns[15:len(df.columns)], axis=1)

    # Encontra as linhas que possuem valores nulos
    invalid_values = df[df.isnull().any(axis=1)]

    # Dropa as linhas com valores nulos
    df = df.drop(invalid_values.index)

    # Cria um novo DataFrame e pega apenas a coluna do Município
    municipios = pd.DataFrame()
    municipios['Município'] = df['Município']

    # Separa a coluna de município em várias colunas com um split. Utilizado para separar o código do município do nome
    municipios = municipios['Município'].str.split(' ', expand=True)

    # Pega apenas a primeira coluna, que é o código do município
    municipios_code = municipios.iloc[:, 0]

    # Remove a coluna do código e concatena todos os demais valores não nulos e substitui no DataFrame original
    municipios = municipios.drop(municipios.columns[0], axis=1)
    municipios_name = municipios.stack().groupby(level=0).agg(' '.join)

    df['Município'] = municipios_name

    # Adiciona o código do município como primeira coluna do DataFrame
    df.insert(0, 'Código Município', municipios_code)

    # O código da região é dado pelo 2 primeiros dígitos do código do município.
    # O código abaixo extrai apenas os dígitos referentes ao código da região e cria uma nova coluna no DataFrame
    regiao_code = df['Código Município'].apply(lambda x: x[:2])
    df.insert(1, 'Código Estado', regiao_code)

    # Agrupa por região e soma as colunas
    grouped_df = df.groupby(['Código Estado']).sum(numeric_only=True)

    # Reseta o index do DataFrame
    grouped_df = grouped_df.reset_index()

    # Atribui a cada código do Estado, uma 'label' do nome do Estado
    region = grouped_df.apply(code_to_name_region, axis=1)
    grouped_df.insert(1, 'Estado', region)

    # Ordena pelo o Estado
    grouped_df = grouped_df.sort_values('Estado')

    # Separa por cada período do vida escolar e soma as linhas
    anos_iniciais = grouped_df[['6  anos', '7  anos', '8  anos', '9  anos', '10 anos']]
    anos_iniciais = anos_iniciais.sum(axis=1)
    anos_finais = grouped_df[['11 anos', '12 anos', '13 anos', '14 anos']]
    anos_finais = anos_finais.sum(axis=1)
    ensino_medio = grouped_df[['15 anos', '16 anos', '17 anos']]
    ensino_medio = ensino_medio.sum(axis=1)

    # Cria um novo DataFrame contendo todas as informações agrupadas
    qtd_por_faixa = grouped_df.iloc[:, 0:2]
    qtd_por_faixa['EF (Iniciais)'] = anos_iniciais
    qtd_por_faixa['EF (Finais)'] = anos_finais
    qtd_por_faixa['EM'] = ensino_medio

    # qtd_por_faixa contém a quantidade de pessoas que se enquandram em cada faixa do período escola e, logo, estariam aptas a estarem matriculadas em uma escola
    # As faixas foram obtidas através de: https://www.colegiopoliedro.com.br/blog/existe-idade-certa-para-cada-serie-escolar/
    # qtd_por_faixa
    qtd_por_faixa['Ano'] = year

    # Remove a linha que possui o 'Total'
    qtd_por_faixa.drop(qtd_por_faixa[qtd_por_faixa['Código Estado'] == 'To'].index, inplace=True)

    return qtd_por_faixa


# Salva o DataFrame em um arquivo .CSV
def save_file(dataframe, path=''):
    if path == '':
        path = 'drive/MyDrive/PopulacaoPorIdadeTotalizador.csv'
    else:
        if str(path).endswith('/'):
            path = path[0:-1]

        path = f'{path}/PopulacaoPorIdadeTotalizador.csv'

    with open(path, 'w') as file:
        file.write(dataframe.to_csv(index=False, encoding='utf-8', lineterminator='\n', sep=';'))


def start(c_max_year, c_min_year, read_path, save_path):
    # Armazena o resultado total de todos os anos
    total_df = pd.DataFrame()

    # Ano dos arquivos
    max_year = c_max_year
    min_year = c_min_year

    year = min_year  # Ano atual sendo lido no for abaixo
    year_range = (max_year - min_year) + 2  # Quantidade de anos a serem lidos

    # Função para ler todos os arquivos de todos os anos e concatenar em apenas um DataFrame
    for i in range(1, year_range):
        try:
            data = read_file(year, read_path=read_path)

            # Lê o arquivo especificado pelo o ano e concatena com os dados já existentes (adiciona linhas no DataFrame)
            total_df = pd.concat([total_df, data], ignore_index=True, axis=0)
        except Exception as ex:
            print(year)
            print(ex)
        finally:
            year += 1

    save_file(total_df, path=save_path)

    # Esse DataFrame armazena todos os resultados obtidos a partir dos CSVs "População por idade" e armazena em um único arquivo (agrupado por Estado)
    # População por idade indica a quantidade de pessoas que "deveriam" estar matriculadas na escola com base na idade
    # total_df
