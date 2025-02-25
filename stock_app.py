import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import pytz
from matplotlib.widgets import Cursor
import pandas as pd

def fetch_data():
    ticker = ticker_entry.get().upper()
    date_str = date_entry.get()
    timezone = timezone_var.get()

    try:
        # 解析输入日期
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        ny_tz = pytz.timezone('America/New_York')
        
        # 计算纽约时间交易时段
        trade_day = ny_tz.localize(target_date)
        trade_start = trade_day.replace(hour=9, minute=30)
        trade_end = trade_day.replace(hour=16, minute=0)
        
        # 计算24小时时间范围（包含前24小时+当日交易时段）
        data_start = trade_start - timedelta(hours=24)
        data_end = trade_end
        
        # 转换为UTC
        start_utc = data_start.astimezone(pytz.utc).replace(tzinfo=None)
        end_utc = data_end.astimezone(pytz.utc).replace(tzinfo=None)

        # 获取数据
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_utc, end=end_utc, interval="1m")

        if df.empty:
            messagebox.showerror("Error", f"No data for {ticker} between {data_start} and {data_end}")
            return

        # 时区转换
        target_tz = pytz.timezone('Asia/Shanghai') if timezone == "Beijing" else ny_tz
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        df = df.tz_convert(target_tz)
        
        # 过滤出目标时间范围（前24小时+当日交易时段）
        filter_start = data_start.astimezone(target_tz)
        filter_end = data_end.astimezone(target_tz)
        df = df[(df.index >= filter_start) & (df.index <= filter_end)]
        
        if df.empty:
            messagebox.showerror("Error", "No data in selected time window")
            return

        create_chart(df, ticker, target_tz)
        create_data_table(df)

    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")

def create_chart(df, ticker, target_tz):
    plt.close('all')
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [3, 1]})
    
    # 绘制价格
    ax1.plot(df.index, df['Close'], 
            color='#1f77b4',
            linewidth=1.5,
            marker='o',
            markersize=4,
            markerfacecolor='#ff7f0e',
            markeredgewidth=0.5)
    
    # 设置时间轴
    ax1.xaxis.set_major_locator(HourLocator(interval=3))
    ax1.xaxis.set_minor_locator(MinuteLocator(byminute=[30]))
    ax1.xaxis.set_major_formatter(DateFormatter('%m/%d %H:%M', tz=target_tz))
    ax1.grid(which='major', color='#dddddd', linestyle='--')
    ax1.grid(which='minor', color='#eeeeee', linestyle=':')
    
    ax1.set_ylabel('Price', color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    ax1.set_title(f"{ticker} Price & Volume ({target_tz.zone} Time)", pad=20)

    # 成交量处理
    colors = []
    for i in range(len(df)):
        if df['Close'][i] > df['Open'][i]:
            colors.append('#2ca02c')  # 上涨绿色
        elif df['Close'][i] < df['Open'][i]:
            colors.append('#d62728')  # 下跌红色
        else:
            colors.append('#7f7f7f')   # 平盘灰色
    
    ax2.bar(df.index, df['Volume'], color=colors, width=0.002, alpha=0.8)
    ax2.set_ylabel('Volume')
    ax2.xaxis.set_major_formatter(DateFormatter('%m/%d %H:%M', tz=target_tz))
    
    # 光标交互
    cursor = Cursor(ax1, useblit=True, color='#9467bd', linewidth=1)
    annot = ax1.annotate('', xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w", alpha=0.9),
                        arrowprops=dict(arrowstyle="->"))
    
    def update_annot(event):
        if event.inaxes == ax1:
            x = event.xdata
            y = event.ydata
            dt = mdates.num2date(x).astimezone(target_tz)
            annot.xy = (x, y)
            annot.set_text(f"{dt.strftime('%Y-%m-%d %H:%M:%S')}\nPrice: {y:.2f}")
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            annot.set_visible(False)
            fig.canvas.draw_idle()
    
    fig.canvas.mpl_connect("motion_notify_event", update_annot)
    plt.tight_layout()
    plt.show()

def create_data_table(df):
    table_window = tk.Toplevel()
    table_window.title("Historical Data")
    
    # 创建带滚动条的表格
    tree = ttk.Treeview(table_window, columns=('Time', 'Open', 'High', 'Low', 'Close', 'Volume'), show='headings')
    vsb = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_window, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    # 列配置
    tree.heading('Time', text='Time (' + str(df.index.tz) + ')')
    tree.column('Time', width=150, anchor='w')
    for col in ['Open', 'High', 'Low', 'Close']:
        tree.heading(col, text=col)
        tree.column(col, width=90, anchor='e')
    tree.heading('Volume', text='Volume')
    tree.column('Volume', width=120, anchor='e')
    
    # 填充数据
    for index, row in df.iterrows():
        time_str = index.strftime('%Y-%m-%d %H:%M')
        tree.insert('', 'end', values=(
            time_str,
            f"{row['Open']:.2f}",
            f"{row['High']:.2f}",
            f"{row['Low']:.2f}",
            f"{row['Close']:.2f}",
            f"{row['Volume']:,}"
        ))
    
    # 布局
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    table_window.grid_rowconfigure(0, weight=1)
    table_window.grid_columnconfigure(0, weight=1)

# GUI界面
root = tk.Tk()
root.title("Stock Analysis Pro 4.0")
root.geometry("400x220")

style = ttk.Style()
style.configure('TButton', font=('Arial', 10), padding=6)
style.configure('TLabel', font=('Arial', 10))

main_frame = ttk.Frame(root, padding=15)
main_frame.pack(expand=True)

ttk.Label(main_frame, text="Stock Ticker:").grid(row=0, column=0, sticky=tk.W, pady=3)
ticker_entry = ttk.Entry(main_frame, width=15)
ticker_entry.grid(row=0, column=1, padx=5)
ticker_entry.insert(0, "AAPL")

ttk.Label(main_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=3)
date_entry = ttk.Entry(main_frame, width=15)
date_entry.grid(row=1, column=1, padx=5)
date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

ttk.Label(main_frame, text="Timezone:").grid(row=2, column=0, sticky=tk.W, pady=3)
timezone_var = tk.StringVar(value="Beijing")
timezone_combo = ttk.Combobox(main_frame, textvariable=timezone_var, 
                            values=["Beijing", "New York"], width=12)
timezone_combo.grid(row=2, column=1)

fetch_btn = ttk.Button(main_frame, text="Generate Report", command=fetch_data)
fetch_btn.grid(row=3, column=0, columnspan=2, pady=12)

root.mainloop()