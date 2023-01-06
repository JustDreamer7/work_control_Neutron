import cycler
from matplotlib import pyplot as plt


class GraphsDrawing:
    def __init__(self, start_date, end_date, path_to_pic):
        self.start_date = start_date
        self.end_date = end_date
        self.path_to_pic = path_to_pic
        self.box = {'facecolor': 'white',  # цвет области
                    'edgecolor': 'red',  # цвет крайней линии
                    'boxstyle': 'round'}

    def __del__(self):
        """Деструктор, закрывающий все объекты Figure, созданные в процессе работы класса."""
        plt.close('all')

    @staticmethod
    def change_design():
        """Метод, который должен применяться вначале, для изменения размера и веса шрифта. А также для изменения,
        цвета линий на графиках. Без него цвета, когда количество линий > 10 начнут повторяться"""
        font = {'weight': 'bold',
                'size': 18}
        plt.rc('font', **font)
        plt.rc('axes',
               prop_cycle=(
                   cycler.cycler('color', ['r', 'g', 'b', 'darkblue', 'lawngreen', 'hotpink', 'c', 'y', 'm', 'orange',
                                           'burlywood', 'darkmagenta', 'grey', 'darkslategray', 'saddlebrown',
                                           'lightsalmon'])))
        return None

    def graph_format(self, y_lim, x_label, y_label):
        """Метод, прописывающий неизменный формат для графиков, желательно добавить смену figsize и fontsize"""
        plt.figure(figsize=(18, 10))
        plt.xlabel(x_label, fontsize=40)
        plt.ylabel(y_label, fontsize=40)
        plt.grid()
        plt.minorticks_on()
        plt.tick_params(axis='both', which='minor', direction='out', length=10, width=2, pad=10)
        plt.tick_params(axis='both', which='major', direction='out', length=20, width=4, pad=10)
        plt.grid(which='minor',
                 color='k',
                 linestyle=':')
        plt.ylim(y_lim)
        plt.xlim([self.start_date, self.end_date])
