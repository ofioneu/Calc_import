from asyncio import events
import PySimpleGUI as sg
import configparser
import requests
import pandas as pd
import datetime

def calc(preco_invoice, frete_usd, custo_real):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read('config.ini')
    api_usdbrl =  config['API_USD_BRL']['usd_brl'] 
    
    custo_real=float(custo_real)
    
    response = requests.get(api_usdbrl)
    response_json = response.json()
    moeda_brl = float(response_json['USDBRL']['ask'])
    #moeda_brl = 5.30
    
    
    tax_alibaba = float(config['TAX']['tax_alibaba'])
    percent_import = float(config['TAX']['tax_simple'])
    percent_iof = float(config['TAX']['iof'])
    percent_icms = float(config['TAX']['icms'])
    tax_fix_dhl = float(config['TAX']['tax_fix_dhl'])
    
    #convertendo valores prod e ship em real
    vprod_brl = preco_invoice * moeda_brl
    vfrete_brl = frete_usd * moeda_brl

    vbrl = (vprod_brl + vfrete_brl)
    

    tax_import = round(float(vbrl * (percent_import/100)),2)
    tax_iof = round(vbrl * (percent_iof/100),2)

    tax_icms = round(((vbrl + tax_import)/(1-(percent_icms/100))) * (percent_icms/100),2)

    v_total_tributos = round((tax_import + tax_icms + tax_iof + tax_fix_dhl),2)

    v_total_compra = round((vbrl + v_total_tributos),2)
    
    total_produto = round((v_total_compra + (custo_real*moeda_brl)),2)
    
    return [tax_import, tax_icms, tax_iof, v_total_tributos, v_total_compra, total_produto]

resultado_array=[]


sg.theme('DarkBlue8')    # Keep things interesting for your users

# ------ Menu Definition ------ #      
menu_def = [['File', ['Open', 'Save', 'Exit'  ]],]

headings =['TAX IMPORT', 'ICMS', 'IOF','Total Imposto', 'Preco final', 'Custo total']

layout = [
          [sg.Menu(menu_def, )],
          [sg.Text('PRECO REAL (USD)')],
          [sg.Input(key='-VALOR_REAL-')],
          [sg.Text('PRECO INVOICE (USD)')],      
          [sg.Input(key='-PROD_USD-')],
          [sg.Text('Frete (USD)')],
          [sg.Input(key='-FRETE_USD-')],
          [sg.Text('CARREGUE O ARQUIVO')], 
          [sg.Input(key = '-XLSX-'), sg.FileBrowse('FileBrowse')],     
          [sg.Table(values=resultado_array, headings = headings, auto_size_columns=True,
                    display_row_numbers=True,
                    justification='center',
                    key='-TABLE-',
                    enable_events=True,
                    row_height=20,)],       
          [sg.Button('CALCULAR'), sg.Button('Clear', enable_events= True), sg.Button('Reset'), sg.Button('Exportar XLSX'), sg.Exit()]
          ]      

window = sg.Window('Calculadora importação', layout)      

while True: 
    xlsx_array =[]
    event, values = window.read()
    
    if event == sg.WIN_CLOSED or event == 'Exit':
        break   # The Event Loop
    real, invoice, frete, arq = values['-VALOR_REAL-'], values['-PROD_USD-'], values['-FRETE_USD-'], values['-XLSX-']
    
    if real and invoice and frete or event == "-XLSX-":
        prod_usd = float(values['-PROD_USD-'])
        frete_usd = float(values['-FRETE_USD-'])
        v_real_produto = float(values['-VALOR_REAL-'])
        resultado = calc(prod_usd,frete_usd, v_real_produto)
    else:
        pass
    
    if event == 'CALCULAR' and len(arq) <= 0:
        arq = None
        window['Clear'].update(visible=True)
        resultado_array.append(resultado)        
        window['-TABLE-'].update(values=resultado_array)
    
    elif len(arq) > 0 :
        window['Clear'].update(visible=False)
        patch_xlsx = values['-XLSX-']
        xlsx = pd.read_excel(patch_xlsx) # abre o arquivo xlsx
        frame = pd.DataFrame(xlsx)
        invoice_array = []
        frete_array = []
        real_array = []
        
        for i in frame['USD'].dropna():
            invoice_array.append(i)
        
        for i in frame['FRETE'].dropna():
            frete_array.append(i)
        
        for i in frame['PRECO REAL'].dropna():
            real_array.append(i)
        
        for (a, b, c) in zip(invoice_array, frete_array, real_array):    
            resultado = calc(a,b,c)
            xlsx_array.append(resultado)

        
        window['-TABLE-'].update(values=xlsx_array)
        
    
    if event == 'Clear' and arq == '':
        window['-TABLE-'].Update('')
        if len(resultado_array)<=1:
            del(resultado_array[0])
        else:
            resultado_array.pop()
    if event == 'Reset':
        window['-TABLE-'].Update('')
        resultado_array.clear() 
    
    if event == 'Exportar XLSX':
        xlsx_frame = pd.DataFrame(resultado_array, columns=headings)
        hoje = datetime.datetime.now()
        str_hoje =  hoje.strftime("%Y_%m_%d %H_%M_%S")
        xlsx_frame.to_excel(f'{str_hoje}.xlsx')
    

window.close()





