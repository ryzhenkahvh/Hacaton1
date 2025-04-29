import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from datetime import datetime
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

data = pd.read_excel('Задание_2_Потребление_электроэнергии_Апрель.xlsx', header=1)

min_consumption = 10
tariff = 0.2
time_step = 0.5 #в часах
max_days = 30
#тут будут устанавливаться не дефолтные значения для min_consumption, tariff
# min_consumption = float(input("Введите минимальное потребление: "))
# tariff = float(input("Введите тариф: "))

data_time = data.iloc[:, :2]
data_days = data.iloc[:, 0]
data_hours = data_time.iloc[:, 1]
by_time_consumption = data.iloc[:, 2:].sum(axis=1)

# print(by_time_consumption)

sum = data.iloc[:, 2:].sum()
total_sum = data.iloc[:, 2:].sum().sum()
sum_price = total_sum * tariff

# print(total_sum)

optimization = data.iloc[:, 2:].mask(data.iloc[:, 2:] < min_consumption, 0)
opt_sum = optimization.sum()
total_opt_sum = optimization.sum().sum()
opt_price = total_opt_sum * tariff

# print(optimization)

# в csv как потенциальный выигрыш, эксель тоже как доп инфа
difference = sum - opt_sum
total_diff = total_sum - total_opt_sum
diff_price = total_diff * tariff

opt_nan = optimization.mask(optimization == 0)
opt_mean = opt_nan.mean()
std_deviation = opt_nan.std()
n_std = 1.5
# min_peak_height = opt_mean + n_std * std_deviation
min_peak_height = opt_mean.fillna(0) + n_std * std_deviation.fillna(0)

peaks = optimization.where(
    optimization > min_peak_height[optimization.columns]
)
peaks_with_time = pd.concat([data_time, peaks], axis=1)

# print(peaks)

min_dip_height = opt_mean - n_std * std_deviation

dips = optimization.where(
    optimization < min_dip_height[optimization.columns]
)
dips_with_time = pd.concat([data_time, dips], axis=1)

# print(dips)

#список не работающих
low_consumption = data.iloc[:, 2:].where((data.iloc[:, 2:] > 0) & (data.iloc[:, 2:] < min_consumption))
low_consumption_with_time = pd.concat([
    data.iloc[:, :2],
    low_consumption
], axis=1).dropna(how='all', subset=low_consumption.columns)

# print(low_consumption)

#перераспределение пиков на не работающие части

# redistributed_data = optimization.copy()
redistributed_turned_on = data.copy()
# print(redistributed_data)
for col in redistributed_turned_on.columns[2:]:
    peak_mask = (peaks[col].notna())
    low_mask = (low_consumption[col].notna())

    if peak_mask.any() and low_mask.any():
        excess_power = (redistributed_turned_on.loc[peak_mask, col] - opt_mean[col]).sum()

        # available_capacity = (min_consumption - redistributed_data.loc[low_mask, col]).sum()
        available_capacity = (opt_mean[col] - redistributed_turned_on.loc[low_mask, col]).sum()
        redistribution_ratio = min(1, excess_power / available_capacity) if available_capacity > 0 else 0
        redistributed_turned_on.loc[peak_mask, col] = opt_mean[col] + 0.5 * (redistributed_turned_on.loc[peak_mask, col] - opt_mean[col])
        redistributed_turned_on.loc[low_mask, col] += (min_consumption - redistributed_turned_on.loc[low_mask, col]) * redistribution_ratio

# redistributed_with_time = pd.concat([data_time, redistributed_data.iloc[:, 2:]], axis=1)

# print(redistributed_turned_on)

#перераспределение пиков на упадки

# средние значения пиков и упадков (игнорируя NaN)       следи что бы использовалась копия оптимизации
peaks_mean = peaks.mean()
dips_mean = dips.mean()
correction_factor = opt_mean - dips_mean

redistributed_dips = optimization.copy()

# for col in optimization.columns[2:]:
#     redistributed_dips.loc[peaks[col].notna(), col] -= 0.5 * (peaks[col] - peaks_mean[col])
#    redistributed_dips.loc[dips[col].notna(), col] += 0.5 * (dips_mean[col] - dips[col])

for col in optimization.columns[2:]:
    redistributed_dips.loc[peaks[col].notna(), col] -= 0.5 * (peaks[col] - peaks_mean[col])
    redistributed_dips.loc[dips[col].notna(), col] += 0.5 * (dips_mean[col] - dips[col])

# optimization_corrected = optimization_corrected.clip(lower=0)
redistributed_dips = pd.concat([data_time, redistributed_dips], axis=1)
# print(redistributed_dips)

copy_data = data.copy()
temp_file = "temp_output.xlsx"
copy_data.to_excel(temp_file, index=False, engine='openpyxl')

wb = load_workbook(temp_file)
ws = wb.active

red_fill = PatternFill(start_color="FF8080", end_color="FF8080", fill_type="solid")
yellow_fill = PatternFill(start_color="FFFF60", end_color="FFFF60", fill_type="solid")

for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
    for cell in row:
        if cell.column > 2:  # Пропускаем первые 2 столбца

            df_row = cell.row - 2  # Excel строка 2 → pandas строка 0
            df_col = cell.column - 1  # Excel столбец 3 → pandas столбец 2

            original_value = data.iloc[df_row, df_col]
            optimized_value = optimization.iloc[df_row, df_col - 2]  # Учитываем что optimization начинается с 3-го столбца

            if optimized_value == 0 and original_value != 0:
                cell.fill = yellow_fill

            peaks_col = cell.column - 3  # Настройте это смещение по необходимости
            if 0 <= peaks_col < len(peaks.columns) and not pd.isna(peaks.iloc[df_row, peaks_col]):
                if peaks.iloc[df_row, peaks_col] == original_value:
                    cell.fill = red_fill

output_file = "analyzed_marked.xlsx"
wb.save(output_file)

with pd.ExcelWriter(output_file, engine="openpyxl", mode="a") as writer:
    peaks_with_time.to_excel(writer, sheet_name="Пиковые значения", index=False)
    low_consumption_with_time.to_excel(writer, sheet_name="Не работает, но включено", index=False)
    redistributed_turned_on.to_excel(writer, sheet_name="Перераспределено(вкл)", index=False, float_format="%.2f")
    redistributed_dips.to_excel(writer, sheet_name="Перераспределено(упадки)", index=False, float_format="%.2f")
os.remove(temp_file)

time_consumption = pd.DataFrame({
    'Время': data_hours.values,
    'Потребление': by_time_consumption.values
})

min_count = time_consumption.groupby('Время').size().min()
if min_count > max_days:
  time_consumption = time_consumption.tail(max_days)

balanced_data = time_consumption.groupby('Время').head(min_count)

#список потребления в одно время потребление список, время значение по котороому группируют [1, 2, 3]
hourly_stats = balanced_data.groupby('Время').agg({
    'Потребление': ['sum', 'mean', 'max', 'count']
})
hourly_stats_sorted = hourly_stats.sort_values(by=('Потребление', 'sum'), ascending=False)
hourly_stats.columns = ['Суммарное', 'Среднее','Максимальное', 'Повторы']

top_peaks = hourly_stats.nlargest(5, ('Суммарное'))

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
#чекай есть ли смысл в среднем для дней
daily_stats.columns = ['Суммарное', 'Среднее', 'Максимальное']

# hourly_original = balanced_data.groupby('Время')['Потребление'].sum()
redistributed_hourly = redistributed_turned_on.iloc[:, 2:].sum(axis=1)
hourly_redistributed = pd.DataFrame({
    'Время': data_hours.values[:len(redistributed_hourly)],
    'Потребление': redistributed_hourly.values
}).groupby('Время')['Потребление'].sum()

redistributed_hourly_second = redistributed_dips.iloc[:, 2:].sum(axis=1)
hourly_redistributed_second = pd.DataFrame({
    'Время': data_hours.values[:len(redistributed_hourly_second)],
    'Потребление': redistributed_hourly_second.values
}).groupby('Время')['Потребление'].sum()

#потребление по часам  (на него наложить оптимизацию???)

plt.figure(figsize=(14, 7))
plt.plot(hourly_stats.index.astype(str), hourly_stats['Суммарное'], label="Потребление", marker='o', color='#1f77b4', linewidth=2)
#######################################################################################################################
plt.plot(hourly_redistributed.index.astype(str), hourly_redistributed.values,
         label="После перераспределения(не работает)", marker='s', color='#2ca02c', linewidth=2)

plt.plot(hourly_redistributed_second.index.astype(str), hourly_redistributed_second.values,
         label="После перераспределения(упадки)", marker='s', color='#9ca03a', linewidth=2)
#############################################################################################################
plt.xlabel("Время")
plt.ylabel("Суммарное потребление (кВт*ч)")
plt.title("Суммарное потребление по времении")
plt.xticks(rotation=45)
# plt.title("Среднее потребление по времении")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('consumption_by_time.png')
plt.show()

#потребление по дням
plt.figure(figsize=(12, 6))
x = daily_stats.index
y = daily_stats['Суммарное']
plt.plot(x, y, label = "Потребление", marker='o', linewidth=2)
plt.xlabel("Даты")
plt.ylabel("Суммарное потребление (кВт*ч)")
plt.title("Суммарное потребление по дням")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('consumption_by_days.png')
plt.show()

plt.figure(figsize=(14, 7))

# Создаем столбчатую диаграмму
bars = plt.bar(daily_stats.index, daily_stats['Суммарное'],
               color='#1f77b4', alpha=0.7, label='Потребление')

# Добавляем значения на столбцы
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}',
             ha='center', va='bottom', fontsize=8)

# Настройки графика
plt.xlabel("Даты", fontsize=12)
plt.ylabel("Суммарное потребление (кВт·ч)", fontsize=12)
plt.title("Суммарное потребление по дням", fontsize=14, pad=20)
plt.xticks(rotation=45)

# Добавляем линию среднего потребления
mean_consumption = daily_stats['Суммарное'].mean()
plt.axhline(y=mean_consumption, color='r', linestyle='--',
            label=f'Среднее: {mean_consumption:.1f} кВт·ч')

plt.legend(fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Сохраняем график
plt.savefig('consumption_by_days_bar.png', dpi=300, bbox_inches='tight')
plt.show()

with pd.ExcelWriter('time_analysis.xlsx') as writer:
    daily_stats.to_excel(writer, sheet_name='Потребление по дням', float_format="%.2f")
    hourly_stats.to_excel(writer, sheet_name='Среднее потребление по временным интервалам', float_format="%.2f")
    top_peaks.to_excel(writer, sheet_name='Топ пиковых временных интервалов', float_format="%.2f")

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

#эту же информацию можно добавить в сообщение тг, тк здесь перечислено главное
report_lines = [
    ["Дата создания", datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    ["Временной отрезок", ],
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

print(f"Файл consumption_report.csv успешно создан!")
