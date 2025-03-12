import streamlit as st
import pandas as pd
import io

def filtrar_pagamentos_numericos_e_termos(arquivo_excel, termos_excluir):
    try:
        # Carregar o arquivo Excel
        df = pd.read_excel(arquivo_excel)

        # Remover espaços extras no nome das colunas
        df.columns = df.columns.str.strip()

        # Filtrar linhas onde a primeira célula contém os termos a excluir
        mascara_termos = ~df.iloc[:, 0].str.contains('|'.join(termos_excluir), case=False, na=False)
        df_sem_termos = df[mascara_termos]

        # Filtrar onde a primeira célula é numérica
        df_filtrado = df_sem_termos[pd.to_numeric(df_sem_termos.iloc[:, 0], errors='coerce').notna()]

        # Verificar se a coluna CPF/CNPJ existe
        possiveis_nomes = ["CPF/CNPJ", "CPF", "CNPJ", "cpf/cnpj", "Cpf/Cnpj"]
        nome_coluna = next((col for col in possiveis_nomes if col in df_filtrado.columns), None)

        if nome_coluna:
            df_filtrado[nome_coluna] = df_filtrado[nome_coluna].astype(str).str.strip()

            # Adicionar zero à esquerda para CPF/CNPJ com 10 caracteres
            df_filtrado[nome_coluna] = df_filtrado[nome_coluna].apply(
                lambda x: '0' + x if x.isdigit() and len(x) == 10 else x
            )
        else:
            st.error("Coluna 'CPF/CNPJ' não encontrada! Verifique se o nome está correto.")

        return df_filtrado

    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
        return None

def main():
    st.title("Filtragem de Pagamentos")

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
                st.dataframe(df_filtrado.astype(str))

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
