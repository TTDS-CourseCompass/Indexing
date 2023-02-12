import os
import xml.etree.ElementTree as ET
from Index import Index


def create_index(data_dir, fileout):
    files = os.scandir(data_dir)

    # num of docs term appears in
    term_freq = {}
    # docs that a term appears in
    term_doc_appearances = {}
    # positions of appearances of term in each doc
    term_positions = {}
    doc_no = 0
    for f in files:
        inp_dir = data_dir + f.name
        print("===============================================")
        print(inp_dir)
        print(doc_no)
        doc_no = create_index_xml(inp_dir, doc_no, term_freq, term_doc_appearances, term_positions)
        # exit()

    with open(fileout, 'w', encoding='utf-8') as w:
        for k in sorted(term_freq):
            # print(f"{k}: {term_freq[k]}")
            w.write(f"{k}: {term_freq[k]}\n")
            for doc in sorted(term_doc_appearances[k]):
                line = f"\t{doc}: "
                # print(f"{doc}: {term_positions[(k, doc)]}")
                for pos in term_positions[(k, doc)]:
                    line += f"{pos},"
                line = f"{line[:-1]}\n"
                w.write(line)


def create_index_xml(filein, doc_no, term_freq, term_doc_appearances, term_positions):
    tree = ET.parse(filein)
    root = tree.getroot()
    # print(root.tag)

    for elem in root:
        # print("=======")
        # print(elem.tag)
        if elem.tag == "source":
            source = elem.text
            continue
        elif elem.tag == "date":
            date = elem.text
            continue
        elif elem.tag == "course":
            continue
        elif elem.tag == "lectures":
            max_doc_no = indexLectureElem(elem, doc_no, term_freq, term_doc_appearances, term_positions)
        elif elem.tag == "videos":
            continue

    return max_doc_no+1


def indexLectureElem(root, doc_no, term_freq, term_doc_appearances, term_positions):
    max_doc_no = doc_no
    for lecture_elem in root:
        if lecture_elem.tag != "lecture":
            continue
        for elem in lecture_elem:
            print(elem)
            # print("=======")
            # print(elem.tag)
            if elem.tag == "lectureno":
                lecture_no = int(elem.text)
            if elem.tag != "slides":
                continue
            counter = 1
            for subelem in elem:
                # print(subelem.tag, len(subelem.text))
                slide_no, slidetext = list(subelem)

                # doc_no = lecture_no + int(slide_no.text)
                current_doc_no = doc_no + lecture_no
                print(current_doc_no)
                max_doc_no = max(max_doc_no, current_doc_no)

                if not slidetext.text:
                    continue
                # for clean data
                tokens = slidetext.text.split(" ")
                # for only tokenizing and casefolding
                # tokens = preprocessing.tokenize(subelem.text.lower())
                for t in tokens:
                    # add term to doc appearance dictionary
                    if t in term_doc_appearances:
                        term_doc_appearances[t].add(current_doc_no)
                    else:
                        term_doc_appearances[t] = {current_doc_no}

                    # add term to frequency dictionary
                    term_freq[t] = len(term_doc_appearances[t])

                    # add term to positions dictionary
                    if (t, current_doc_no) in term_positions:
                        term_positions[(t, current_doc_no)].append(counter)
                    else:
                        term_positions[(t, current_doc_no)] = [counter]
                    counter += 1
    return max_doc_no

def load_index(filein):
    term_freq = {}
    term_doc_appearances = {}
    term_positions = {}
    with open(filein, "r", encoding='utf-8') as f:
        for line in f:
            if line[0] != '\t':
                terms = line.split(": ")
                term_freq[terms[0]] = int(terms[1])
                key = terms[0]
                # print("-----------")
                # print("header:", repr(terms[0]), repr(int(terms[1])))
            # print(repr(line))
            else:
                terms = line.split(": ")
                doc = int(terms[0])
                if key in term_doc_appearances:
                    term_doc_appearances[key].add(doc)
                else:
                    term_doc_appearances[key] = {doc}

                positions = [int(s) for s in terms[1].split(',')]
                term_positions[(key, doc)] = set(positions)
                # print("footer:", repr(int(terms[0])), repr(positions))

    return Index(term_freq, term_doc_appearances, term_positions)
