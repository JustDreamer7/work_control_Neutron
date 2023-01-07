# from docx.enum.style import WD_STYLE_TYPE
# from docx.enum.table import WD_TABLE_ALIGNMENT
# from docx.shared import Cm
# from docx.shared import Inches
# from docx.shared import Pt
import datetime

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement, ns


def create_element(name):
    return OxmlElement(name)


def create_attribute(element, name, value):
    element.set(ns.qn(name), value)


def add_page_number(paragraph):
    """Метод, добавляющий номера страниц в word."""
    # выравниваем параграф по центру
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    # запускаем динамическое обновление параграфа
    page_num_run = paragraph.add_run()
    # обозначаем начало позиции вывода
    fld_char1 = create_element('w:fldChar')
    create_attribute(fld_char1, 'w:fldCharType', 'begin')
    # задаем вывод текущего значения страницы PAGE (всего страниц NUM PAGES)
    instr_text = create_element('w:instrText')
    create_attribute(instr_text, 'xml:space', 'preserve')
    instr_text.text = "PAGE"
    # обозначаем конец позиции вывода
    fld_char2 = create_element('w:fldChar')
    create_attribute(fld_char2, 'w:fldCharType', 'end')
    # добавляем все в наш параграф (который формируется динамически)
    page_num_run._r.append(fld_char1)
    page_num_run._r.append(instr_text)
    page_num_run._r.append(fld_char2)


def time_breaks_counter(brake_frame):
    breaks = len(brake_frame.index)
    fail_str_begin = []
    fail_str_end = []
    lost_minutes = []
    for i in range(len(brake_frame.index)):
        fail_str_begin.append(f"{brake_frame['StartDate'][i]}  {brake_frame['StartTime'][i]}")
        fail_str_end.append(f"{brake_frame['EndDate'][i]}  {brake_frame['EndTime'][i]}")
        lost_minutes.append(round((datetime.datetime.combine(brake_frame['EndDate'][i],
                                                             brake_frame['EndTime'][i]) -
                                   datetime.datetime.combine(brake_frame['StartDate'][i],
                                                             brake_frame['StartTime'][i])).total_seconds() / 60, 2))
    return fail_str_begin, fail_str_end, lost_minutes, breaks
