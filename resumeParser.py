import sys
import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import json


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
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    string = retstr.getvalue()
    retstr.close()
    return string


def main(argv):
    print(f"Parsing {argv[1]}")
    name = re.search(r"\\(.+)\.pdf", argv[1]).groups(0)
    contact = {'name': name}
    summary, work_exp, edu = dict(), dict(), dict()
    work_flag = False
    degree = ['MSc', 'MBA', 'BSc']
    content = convertPDFToText(argv[1]).splitlines()
    # content = convertPDFToText("ResumeLinkedin.pdf").splitlines()
    # content = convertPDFToText("resume.pdf").splitlines()
    for i, line in enumerate(content):
        if not line:
            continue

        m = re.match(r'([+(]?\d+[)\-]?\d{9})', line)
        if m:
            contact['phone'] = m.groups(1)

        m = re.match(r'(.+@.+)', line)
        if m and '.' in content[i+1]:
            contact['email'] = m.groups(1)[0] + content[i+1]

        if re.match(r'^Summary$', line):
            summary['summary'] = content[i+1]

        if re.match(r'^Education', line):
            work_flag = False
        if any(deg in line for deg in degree):
            edu[content[i-1]] = content[i].encode('ascii', 'ignore').decode()

        if re.match(r'^Experience$', line):
            work_flag = True
        elif work_flag and not content[i-1] and ord(content[i][0]) < 127 and content[i+1]:
            work_exp[content[i]] = content[i+1]


    print(json.dumps(contact))
    print(json.dumps(summary))
    print(json.dumps(work_exp))
    print(json.dumps(edu))


if __name__ == '__main__':
    main(sys.argv)


