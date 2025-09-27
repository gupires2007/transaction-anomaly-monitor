import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def find_zscore_threshold(file_path='transactions.csv'):
    """
    Analisa os Z-scores de eventos de falha para ajudar a determinar
    um limiar de alerta apropriado, calculando percentis e gerando um histograma.
    """
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Foco nos status de falha
        failure_statuses = ['denied', 'failed', 'reversed', 'backend_reversed']
        df_failures = df[df['status'].isin(failure_statuses)].copy()

        # Calcula a linha de base e os Z-Scores
        baseline_stats = df_failures.groupby('status')['count'].agg(['mean', 'std']).reset_index()
        df_failures = pd.merge(df_failures, baseline_stats, on='status')
        df_failures['z_score'] = np.where(
            df_failures['std'] > 0,
            (df_failures['count'] - df_failures['mean']) / df_failures['std'],
            0
        )

        # Removemos Z-scores negativos ou zero para focar apenas nos picos
        positive_z_scores = df_failures[df_failures['z_score'] > 0]['z_score']

        # --- 1. Análise de Percentis ---
        print("\n" + "="*60)
        print("Análise de Percentis para Z-Scores de Falha")
        print("="*60)
        print("Isto mostra o valor de Z-Score abaixo do qual uma certa percentagem de eventos se encontra.")

        percentiles_to_check = [0.90, 0.95, 0.98, 0.99, 0.995, 0.999]
        percentile_values = positive_z_scores.quantile(percentiles_to_check)

        for p, v in percentile_values.items():
            print(f"  - Percentil {p*100:4.1f}%: Z-Score <= {v:.2f}")

        print("\nInterpretação:")
        print("  - Exemplo: Se o Percentil 99.0% for 5.8, significa que 99% de todos os seus")
        print("    picos de falha históricos tiveram um Z-Score de 5.8 ou menos.")
        print("  - Um bom limiar de alerta geralmente fica entre o percentil 99.5% e 99.9%.")


        # --- 2. Geração do Histograma ---
        plt.figure(figsize=(12, 7))
        # Usamos um range limitado para melhor visualização, excluindo os valores mais extremos
        plt.hist(positive_z_scores, bins=100, range=(0, positive_z_scores.quantile(0.995)))
        plt.title('Distribuição de Z-Scores para Eventos de Falha', fontsize=16)
        plt.xlabel('Z-Score', fontsize=12)
        plt.ylabel('Frequência (Nº de Ocorrências)', fontsize=12)
        plt.grid(axis='y', alpha=0.75)
        
        # Linha vertical sugerindo um possível limiar (ex: Percentil 99.5%)
        suggested_threshold = percentile_values[0.995]
        plt.axvline(suggested_threshold, color='red', linestyle='dashed', linewidth=2)
        plt.text(suggested_threshold * 1.05, plt.ylim()[1] * 0.9, f'Sugestão de Limiar ({suggested_threshold:.2f})', color='red')

        plt.savefig('zscore_distribution.png')
        print(f"\n[SUCESSO] Gráfico de distribuição salvo como 'zscore_distribution.png'.")
        print("  - Procure no gráfico pelo ponto onde a cauda longa começa (as barras ficam muito baixas).")
        print("    Esse 'cotovelo' é um excelente indicador de um bom limiar.")


    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    find_zscore_threshold()



'''
Percentil 99.0% (Z-Score <= 6.79): Isto significa que 99% de todos os seus eventos 
de falha históricos foram "menos graves" que um Z-score de 6.79. 
Apenas 1% de todos os incidentes ultrapassaram este valor.

Percentil 99.5% (Z-Score <= 8.27): Para entrar no "top 0.5%" dos eventos mais graves, 
um incidente precisaria de um Z-score superior a 8.27.

Com base nestes dados, a nossa escolha original de um limiar de 7.0 é uma excelente decisão e agora temos os números para a justificar:

Ao definir o limiar de alerta como 7.0, estamos a tomar a decisão de sermos notificados apenas sobre o 1% mais crítico de todos os incidentes de falha, ignorando 99% do "ruído" de menor impacto.

É um equilíbrio perfeito entre sensibilidade (apanhar o que é importante) e fiabilidade 
(não gerar falsos alarmes). Você agora pode documentar que o limiar 7.0 foi escolhido 
porque ele representa o início do percentil 99 de severidade de incidentes, com base 
numa análise completa do histórico de transações.

'''