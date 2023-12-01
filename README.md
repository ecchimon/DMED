Script responsável por ler arquivos xml, localizados na pasta nfs, para a geração do arquivo DMED para apresentar ao governo.
O arquivo DMED deve ser apresentado à Receita Federal todo início de ano contendo todos os pagamentos efetuados a uma instituição de saúde por Pessoas Jurídicas.
O layout do arquivo pode ser encontrado no site da Receita Federal.
O objetivo deste script é usar os arquivos xmls gerados pelo provedor de Notas Fiscais de Serviço, contendo todas as Notas Fiscais emitidas no ano e filtrar, removendo as NFs canceladas e as emitidas para pessoa jurídica.
O script separa em duas partes o trabalho.
Na primeira ele lê o(s) arquivo(s) xml e gera um arquivo csv. Na segunda etapa ele lê este arquivo csv e gera o arquivo no layout da DMED.
É importante esta primeira parte estar dividida, pois permite que voce gere relatórios para conferência.
