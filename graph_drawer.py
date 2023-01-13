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

    def graph_format(self, y_lim, x_lim, x_label, y_label):
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
        plt.xlim(x_lim)

    def r_distribution(self, r_dist_frame, single_date):
        self.graph_format(y_lim=[0, 12000], x_lim=[0, 100], x_label='R', y_label='Число событий')
        plt.text(43, 12000, f"за {single_date.day:02}.{single_date.month:02}.{single_date.year:02}", bbox=self.box,
                 fontsize=20)
        for det in range(1, 5):
            plt.plot(r_dist_frame.index, r_dist_frame[f'det_{det}'], label=f'Детектор {det}', linewidth=4.5)
        plt.legend(loc="upper right")
        path_pic = f'{self.path_to_pic}\\r_dist{single_date.day}-{single_date.month}-{single_date.year}.png'
        plt.savefig(path_pic, bbox_inches='tight')
        return path_pic

    def front_time_dist(self, front_time_frame, single_date):
        self.graph_format(y_lim=[1, 10000], x_lim=[0, 200], x_label='Время нарастаний фронта', y_label='Число событий')
        plt.yscale('log')
        plt.text(43, 12000, f"за {single_date.day:02}.{single_date.month:02}.{single_date.year:02}", bbox=self.box,
                 fontsize=20)
        for det in range(1, 5):
            plt.plot(front_time_frame.index, front_time_frame[f'det_{det}'], label=f'Детектор {det}', linewidth=4.5)
        plt.legend(loc="upper right")
        path_pic = f'{self.path_to_pic}\\front_time{single_date.day}-{single_date.month}-{single_date.year}.png'
        plt.savefig(path_pic, bbox_inches='tight')
        return path_pic

    def n_amp_dist(self, n_amp_frame, single_date):
        self.graph_format(y_lim=[1, 10000], x_lim=[0, 250], x_label='Амплитуда', y_label='Число событий')
        plt.yscale('log')
        plt.text(110, 10000, f"за {single_date.day:02}.{single_date.month:02}.{single_date.year:02}", bbox=self.box,
                 fontsize=20)
        n_line_list, noise_line_list = [], []
        for det in range(1, 5):
            n_line, =  plt.plot(n_amp_frame.index, n_amp_frame[f'det_{det}'], label=f'Детектор {det}', linewidth=4.5)
            noise_line, =  plt.plot(n_amp_frame.index, n_amp_frame[f'noise_{det}'], label=f'Детектор {det}', linewidth=4.5)
            n_line_list.append(n_line)
            noise_line_list.append(noise_line)
        first_legend = plt.legend(handles=n_line_list, loc='upper center', bbox_to_anchor=(0.75, 1), title='Нейтроны')
        plt.gca().add_artist(first_legend)
        plt.legend(handles=noise_line_list, loc='upper right', title='Шумы')
        path_pic = f'{self.path_to_pic}\\n_amp{single_date.day}-{single_date.month}-{single_date.year}.png'
        plt.savefig(path_pic, bbox_inches='tight')
        return path_pic
    # Доделать функцию с графиком.
    @staticmethod
    def pressure_graph(type_of_impulse_sign):
        fig, axs = plt.subplots(figsize=(18, 18), nrows=4, sharex='col')
        for det in range(1, 5):
            ax = axs[det - 1]
            ax.set_title(f'Детектор {det}', fontsize=18, loc='left')
            if det == 5:
                ax.set_xlabel('Давление', fontsize=20)
            ax.set_ylabel(type_of_impulse_sign + r'$, (300с)^{-1}$', fontsize=15)
