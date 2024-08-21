"""
This app helps you plan your path to your next stage of personal finance.
It is a dashboard that shows you the effects of tuning different numbers.
The exact toolset presented will depend on where you're currently at.
The UI will evolve/unlock new tools as you progress through different stages.
"""
import tkinter as tk
from tkinter import ttk
from widgets import (
    BudgetWidget,
    DebtPayoffWidget,
    FireWidget
)


if __name__ == '__main__':
    # create main dashboard window
    ROOT = tk.Tk()
    ROOT.title('Money Dashboard')
    tabs = ttk.Notebook(ROOT)
    tabs.add(BudgetWidget(tabs), text='Budget')
    tabs.add(DebtPayoffWidget(tabs), text='Debt')
    tabs.add(FireWidget(tabs), text='Wealth')
    tabs.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)
    ROOT.mainloop()
