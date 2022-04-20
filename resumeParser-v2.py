from glob import glob
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from io import StringIO
import os, re
import json
from pdfminer.layout import LTTextLine, LTChar, LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.converter import PDFPageAggregator


def convertPDFToText(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    string = retstr.getvalue()
    retstr.close()
    return string


def get_objects(layout):
    isiterable = lambda obj: isinstance(obj, str) or getattr(obj, '__iter__', False)
    objs = []
    for obj in layout:
        if isiterable(obj):
            for element in obj:
                objs.append(element)
        else:
            objs.append(obj)
    return objs


def get_name(resume):
    fp = open(resume, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    objs = []
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        layout = device.get_result()
        objs.append(sorted(get_objects(layout), key=lambda x: x.y0, reverse=True))
    objs = sum(objs, [])
    name = ''
    for obj in objs:
        if isinstance(obj, LTTextLine):
            for char in obj:
                if isinstance(char, LTChar):
                    if char.size > 23:
                        name = obj.get_text()
                        break
    name = name.strip().split(' ')
    return ' '.join(name)


def check_field(text):
    info = {"Contact", "Top Skills", "Languages", "Certifications", "Publications",
            "Honors-Awards", "Summary", "Experience", "Education"}
    text = [s for s in text if s]
    fields = set()
    for s in text:
        if s in info:
            fields.add(s)

    return fields


def get_current_job(resume, content):
    # content is a splitlined list
    name = get_name(resume)
    i = content.index(name) + 1
    while not content[i]:
        i += 1
    job = []
    while content[i]:
        job.append(content[i])
        i += 1
    return job


def get_location(job):
    return [job.pop()]


def get_top_skills(content):
    # content is a splitlined list
    skills = []
    try:
        i = content.index("Top Skills") + 1
        while content[i]:
            if "," in content[i]:
                tmp = [ele.strip() for ele in content[i].split(",")]
                skills.extend(tmp)
            else:
                skills.append(content[i])
            i += 1
    except Exception as e:
        print(e)

    return skills


def get_languages(content):
    # content is a splitlined list
    languages = []
    try:
        i = content.index("Languages") + 1
        while content[i]:
            languages.append(content[i])
            i += 1
    except Exception as e:
        print(e)

    return languages

def get_certifications(content):
    # content is a splitlined list
    certs = []
    try:
        i = content.index("Certifications") + 1
        while content[i]:
            certs.append(content[i])
            i += 1
    except Exception as e:
        print(e)

    return certs


def get_publications(content):
    # content is a splitlined list
    pubs = []
    try:
        i = content.index("Publications") + 1
        while content[i]:
            pubs.append(content[i])
            i += 1
    except Exception as e:
        print(e)

    return pubs


def get_honors_awards(content):
    # content is a splitlined list
    honors = []
    try:
        i = content.index("Honors-Awards") + 1
        while content[i]:
            honors.append(content[i])
            i += 1
    except Exception as e:
        print(e)

    return honors


def get_summary(content):
    # content is a splitlined list
    summ = []
    try:
        i = content.index("Summary") + 1
        while content[i]:
            summ.append(content[i])
            i += 1
    except Exception as e:
        print(e)

    res = ''
    if len(summ) > 2:
        res = ' '.join(summ[1:])
    return res[:200]


def get_work_exp(content):
    return


def get_education(content):
    edu = []
    try:
        i = content.index("Education") + 1
        while not content[i] or content[i][:4] == "Page":
            i += 1
        while content[i]:
            edu.append(content[i])
            i += 1
    except Exception as e:
        print(e)

    return edu


def parseResume(path):
    name = get_name(path)
    text = convertPDFToText(path)
    text = re.sub(r'\xa0', ' ', text).splitlines()
    # contact = {'email': email, 'phone': phone}
    top_skills = get_top_skills(text)
    current_job = get_current_job(resume, text)
    loc = get_location(current_job)
    languages = get_languages(text)
    certs = get_certifications(text)
    pubs = get_publications(text)
    honors = get_honors_awards(text)
    summ = get_summary(text)
    work_exp = get_work_exp(text)
    edu = get_education(text)
    data = {
        'name': name,
        'top_skills': top_skills,
        'current_job': current_job,
        'loc': loc,
        'languages': languages,
        'certs': certs,
        'pubs': pubs,
        'honors': honors,
        'summ': summ,
        'work_exp': work_exp,
        'edu': edu,
    }
    return data

if __name__ == "__main__":
    resumes = glob("resumes/**/*.pdf", recursive=True)

    filename = 'resume_data.json'
    open(filename, "w").close()  # clean the file

    for i, resume in enumerate(resumes):
        print(resume)
        resume_data = parseResume(resume)
        with open(filename, 'a') as json_file:
            json.dump(resume_data, json_file)
            json_file.write("\n")


