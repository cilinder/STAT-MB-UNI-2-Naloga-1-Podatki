import xml.etree.ElementTree as ET
import csv
from numpy import random
import zipfile
import os
import random
import pandas as pd

def readData():
    data = []
    with open('DN1.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            data.append(row)
        headers = data[0]
        data = data[1:]
        results = data[-3:]
        results = [res[1:] for res in results]
        data = data[0:-3]

    return (headers, data, results)

# Using XML Moodle format
# documented here: https://docs.moodle.org/405/en/Moodle_XML_formatl

def generateTable(headers, data):
    table = '<table style="border: 1px solid black; border-collapse: collapse;">\n'
    table += '<tr>\n'
    for key in headers:
        table += f'<th style="border: 1px solid black; border-collapse: collapse;">{key}</th>\n'
    table += '</tr>\n'
    for row in data:
        table += '<tr>\n'
        for key in headers:
            table += f'<td style="border: 1px solid black; border-collapse: collapse;">{row[key]}</td>\n'
        table += '</tr>\n'

    table += '</table>\n'
    return table

def generateDataVariations(data, headers, names):
    # For each student in `names`, generate a variation of the data
    # Which is a randomly perturbed version of the original
    for name in names:
        perturbed_data = []
        for row in data:
            perturbed_data.append({
                "ID": row["ID"],
                "pnevmo": row["pnevmo"],
                "FEV1": int(row["FEV1"]) + random.normal(0,1)
            })
        with open(f'podatki/podatki_{name}.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in perturbed_data:
                writer.writerow(row)
        with zipfile.ZipFile(f'podatki/podatki_{name}.zip', 'w') as zf:
            zf.write(f'podatki/podatki_{name}.csv', arcname=f'podatki_{name}.csv')
        os.remove(f'podatki/podatki_{name}.csv')

vprasanja = [
    "Senzitivnost testa se zmanjša, specifičnost pa zveča.",
    "Senzitivnost se lahko zmanjša ali zveča, glede specifičnosti pa ne moremo podati nobenih zaključkov.",
    "Obe senzitivnost in specifičnost testa se zvečata.",
    "Senzitivnost testa se zveča, specifičnost pa zmanjša.",
    "Obe senzitivnost in specifičnost testa ostaneta nespremenjeni.",
]

def generateMoodleXML(headers, data, results):
    # Create the structure of the XML file
    quiz = ET.Element("quiz")

    for i in range(20):

        data_i = [[data[j][0], data[j][i+1]] for j in range(len(data))]
        df1 = pd.DataFrame(
            data_i,
            columns=['Pnevmo', 'FEV1'],
        )
        df1["FEV1"] = df1["FEV1"].astype(float)
        df1.to_excel(f'podatki/podatki_{i+1}.xlsx', index=False)

        question = ET.SubElement(quiz, "question")
        question.set("type", "cloze")
        name_tag = ET.SubElement(question, "name")
        name_text = ET.SubElement(name_tag, "text")
        name_text.text = f"<![CDATA[Vprašanje {i + 1}]]>"
        questiontext = ET.SubElement(question, "questiontext")
        text = ET.SubElement(questiontext, "text")

        premesana_vprasanja = ''
        abcd = ['A', 'B', 'C', 'D', 'E']
        random.shuffle(vprasanja)
        for i in range(len(vprasanja)):
            if vprasanja[i] == "Senzitivnost testa se zveča, specifičnost pa zmanjša.":
                premesana_vprasanja += f'~={abcd[i]}. {vprasanja[i]}'
            else:
                premesana_vprasanja += f'~{abcd[i]}. {vprasanja[i]}'
        
        premesana_vprasanja = premesana_vprasanja[1:]

        text.text = f'''<![CDATA[
V datoteki so podatki o 40 rudarjih iz študije “Mine workers and pneumoconiosis” (Campbell, Machin: Medical statistics. New York: Wiley, 1995). 
Podatki vključujejo izmerjeni pljučni volumen (forsirani ekspiratorni volumen; FEV1) ter status o prisotni pnevmokoniozi – bolezni pljuč
(spremenljivka pnevmo z vrednostmi da, v primeru, da je bila bolezen klinično diagnosticirana, oz. ne v primeru odsotnosti bolezni). 

Nalogo rešujte v Excelu. Ustvarite novo spremenljivko, ki bo imela vrednost da, če je FEV1 manjši ali enak 75, v nasprotnem primeru nastavi vrednost ne.
<br><br> 
<a href="https://github.com/cilinder/STAT-MB-UNI-2-Naloga-1-Podatki/raw/refs/heads/main/podatki/podatki_{i+1}.xlsx" download>Prenesi podatke</a>
<br><br>

<ol>
    <li>
        Izračunajte senzitivnost (občutljivost) in specifičnost diagnostičnega testa, ki napovede pnevmokoniozo v primeru, ko FEV1 ≤ 75. Odgovora podajte v procentih na 1 decimalko natančno, kot decimalno ločilo uporabite piko. Pri reševanju si pomagajte z vrtilno tabelo.
        <br>
        Senzitivnost: (4 točke) {{4:NUMERICAL:={results[0][i]}:0.1}} %
        <br>
        Specifičnost: (4 točke) {{4:NUMERICAL:={results[1][i]}:0.1}} %
    </li>
    <br>
    <li>
        Kolikšna je verjetnost, da vaš test, ki ga uporabite za testiranje 6 neodvisnih pacientov, ki imajo pnevmokoniozo, dejansko vseh 6 pacientov diagnosticira kot bolne? Odgovor podajte v procentih na 1 decimalko natančno, kot decimalno ločilo uporabite piko.
        <br>
        Verjetnost je: (2 točki) {{2:NUMERICAL:={results[2][i]}:0.1}} %
    </li>
    <br>
    <li>
        Senzitivnost (občutljivost) in specifičnost izračunajte še za kriterije: FEV1 ≤ 60, FEV1 ≤ 70, FEV1 ≤ 80, FEV1 ≤ 90, FEV1 ≤ 100, FEV1 ≤ 110 ter rezultate grafično predstavite s krivuljo ROC. Graf naložite v Excelovi datoteki v spletno učilnico pod razdelek DN1. (5 točk)
    </li>
    <br>
    <li>
        Kako se spremenita senzitivnost (občutljivost) in specifičnost, če namesto kriterija FEV1 ≤ 75 za klasifikacijo prisotnosti bolezni uporabimo kriterij FEV1 ≤ 80? (5 točk)
        <br>
        {{5:MCV:{premesana_vprasanja}}}
    </li>
</ol>
        ]]>'''

        shuffle_answers = ET.SubElement(question, "shuffleanswers")
        shuffle_answers.text = "0"

        # Write the XML to a file
        tree = ET.ElementTree(quiz)
        ET.indent(tree, space="\t", level=0)
        tree.write('vprasanja.xml', encoding='utf-8', xml_declaration=True)

    new_lines = []
    with open("vprasanja.xml", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.replace("&lt;", "<").replace("&gt;", ">")
            new_lines.append(line)

    with open("vprasanja.xml", "w") as file:
        file.writelines(new_lines)


if __name__ == "__main__":
    random.seed(2024)
    (headers, data, results) = readData()
    # # generateDataVariations(data, headers, names)

    generateMoodleXML(headers, data, results)
    # print(f"Generated vprasanja.xml with {10} questions")