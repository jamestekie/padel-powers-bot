# Analýza otázek Hospodského kvízu

Rozbor otázek z webu hospodskykviz.cz za období 26. 6. 2025 až 5. 11. 2026. Cílem je zjistit, co se vyplatí učit.

## Odkud data jsou

Web u každého týmu veřejně ukazuje detail každého odehraného večera. U každé otázky je vidět prvních 30 znaků zadání, oficiální správná odpověď a po rozkliknutí celostátní úspěšnost. Plné znění otázek web neukazuje.

Stáhl jsem večery dvou silných pražských týmů a sloučil je.

| Údaj | Hodnota |
|---|---|
| Různých kvízů | 80 |
| Z toho běžných týdenních | 68 |
| Z toho speciálů a finále | 12 |
| Otázek celkem | 3 975 |
| Otázek v běžných kvízech | 3 375 |
| Otázek s celostátní úspěšností | 3 973 |

Soubory:

- `data/otazky.csv` obsahuje všechny otázky se začátkem zadání, odpovědí, kategorií a úspěšností.
- `data/temata.csv` obsahuje všechna témata s kategorií a průměrnou úspěšností.
- `KATALOG_TEMAT.md` je čitelný seznam témat podle kategorií, seřazený od nejtěžších.
- `scripts/` obsahuje skripty pro stažení a zpracování.

Omezení dat:

- Kategorie přiřadil jazykový model podle začátků otázek a odpovědí. Nejsou to oficiální tematické ligy pořadatele.
- Číselné doplňovačky a 56. otázka v datech nejsou.
- Z úryvku a odpovědi jde celou otázku zrekonstruovat u 11 % otázek. U dalších 69 % je jasné téma a fakt. U 20 % nejde nic, protože odpověď je jen písmeno nebo přiřazení.

## Stavba večera

Večer má 10 témat po 5 otázkách. Pořadí je z velké části pevné.

| Téma | Co tam bývá | Průměrná úspěšnost |
|---|---|---|
| 1 | Aktuality, vždy | 65 % |
| 2 | Vědomostní téma | 59 % |
| 3 | Slovní hříčky a logika, ve 2 ze 3 kvízů | 72 % |
| 4 | Vědomostní téma, často film nebo zeměpis | 60 % |
| 5 | Vědomostní téma, často gastronomie | 63 % |
| 6 | Poslechové nebo audiovizuální, v 96 % kvízů | 62 % |
| 7 | Vědomostní téma | 59 % |
| 8 | Vědomostní téma | 62 % |
| 9 | Vědomostní téma nebo všehochuť se společným klíčem | 60 % |
| 10 | Volnější téma, někdy iKNOW za 3 body | 61 % |

Tři z deseti témat jsou tedy předem známá: aktuality, hříčky a poslech. Tvoří 30 % bodů.

Průměrný tým získá 31 bodů z 50. Špičkové pražské týmy mají 40 až 50.

## Váha kategorií

Podíl otázek v běžných týdenních kvízech. Sloupec „ztráta“ říká, kolik bodů za večer v dané kategorii nechá průměrný tým ležet. Je to hlavní ukazatel, kde se dá nejvíc získat.

| Kategorie | Otázek na večer | Podíl | Úspěšnost | Ztráta bodů | Podíl těžkých otázek |
|---|---|---|---|---|---|
| Film a seriály | 6,6 | 13,2 % | 64 % | 2,4 | 12 % |
| Hudba | 5,3 | 10,7 % | 62 % | 2,0 | 11 % |
| Aktuality | 5,0 | 10,1 % | 65 % | 1,8 | 10 % |
| Společnost | 4,4 | 8,9 % | 62 % | 1,7 | 17 % |
| Příroda | 4,3 | 8,7 % | 61 % | 1,7 | 19 % |
| Zeměpis | 4,0 | 8,0 % | 62 % | 1,5 | 12 % |
| Sport | 3,1 | 6,3 % | 59 % | 1,3 | 19 % |
| Historie | 3,1 | 6,3 % | 59 % | 1,3 | 17 % |
| Slovní hříčky a logika | 2,9 | 5,9 % | 72 % | 0,8 | 9 % |
| Gastronomie | 2,9 | 5,8 % | 64 % | 1,1 | 17 % |
| Věda a technika | 2,8 | 5,6 % | 58 % | 1,2 | 21 % |
| Literatura a jazyk | 2,4 | 4,9 % | 60 % | 1,0 | 19 % |
| Umění a kultura | 1,9 | 3,8 % | 62 % | 0,7 | 15 % |
| Hry a popkultura | 1,0 | 1,9 % | 55 % | 0,4 | 15 % |

Těžká otázka znamená celostátní úspěšnost pod 35 %.

Co z tabulky plyne:

- **Popkultura rozhoduje.** Film, seriály a hudba dávají dohromady skoro čtvrtinu bodů. S aktualitami a společností je to 43 %.
- **Školní znalosti jsou menšina.** Historie, zeměpis, příroda, věda a literatura dávají dohromady 33 %.
- **Obtížnost je vyrovnaná.** Kategorie se liší jen mezi 55 a 65 %. Rozhoduje tedy váha, ne obtížnost.
- **Váhy jsou stabilní.** Mezi druhým pololetím 2025 a rokem 2026 se podíly kategorií liší nejvýš o 4 procentní body.

## Otázky se neopakují

Mezi 80 kvízy se opakovaly jen 3 otázky. Učit se staré otázky nazpaměť tedy nemá smysl. Opakují se ale typy témat a okruhy odpovědí.

Témata, která se vracejí nejčastěji: vlajky, Maďarsko, zvířata podle fotek, horory, přezdívky, národní sporty, olympijské hry, sportovní trofeje, pohřbívání, antická rčení, Simpsonovi, coververze, videoklipy, snídaně, sázení a hazard.

Nejčastější odpovědi jsou státy: Francie, Brazílie, Japonsko, Itálie, Belgie, severské země, Nový Zéland.

## Formáty otázek

| Formát | Otázek na večer | Úspěšnost |
|---|---|---|
| Výběr z možností A až D | 5,7 | 58 % |
| Přiřazování čtyř dvojic | 2,8 | 57 % |
| Otázka k obrázku, podle textu zadání | nejméně 2,9 | 61 % |
| Půlbodová otázka se dvěma částmi | 10,5 | |
| iKNOW | téma jen v 1 z 20 kvízů | 32 % |

Každá pátá otázka dává půl bodu za částečnou odpověď. Vyplatí se proto vždy napsat aspoň jednu část.

## Aktuality

První téma je vždy 5 otázek z posledního týdne. Zadání nejčastěji začíná slovy „Minulý týden“ nebo dnem v týdnu.

Složení podle obsahu:

- asi 47 % politika, společnost, celebrity a kuriozity
- asi 19 % sport
- asi 10 % film a televize
- zbytek věda, příroda, hudba a hry

Typická otázka se neptá na hlavní zprávu, ale na detail nebo kuriozitu z ní. Příklady odpovědí: eskalátor u Donalda Trumpa, lanovka na Petřín, 3D tisk kaple v Litomyšli.

## Doporučená příprava

Seřazeno podle poměru zisku a námahy.

1. **Aktuality, každý týden 30 až 45 minut.** Je to 5 jistých otázek a průměrný tým z nich ztrácí 1,8 bodu. Projít týdenní shrnutí zpráv, sportovní výsledky s českou stopou, premiéry filmů a seriálů, bulvár a kuriozity. Číst dva až tři dny před kvízem.
2. **Film a seriály.** Největší kategorie. Nejčastější okruhy: české filmy a herci, hlášky, kultovní filmy 80. a 90. let, horory, seriály ze streamovacích služeb, Simpsonovi, večerníčky. Těžká bývají témata o tvůrcích a adaptacích.
3. **Hudba a poslech.** Šesté téma je skoro vždy poslech. Ukázky spojuje společné slovo nebo motiv. Opakují se česká i slovenská popová scéna, světové hity po roce 2000, rockové kapely a filmová hudba. Pomůže poslouchat žebříčky hitů po dekádách a umět interpreta i název.
4. **Slovní hříčky.** Třetí téma je ve dvou ze tří kvízů hříčka. Úspěšnost je vysoká, takže chyba tu stojí pořadí. Trénovat přesmyčky, slova ukrytá v textu, doplňování písmen a homonyma.
5. **Příroda.** Nejvíc těžkých otázek mezi velkými kategoriemi. Opakuje se poznávání zvířat z fotek, česká fauna a flóra, lidské tělo. Vyplatí se atlas českých zvířat, hub a rostlin.
6. **Zeměpis.** Vlajky, obrysy států, hlavní města, sousedé států, česká místa a památky. Dobře se učí z kartiček.
7. **Společnost.** Roztříštěná kategorie, cíleně se učí špatně. Nejvíc pomůže obecný přehled o politice, značkách a celebritách.
8. **Sport a historie.** Menší váha, ale nižší úspěšnost. Ve sportu olympijské hry, trofeje, národní sporty a čeští sportovci. V historii české dějiny 20. století, antika a kuriozity.

Pro tým platí jednoduché pravidlo: rozdělit si kategorie tak, aby film, hudbu, aktuality a přírodu měl každou někdo na starost.
