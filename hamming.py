# hamming.py

def get_parity_bit_count(data_length):
    """
    Veri uzunluğuna göre gerekli parite biti sayısını hesaplar.
    2^p >= d + p + 1 kuralını kullanır.
    """
    p = 0
    while (2**p) < (data_length + p + 1):
        p += 1
    return p

def calculate_parity_bits(data_bits):
    """
    Verilen ikilik veri bitleri için Hamming SEC-DED kodunu hesaplar.
    Dinamik olarak parite biti sayısını belirler ve global parite ekler.
    """
    data_length = len(data_bits)
    parity_count = get_parity_bit_count(data_length)
    
    # Toplam Hamming kodu uzunluğu (veri + parite)
    total_encoded_length = data_length + parity_count
    hamming_code_list = ['x'] * (total_encoded_length + 1) # 1-based index için fazladan bir eleman

    # Veri bitlerini doğru pozisyonlara yerleştir
    data_bit_index = 0
    for i in range(1, total_encoded_length + 1):
        if not (i & (i - 1) == 0): # Eğer i 2'nin kuvveti değilse (parite biti değilse)
            hamming_code_list[i] = data_bits[data_bit_index]
            data_bit_index += 1

    # Parite bitlerini hesapla
    for p_pos_power in range(parity_count):
        p = 2**p_pos_power
        count = 0
        for i in range(1, total_encoded_length + 1):
            if (i & p) != 0 and hamming_code_list[i] == '1':
                count += 1
        hamming_code_list[p] = '1' if count % 2 != 0 else '0'

    # Tüm bitlerin XOR'u ile global parite bitini hesapla (1-based indexler dahil)
    final_hamming_without_global = ''.join(hamming_code_list[1:])
    total_ones_for_global_parity = sum(1 for bit in final_hamming_without_global if bit == '1')
    global_parity_bit = '1' if total_ones_for_global_parity % 2 != 0 else '0'
    
    return final_hamming_without_global + global_parity_bit

def inject_error(code, bit_position):
    """ Belirtilen bit pozisyonunu tersine çevir (1-based) """
    if bit_position < 1 or bit_position > len(code):
        # Bu hata main.py'de yakalanıyor, burada sadece orijinal kodu döndür.
        return code 
    code_list = list(code)
    code_list[bit_position - 1] = '0' if code_list[bit_position - 1] == '1' else '1'
    return ''.join(code_list)

def detect_and_correct(code):
    """ 
    Hamming SEC-DED kodunu kullanarak hata tespiti ve düzeltme yapar.
    Tek bit hatalarını düzeltir, çift bit hatalarını tespit eder.
    """
    original_code = list(code) 
    
    # Global parite bitini ayır (son bit)
    global_parity_bit_val = original_code[-1]
    encoded_bits = original_code[:-1] # Kodlanmış kısım (veri + parite)

    total_encoded_length = len(encoded_bits) # Veri + parite bitlerinin uzunluğu
    
    # Parite bit pozisyonlarını dinamik olarak belirle
    parity_positions = []
    p_power = 0
    while (2**p_power) <= total_encoded_length:
        parity_positions.append(2**p_power)
        p_power += 1
    
    syndrome = 0
    
    for p in parity_positions:
        count = 0
        for i in range(1, total_encoded_length + 1): # 1-based index
            if (i & p) != 0 and encoded_bits[i - 1] == '1': # encoded_bits 0-based
                count += 1
        if count % 2 != 0:
            syndrome += p

    # Global parite kontrolü
    total_ones_in_encoded = sum(1 for bit in encoded_bits if bit == '1')
    has_global_parity_error = (total_ones_in_encoded + int(global_parity_bit_val)) % 2 != 0

    corrected_code = original_code.copy()
    error_type = "No Error"

    if syndrome == 0 and not has_global_parity_error:
        error_type = "No Error"
    elif syndrome == 0 and has_global_parity_error:
        # Syndrome 0 ama global parite hatalı ise: Çift hata
        error_type = "Double Bit Error Detected" 
    elif syndrome != 0 and not has_global_parity_error:
        # Syndrome sıfır değil ama global parite hatalı değilse: Çift hata
        error_type = "Double Bit Error Detected"
    elif syndrome != 0 and has_global_parity_error:
        # Syndrome sıfır değil ve global parite hatalı ise: Tek bit hatası
        error_type = f"Single Bit Error at position {syndrome}"
        # Düzelt (index-1 çünkü Python 0-based)
        if 1 <= syndrome <= len(corrected_code): 
            corrected_code[syndrome - 1] = '0' if corrected_code[syndrome - 1] == '1' else '1'
        else:
            error_type = f"Warning: Syndrome ({syndrome}) out of bounds for code length {len(corrected_code)}. Error type may be ambiguous."
            
    return ''.join(corrected_code), syndrome, error_type