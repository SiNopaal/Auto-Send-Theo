from eth_account import Account
import concurrent.futures
from colorama import Fore, Style

def generate_addresses(count, filename="address.txt"):
    """Menghasilkan alamat Ethereum dan menyimpannya ke file secara lebih efisien."""
    addresses = []
    
    def create_address(_):
        return Account.create().address
    
    # Menggunakan ThreadPoolExecutor untuk mempercepat pembuatan alamat
    with concurrent.futures.ThreadPoolExecutor() as executor:
        addresses = list(executor.map(create_address, range(count)))
    
    # Simpan ke file secara batch untuk efisiensi I/O
    with open(filename, "a") as file:
        file.writelines(address + "\n" for address in addresses)
    
    print(Fore.GREEN + f"{count} Address berhasil dibuat dan disimpan di {filename}" + Style.RESET_ALL)
    return addresses

if __name__ == "__main__":
    jumlah = int(input(Fore.CYAN + "Masukkan jumlah Address yang ingin dibuat: " + Style.RESET_ALL))
    generate_addresses(jumlah)
