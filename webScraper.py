"""
Web Scraper
Autor: Ondřej Kalivoda, 3.A
email: Kaliv15522@mot.sps-dopravni.cz
"""

import requests
import bs4 as bs
import csv
import sys
import time
from urllib.parse import urlparse, parse_qs

cisla_obci = []
nazvy_obci = []
pocty_volicu = []
pocty_obalek = []
pocty_valid_obalek = []

vsechny_hlasy_stran_za_obce = []

nazvy_stran = set()

def scrape(odkaz, nazev_vystupniho_souboru):
    print("DEBUG: Funkce scrape byla spuštěna.")
    parsed_odkaz = urlparse(odkaz)
    query_params = parse_qs(parsed_odkaz.query)

    kraj_param = query_params.get('xkraj', [''])[0]
    vyber_param = query_params.get('xvyber', [''])[0]
    print(f"DEBUG: Extrahované parametry: xkraj={kraj_param}, xvyber={vyber_param}")

    try:
        print(f"DEBUG: Pokouším se stáhnout hlavní URL: {odkaz}")
        page_response = requests.get(odkaz, timeout=10)
        page_response.raise_for_status()
        print("DEBUG: Hlavní URL úspěšně stažena.")
    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování hlavní URL '{odkaz}': {e}")
        sys.exit(1)

    soup = bs.BeautifulSoup(page_response.text, 'html.parser')

    hledam_jmeno_obce = soup.find_all("td", class_="overflow_name")
    hledam_cislo_obce = soup.find_all("td", class_="cislo")

    if not hledam_cislo_obce or not hledam_jmeno_obce:
        print("DEBUG: Na hlavní stránce nebyly nalezeny žádné obce (nebo elementy s jejich názvy/čísly).")

    for cislo_obce_element in hledam_cislo_obce:
        cisla_obci.append(cislo_obce_element.text.strip())
    for td_element in hledam_jmeno_obce:
        nazvy_obci.append(td_element.text.strip())

    print(f"Počet obcí ke zpracování: {len(cisla_obci)}")

    count = 0
    for aktualni_cislo_obce in cisla_obci:
        adresa = (
            f"https://www.volby.cz/pls/ps2017nss/ps311?"
            f"xjazyk=CZ&xkraj={kraj_param}&xobec={aktualni_cislo_obce}&xvyber={vyber_param}"
        )
        
        time.sleep(0.5)

        try:
            response = requests.get(adresa, timeout=10)
            response.raise_for_status()
            soup1 = bs.BeautifulSoup(response.text, 'html.parser')
            count += 1
            print(f"Processing obec ID: {aktualni_cislo_obce}, count: {count}")

            volice = soup1.find("td", class_="cislo", headers="sa2")
            pocty_volicu.append(volice.text.replace('\xa0', ' ').strip() if volice else "N/A")

            obalky = soup1.find("td", class_="cislo", headers="sa5")
            pocty_obalek.append(obalky.text.replace('\xa0', ' ').strip() if obalky else "N/A")

            valid_obalky = soup1.find("td", class_="cislo", headers="sa6")
            pocty_valid_obalek.append(valid_obalky.text.replace('\xa0', ' ').strip() if valid_obalky else "N/A")

            aktualni_nazvy_stran_obec = []
            aktualni_hlasy_stran_obec = []

            aktualni_nazvy_stran_obec.extend([s.text.strip() for s in soup1.find_all("td", class_="overflow_name", headers="t1sa1 t1sb2")])
            aktualni_hlasy_stran_obec.extend([h.text.replace('\xa0', ' ').strip() for h in soup1.find_all("td", class_="cislo", headers="t1sa2 t1sb3")])

            aktualni_nazvy_stran_obec.extend([s.text.strip() for s in soup1.find_all("td", class_="overflow_name", headers="t2sa1 t2sb2")])
            aktualni_hlasy_stran_obec.extend([h.text.replace('\xa0', ' ').strip() for h in soup1.find_all("td", class_="cislo", headers="t2sa2 t2sb3")])

            party_votes_for_this_obec = {}
            for j, party_name in enumerate(aktualni_nazvy_stran_obec):
                if j < len(aktualni_hlasy_stran_obec):
                    hlasy = aktualni_hlasy_stran_obec[j]
                    party_votes_for_this_obec[party_name] = hlasy
                    nazvy_stran.add(party_name)
                else:
                    party_votes_for_this_obec[party_name] = "0"

            vsechny_hlasy_stran_za_obce.append(party_votes_for_this_obec)

            print(f"  Úspěšně zpracována obec: {aktualni_cislo_obce}")

        except requests.exceptions.RequestException as e:
            print(f"Adresa nefunguje pro obec {aktualni_cislo_obce}, chyba: {adresa}")
            pocty_volicu.append("N/A")
            pocty_obalek.append("N/A")
            pocty_valid_obalek.append("N/A")
            vsechny_hlasy_stran_za_obce.append({})
            continue
        except AttributeError:
            print(f"Varování: Některá data (voliči/obálky/strany) nebyla nalezena pro obec {aktualni_cislo_obce} na {adresa}. Nastaveno na N/A.")
            pocty_volicu.append("N/A")
            pocty_obalek.append("N/A")
            pocty_valid_obalek.append("N/A")
            vsechny_hlasy_stran_za_obce.append({})
            continue
        except Exception as e:
            print(f"Nastala neočekávaná chyba při zpracování obce {aktualni_cislo_obce}: {e}")
            pocty_volicu.append("N/A")
            pocty_obalek.append("N/A")
            pocty_valid_obalek.append("N/A")
            vsechny_hlasy_stran_za_obce.append({})
            continue


    headers = ["Cislo Obce", "Nazev Obce", "Pocet Volicu", "Pocet Obalek", "Pocet Validnich Obalek"]
    dynamic_party_headers = sorted(list(nazvy_stran))
    headers.extend(dynamic_party_headers)

    try:
        with open(nazev_vystupniho_souboru, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, restval="0")

            writer.writeheader()

            pocet_obci_k_zapisu = len(cisla_obci)
            for i in range(pocet_obci_k_zapisu):
                row_data = {
                    "Cislo Obce": cisla_obci[i],
                    "Nazev Obce": nazvy_obci[i],
                    "Pocet Volicu": pocty_volicu[i],
                    "Pocet Obalek": pocty_obalek[i],
                    "Pocet Validnich Obalek": pocty_valid_obalek[i]
                }

                if i < len(vsechny_hlasy_stran_za_obce):
                    row_data.update(vsechny_hlasy_stran_za_obce[i])

                writer.writerow(row_data)

        print(f"\nData byla úspěšně uložena do souboru '{nazev_vystupniho_souboru}'")

    except IndexError as e:
        print(f"\nChyba při zápisu do CSV: Nesoulad v délce seznamů. Zkontrolujte, zda se všechny seznamy plní pro každou obec. Chyba: {e}")
    except Exception as e:
        print(f"\nNastala neočekávaná chyba při zápisu do CSV: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Použití: python nazev_skriptu.py <url_ke_scrapovani> <nazev_vystupniho_souboru.csv>")
        print("Příklad: python volby_scraper.py https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103 vysledky_voleb_2017.csv")
        sys.exit(1)

    scrape_url = sys.argv[1]
    output_filename = sys.argv[2]

    if not output_filename.endswith(".csv"):
        output_filename += ".csv"

    scrape(scrape_url, output_filename)