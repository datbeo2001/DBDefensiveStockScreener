import connection as conn
import easygui as ez
import os
import re
from pathlib import Path
from write_result_to_excel import create_file_path, write_to_excel_and_save


class StockScreener:
    def __init__(self):
        self.conn, self.curr = conn.create_connection()
        self._gui_criteria = {"Price/Earnings": "", "Price/Sales": "", "Price/Book": "",
                              "Return On Equity": "", "5-Year Annual Revenue Growth Rate": "",
                              "Exchange": "", "Current Price/High Price": ""}
        self._criteria_reference = {"Price/Earnings": "pe", "Price/Sales": "ps", "Price/Book": "pb",
                           "Return On Equity": "roe", "5-Year Annual Revenue Growth Rate": "rg5y",
                           "Exchange": "exchange", "Current Price/High Price": "current_price/high_price"}
        self._criteria = {"pe": "", "ps": "", "pb": "", "rg5y": "",
                          "current_price/high_price": "", 'roe': "", "exchange": ""}

    def start_gui(self):
        """Start the program"""
        again = True
        self._display_message("Welcome to Defensive Stock Screener, click Next to continue", "Next")
        dir_path = self._display_directory_chooser()
        if dir_path is None:
            again = False
        while again:
            dir_path = Path(dir_path)
            file_name = self._enter_box("Please choose a file name (If nothing is entered, file name will be result)")
            if file_name is None:
                break
            file_path = create_file_path(file_name, dir_path)
            fields, values = self._display_criteria()
            if values is None:
                break
            while self._check_follow_guidelines(values):
                fields, values = self._display_criteria()
                if values is None:
                    break
            if values is None:
                break
            self._add_values_to_criteria(fields, values)
            query = conn.create_query(self._criteria)
            result = conn.execute_query(self.curr, query)
            if result:
                write_to_excel_and_save(file_path, result)
                self._display_message(f"Results have been written to {file_path}")
            else:
                self._display_message("Nothing was found")
            again = self._run_again("Do you want to run again?")
            if again:
                answer = self._run_again(f"Do you want to use directory path {dir_path} again?")
                if not answer:
                    dir_path = self._display_directory_chooser()
                    if dir_path is None:
                        again = False
            else:
                again = False
        self._display_message("Thank you for using DefensiveStockScreener", "Exit")

    def _check_follow_guidelines(self, values: [str]) -> bool:
        """Check if the values from the users follow a certain guideline."""
        pattern = re.compile(r"^(<|<=|>=|>|=) (\d+|\d+\.\d+)$")
        exchange = values[2].lower().strip()
        supported_exchange = {'us', 'vn'}
        if exchange not in supported_exchange:
            return True
        for text in values:
            if text.lower().strip() != "any" and text.lower().strip() not in supported_exchange and \
                    pattern.match(text.strip()) is None:
                return True
        return False

    def _add_values_to_criteria(self, fields: [str], values: [str]) -> None:
        for crit, value in zip(fields, values):
            self._gui_criteria[crit] = value

        for c, v in self._gui_criteria.items():
            self._criteria[self._criteria_reference[c]] = v

    def _display_message(self, message: str, ok_button="Ok") -> None:
        ez.msgbox(message, ok_button=ok_button)

    def _display_criteria(self) -> ([str], [str]):
        msg = "Enter your desired criteria (A comparison operator followed by a space followed by a value or Any" \
              " if you don't want to use the criteria during the filtering.)." \
              " For 'exchange', enter US for the US market."
        title = "Criteria dashboard"
        fields = sorted(self._gui_criteria.keys())
        values = [">= 10", "<= 0.7", "US", "<= 0.7", "< 10", "< 1", "Any"]
        return_values = ez.multenterbox(msg, title, fields, values)
        return fields, return_values

    def _display_directory_chooser(self) -> os.path:
        self._display_message("Please choose where you want to save your results")
        return self._directory_chooser()

    def _run_again(self, msg: str) -> bool:
        return ez.ynbox(msg=msg)

    def stop_gui(self) -> None:
        conn.close_connection(self.conn, self.curr)

    def _directory_chooser(self) -> os.path:
        return ez.diropenbox(title="Choose your directory")

    def _enter_box(self, msg: str) -> str:
        return ez.enterbox(msg=msg, default="result")
