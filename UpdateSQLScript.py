from ATD_email_account_extraction import EmailReader
import re
from datetime import datetime, timedelta


class UpdateSQLScript:
    def __init__(self, file_path="script.sql"):
        self.file_path = file_path
        with open(self.file_path, "r") as file:
            sql_content = file.read()
            self.existing_accounts = re.findall(r"\b\d{11}\b", sql_content)

    def update_accounts(self, list_of_accounts):
        for account in list_of_accounts:
            if account not in self.existing_accounts:
                self.existing_accounts.append(account)

        self.existing_accounts_wrapped = [
            f"'{account}'" for account in self.existing_accounts
        ]

    def update_dates(
        self,
        look_back_days_max=3,
        look_back_days_min=1,
    ):
        self.oldest_date = (
            datetime.now() - timedelta(days=look_back_days_max)
        ).strftime("%Y-%m-%d")
        self.latest_date = (
            datetime.now() - timedelta(days=look_back_days_min)
        ).strftime("%Y-%m-%d")

    def write_updated_script_to_file(self):
        script = """select * from accounts a left join transactions b\non a.id = b.account_id
    where 
    a.batchentrydate > '%s'
    AND
    a.batchentrydate < '%s'
    AND
    trim(a.ACCOUNTNO) IN (
    %s )""" % (
            self.oldest_date,
            self.latest_date,
            ",\n".join(self.existing_accounts_wrapped),
        )
        with open(self.file_path, "w") as file:
            file.write(script)


if __name__ == "__main__":
    reader = EmailReader()
    print("new accounts:", reader.extract_ATD_email_account_numbers())
    up = UpdateSQLScript()
    up.update_accounts(reader.extract_ATD_email_account_numbers())
    up.update_dates(10, 0)
    up.write_updated_script_to_file()
