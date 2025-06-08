# memory.py

from hamming import calculate_parity_bits, inject_error

class Memory:
    def __init__(self):
        self.storage = {}

    def write(self, address: int, data_bits: str):
        """
        Adrese veri yaz. Hamming kodu hesaplanır ve saklanır.
        Veri uzunluğu 8, 16 veya 32 bit olabilir.
        """
        data_length = len(data_bits)
        if data_length not in [8, 16, 32] or not all(c in '01' for c in data_bits):
            raise ValueError(f"{data_length} bitlik veri geçerli değil. 8, 16 veya 32 bit olmalı ve sadece 0/1 içermelidir.")
        
        encoded = calculate_parity_bits(data_bits)
        self.storage[address] = encoded
        return encoded

    def read(self, address: int):
        """
        Adresteki kodlanmış veriyi döndürür. Yoksa None.
        """
        return self.storage.get(address, None)

    def inject_error(self, address: int, bit_position: int):
        """
        Adresteki veriye hata (bit flip) uygular.
        """
        if address not in self.storage:
            raise ValueError("Belirtilen adreste veri yok.")
        
        current_code = self.storage[address]
        corrupted = inject_error(current_code, bit_position)
        self.storage[address] = corrupted
        return corrupted

    def get_all_memory(self):
        """
        Bellekteki tüm verileri adreslerle birlikte döndürür.
        """
        return dict(self.storage)