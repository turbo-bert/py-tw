from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import A3
from reportlab.lib.pagesizes import landscape


from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
#pdfmetrics.registerFont(TTFont('Andale', '/src/private/g10/Andale Mono.ttf'))


#from tabulate import tabulate
import logging

__all__ = [
    'Page',
    'Document7293',
    'Document50136',
    'Document103136',
    'Doc',
    'DINA4',
    'DINA3',
    'DINA4L'
]


a4_w, a4_h = A4
pagecfg_a4 = {"ma_top": 8, "ma_left": 5, "lh": 4 * mm, "w": a4_w, "h": a4_h, "fontsize": 11}

a3_w, a3_h = A3
pagecfg_a3 = {"ma_top": 8, "ma_left": 5, "lh": 4 * mm, "w": a3_w, "h": a3_h, "fontsize": 11}

#pagecfg = {"ma_top": 8, "ma_left": 5, "lh": 4 * mm, "w": a4_w, "h": a4_h, "fontsize": 11}
pagecfg = None


class Page:

    def __init__(self):
        self.commands = []

    def multi(self, row1, col1, text):
        lstart=row1
        for line in text.split("\n"):
            self.commands.append(["text", lstart, col1, line])
            lstart+=1

    def text(self, row1, col1, text):
        self.commands.append(["text", row1, col1, text])

    def textb(self, row1, col1, text):
        self.commands.append(["textb", row1, col1, text])

    def hr(self):
        self.commands.append(["hr"])

    def image(self, row1, col1, imagefile, scal, scaln):
        self.commands.append(["image", row1, col1, imagefile, scal, scaln])

    def image_manual_mm(self, x_mm, y_mm, w_mm, h_mm, imagefile):
        self.commands.append(["image_manual_mm", x_mm, y_mm, w_mm, h_mm, imagefile])

    def table(self, data, headers, row1, col1, title=None):
        self.commands.append(["table", data, headers, row1, col1, title])


class Document7293:

    def __init__(self, is_landscape=False):
        global pagecfg
        pagecfg=pagecfg_a4
        self._pages = []
        self._current_page = 1
        self._landscape = is_landscape

    def page(self, no) -> Page:
        while self.pagecount() < no:
            self._pages.append(Page())
        return self._pages[no-1]

    def pagecount(self):
        return len(self._pages)

    @staticmethod
    def __text(c, row1, col1, text):
        global pagecfg
        c.saveState()
        c.setFont("Courier", 10)
        c.drawString(pagecfg["ma_left"]*mm, A4[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"], " " * (col1-1) + text)
        c.restoreState()

    @staticmethod
    def __textb(c, row1, col1, text):
        global pagecfg
        c.saveState()
        c.setFont("Courier-Bold", 10)
        c.drawString(pagecfg["ma_left"]*mm, A4[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"], " " * (col1-1) + text)
        c.restoreState()

    def build(self, filename):
        global pagecfg

        c = None

        if self._landscape:
            c = canvas.Canvas(
                filename,
                pagesize=landscape((pagecfg["w"], pagecfg["h"]))
            )
        else:
            c = canvas.Canvas(
                filename,
                pagesize=(pagecfg["w"], pagecfg["h"])
            )


        i = 1
        for page in self._pages:
            # print("%d %s" % (i, page._commands))

            for command in page.commands:
                cmd_name = command[0]
                cmd_params = command[1:]

                if cmd_name == "image":
                    row1 = cmd_params[0]
                    col1 = cmd_params[1]
                    charwidth = (210 * mm - 5 * mm) / 97
                    lh = pagecfg["lh"]
                    x = pagecfg["ma_left"]*mm + (col1-1)*charwidth
                    y = pagecfg["h"] - pagecfg["ma_top"]*mm - (row1-1)*pagecfg["lh"]
                    scal = cmd_params[3]
                    scaln = int(cmd_params[4])
                    scal_w = None
                    scal_h = None
                    filename = cmd_params[2]
                    dims = filename.split(".")[-2].split("x")
                    if len(dims) == 1:
                        dims = dims.split("-")
                    w = int(dims[-2])
                    h = int(dims[-1])
                    if scal == "h":
                        scal_h = lh*scaln
                        scal_w = w/h*scal_h
                    if scal == "w":
                        scal_w = charwidth*scaln
                        scal_h = h/w*scal_w
                    c.drawImage(cmd_params[2], x=x, y=y, height=scal_h, width=scal_w)

                if cmd_name == "image_manual_mm":
                    #        self.commands.append(["image_manual_mm", x_mm, y_mm, w_mm, h_mm, imagefile])
                    x_mm = cmd_params[0]
                    y_mm = cmd_params[1]
                    w_mm = cmd_params[2]
                    h_mm = cmd_params[3]
                    imagefile = cmd_params[4]
                    x = x_mm*mm
                    y = y_mm*mm
                    c.drawImage(imagefile, x=x, y=y, height=h_mm*mm, width=w_mm*mm)

                if cmd_name == "table":
                    (data, headers, row1, col1, title) = cmd_params
                    if title is not None:
                        self.__text(c, row1, col1, title)
                        self.__text(c, row1, col1, "_"*len(title))
                        row1 += 2
                    o = tabulate(data, headers=headers, tablefmt="fancy").split("\n")
                    o_line = row1
                    o_col = col1
                    o_line_start = o_line
                    for tline in o:
                        if o_line == o_line_start:
                            self.__textb(c, o_line, o_col, tline)
                        else:
                            self.__text(c, o_line, o_col, tline)
                        o_line += 1

                if cmd_name == "text":
                    row1 = cmd_params[0]
                    col1 = cmd_params[1]
                    text = cmd_params[2]

                    c.saveState()
                    c.setFont("Courier", 10)

                    if self._landscape:
                        c.drawString(
                            pagecfg["ma_left"]*mm,
                            A4[0]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"],
                            " " * (col1-1) + text
                        )
                    else:
                        c.drawString(
                            pagecfg["ma_left"]*mm,
                            A4[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"],
                            " " * (col1-1) + text
                        )
                    c.restoreState()

                if cmd_name == "textb":
                    row1 = cmd_params[0]
                    col1 = cmd_params[1]
                    text = cmd_params[2]

                    c.saveState()
                    c.setFont("Courier-Bold", 10)
                    c.drawString(
                        pagecfg["ma_left"]*mm,
                        A4[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"],
                        " " * (col1-1) + text
                    )
                    c.restoreState()

            i += 1
            c.showPage()
        c.save()

    def generate_page_numbers_7280(self):
        n = self.pagecount()
        i = 1
        for page in self._pages:
            page.text(72, 80, "%d / %d" % (i, n))
            i += 1

    def page_numbers(self):
        self.generate_page_numbers_7280()

    def generate_page_numbers_180(self):
        n = self.pagecount()
        i = 1
        for page in self._pages:
            page.text(1, 80, "%d / %d" % (i, n))
            i += 1

class Document103136:

    def __init__(self, is_landscape=False):
        global pagecfg
        pagecfg=pagecfg_a3

        self._pages = []
        self._current_page = 1
        self._landscape = is_landscape

    def page(self, no) -> Page:
        while self.pagecount() < no:
            self._pages.append(Page())
        return self._pages[no-1]

    def pagecount(self):
        return len(self._pages)

    @staticmethod
    def __text(c, row1, col1, text):
        global pagecfg
        c.saveState()
        c.setFont("Courier", 10)
        c.drawString(pagecfg["ma_left"]*mm, A3[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"], " " * (col1-1) + text)
        c.restoreState()

    @staticmethod
    def __textb(c, row1, col1, text):
        global pagecfg
        c.saveState()
        c.setFont("Courier-Bold", 10)
        c.drawString(pagecfg["ma_left"]*mm, A3[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"], " " * (col1-1) + text)
        c.restoreState()

    def build(self, filename):
        global pagecfg

        c = None

        if self._landscape:
            c = canvas.Canvas(
                filename,
                pagesize=landscape((pagecfg["w"], pagecfg["h"]))
            )
        else:
            c = canvas.Canvas(
                filename,
                pagesize=(pagecfg["w"], pagecfg["h"])
            )


        i = 1
        for page in self._pages:
            # print("%d %s" % (i, page._commands))

            for command in page.commands:
                cmd_name = command[0]
                cmd_params = command[1:]

                if cmd_name == "image":
                    row1 = cmd_params[0]
                    col1 = cmd_params[1]
                    charwidth = (210 * mm - 5 * mm) / 97
                    lh = pagecfg["lh"]
                    x = pagecfg["ma_left"]*mm + (col1-1)*charwidth
                    y = pagecfg["h"] - pagecfg["ma_top"]*mm - (row1-1)*pagecfg["lh"]
                    scal = cmd_params[3]
                    scaln = int(cmd_params[4])
                    scal_w = None
                    scal_h = None
                    filename = cmd_params[2]
                    dims = filename.split(".")[-2].split("x")
                    if len(dims) == 1:
                        dims = dims.split("-")
                    w = int(dims[-2])
                    h = int(dims[-1])
                    if scal == "h":
                        scal_h = lh*scaln
                        scal_w = w/h*scal_h
                    if scal == "w":
                        scal_w = charwidth*scaln
                        scal_h = h/w*scal_w
                    c.drawImage(cmd_params[2], x=x, y=y, height=scal_h, width=scal_w)

                if cmd_name == "image_manual_mm":
                    #        self.commands.append(["image_manual_mm", x_mm, y_mm, w_mm, h_mm, imagefile])
                    x_mm = cmd_params[0]
                    y_mm = cmd_params[1]
                    w_mm = cmd_params[2]
                    h_mm = cmd_params[3]
                    imagefile = cmd_params[4]
                    x = x_mm*mm
                    y = y_mm*mm
                    c.drawImage(imagefile, x=x, y=y, height=h_mm*mm, width=w_mm*mm)

                if cmd_name == "table":
                    (data, headers, row1, col1, title) = cmd_params
                    if title is not None:
                        self.__text(c, row1, col1, title)
                        self.__text(c, row1, col1, "_"*len(title))
                        row1 += 2
                    o = tabulate(data, headers=headers, tablefmt="fancy").split("\n")
                    o_line = row1
                    o_col = col1
                    o_line_start = o_line
                    for tline in o:
                        if o_line == o_line_start:
                            self.__textb(c, o_line, o_col, tline)
                        else:
                            self.__text(c, o_line, o_col, tline)
                        o_line += 1

                if cmd_name == "text":
                    row1 = cmd_params[0]
                    col1 = cmd_params[1]
                    text = cmd_params[2]

                    c.saveState()
                    c.setFont("Courier", 10)

                    if self._landscape:
                        c.drawString(
                            pagecfg["ma_left"]*mm,
                            A3[0]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"],
                            " " * (col1-1) + text
                        )
                    else:
                        c.drawString(
                            pagecfg["ma_left"]*mm,
                            A3[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"],
                            " " * (col1-1) + text
                        )
                    c.restoreState()

                if cmd_name == "textb":
                    row1 = cmd_params[0]
                    col1 = cmd_params[1]
                    text = cmd_params[2]

                    c.saveState()
                    c.setFont("Courier-Bold", 10)
                    c.drawString(
                        pagecfg["ma_left"]*mm,
                        A3[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"],
                        " " * (col1-1) + text
                    )
                    c.restoreState()

            i += 1
            c.showPage()
        c.save()

    def generate_page_numbers_7280(self):
        n = self.pagecount()
        i = 1
        for page in self._pages:
            page.text(72, 80, "%d / %d" % (i, n))
            i += 1

    def page_numbers(self):
        self.generate_page_numbers_7280()

    def generate_page_numbers_180(self):
        n = self.pagecount()
        i = 1
        for page in self._pages:
            page.text(1, 80, "%d / %d" % (i, n))
            i += 1



def Doc():
    return Document7293()

def DINA4():
    return Document7293()

def DINA3():
    return Document103136()

def DINA4L():
    return Document7293(is_landscape=True)

def Document50136():
    return Document7293(is_landscape=True)


class Presentation:

    def __init__(self, fontsize_mm=10):
        self._pages = []
        self._current_page = 1
        self._fontsize = fontsize_mm * mm


    def page(self, no) -> Page:
        while self.pagecount() < no:
            self._pages.append(Page())
        return self._pages[no-1]

    def pagecount(self):
        return len(self._pages)

    @staticmethod
    def __text(c, row1, col1, text):
        global pagecfg
        c.saveState()
        c.setFont("Courier", 38)
        c.drawString(pagecfg["ma_left"]*mm, A4[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"], " " * (col1-1) + text)
        c.restoreState()

    @staticmethod
    def __textb(c, row1, col1, text):
        global pagecfg
        c.saveState()
        c.setFont("Courier-Bold", 38)
        c.drawString(pagecfg["ma_left"]*mm, A4[1]-pagecfg["ma_top"]*mm-(row1-1)*pagecfg["lh"], " " * (col1-1) + text)
        c.restoreState()

    def build(self, filename):
        global pagecfg

        c = canvas.Canvas(
            filename,
            pagesize=landscape((pagecfg["w"], pagecfg["h"]))
        )

        i = 1
        for page in self._pages:
            # print("%d %s" % (i, page._commands))

            for command in page.commands:
                cmd_name = command[0]
                cmd_params = command[1:]

                if cmd_name == "image":
                    row1 = cmd_params[0]
                    col1 = cmd_params[1]
                    charwidth = (210 * mm - 5 * mm) / 97
                    lh = pagecfg["lh"]
                    x = pagecfg["ma_left"]*mm + (col1-1)*charwidth
                    y = pagecfg["h"] - pagecfg["ma_top"]*mm - (row1-1)*pagecfg["lh"]
                    scal = cmd_params[3]
                    scaln = int(cmd_params[4])
                    scal_w = None
                    scal_h = None
                    filename = cmd_params[2]
                    dims = filename.split(".")[-2].split("x")
                    if len(dims) == 1:
                        dims = dims.split("-")
                    w = int(dims[-2])
                    h = int(dims[-1])
                    if scal == "h":
                        scal_h = lh*scaln
                        scal_w = w/h*scal_h
                    if scal == "w":
                        scal_w = charwidth*scaln
                        scal_h = h/w*scal_w
                    c.drawImage(cmd_params[2], x=x, y=y, height=scal_h, width=scal_w)

                if cmd_name == "image_manual_mm":
                    #        self.commands.append(["image_manual_mm", x_mm, y_mm, w_mm, h_mm, imagefile])
                    x_mm = cmd_params[0]
                    y_mm = cmd_params[1]
                    w_mm = cmd_params[2]
                    h_mm = cmd_params[3]
                    imagefile = cmd_params[4]
                    x = x_mm*mm
                    y = y_mm*mm
                    c.drawImage(imagefile, x=x, y=y, height=h_mm*mm, width=w_mm*mm)

                if cmd_name == "table":
                    (data, headers, row1, col1, title) = cmd_params
                    if title is not None:
                        self.__text(c, row1, col1, title)
                        self.__text(c, row1, col1, "_"*len(title))
                        row1 += 2
                    o = tabulate(data, headers=headers, tablefmt="fancy").split("\n")
                    o_line = row1
                    o_col = col1
                    o_line_start = o_line
                    for tline in o:
                        if o_line == o_line_start:
                            self.__textb(c, o_line, o_col, tline)
                        else:
                            self.__text(c, o_line, o_col, tline)
                        o_line += 1

                if cmd_name == "text":
                    print("text")
                    row1 = cmd_params[0]
                    col1 = cmd_params[1]
                    text = cmd_params[2]

                    c.saveState()
                    c.setFont("Andale", self._fontsize)
                    c.drawString(
                        pagecfg["ma_left"]*mm,
                        A4[1-1]-pagecfg["ma_top"]*mm-(row1-1)*self._fontsize/mm*2.8,
                        " " * (col1-1) + text
                    )
                    c.restoreState()

                if cmd_name == "textb":
                    row1 = cmd_params[0]
                    col1 = cmd_params[1]
                    text = cmd_params[2]

                    c.saveState()
                    c.setFont("Andale", self._fontsize)
                    c.drawString(
                        pagecfg["ma_left"]*mm,
                        A4[1-1]-pagecfg["ma_top"]*mm-(row1-1)*self._fontsize/mm*2.8,
                        " " * (col1-1) + text
                    )
                    c.restoreState()

            i += 1
            c.showPage()
        c.save()

    def generate_page_numbers_7280(self):
        n = self.pagecount()
        i = 1
        for page in self._pages:
            page.text(72, 80, "%d / %d" % (i, n))
            i += 1

    def generate_page_numbers_180(self):
        n = self.pagecount()
        i = 1
        for page in self._pages:
            page.text(1, 80, "%d / %d" % (i, n))
            i += 1



class FlatMaker:

    def __init__(self, the_doc):
        self.the_doc = the_doc
        self.cpage = 1
        self.ccol = 1
        self.cline = 1

    def to(self, line=None, col=None, page=None):
        if line is not None:
            self.cline = line
        if col is not None:
            self.ccol = col
        if page is not None:
            self.cpage = page
        return self

    def framebox(self, lines, subtitle=None):
        lines_ = lines
        h = len(lines_) + 2
        w = 0
        for line in lines_:
            if len(line) > w:
                w = len(line)

        w += 2

        line_start = self.cline
        col_start = self.ccol

        self.the_doc.page(self.cpage).text(line_start,col_start, ' %s ' % (w*'_'))
        self.the_doc.page(self.cpage).text(line_start+1,col_start, '|%s|' % (w*' '))

        for i in range(0,len(lines_)):
            self.the_doc.page(self.cpage).text(line_start+2+i,col_start, '|%s|' % (w*' '))
            self.the_doc.page(self.cpage).text(line_start+2+i,col_start+2, lines_[i])


        self.the_doc.page(self.cpage).text(line_start+h,col_start, '|%s|' % (w*' '))
        self.the_doc.page(self.cpage).text(line_start+h,col_start, ' %s ' % (w*'_'))
        
        if subtitle is not None:
            self.the_doc.page(self.cpage).text(line_start+h+1,col_start+w-len(subtitle)+2,subtitle)
        return self

    def fixbox(self, lines, subtitle=None, w=10, h=10):
        lines_ = []
        for line in lines:
            x = line + ' ' * (w-len(line))
            lines_.append(x)
        while len(lines_) < h:
            lines_.append('')

        return self.framebox(lines_, subtitle=subtitle)
