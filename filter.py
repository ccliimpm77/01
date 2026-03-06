import requests
import xml.etree.ElementTree as ET
import gzip
import sys
import io

def main():
    # URL di EPGItalia (che è un file GZ)
    EPG_URL = "https://www.epgitalia.tv/gzip"
    CHANNELS_FILE = "canali.txt"
    OUTPUT_FILE = "epg.xml"

    # 1. Impostiamo un "User-Agent" per non farci bloccare dal sito
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 2. Leggiamo i canali scelti
        with open(CHANNELS_FILE, "r") as f:
            wanted = set(line.strip() for line in f if line.strip())
        print(f"Cerco i canali: {wanted}")

        # 3. Scarichiamo il file
        print(f"Scaricamento da {EPG_URL}...")
        response = requests.get(EPG_URL, headers=headers, timeout=60)
        response.raise_for_status()

        # 4. Decomprimiamo il file GZIP
        print("Decompressione file GZIP...")
        try:
            content = gzip.decompress(response.content)
        except Exception:
            # Se il file non fosse compresso per qualche motivo, usiamo il contenuto grezzo
            content = response.content

        # 5. Analisi XML
        print("Analisi XML e filtraggio...")
        root = ET.fromstring(content)
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

        print(f"Trovati {c_count} canali e {p_count} programmi.")

        # 6. Salvataggio
        tree = ET.ElementTree(new_root)
        tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
        print(f"File {OUTPUT_FILE} creato correttamente!")

    except Exception as e:
        print(f"ERRORE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
