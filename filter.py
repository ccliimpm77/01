import requests
import xml.etree.ElementTree as ET
import gzip
import sys

def main():
    # Prova a usare l'URL diretto del file compresso
    EPG_URL = "https://www.epgitalia.tv/gzip"
    CHANNELS_FILE = "canali.txt"
    OUTPUT_FILE = "01.xml"

    # User-Agent molto realistico per evitare blocchi
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        # 1. Leggi canali.txt
        with open(CHANNELS_FILE, "r") as f:
            wanted = set(line.strip() for line in f if line.strip())
        print(f"[*] Canali da cercare: {len(wanted)}")

        # 2. Scarica il file
        print(f"[*] Scaricamento da: {EPG_URL}")
        response = requests.get(EPG_URL, headers=headers, timeout=60, allow_redirects=True)
        
        print(f"[*] Risposta del server: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[-] ERRORE: Il sito ha risposto con codice {response.status_code}")
            print("Probabilmente il sito sta bloccando GitHub. Prova a usare un altro link sorgente.")
            sys.exit(1)

        # 3. Decomprimi
        print("[*] Decompressione dati...")
        try:
            # EPGItalia a volte manda file già decompressi o GZIP
            if response.content[:2] == b'\x1f\x8b': # Firma magica dei file GZIP
                data = gzip.decompress(response.content)
            else:
                data = response.content
        except Exception as e:
            print(f"[-] Errore decompressione: {e}")
            data = response.content

        # 4. Parsing XML
        print("[*] Analisi XML (attendere)...")
        # Usiamo 'fromstring' con gestione encoding
        root = ET.fromstring(data)
        new_root = ET.Element("tv", root.attrib)

        c_count = 0
        for c in root.findall("channel"):
            if c.get("id") in wanted:
                new_root.append(c)
                c_count += 1
        
        p_count = 0
        for p in root.findall("programme"):
            if p.get("channel") in wanted:
                new_root.append(p)
                p_count += 1

        print(f"[+] Successo! Trovati {c_count} canali e {p_count} programmi.")

        # 5. Scrittura file
        ET.ElementTree(new_root).write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
        print(f"[+] File {OUTPUT_FILE} salvato.")

    except Exception as e:
        print(f"[-] ERRORE GENERALE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
