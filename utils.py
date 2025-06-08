# utils.py

def is_valid_binary_string(s, expected_lengths=None):
    """
    Verilen string sadece 0 ve 1'lerden oluşuyor mu?
    (isteğe bağlı olarak beklenen uzunluk listesi kontrolü)
    """
    if not isinstance(s, str) or not all(c in '01' for c in s):
        return False
    if expected_lengths is not None:
        if isinstance(expected_lengths, int): # Eğer tek bir sayı bekleniyorsa
            return len(s) == expected_lengths
        elif isinstance(expected_lengths, list): # Eğer liste olarak uzunluklar bekleniyorsa
            return len(s) in expected_lengths
    return True

def format_hamming_code(code):
    """
    Hamming kodunu parçalara ayırarak okunabilir hale getir.
    Dinamik olarak parite (P) ve veri (D) bitlerini etiketler.
    Global parite (GP) en sondadır.
    """
    if not code:
        return "Boş Kod"
    
    if len(code) < 1: 
        return code

    # Global parite bitini ayır (son bit)
    global_parity_bit = code[-1]
    encoded_part = code[:-1] # Veri ve diğer parite bitleri (1-based index gibi düşünülecek)

    # Parite bit pozisyonlarını bul (2'nin kuvvetleri)
    parity_positions = []
    p_power = 0
    while (2**p_power) <= len(encoded_part):
        parity_positions.append(2**p_power)
        p_power += 1
    
    formatted_parts = []
    data_bit_counter = 1
    
    for i in range(1, len(encoded_part) + 1): # 1-based index
        bit = encoded_part[i-1] # Python 0-based index
        if i in parity_positions:
            formatted_parts.append(f"P{i}:{bit}")
        else:
            formatted_parts.append(f"D{data_bit_counter}:{bit}")
            data_bit_counter += 1
            
    formatted_parts.append(f"GP:{global_parity_bit}")
    return ' '.join(formatted_parts)


def binary_to_hex(bin_str):
    """İkilik diziyi hexadecimal stringe dönüştür"""
    if not bin_str:
        return ""
    try:
        return hex(int(bin_str, 2))
    except ValueError:
        return "Geçersiz ikilik"

def hex_to_binary(hex_str, bit_length=8):
    """Hexadecimal stringi ikili stringe çevir"""
    if not hex_str:
        return ""
    try:
        return bin(int(hex_str, 16))[2:].zfill(bit_length)
    except ValueError:
        return "Geçersiz heksadesimal"