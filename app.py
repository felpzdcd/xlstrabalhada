import streamlit as st
import pandas as pd
import io

def filtrar_pagamentos_numericos_e_termos(arquivo_excel, termos_excluir):
    """
    Filtra um arquivo Excel mantendo apenas as linhas onde a primeira célula é numérica
    e exclui linhas com termos específicos na primeira coluna.
    Adiciona um zero à esquerda em CPF/CNPJ com 10 caracteres.
    """
    try:
        # Carrega a planilha Excel a partir do BytesIO
        df = pd.read_excel(arquivo_excel)

        # Converte a primeira coluna para string (para lidar com valores mistos)
        df.iloc[:, 0] = df.iloc[:, 0].astype(str)

        # Filtra as linhas que não contêm os termos a serem excluídos
        mascara_termos = ~df.iloc[:, 0].str.contains('|'.join(termos_excluir), case=False, na=False)
        df_sem_termos = df[mascara_termos]

        # Filtra as linhas onde a primeira célula é numérica
        df_filtrado = df_sem_termos[pd.to_numeric(df_sem_termos.iloc[:, 0], errors='coerce').notna()]

        # Garante que a coluna 'CPF/CNPJ' seja tratada como string
        if 'CPF/CNPJ' in df_filtrado.columns:
            df_filtrado['CPF/CNPJ'] = df_filtrado['CPF/CNPJ'].astype(str).str.strip()

            # Adiciona um zero à esquerda em CPF/CNPJ com 10 caracteres
            df_filtrado['CPF/CNPJ'] = df_filtrado['CPF/CNPJ'].apply(lambda x: '0' + x if len(x) == 10 else x)

        return df_filtrado

    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
        return None

def main():
    st.title("Filtragem de Pagamentos")

    # Restrição de acesso
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if usuario == "tesouraria" and senha == "alcif0@":
        arquivo_excel = st.file_uploader("Carregue o arquivo Excel", type=["xls", "xlsx"])

        if arquivo_excel is not None:
            termos_excluir = [
                'ITABUNA', 'Vencimento', 'Qtde de Reg.:', 'Total da Unidade', 'ALCIR - ITABUNA',
                'ADMINISTRATIVO', 'BELO HORIZONTE', 'ALAGOAS', 'ESPIRITO SANTO', 'SAO PAULO - CAPITAL',
                'CEARA', 'RIO DE JANEIRO', 'PARANÁ', 'RIO GRANDE DO SUL', 'SAO PAULO - INTERIOR',
                'ITABUNA - ALCIR FREITAS ME', 'MATO GROSSO DO SUL', 'SANTA CATARINA', 'MATO GROSSO',
                'PARAÍBA', 'PIAUÍ', 'RORAIMA', 'SUB - 3RN INTERMEDIACOES DE NEGOCIOS LTDA - PAN',
                'FREI INOCÊNCIO', 'ALPERCATA', 'SUB - SPERANDIO SOLUCOES LTDA - C6',
                'SUB - 3RN INTERME. DE NEGOCIOS LTDA - C6', 'SUB - SPERANDIO SOLUCOES LTDA - FACTA'
            ]

            df_filtrado = filtrar_pagamentos_numericos_e_termos(arquivo_excel, termos_excluir)

            if df_filtrado is not None:
                st.write("DataFrame filtrado:")
                st.dataframe(df_filtrado.astype(str)) # Garante a conversão para string antes de exibir

                # Opção para baixar o arquivo filtrado
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_filtrado.to_excel(writer, index=False)
                output.seek(0)
                st.download_button(
                    label="Baixar arquivo filtrado",
                    data=output,
                    file_name="pagamentos_filtrados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    elif usuario and senha:
        st.error("Usuário ou senha incorretos.")

if __name__ == "__main__":
    main()
