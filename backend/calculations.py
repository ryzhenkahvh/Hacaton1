import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from datetime import datetime
import csv
import os
import matplotlib.pyplot as plt

data = pd.read_excel('Задание_2_Потребление_электроэнергии_Апрель.xlsx', header=1)

min_consumption = 10
tariff = 0.2
time_step = 0.5 #в часах
max_days = 30
#тут будут устанавливаться не дефолтные значения для min_consumption, tariff
#

data_time = data.iloc[:, :2]
data_days = data.iloc[:, 0]
data_hours = data_time.iloc[:, 1]
by_time_consumption = data.iloc[:, 2:].sum(axis=1)

sum = data.iloc[:, 2:].sum()
total_sum = data.iloc[:, 2:].sum().sum()
sum_price = total_sum * tariff

optimization = data.mask(data.iloc[:, 2:] < min_consumption, 0)
opt_sum = optimization.iloc[:, 2:].sum()
total_opt_sum = optimization.iloc[:, 2:].sum().sum()
opt_price = total_opt_sum * tariff

opt_nan = optimization.mask(optimization == 0)
opt_mean = opt_nan.mean()
std_deviation = opt_nan.std()
n_std = 1.5
min_peak_height = opt_mean + n_std * std_deviation

peaks = optimization.iloc[:, 2:].where(
    optimization.iloc[:, 2:] > min_peak_height[optimization.columns[2:]]
)
peaks_with_time = pd.concat([data_time, peaks], axis=1)

difference = sum - opt_sum
total_diff = total_sum - total_opt_sum
diff_price = total_diff * tariff

#создание marked excel
copy_data = data.copy()
temp_file ="temp_output.xlsx"
copy_data.to_excel(temp_file, index=False, engine='openpyxl')

wb = load_workbook(temp_file)
ws = wb.active

red_fill = PatternFill(start_color="FF8080", end_color="FF8080", fill_type="solid")  # Красный для пиков
yellow_fill = PatternFill(start_color="FFFF60", end_color="FFFF60", fill_type="solid")  # Желтый для нулей

for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
  for cell in row:
    if cell.column > 2:
      col_name = ws.cell(row=1, column=cell.column).value
      original_value = data.iloc[cell.row-2, cell.column-1]
      optimized_value = optimization.iloc[cell.row-2, cell.column-1]

      if optimized_value == 0 and original_value != 0:
        cell.fill = yellow_fill

      if not pd.isna(peaks.iloc[cell.row-2, cell.column-3]) and peaks.iloc[cell.row-2, cell.column-3] == original_value:
        cell.fill = red_fill


output_file = "analyzed_marked.xlsx"
#output_file = "C:/Users/Ваше_имя/Desktop/formatted_result.xlsx"  # Для Windows
wb.save(output_file)

with pd.ExcelWriter(output_file, engine="openpyxl", mode="a") as writer:
    peaks_with_time.to_excel(writer, sheet_name="Peaks data", index=False)
os.remove(temp_file)

#начало рассчета времени
time_consumption = pd.DataFrame({
    'Время': data_hours.values,
    'Потребление': by_time_consumption.values
})

min_count = time_consumption.groupby('Время').size().min()
if min_count > max_days:
  time_consumption = time_consumption.tail(max_days)

balanced_data = time_consumption.groupby('Время').head(min_count)

#список потребления в одно время, время значение по котороому группируют [1, 2, 3]
hourly_stats = balanced_data.groupby('Время').agg({
    'Потребление': ['sum', 'mean', 'max', 'count']
}).sort_values(by=('Потребление', 'sum'), ascending=False)
hourly_stats.columns = ['Суммарное', 'Среднее', 'Максимальное', 'Повторы']

top_peaks = hourly_stats.nlargest(5, ('Суммарное'))
print(hourly_stats['Повторы'].unique())

days_consumption = pd.DataFrame({
    'Дата': data_days.values,
    'Потребление': by_time_consumption.values
})
days_count = min_count
if days_count > max_days:
  days_consumption = days_consumption.tail(max_days)

dates = days_consumption.groupby('Дата').head(min_count)

daily_stats = dates.groupby('Дата').agg({
    'Потребление': ['sum', 'mean', 'max']
})
daily_stats.columns = ['Суммарное', 'Среднее', 'Максимальное']

#запись в csv и excel аналитики по времени и датам
with pd.ExcelWriter('time_analysis.xlsx') as writer:
    daily_stats.to_excel(writer, sheet_name='Потребление по дням')
    hourly_stats.to_excel(writer, sheet_name='Среднее потребление по временным интервалам')
    top_peaks.to_excel(writer, sheet_name='Топ пиковых временных интервалов')

report_data = [
    ["Дата анализа", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    ["Шаг времени (часы)", time_step],
    ["Топ-5 пиковых периодов", ""],
    *[[f"{time}", f"{value:.2f} кВт*ч"]
      for time, value in zip(top_peaks.index, top_peaks[('Суммарное')])],
    ["Среднее потребление в пик", f"{top_peaks[('Среднее')].mean():.2f} кВт*ч"],
    ["Максимальное потребление в пик", f"{top_peaks[('Максимальное')].max():.2f} кВт*ч"]
]

with open('time_consumption_report.csv', 'w', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerows(report_data)

#аналитика по потреблению энергии в целом по всему excel
#!!! csv, эту же информацию можно добавить в сообщение тг, тк здесь перечислено главное
report_lines = [
    ["Дата создания", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    ["Минимальное потребление (кВт*ч)", min_consumption],
    ["Тариф (byn)", tariff],
    ["Общая сумма потребления (кВт*ч)", total_sum],
    ["Сумма к оплате (byn)", sum_price],
    ["Потребление не работающих приборов (кВт*ч)", total_diff],
    ["Сумма к оплате за не работающие приборы (byn)", diff_price],
    ["Общая сумма потребления после оптимизации (кВт*ч)", total_opt_sum],
    ["Сумма после оптимизации (byn)", opt_price]
]

with open('consumption_report.csv', 'w', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerows(report_lines)

# print(f"Файл consumption_report.csv успешно создан!")
