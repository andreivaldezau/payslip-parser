from datetime import datetime
import os
import pdfplumber
import re
import pandas as pd


def pdfplumber_extract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text: str = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text


df_list: list = []
folder_path: str = os.getcwd() + "/payslips"
for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):
        input_file: str = os.path.join(folder_path, filename)
        try:
            payslip: str = pdfplumber_extract(input_file)
            print(payslip)
            # Extract dates in format "DD/MM/YYYY"
            pattern = r"\d{2}/\d{2}/\d{4}"
            dates: list[str] = re.findall(pattern, payslip, re.MULTILINE)

            # Extract values in format "{-}{dollar}.{cents}"
            # pattern = r"^\d*\.\d{2}(?: \d*\.\d{2})*$"
            pattern = r"^\s*(?:-?\d*\.\d{2}\s*)+$"
            matches: list[str] = re.findall(pattern, payslip, re.MULTILINE)

            # Create dataframe for payslip
            date: datetime = datetime.strptime(dates[1], "%d/%m/%Y").date()
            earnings: list[int] = [float(x) for x in matches[0].split()]
            ytd: list[int] = [float(x) for x in matches[1].split()]
            if len(ytd) == 4:
                ytd.insert(2, 0.0)
            frame: list[datetime | int] = [date] + earnings + ytd
            df_list.append(
                pd.DataFrame(
                    [frame],
                    columns=[
                        "Pay Date",
                        "Gross",
                        "Taxable Income",
                        "Pre Tax Allows/Deds",
                        "Post Tax Allows/Deds",
                        "Tax",
                        "Net Income",
                        "YTD Gross",
                        "YTD Taxable Income",
                        "YTD Deductions",
                        "YTD Tax",
                        "YTD Net",
                    ],
                )
            )
        except RuntimeError:
            print("An error occurred during runtime.")


df: pd.DataFrame = pd.concat(df_list, ignore_index="True")
df = df.sort_values("Pay Date")
df.to_csv("output.csv", index=False)
