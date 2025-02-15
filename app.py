"""
This app helps you plan your path to your next stage of personal finance.
It is a dashboard that shows you the effects of tuning different numbers.
The exact toolset presented will depend on where you're currently at.
The UI will evolve/unlock new tools as you progress through different stages.
"""
import tkinter as tk
from widgets import BudgetWidget


if __name__ == '__main__':
    # create main dashboard window
    ROOT = tk.Tk()
    ROOT.title('Stage 0')
    BudgetWidget(ROOT).pack(expand=True, fill=tk.BOTH, padx=2, pady=2)
    ROOT.mainloop()
