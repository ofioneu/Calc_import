import PySimpleGUI as sg
import configparser
import requests
import pandas as pd

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
    

    tax_import = float(vbrl * (percent_import/100))
    tax_iof = round(vbrl * (percent_iof/100),2)

    tax_icms = round(((vbrl + tax_import)/(1-(percent_icms/100))) * (percent_icms/100),2)

    v_total_tributos = round((tax_import + tax_icms + tax_iof + tax_fix_dhl),2)

    v_total_compra = round((vbrl + v_total_tributos),2)
    
    total_produto = round((v_total_compra + (custo_real*moeda_brl)),2)
    
    return [tax_import, tax_icms, tax_iof, v_total_tributos, v_total_compra, total_produto]

resultado_array=[]


sg.theme('DarkBlue8')    # Keep things interesting for your users

headings =['TAX IMPORT', 'ICMS', 'IOF','Total Imposto', 'Preco final', 'Custo total']

layout_1 = [
          [sg.Text('PRECO REAL (USD)')],
          [sg.Input(key='-VALOR_REAL-')],
          [sg.Text('PRECO INVOICE (USD)')],      
          [sg.Input(key='-PROD_USD-')],
          [sg.Text('Frete (USD)')],
          [sg.Input(key='-FRETE_USD-')],     
          [sg.Table(values=resultado_array, headings = headings, auto_size_columns=True,
                    display_row_numbers=True,
                    justification='center',
                    key='-TABLE-',
                    row_height=20,)] ,       
          [sg.Button('CALC'), sg.Button('Clear'), sg.Button('Reset'), sg.Exit()]
          ]

layout_2 = [
    [sg.Input(key = '-XLSX-'), sg.FileBrowse('FileBrowse')],
    [sg.Table(values=resultado_array, headings = headings, auto_size_columns=True,
                    display_row_numbers=True,
                    justification='center',
                    key='-TABLE_XLSX-',
                    row_height=20,)] ,
    [sg.Button('Calcular'), sg.Button('Clear'), sg.Button('Reset'), sg.Exit()]
]      

layout = [[sg.Column(layout_1, element_justification = 'c'), sg.Column(layout_2, element_justification = 'c', vertical_alignment = 't')]]
window = sg.Window('Calculadora importação', layout)      

while True: 
    event, values = window.read()
    
    if event == sg.WIN_CLOSED or event == 'Exit':
        break   # The Event Loop
    real, invoice, frete = values['-VALOR_REAL-'], values['-PROD_USD-'], values['-FRETE_USD-']
    
    if real and invoice and frete:
        prod_usd = float(values['-PROD_USD-'])
        frete_usd = float(values['-FRETE_USD-'])
        v_real_produto = float(values['-VALOR_REAL-'])
        resultado = calc(prod_usd,frete_usd, v_real_produto)
    else:
        pass
    
    if event == 'CALC':
        resultado_array.append(resultado)        
        window['-TABLE-'].update(values=resultado_array)
    
    if event == 'Clear':
        window['-TABLE-'].Update('')
        if len(resultado_array)<=1:
            del(resultado_array[0])
        else:
            resultado_array.pop()
    if event == 'Reset':
        window['-TABLE-'].Update('')
        resultado_array.clear()
    
    if event == 'Calcular':
        patch_xlsx = values['-XLSX-']
        xlsx = pd.read_excel(patch_xlsx) # abre o arquivo xlsx
        frame = pd.DataFrame(xlsx)
        invoice_array = []
        frete_array = []
        real_array = []
        xlsx_array =[]
        for i in frame['USD'].dropna():
            invoice_array.append(i)
        
        for i in frame['FRETE'].dropna():
            frete_array.append(i)
        
        for i in frame['PRECO REAL'].dropna():
            real_array.append(i)
        
        for (a, b, c) in zip(invoice_array, frete_array, real_array):    
            resultado = calc(a,b,c)
            xlsx_array.append(resultado)
        window['-TABLE_XLSX-'].update(values=xlsx_array)
        
            
    
        


window.close()





