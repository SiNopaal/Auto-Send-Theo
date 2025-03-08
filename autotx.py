from web3 import Web3
import asyncio
import random
from colorama import Fore, Style, init
from asyncio import Semaphore, Lock

# Inisialisasi colorama
init(autoreset=True)

# Konfigurasi
rpc_url = "https://testnet-rpc1.autheo.com"  # RPC testnet
web3 = Web3(Web3.HTTPProvider(rpc_url))

# Pastikan koneksi berhasil
if not web3.is_connected():
    print(Fore.RED + "❌ Gagal terhubung ke testnet!")
    exit()

# Data transaksi
sender_address = "Youraddres"
private_key = "YourPrivateKey"

# Rentang jumlah transfer dalam Wei (misal 0.005 - 0.02 ETH)
min_amount = web3.to_wei(0.005, 'ether')
max_amount = web3.to_wei(0.02, 'ether')

with open("address.txt", "r") as file:
    receiver_addresses = [line.strip() for line in file if Web3.is_address(line.strip())]

if not receiver_addresses:
    print(Fore.RED + "❌ Tidak ada alamat penerima yang valid!")
    exit()

# Input jumlah transfer dari pengguna
transfer_count = int(input(Fore.CYAN + "Mau Berapa kali Transfer Ngabb?: " + Style.RESET_ALL))

# Semaphore untuk membatasi transaksi bersamaan
semaphore = Semaphore(5)
nonce_lock = Lock()
confirmed_txns = set()  # Menyimpan transaksi yang telah dikonfirmasi

async def send_transaction(receiver_address, index):
    """Mengirim transaksi ke alamat penerima secara berurutan."""
    global nonce
    async with nonce_lock:
        current_nonce = nonce
        nonce += 1
    
    async with semaphore:
        try:
            amount = random.randint(min_amount, max_amount) 
            transaction = {
                'to': receiver_address,
                'value': amount,
                'gas': 21000,
                'gasPrice': web3.to_wei('5', 'gwei'),
                'nonce': current_nonce,
                'chainId': 785
            }
            
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
            txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            txn_hash_hex = web3.to_hex(txn_hash)
            
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, txn_hash)
            if receipt.status == 1:
                if txn_hash_hex not in confirmed_txns:
                    confirmed_txns.add(txn_hash_hex)
                    print(Fore.GREEN + f"({index}) ✅ {receiver_address}")
                    print(Fore.YELLOW + f"    🔗 Hash: {txn_hash_hex} ✔ Done Bwaang!")
            else:
                print(Fore.GREEN + f"({index}) ✅ {receiver_address}")
                print(Fore.YELLOW + f"    🔗 Hash: {txn_hash_hex} ⚠ Transaksi gagal, tetapi sudah diproses!")
        except Exception as e:
            print(Fore.RED + f"❌ Gagal mengirim transaksi ke {receiver_address}: {e}")
            await asyncio.sleep(5)  # Mengurangi delay retry

async def main():
    """Fungsi utama untuk mengelola transaksi secara berurutan."""
    global nonce
    nonce = web3.eth.get_transaction_count(sender_address, "pending")
    
    print(Fore.MAGENTA + "==================== TRANSAKSI DIMULAI ====================")
    
    tasks = []
    index = 1
    for _ in range(transfer_count):
        for receiver in receiver_addresses:
            tasks.append(send_transaction(receiver, index))
            index += 1
    
    await asyncio.gather(*tasks)  # Menjalankan transaksi secara paralel
    
    print(Fore.MAGENTA + "==================== TRANSAKSI SELESAI ====================")

if __name__ == "__main__":
    asyncio.run(main())
