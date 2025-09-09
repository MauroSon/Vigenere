def vigenere_encrypt(plaintext, key):

    ciphertext = []
    key = key.upper()
    key_index = 0

    if not key.isalpha():
        raise ValueError("A chave deve conter apenas letras.")

    for char in plaintext:
        if char.isalpha():
            key_shift = ord(key[key_index]) - ord('A')
            start = ord('A') if char.isupper() else ord('a')
            char_code = ord(char) - start
            new_code = (char_code + key_shift) % 26
            ciphertext.append(chr(start + new_code))
            key_index = (key_index + 1) % len(key)
        else:
            ciphertext.append(char)
    return "".join(ciphertext)

def main():
    print("______ Cifrador Vigenère de Arquivos______")
    
    input_filename = input("Digite o nome do arquivo de entrada (ex: mensagem.txt): ")
    output_filename = input("Digite o nome do arquivo de saída (ex: cifrado.txt): ")
    keyword = input("Digite a palavra-chave: ")

    try:
        # Validação da chave
        if not keyword.isalpha() or not keyword:
            print("\nErro: A palavra-chave deve conter apenas letras e não pode ser vazia.")
            return

        # Ler o arquivo de entrada
        with open(input_filename, 'r', encoding='utf-8') as f:
            message = f.read()
        print(f"Arquivo '{input_filename}' lido com sucesso.")

        # Criptografar a mensagem
        encrypted_message = vigenere_encrypt(message, keyword)

        # Salvar o resultado no arquivo de saída
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(encrypted_message)
        
        print(f"Mensagem criptografada e salva com sucesso em '{output_filename}'.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{input_filename}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()