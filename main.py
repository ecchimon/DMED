import xmltodict
import os
import pandas as pd
import sys
 

def pegar_infos(nome_arquivo, valores):
    # print(f"Pegou as informações {nome_arquivo}")
    with open(f'nfs/{nome_arquivo}', "rb") as arquivo_xml:
        dic_arquivo = xmltodict.parse(arquivo_xml)
        #print(json.dumps(dic_arquivo, indent=4))
        print('Listando arquivo ', arquivo)
        
        it = 0
        # Padrão Resplendor
        lista_nf = dic_arquivo['ConsultarNfseFaixaResposta']['ListaNfse']['CompNfse']
        # Padrão Aimorés
        #lista_nf = dic_arquivo['ConsultarNfseServicoPrestadoResposta']['ListaNfse']['CompNfse'] 
        for i in lista_nf:

            # Padrão Resplendor 
            collect_nf = dic_arquivo['ConsultarNfseFaixaResposta']['ListaNfse']['CompNfse'][it]
            # Padrão Aimorés
            #collect_nf = dic_arquivo['ConsultarNfseServicoPrestadoResposta']['ListaNfse']['CompNfse'][it]
            
            valor_nf = ""
            tomador_cpf = ""
            tomador_nome = ""
            numero_nf = collect_nf["Nfse"]["InfNfse"]["Numero"]
            data_nf   = collect_nf['Nfse']["InfNfse"]["DataEmissao"]
            data_nf   = data_nf[0:10]
            valor_nf   = collect_nf['Nfse']["InfNfse"]["ValoresNfse"]["ValorLiquidoNfse"]
            if "Cpf" in collect_nf['Nfse']["InfNfse"]["DeclaracaoPrestacaoServico"]["InfDeclaracaoPrestacaoServico"]["Tomador"]["IdentificacaoTomador"]["CpfCnpj"]:
                tomador_cpf = collect_nf['Nfse']["InfNfse"]["DeclaracaoPrestacaoServico"]["InfDeclaracaoPrestacaoServico"]["Tomador"]["IdentificacaoTomador"]["CpfCnpj"]["Cpf"]
            else:
                tomador_cpf   = collect_nf['Nfse']["InfNfse"]["DeclaracaoPrestacaoServico"]["InfDeclaracaoPrestacaoServico"]["Tomador"]["IdentificacaoTomador"]["CpfCnpj"]["Cnpj"]
            tomador_nome   = collect_nf['Nfse']["InfNfse"]["DeclaracaoPrestacaoServico"]["InfDeclaracaoPrestacaoServico"]["Tomador"]["RazaoSocial"]
            tomador_nome = tomador_nome.upper()
            tomador_nome = tomador_nome.replace('.','')
            if "NfseCancelamento" in collect_nf:
                cancela_nf = "***Cancelada***"
            else:
                cancela_nf = ""
            print(it, numero_nf, data_nf, tomador_cpf, tomador_nome, valor_nf, cancela_nf)
            if len(tomador_cpf.strip()) < 14: # Apenas cpf, ignora cnpj
                if cancela_nf == '':
                    valores.append([numero_nf, data_nf, tomador_cpf, tomador_nome, valor_nf, cancela_nf])
            it = it + 1


lista_arquivos = os.listdir("nfs")

colunas = ["Nfe", "Emissao", "Cpf", "Nome", "Valor", "cancelada"]
valores = []
for arquivo in lista_arquivos:
    pegar_infos(arquivo, valores)

tabela = pd.DataFrame(columns=colunas, data=valores)
tabela.to_csv("NotasFiscais.csv", index=False)

# Encerrado a leitura dos xmls e arquivo com as notas gravados
# -------------------------------------------------------------
# Iniciando segunda parte
# Abrir o arquivo gerado e eliminar as notas fiscais de PJ
# e as canceladas
df = pd.read_csv('NotasFiscais.csv', sep = ',', encoding = ("utf-8'"), dtype={"Nfe" : "object","Emissao" : "object","Cpf" : "object", "Valor" : "float64"})
dmed = pd.DataFrame()
tamanho = len(df)
frase = 'Total de notas lidas: ' + str(tamanho)
print(frase)
valor = ''
nome = ''
cpf = ''
cancela = ''

# Linhas do cabeçalho
#Algumas informações não precisam ser preenchidas
# Dmed|Ano referência|Ano calendário|É retificadora?|Número do recibo se retificadora|Número do layout usado   
linha1 = 'Dmed|2022|2021|N||S5830B|'
# RESPO|CPF do responsável|Nome do responsável pelas informações|DDD|Telefone|Ramal|Fax|Email
linha2 = 'RESPO|CPFDORESPON|FULANO DE TAL|12|12345678||||'
# DECPJ|CNPJ da empresa|Nome da empresa|1 se prestador de serviço de saúde|Registro ANS|Registro CNES|CPF do responsável pelo CNPJ?|Especial?|Data evento|Possui registro ANS?
linha3 = 'DECPJ|12345678901234|CLINICA PROVEDORA DE SERVICO MEDICO|1||1234567|12345678901|N|||'
linha4 = 'PSS|'
# Prefixo das linhas de dados
linha5 = 'RPPSS'
# Linha de final de arquivo
linha6 = 'FIMDmed|'

#display(df[['Cpf']])
print(df)

for index, row in df.iterrows():
    #print(row)
    cpf = str(row['Cpf'])
    nome = row['Nome']
    valor = row['Valor']
    cancela = row['cancelada']
    frase = ''
    frase = 'Analisada nota: ' + str(index) + ' de: ' + str(tamanho)
    print('\r' + frase.strip(),end='')
    if len(str(cpf).strip()) < 12:
        if len(str(cancela).strip()) == 3:
            cpf = cpf.rjust(11,'0')
            #print(cpf.rjust(11,'0') ,'|', nome,'|', valor,'|',cancela)
            dmed = dmed.append({'uCpf': cpf,'uNome':nome,'uValor':valor}, ignore_index=True) 
print(dmed)              
dmedsorted = dmed.sort_values(by=['uCpf'])
dmedgrouped = dmedsorted.groupby(['uCpf','uNome']).sum().reset_index()

# Notas para a Dmed separadas e agrupadas por cpf
# --------------------------------------------------------------
# Iniciando a última parte
# Gravando o arquivo da Dmed

orig_stdout = sys.stdout
sys.stdout=open('Dmed2022.txt','w') #Local do arquivo da Dmed

print(linha1)
print(linha2)
print(linha3)
print(linha4)
for index, row in dmedgrouped.iterrows():
    ftotal = row['uValor']
    total = str("%.2f" % ftotal)
    total = total.replace('.', '')
    linha = linha5 + '|' + row['uCpf'] + '|' + row['uNome'] + '|' + total 
    print(linha)
print(linha6)
sys.stdout.close()
sys.stdout=orig_stdout 
print(' ')
print('total de notas válidas: ' + str(len(dmedsorted)))
print('total de cpfs agrupados: ' + str(len(dmedgrouped)))
print('-----------------------------------------------------------------')
print('Demed gerada com sucesso!')
