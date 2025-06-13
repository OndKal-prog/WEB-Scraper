Tento Python program funguje jako **web scraper**, který stahuje data o volbách z webu [volby.cz](http://volby.cz) a ukládá je do souboru ve formátu CSV.
---
### Jak program spustit:

Program se spouští z příkazové řádky se dvěma argumenty:
1.  **URL adresa:** Odkaz na webovou stránku s přehledem obcí pro dané volby.
2.  **Název souboru:** Cesta a název CSV souboru, do kterého se uloží výsledky.

## Příklad vstupu

```bash
python webScraper.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" "vysledky_okres_prostejov_2017.csv"
```

V tomto příkladu:
* `python webScraper.py` spustí program.
* `"https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"` je **URL adresa** odkazující na výsledky voleb pro okres Prostějov v Olomouckém kraji v roce 2017.
* `"vysledky_jihocesky_kraj_2017.csv"` je **název výstupního souboru**, do kterého budou data uložena.

Je důležité, aby **URL adresa byla uzavřena v uvozovkách**, zejména pokud obsahuje speciální znaky jako `&`, aby ji systém interpretoval jako jeden argument.



---
### Jak program funguje:


Po spuštění program provede následující kroky:

1.  **Načtení hlavní stránky:** Nejprve stáhne HTML obsah zadané URL adresy. Z této stránky pak zjistí **seznam všech obcí** v daném územním celku, včetně jejich čísel a názvů. Během tohoto kroku se dynamicky extrahují parametry jako kraj (`xkraj`) a typ voleb (`xvyber`) z hlavní URL, aby se zajistilo, že navazující dotazy budou správné.

2.  **Získání detailních dat pro každou obec:** Pro každou nalezenou obec program sestaví novou URL adresu, která vede na její detailní volební výsledky. Poté navštíví každou z těchto stránek a extrahuje konkrétní informace:
    * **Počet voličů**
    * **Počet odevzdaných obálek**
    * **Počet platných hlasů**
    * **Rozdělení hlasů pro jednotlivé politické strany**.
    Mezi jednotlivými dotazy na web server je přidána krátká pauza (0.5 sekundy), aby nedošlo k jeho přetížení a aby se předešlo zablokování scraperu.

3.  **Zpracování a ukládání dat:**
    * Všechna sebraná data se shromažďují do interních seznamů.
    * Názvy všech nalezených politických stran jsou ukládány do sady (`set`), což zaručuje jejich unikátnost a slouží k vytvoření dynamických hlaviček v CSV souboru.
    * Nakonec program vytvoří CSV soubor s názvem zadaným jako argument. První sloupce obsahují obecné informace o obci (číslo, název, počet voličů, obálek, platných hlasů), zatímco další sloupce dynamicky reprezentují hlasy pro jednotlivé politické strany. Pokud strana v dané obci nezískala žádné hlasy nebo nebyla v daných volbách aktivní, je hodnota nastavená na "0".

Program je navržen tak, aby byl robustní, s ošetřením chyb pro problémy s připojením, timeouty a chybějícími daty na webových stránkách. V případě jakékoli chyby vypíše příslušnou zprávu do konzole.
