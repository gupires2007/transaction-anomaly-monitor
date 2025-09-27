import pandas as pd
import numpy as np

def analyze_transaction_anomalies(file_path='transactions.csv'):
    """
    Analisa um histórico de transações para identificar picos de falhas e quedas de aprovações,
    e apresenta um relatório unificado e cronológico dos incidentes.
    """
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # --- ANÁLISE DE PICOS DE FALHA ---
        failure_statuses = ['denied', 'failed', 'reversed', 'backend_reversed']
        df_failures = df[df['status'].isin(failure_statuses)].copy()
        baseline_stats_failures = df_failures.groupby('status')['count'].agg(['mean', 'std']).reset_index()
        df_failures = pd.merge(df_failures, baseline_stats_failures, on='status')
        df_failures['z_score'] = np.where(df_failures['std'] > 0, (df_failures['count'] - df_failures['mean']) / df_failures['std'], 0)
        failure_threshold = 7.0
        failure_anomalies = df_failures[df_failures['z_score'] > failure_threshold]

        # --- ANÁLISE DE QUEDAS DE APROVAÇÃO ---
        df_approved = df[df['status'] == 'approved'].copy()
        approved_mean = df_approved['count'].mean()
        approved_std = df_approved['count'].std()
        df_approved['z_score'] = (df_approved['count'] - approved_mean) / approved_std
        approved_threshold = -3.0
        approved_anomalies = df_approved[df_approved['z_score'] < approved_threshold]

        # --- APRESENTAÇÃO DOS RESULTADOS ---
        print("\n" + "="*60)
        print("RELATÓRIO DE ANÁLISE DE TRANSAÇÕES")
        print("="*60)

        print("\n--- Parâmetros de Linha de Base Utilizados na Análise ---\n")
        print("1. Picos de Falha (Alerta se Z-Score > 7.0):")
        print(baseline_stats_failures.to_string(index=False))
        print("\n2. Quedas de Aprovação (Alerta se Z-Score < -3.0):")
        print(f"   - Média (μ) para 'approved': {approved_mean:.4f}")
        print(f"   - Desvio Padrão (σ) para 'approved': {approved_std:.4f}")
        print("-" * 60)

        # --- NOVO: Unifica e ordena todos os alertas por data e hora ---
        # Concatena os dois dataframes de anomalias
        all_anomalies = pd.concat([failure_anomalies, approved_anomalies])

        if not all_anomalies.empty:
            # Ordena o dataframe combinado pelo timestamp
            all_anomalies_sorted = all_anomalies.sort_values(by='timestamp')
            
            print(f"\n[ALERTA] Cronologia de {len(all_anomalies_sorted)} Incidentes Detetados:\n")
            # Seleciona e exibe as colunas relevantes
            print(all_anomalies_sorted[['timestamp', 'status', 'count', 'z_score']].to_string(index=False))
        else:
            print("\n[INFO] Nenhum incidente (pico de falha ou queda de aprovação) foi detetado.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    analyze_transaction_anomalies()


    '''
    A conclusão mais importante destes dados é que diferentes status de falha têm sensibilidades 
    muito diferentes. Status failed e backend_reversed: São eventos raríssimos. 
    A média de ocorrências deles é próxima de zero (mean de 0.06 e 0.19). Por isso, 
    qualquer pequena quantidade já é um sinal de alerta extremo. Note como apenas 
    4 transações failed já geram um Z-score altíssimo de 8.26. Isso indica um evento muito grave.
Status denied: É um evento comum. A média é de quase 7 transações por minuto, 
com uma variação considerável (std de 5.34). Por isso, é necessário um volume 
muito maior (acima de 50) para que o sistema atinja um Z-score similar e seja 
considerado um incidente grave. Este é o padrão que usaremos para o monitoramento: 
o sistema de alertas precisa ser muito sensível a picos de failed e backend_reversed, 
mas mais tolerante com a variação normal de denied. A beleza do Z-score é que 
ele normaliza tudo isso para nós. 
Agora que temos um padrão claro, podemos definir um limiar de alerta. 
Com base nos seus resultados, um Z-score acima de 7.0 parece ser um excelente 
ponto de partida, pois capturaria todos esses incidentes graves que a análise histórica encontrou.

Limiar de Falha (> 7.0):

O que fizemos: Nós executámos o script de análise no seu histórico completo e 
listámos as 30 maiores anomalias. O que observámos: Naquela lista, os eventos que 
pareciam ser "incidentes reais" (como um pico súbito de transações failed ou denied) 
tinham Z-scores massivos, todos acima de 8.0. 
A Decisão: Escolhemos 7.0 como um limiar seguro e conservador. 
Ele é alto o suficiente para ignorar o "ruído" normal do sistema, mas baixo 
o suficiente para garantir que todos os incidentes graves que já aconteceram 
no seu histórico teriam sido detetados.

Limiar de Aprovação (< -3.0):

O que fizemos: Aqui, seguimos uma convenção estatística padrão para deteção de anomalias.
O que significa: Um Z-score de -3.0 significa que o valor observado está 3 
desvios padrão abaixo da média. Num sistema com distribuição normal, 
um evento como este tem uma probabilidade de acontecer de apenas 0.1%. 
É um evento estatisticamente muito raro. A Decisão: Começar com -3.0 
é uma prática recomendada. É um sinal forte de que algo está errado com o 
fluxo de aprovações e merece investigação imediata.
'''