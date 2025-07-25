import requests
import json
import sys

# --- KONFIGURASI ---
# URL sumber untuk mengambil data IP dan Domain.
IP_CIDR_URL = "https://raw.githubusercontent.com/HybridNetworks/whatsapp-cidr/main/WhatsApp/whatsapp_cidr_ipv4.txt"
DOMAIN_LIST_URL = "https://raw.githubusercontent.com/HybridNetworks/whatsapp-cidr/main/WhatsApp/whatsapp_domainlist.txt"
OUTPUT_JSON_FILE = "rules/whatsapp_rules.json"

def fetch_data_from_url(url):
    """
    Mengambil konten teks dari sebuah URL.
    Mengembalikan None jika terjadi kesalahan.
    """
    try:
        response = requests.get(url, timeout=15) # Menambahkan timeout 15 detik
        response.raise_for_status()  # Akan memunculkan error untuk status HTTP 4xx/5xx
        print(f"Berhasil mengambil data dari: {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"GAGAL mengambil data dari {url}: {e}", file=sys.stderr)
        return None

def parse_list(content, comment_char='#'):
    """
    Mem-parsing konten teks menjadi sebuah list, mengabaikan baris komentar dan baris kosong.
    """
    if not content:
        return []
    
    parsed_items = []
    for line in content.splitlines():
        # Menghapus spasi di awal/akhir baris
        stripped_line = line.strip()
        # Mengabaikan baris yang kosong atau yang diawali dengan karakter komentar
        if stripped_line and not stripped_line.startswith(comment_char):
            parsed_items.append(stripped_line)
            
    return parsed_items

def main():
    """
    Fungsi utama untuk menjalankan proses pengambilan, pem-parsingan, dan penyimpanan data.
    """
    print("Memulai proses pembaruan aturan WhatsApp...")
    
    # Mengambil dan mem-parsing IP CIDR
    print("Mengambil daftar IP CIDR...")
    ip_content = fetch_data_from_url(IP_CIDR_URL)
    
    # Mengambil dan mem-parsing Domain
    print("Mengambil daftar Domain...")
    domain_content = fetch_data_from_url(DOMAIN_LIST_URL)

    # Memeriksa apakah pengambilan data berhasil sebelum melanjutkan
    if ip_content is None or domain_content is None:
        print("\nProses dihentikan karena satu atau lebih file sumber gagal diunduh.", file=sys.stderr)
        sys.exit(1) # Keluar dari skrip dengan status error

    ip_cidrs = parse_list(ip_content)
    print(f"Ditemukan {len(ip_cidrs)} IP CIDR yang valid.")

    domains = parse_list(domain_content)
    print(f"Ditemukan {len(domains)} domain yang valid.")

    # Membuat struktur data JSON sesuai format yang diinginkan
    output_data = {
        "version": 2,
        "rules": [
            {
                # Menggunakan sorted() agar urutan data di file JSON selalu konsisten
                "domain_suffix": sorted(domains),
                "ip_cidr": sorted(ip_cidrs)
            }
        ]
    }

    # Menyimpan data ke file JSON
    try:
        with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        print(f"Berhasil menyimpan aturan ke file: {OUTPUT_JSON_FILE}")
    except IOError as e:
        print(f"Gagal menulis ke file {OUTPUT_JSON_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nProses pembaruan selesai dengan sukses.")

if __name__ == "__main__":
    main()
