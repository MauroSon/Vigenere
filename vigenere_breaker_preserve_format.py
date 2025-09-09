# Vigenère Breaker para Thonny
# Lê texto cifrado do arquivo "ciphertext.txt"

LANG = "EN"  # pode ser "EN" ou "PT"

# --- Frequências esperadas do inglês ---
EN_FREQ = {
 'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04253, 'E': 0.12702,
 'F': 0.02228, 'G': 0.02015, 'H': 0.06094, 'I': 0.06966, 'J': 0.00153,
 'K': 0.00772, 'L': 0.04025, 'M': 0.02406, 'N': 0.06749, 'O': 0.07507,
 'P': 0.01929, 'Q': 0.00095, 'R': 0.05987, 'S': 0.06327, 'T': 0.09056,
 'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150, 'Y': 0.01974,
 'Z': 0.00074
}

PT_FREQ = {
    'A': 0.1463, 'B': 0.0104, 'C': 0.0388, 'D': 0.0499, 'E': 0.1257,
    'F': 0.0102, 'G': 0.0130, 'H': 0.0128, 'I': 0.0618, 'J': 0.0040,
    'K': 0.0002, 'L': 0.0278, 'M': 0.0474, 'N': 0.0505, 'O': 0.1073,
    'P': 0.0252, 'Q': 0.0120, 'R': 0.0653, 'S': 0.0781, 'T': 0.0434,
    'U': 0.0463, 'V': 0.0167, 'W': 0.0001, 'X': 0.0021, 'Y': 0.0001,
    'Z': 0.0047
}

ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# --- Funções auxiliares ---
def clean_text(s):
    """Remove tudo que não é letra e converte para maiúsculas"""
    result = []
    for char in s:
        if 'A' <= char <= 'Z' or 'a' <= char <= 'z':
            result.append(char.upper())
    return ''.join(result)

def count_occurrences(text):
    """Conta ocorrências de cada caractere"""
    counts = {}
    for char in text:
        if char in counts:
            counts[char] += 1
        else:
            counts[char] = 1
    return counts

# --- Exame de Kasiski ---
def find_repeated_sequences(cipher, min_len=3, max_len=5):
    """Encontra sequências repetidas no texto cifrado"""
    positions = {}
    n = len(cipher)
    
    for L in range(min_len, max_len + 1):
        for i in range(n - L + 1):
            seq = cipher[i:i+L]
            if seq not in positions:
                positions[seq] = []
            positions[seq].append(i)
    
    # Filtra apenas sequências que aparecem mais de uma vez
    repeated = {}
    for seq, pos_list in positions.items():
        if len(pos_list) > 1:
            repeated[seq] = pos_list
    
    return repeated

def kasiski_examination(cipher):
    """Realiza o exame de Kasiski para encontrar possíveis tamanhos de chave"""
    repeated = find_repeated_sequences(cipher)
    
    distances = []
    for seq, positions in repeated.items():
        for i in range(len(positions) - 1):
            distances.append(positions[i+1] - positions[i])
    
    # Conta fatores comuns nas distâncias
    factor_count = {}
    for d in distances:
        for f in range(2, 51):
            if d % f == 0:
                if f in factor_count:
                    factor_count[f] += 1
                else:
                    factor_count[f] = 1
    
    # Ordena fatores por frequência
    sorted_factors = []
    for factor, count in factor_count.items():
        sorted_factors.append((factor, count))
    
    # Ordena em ordem decrescente de contagem
    for i in range(len(sorted_factors)):
        max_idx = i
        for j in range(i + 1, len(sorted_factors)):
            if sorted_factors[j][1] > sorted_factors[max_idx][1]:
                max_idx = j
        sorted_factors[i], sorted_factors[max_idx] = sorted_factors[max_idx], sorted_factors[i]
    
    return sorted_factors[:10]

# --- Índice de Coincidência ---
def index_of_coincidence(text):
    """Calcula o índice de coincidência de um texto"""
    n = len(text)
    if n <= 1:
        return 0.0
    
    counts = count_occurrences(text)
    total = 0
    for count in counts.values():
        total += count * (count - 1)
    
    return total / (n * (n - 1))

def average_ioc_for_keylength(cipher, k):
    """Calcula o IoC médio para um determinado tamanho de chave"""
    columns = [''] * k
    for i, char in enumerate(cipher):
        columns[i % k] += char
    
    total_ioc = 0.0
    count = 0
    for col in columns:
        if len(col) > 1:
            total_ioc += index_of_coincidence(col)
            count += 1
    
    return total_ioc / count if count > 0 else 0.0

# --- Teste Qui-Quadrado ---
def chi_squared_score(counter, total):
    """Calcula a estatística qui-quadrado para um texto"""
    score = 0.0
    for char in ALPH:
        observed = counter.get(char, 0)
        expected = EN_FREQ[char] * total
        if expected > 0:
            score += (observed - expected) ** 2 / expected
    return score

def best_shift_for_column(column_text):
    """Encontra o melhor deslocamento para uma coluna usando qui-quadrado"""
    counts = count_occurrences(column_text)
    total = len(column_text)
    
    best_shift = 0
    best_score = float('inf')
    
    for shift in range(26):
        # Calcula contagens esperadas após o deslocamento
        shifted_counts = {}
        for char in ALPH:
            original_index = (ALPH.index(char) + shift) % 26
            original_char = ALPH[original_index]
            shifted_counts[char] = counts.get(original_char, 0)
        
        score = chi_squared_score(shifted_counts, total)
        if score < best_score:
            best_score = score
            best_shift = shift
    
    return best_shift

def find_key(cipher, key_length):
    """Encontra a chave para um determinado tamanho"""
    key_shifts = []
    
    for i in range(key_length):
        # Extrai a coluna i
        column = []
        j = i
        while j < len(cipher):
            column.append(cipher[j])
            j += key_length
        
        if column:  # Só processa se a coluna não estiver vazia
            shift = best_shift_for_column(''.join(column))
            key_shifts.append(shift)
        else:
            key_shifts.append(0)  # Fallback
    
    # Converte shifts para caracteres
    key = ''.join(ALPH[shift] for shift in key_shifts)
    return key

# --- Decriptação preservando formato ---
def decrypt_vigenere_preserve_format(text, key):
    """Decripta texto preservando caracteres não-alfabéticos e case"""
    result = []
    key_index = 0
    key_length = len(key)
    
    for char in text:
        if 'A' <= char <= 'Z':
            # Caractere maiúsculo
            key_char = key[key_index % key_length]
            cipher_index = ALPH.index(char)
            key_index_val = ALPH.index(key_char)
            plain_index = (cipher_index - key_index_val) % 26
            result.append(ALPH[plain_index])
            key_index += 1
        elif 'a' <= char <= 'z':
            # Caractere minúsculo
            key_char = key[key_index % key_length].upper()
            cipher_index = ALPH.index(char.upper())
            key_index_val = ALPH.index(key_char)
            plain_index = (cipher_index - key_index_val) % 26
            result.append(ALPH[plain_index].lower())
            key_index += 1
        else:
            # Caractere não-alfabético
            result.append(char)
    
    return ''.join(result)

# --- Pontuação em inglês ---

if LANG == "EN":
    FREQ = EN_FREQ
    COMMON_WORDS = ["THE", "BE", "TO", "OF", "AND", "A", "IN", "THAT", "IS", "I",
                    "IT", "FOR", "AS", "WITH", "YOU", "DO", "AT", "THIS", "BUT", "HAVE", "NOT"]
elif LANG == "PT":
    FREQ = PT_FREQ
    COMMON_WORDS = [
        "QUE", "DE", "E", "DO", "DA", "EM", "UM", "PARA", "É", "COM",
        "NÃO", "UMA", "OS", "NO", "SE", "NA", "POR", "MAIS", "AS", "DOS",
        "COMO", "MAS", "FOI", "AO", "ELE", "À", "SUAS", "SEU", "QUEM", "OU"
    ]

def english_score(text):
    """Calcula uma pontuação indicando quão inglês o texto parece"""
    # Conta palavras comuns
    text_upper = text.upper()
    common_word_count = 0
    for word in COMMON_WORDS:
        if word in text_upper:
            common_word_count += 1
    
    # Calcula frequência de caracteres
    counts = count_occurrences(text_upper)
    total_chars = 0
    for count in counts.values():
        total_chars += count
    
    # Calcula similaridade com frequências do inglês
    freq_score = 0.0
    for char, count in counts.items():
        if char in EN_FREQ:
            expected_freq = EN_FREQ[char]
            actual_freq = count / total_chars if total_chars > 0 else 0
            freq_score += 1.0 - abs(expected_freq - actual_freq)
    
    # Combina as duas métricas
    return common_word_count + freq_score

# --- Rotina principal ---
def break_vigenere(text, max_keylength=40, top_results=5):
    """Quebra a cifra de Vigenère e retorna os melhores resultados"""
    cipher_clean = clean_text(text)
    print("Comprimento do texto (apenas letras):", len(cipher_clean))
    
    if len(cipher_clean) < 100:
        print("Aviso: Texto muito curto para análise confiável!")
    
    # Passo 1: Exame de Kasiski
    print("Executando análise Kasiski...")
    kasiski_results = kasiski_examination(cipher_clean)
    print("Candidatos de Kasiski:", kasiski_results)
    
    # Passo 2: Índice de Coincidência
    print("Calculando Índice de Coincidência...")
    ioc_results = []
    for k in range(1, max_keylength + 1):
        avg_ioc = average_ioc_for_keylength(cipher_clean, k)
        ioc_results.append((k, avg_ioc))
    
    # Ordena por IoC (maior é melhor)
    for i in range(len(ioc_results)):
        for j in range(i + 1, len(ioc_results)):
            if ioc_results[j][1] > ioc_results[i][1]:
                ioc_results[i], ioc_results[j] = ioc_results[j], ioc_results[i]
    
    print("Top 10 candidatos por IoC:", ioc_results[:10])
    
    # Combina candidatos de ambos os métodos
    candidates = set()
    for factor, _ in kasiski_results:
        candidates.add(factor)
    for k, _ in ioc_results[:10]:
        candidates.add(k)
    
    # Testa cada candidato
    results = []
    for candidate in candidates:
        if candidate > 0:
            try:
                print(f"Testando tamanho de chave: {candidate}")
                key = find_key(cipher_clean, candidate)
                plaintext = decrypt_vigenere_preserve_format(text, key)
                score = english_score(plaintext)
                results.append((score, candidate, key, plaintext))
            except Exception as e:
                print(f"Erro com tamanho {candidate}: {e}")
    
    # Ordena resultados por pontuação (maior é melhor)
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            if results[j][0] > results[i][0]:
                results[i], results[j] = results[j], results[i]
    
    return results[:top_results]

# --- Entrada do script ---
if __name__ == "__main__":
    print("=== QUEBRADOR DE CIFRA VIGENÈRE ===")
    print("Lendo arquivo 'ciphertext.txt'...")
    
    try:
        with open("Cypher.txt", "r", encoding="utf-8") as arquivo:
            texto = arquivo.read()
        print("Arquivo lido com sucesso!")
        
        print("=" * 50)
        print("Processando...")
        
        resultados = break_vigenere(texto, max_keylength=50, top_results=5)
        
        print("\n" + "=" * 60)
        print("RESULTADOS:")
        print("=" * 60)
        
        for i, (pontuacao, comprimento, chave, texto_decifrado) in enumerate(resultados, 1):
            print(f"\n--- RESULTADO {i} ---")
            print(f"Pontuação: {pontuacao:.2f}")
            print(f"Tamanho da chave: {comprimento}")
            print(f"Chave: {chave}")
            print("-" * 40)
            print("Texto decifrado:")
            print(texto_decifrado[:1000] + ("..." if len(texto_decifrado) > 1000 else ""))
            print()
            
    except FileNotFoundError:
        print("Erro: Arquivo 'ciphertext.txt' não encontrado!")
        print("Certifique-se de que o arquivo está na mesma pasta do script.")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")