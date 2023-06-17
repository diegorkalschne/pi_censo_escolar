import pandas as pd


def read_file(year, read_path):
    if str(read_path).endswith('/'):
        read_path = read_path[0:-1]

    file_path = f'{read_path}/censo{str(year)}.csv'

    # Importa os dados
    microdados = pd.read_csv(file_path, encoding='Latin-1', delimiter=';', low_memory=False)

    # Obtém apenas as colunas de interesse
    matriculas_por_estado = microdados[['NO_UF', 'QT_MAT_FUND_AI', 'QT_MAT_FUND_AF', 'QT_MAT_MED']]

    # Renomeia as colunas
    matriculas_por_estado = matriculas_por_estado.rename(
        columns={"QT_MAT_FUND_AI": "EF (Iniciais)", "QT_MAT_FUND_AF": "EF (Finais)", "QT_MAT_MED": "EM"})

    # Agrupa por Estado e soma as linhas
    matriculas_por_estado = matriculas_por_estado.groupby('NO_UF').sum()

    matriculas_por_estado.index.name = 'Estado'
    matriculas_por_estado = matriculas_por_estado.reset_index()

    matriculas_por_estado['Ano'] = year

    return matriculas_por_estado


# Salva o DataFrame em um arquivos .CSV
def save_file(dataframe, path=''):
    if path == '':
        path = 'drive/MyDrive/MatriculasTotalizador.csv'
    else:
        if str(path).endswith('/'):
            path = path[0:-1]

        path = f'{path}/MatriculasTotalizador.csv'

    with open(path, 'w') as file:
        file.write(dataframe.to_csv(index=False, encoding='utf-8', lineterminator='\n', sep=';'))


def start(c_min_year, c_max_year, read_path, save_path):
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

    # Esse DataFrame armazena todos os resultados obtidos a partir dos CSVs "Censo Escolar" e armazena em um único arquivo (agrupado por Estado)
    # Censo escolar indica a quantidade de matrículas realizadas (separados por Ensino Fundamental e Ensino Médio)
    # total_df
