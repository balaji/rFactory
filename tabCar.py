# Much hacking about to understand how tkinter can provide the GUI that's needed.
# Python 3

import tkinter as tk
from tkinter import ttk

from lib.MC_table import Multicolumn_Listbox
from data.rFactoryConfig import config_tabCar, CarDatafilesFolder, carTags
from data.rFactoryData import getAllCarData, getSingleCarData
import edit.carNtrackEditor as carNtrackEditor

NOFILTER = '---'  # String for not filtering

#########################
# The tab's public class:
#########################


class Tab:
    def __init__(self, parentFrame):
        """ Put this into the parent frame """
        self.parentFrame = parentFrame
        self.settings = None  # PyLint
        o_carData = self.__CarData()
        self.carData = o_carData.fetchData()

        self.mc = Multicolumn_Listbox(
            parentFrame,
            config_tabCar['carColumns'],
            striped_rows=(
                "white",
                "#f2f2f2"),
            command=self.__on_select,
            right_click_command=self.__on_right_click,
            adjust_heading_to_content=False,
            height=30,
            cell_anchor="center")
        # calculate the column widths to fit the headings and the data
        colWidths = []
        for col in config_tabCar['carColumns']:
            colWidths.append(len(col))
        for __, row in self.carData.items():
            for col, column in enumerate(row):
                if len(row[column]) > colWidths[col]:
                    colWidths[col] = len(row[column])
            for col, column in enumerate(row):
                self.mc.configure_column(col, width=colWidths[col] * 7 + 6)
        # Hide the final column (contains DB file ID):
        self.mc.configure_column(
            len(config_tabCar['carColumns']) - 1, width=0, minwidth=0)
        # Justify the data in the first three columns
        self.mc.configure_column(0, anchor='e')
        self.mc.configure_column(1, anchor='w')
        self.mc.configure_column(2, anchor='w')
        self.mc.interior.grid(
            column=0, row=1, pady=2, columnspan=len(
                config_tabCar['carColumns']))

        self.o_filter = self.__Filter(
            parentFrame,
            config_tabCar['carColumns'],
            colWidths,
            o_carData,
            self.mc)
        for _filter in config_tabCar['carFilters']:
            self.o_filter.makeFilter(_filter, self.carData)

        # Initial dummy filter to load data into table
        self.o_filter.filterUpdate(None)

        self.mc.select_row(0)

    def getSettings(self):
        """ Return the settings for this tab """
        return self.settings  # filters too?  Probably not

    def setSettings(self, settings):
        """ Set the settings for this tab """
        self.mc.deselect_all()  # clear what is selected.
        self.o_filter.resetFilters()
        carID = settings[-1]
        for row, car in enumerate(self.carData):
            if carID == self.carData[car]['DB file ID']:
                # the row for carID
                self.mc.select_row(row - 1)
                return
        # Settings not in data
        self.mc.select_row(0)

    def __on_select(self, data):
        self.settings = data
        print('DEBUG')
        print("called command when row is selected")
        print(data)
        print("\n")

    def __on_right_click(self, data):
        """
        On right-clicking car there are two options
        1) Select the specific car
        2) Edit the details
        """
        # don't change data   self.settings = data
        print('DEBUG')
        print("called command when row is right clicked")
        print(data)
        print("\n")

        #ttk.messagebox.askquestion('Car selected')

        top = tk.Toplevel(self.parentFrame)
        top.title("Car editor")

        fields = carTags
        data = getSingleCarData(ident=data[-1], tags=fields)
        o_tab = carNtrackEditor.Editor(
            top, fields, data, DatafilesFolder=CarDatafilesFolder)
        # Need to init the Tab again to get fresh data.

    def get_selection(self):
        """
        Get the data from a set of selected rows
        """
        return self.mc.selected_rows

    class __CarData:
        """ Fetch and filter the car data """

        def __init__(self):
            self.data = None  # Pylint
            self.filteredData = None

        def fetchData(self):
            """ Fetch the raw data from wherever """
            self.data = getAllCarData(
                tags=config_tabCar['carColumns'], maxWidth=20)
            return self.data

        def filterData(self, filters):
            """
            Filter items of the data dict that match all of the filter combobox selections.
            filters is a list of column name, comboBox text() function pairs """
            _data = []
            for _item, _values in self.data.items():
                _data.append(_values.items())

            self.filteredData = []
            for __, _row in self.data.items():
                _match = True
                for _filter in filters:
                    if _row[_filter[0]] != _filter[1](
                    ) and _filter[1]() != NOFILTER:
                        _match = False
                        continue
                if _match:
                    _r = []
                    for colName in config_tabCar['carColumns']:
                        _r.append(_row[colName])
                    self.filteredData.append(_r)

            return self.filteredData

        def setSelection(self, settings):
            """ Match settings to self.data, set table selection to that row """
            # tbd
            pass

    class __Filter:
        """ Filter combobox in frame """

        def __init__(self, mainWindow, columns, colWidths, o_carData, mc):
            self.columns = columns
            self.colWidths = colWidths
            self.mainWindow = mainWindow
            self.o_carData = o_carData
            self.mc = mc
            self.filters = []

        def makeFilter(self, filterName, carData):
            tkFilterText = tk.LabelFrame(self.mainWindow, text=filterName)
            _col = self.columns.index(filterName)
            tkFilterText.grid(column=_col, row=0, pady=0)

            s = set()
            for __, item in carData.items():
                s.add(item[filterName])
            vals = [NOFILTER] + sorted(list(s))
            #modderFilter = tk.StringVar()
            tkComboFilter = ttk.Combobox(
                tkFilterText,
                # textvariable=modderFilter,
                # height=len(vals),
                height=10,
                width=self.colWidths[_col])
            tkComboFilter['values'] = vals
            tkComboFilter.grid(column=1, row=0, pady=5)
            tkComboFilter.current(0)
            tkComboFilter.bind("<<ComboboxSelected>>", self.filterUpdate)
            self.filters.append([filterName, tkComboFilter.get])

        def filterUpdate(self, event):
            """ Callback function when combobox changes """
            carData = self.o_carData.filterData(self.filters)
            self.mc.table_data = carData
            self.mc.select_row(0)

        def resetFilters(self):
            """ Reset all the filters to --- """
            # tbd
            # self.mc.select_row(0)

        def setFilters(self, settings):  # pylint: disable=unused-argument
            """ Set all the filters to settings """
            # tbd
            self.mc.select_row(0)


if __name__ == '__main__':
    # To run this tab by itself for development
    root = tk.Tk()
    tabCar = ttk.Frame(
        root,
        width=1200,
        height=1200,
        relief='sunken',
        borderwidth=5)
    tabCar.grid()

    o_tab = Tab(tabCar)

    root.mainloop()
