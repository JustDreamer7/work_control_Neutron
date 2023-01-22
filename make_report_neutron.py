import time
import warnings

import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

import word_addition


def make_report_neutron(start_date, end_date, report_path, picture_path, neutron_data, pressure_data,
                        proccessing_pressure):
    t1 = time.time()

    warnings.filterwarnings(action='ignore')

    days_amount = len(pd.date_range(start_date, end_date))



    # Далее формирование и запись в word-файл
    doc = Document()
    word_addition.section_choice(doc)
    word_addition.add_new_styles(doc, style_name='PItalic', font_size=11, bold=True, italic=True)
    word_addition.add_new_styles(doc, style_name='Head-style', font_size=14, bold=True)
    word_addition.add_new_styles(doc, style_name='Head-graphic', font_size=13, bold=True, italic=True)

    head = doc.add_paragraph(
        f'Справка о работе установки «Нейтрон» в период с {start_date} по {end_date}', style='Head-style')
    head.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    table_title = doc.add_paragraph('Таблица 1: Календарная эффективность.', style='PItalic')
    table_title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    worktime_table = doc.add_table(5, 4, doc.styles['Table Grid'])
    worktime_table.cell(0, 0).text = '№ детектора'
    worktime_table.cell(0, 1).text = 'Экспозиции, ч.'
    worktime_table.cell(0, 2).text = 'Календарное время, ч.'
    worktime_table.cell(0, 3).text = 'Экспозиция, %'
    worktime_table.cell(1, 0).text = '1'

    word_addition.make_table_bold(worktime_table, cols=4, rows=5)
    doc.add_paragraph()

    fail_str_begin, fail_str_end, lost_minutes, breaks = word_addition.time_breaks_counter(brake_frame=)

    brake_table_title = doc.add_paragraph('Таблица 2: Сводная таблица остановок установки Нейтрон.', style='PItalic')
    brake_table_title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    brake_table = doc.add_table(len(fail_str_begin) + 2, 5, doc.styles['Table Grid'])
    brake_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    brake_table.cell(0, 0).text = '№'
    brake_table.cell(0, 0).merge(brake_table.cell(1, 0))
    brake_table.cell(0, 1).text = 'Время простоя'
    brake_table.cell(1, 1).text = 'c'
    brake_table.cell(1, 2).text = 'по'
    brake_table.cell(0, 1).merge(brake_table.cell(0, 2))
    brake_table.cell(0, 3).text = 'Кол-во потерянных минут (период)'
    brake_table.cell(0, 3).merge(brake_table.cell(1, 3))
    brake_table.cell(0, 4).text = 'Примечание'
    brake_table.cell(0, 4).merge(brake_table.cell(1, 4))

    word_addition.make_table_bold(brake_table, cols=5, rows=len(fail_str_begin) + 2)
    doc.add_paragraph()

    stat_table_title = doc.add_paragraph(r'Таблица 3: Средние скорости счета [(300с)⁻¹]', style='PItalic')
    stat_table_title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    stat_table = doc.add_table(3, 5, doc.styles['Table Grid'])
    stat_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    stat_table.cell(0, 0).text = '№ детектора'
    for det in range(1, 5):
        stat_table.cell(0, det).text = f'{det}'
    stat_table.cell(1, 0).text = 'Скорость счета нейтронных импульсов'

    stat_table.cell(2, 0).text = 'Скорость счета шумовых импульсов'

    word_addition.make_table_bold(brake_table, cols=5, rows=3)
    word_addition.change_cell_size(brake_table, column_num=5, size_arr=[3, 1.075, 1.075, 1.075, 1.075])
    doc.add_paragraph()

    bar_table_title = doc.add_paragraph('Таблица 4: Барометрические коэффициенты β ', style='PItalic')
    bar_table_title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    bar_table = doc.add_table(3, 5, doc.styles['Table Grid'])
    bar_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    bar_table.cell(0, 0).text = '№ детектора'
    bar_table.cell(1, 0).text = 'β нейтронных импульсов, %/мбар'
    bar_table.cell(2, 0).text = 'β шумовых импульсов, %/мбар'
    for det in range(1, 5):
        bar_table.cell(0, det).text = f'{det}'

    word_addition.make_table_bold(brake_table, cols=5, rows=3)
    word_addition.change_cell_size(brake_table, column_num=5, size_arr=[3, 1.075, 1.075, 1.075, 1.075])
    doc.add_paragraph()

    #  if (mask_checker):
    #         doc.add_paragraph('Выборка данных с помощью маски не была произведена',style='Head-style')

    word_addition.page_breaker(doc=doc)

    graphic_header = doc.add_paragraph('Зависимости скорости счета нейтронных импульсов и давления от времени.',
                                       style='Head-graphic')
    graphic_header.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    word_addition.adding_graphic(doc,
                                 title='Рис. 1 - Зависимости скорости счета ' +
                                       'нейтронных импульсов и давления от времени.',
                                 width=7.5,
                                 height=7.9,
                                 picture_path=)

    word_addition.page_breaker(doc=doc)

    graphic_header = doc.add_paragraph('Зависимости скорости счета шумовых импульсов и давления от времени.',
                                       style='Head-graphic')
    graphic_header.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    word_addition.adding_graphic(doc,
                                 title='Рис. 2 - Зависимости скорости счета ' +
                                       'шумовых импульсов и давления от времени.',
                                 width=7.5,
                                 height=7.9,
                                 picture_path=)

    word_addition.page_breaker(doc=doc)

    graphic_header = doc.add_paragraph('Зависимости скорости счета нейтронных импульсов от давления.',
                                       style='Head-graphic')
    graphic_header.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    word_addition.adding_graphic(doc,
                                 title='Рис. 3 - Зависимости скорости счета нейтронных импульсов от давления.',
                                 width=7.5,
                                 height=7.9,
                                 picture_path=)

    word_addition.page_breaker(doc=doc)

    graphic_header = doc.add_paragraph('Зависимости скорости счета шумовых импульсов от давления.',
                                       style='Head-graphic')
    graphic_header.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    word_addition.adding_graphic(doc,
                                 title='Рис. 4 - Зависимости скорости счета шумовых импульсов от давления.',
                                 width=7.5,
                                 height=7.9,
                                 picture_path=)

    word_addition.page_breaker(doc=doc)

    print(time.time() - t1)
