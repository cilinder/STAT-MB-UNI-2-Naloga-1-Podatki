import xml.etree.ElementTree as ET
import csv
from numpy import random
import zipfile
import os

def readData():
    data = []
    with open('pneumo.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        headers = reader.fieldnames
        for row in reader:
            data.append(row)

    return (headers, data)

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

def generateDownloadJavascript():
    data = []
    with open('pneumo.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            data.append(row)

    javascriptCode = f'''
const rows = {[[str(val) for val in row] for row in data]};\n
csvContent = "data:text/csv;charset=utf-8,"

rows.forEach(function(rowArray) {{
    let row = rowArray.join(",");
    csvContent += row + "\\r\\n";
}});
var encodedUri = encodeURI(csvContent);
var link = document.createElement("a");
link.setAttribute("href", encodedUri);
link.setAttribute("download", "my_data.csv");
document.body.appendChild(link); // Required for FF
link.click();

    '''
    return javascriptCode

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

def generateMoodleXML(headers, data, num_questions):
    # Create the structure of the XML file
    quiz = ET.Element("quiz")

    for i in range(num_questions):

        perturbed_data = []
        for row in data:
            perturbed_data.append({
                "ID": row["ID"],
                "pnevmo": row["pnevmo"],
                "FEV1": int(row["FEV1"]) + random.normal(0,1)
            })

        with open(f'podatki/podatki_{i+1}.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in perturbed_data:
                writer.writerow(row)
        with zipfile.ZipFile(f'podatki/podatki_{i+1}.zip', 'w') as zf:
            zf.write(f'podatki/podatki_{i+1}.csv', arcname=f'podatki_{i+1}.csv')
        os.remove(f'podatki/podatki_{i+1}.csv')

        html_table = generateTable(headers, perturbed_data)
        question = ET.SubElement(quiz, "question")
        question.set("type", "cloze")
        name_tag = ET.SubElement(question, "name")
        name_text = ET.SubElement(name_tag, "text")
        name_text.text = f"<![CDATA[Vprašanje {i + 1}]]>"
        questiontext = ET.SubElement(question, "questiontext")
        text = ET.SubElement(questiontext, "text")
        text.text = f'''<![CDATA[
Podane imaš naslednje podatke o pljučnih kapacitetah:
<br>
{html_table}
<br>
<a href="https://raw.githubusercontent.com/cilinder/STAT-MB-UNI-2-Naloga-1-Podatki/refs/heads/main/podatki/podatki_{i+1}.zip" download>Prenesi podatke</a>
<br><br>

Izračunaj koliko je $$a_n$$: 
{{1:NUMERICAL:=2.0000000000000:0.01}}
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
    names = ["Janez Novak", "Borut Pahor", "Tinkara Kovač"]
    (headers, data) = readData()
    # generateDataVariations(data, headers, names)

    generateMoodleXML(headers, data, 10)