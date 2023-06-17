import threading
import time

import censo_escolar_reader as censo
import populacao_por_idade_reader as populacao
from PySimpleGUI import PySimpleGUI as sg
import os

# Global variables
global window


def main():
    global window
    window = build_window()
    listener_window()


# Constrói o layout e exibe a interface gráfica
def build_window():
    # Execute o comando abaixo caso queira ver os demais temas disponíveis
    # sg.theme_previewer()

    # Setando o theme da GUI
    sg.theme('DarkGrey15')

    layout = [
        [sg.Text('Diretório de Entrada', size=(18, 1)), sg.InputText(key='input'), sg.FolderBrowse('Procurar', key='input')],
        [sg.Text('Diretório de Saída', size=(18, 1)), sg.InputText(key='output'), sg.FolderBrowse('Procurar', key='output')],
        [sg.Text('Ano Inicial', size=(18, 1)), sg.InputText(key='ano-inicial', size=(10, 1))],
        [sg.Text('Ano Final', size=(18, 1)), sg.InputText(key='ano-final', size=(10, 1))],
        [sg.Text('', key='validate')],
        [sg.Column([[sg.Button('Processar', key='process-button', size=(20, 2))]], element_justification='c', expand_x=True)],
    ]

    # Constrói a interface gráfica
    font = ("Arial", 12)
    l_window = sg.Window('Censo Escolar', layout, font=font)

    return l_window


# "Listener" para ouvir os eventos da interface gráfica
def listener_window():
    while True:
        events, values = window.read()

        if events == sg.WINDOW_CLOSED:
            # Interface foi fechada (sai do loop)
            break

        if events == 'process-button':
            # Eventos relacionados ao botão de "Processar"
            window['validate'].update('')

            # Verifica se todos os valores foram informados
            if values['ano-inicial'] != '' and values['ano-final'] != '' and values['input'] != '' and values['output'] != '':
                try:
                    initial_year = int(values['ano-inicial'])
                    final_year = int(values['ano-final'])
                except:
                    # Caso de erro na conversão, indica que o valor digitado não contém apenas números
                    window['validate'].update('Verifique os anos. Apenas números são aceitos', text_color='red')
                    continue

                if initial_year >= final_year:
                    window['validate'].update('O ano inicial deve ser menor que o ano final', text_color='red')
                    continue

                input_path = values['input']
                output_path = values['output']

                # Desabilita o botão de processamento
                window['process-button'].update(disabled=True)
                window['validate'].update("Processando dados. Por favor, aguarde...", text_color="purple")

                # Inicia o processamento em uma nova Thread
                x = threading.Thread(target=process, args=(initial_year, final_year, input_path, output_path))
                x.start()

                # Inicia uma nova thread para verificar quando a Thread do processamento concluir
                y = threading.Thread(target=show_confimation, args=(x, output_path))
                y.start()
            else:
                window['validate'].update('Informe todos os valores', text_color='red')


# Responsável por controlar o processamento dos arquivos (população por idade e censo escolar)
def process(initial_year, final_year, input_path, output_path):
    min_year = initial_year
    max_year = final_year

    censo.start(c_max_year=max_year, c_min_year=min_year, read_path=input_path, save_path=output_path)
    populacao.start(c_max_year=max_year, c_min_year=min_year, read_path=input_path, save_path=output_path)


def show_confimation(thread, output_path):
    # Espera a thread de "processamento" concluir para prosseguir com o restante do código
    thread.join()

    window['validate'].update("Processamento finalizado", text_color="green")
    window['process-button'].update(disabled=False)

    time.sleep(1)

    # Abre a pasta de "output" no explorer do Windows
    os.system(f'start {output_path}')


# Inicia o programa
main()
