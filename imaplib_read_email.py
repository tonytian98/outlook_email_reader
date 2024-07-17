import imaplib
import email
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from datetime import datetime
import re


class EmailReader:
    def __init__(self):
        load_dotenv()
        email_address = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_APP_PASSWORD")
        search_date_days = int(os.getenv("LOOK_BACK_DAYS"))
        self.unseen_flag = os.getenv("UNSEEN_EMAIL_ONLY").lower()

        self.search_date = (datetime.now() - timedelta(days=search_date_days)).strftime(
            "%d-%b-%Y"
        )
        print(self.search_date)
        # Connect to the Outlook IMAP server
        self.mail = imaplib.IMAP4_SSL("outlook.office365.com")

        # Login to the email account
        self.mail.login(email_address, password)

    def _extract_text_within_tags(self, html_text):
        pattern = r"<[^>]+>"  # Regular expression pattern to match <any_char_inside>
        matches = re.findall(pattern, html_text)
        return matches

    def _extract_digits(self, text, length=11):
        pattern_str = f"\b\d{{{length}}}\b"
        pattern = re.compile(pattern_str)
        matches = pattern.findall(pattern, text)
        return matches

    def extract_ATD_email_account_numbers(self):
        # Select the inbox folder
        self.mail.select("inbox")
        email_status = ""
        if self.unseen_flag == "true":
            email_status += "UNSEEN"

        # Search for unread emails received after the specified date
        _, data = self.mail.uid(
            "search", None, f"SINCE {self.search_date} " + email_status
        )
        inbox_item_list = data[0].split()

        resulted_account_numbers = []
        # Fetch the email headers
        for item in inbox_item_list:
            _, email_data = self.mail.uid("fetch", item, "(BODY[])")
            print(_, email_data)
            raw_email = email_data[0][1].decode("utf-8")

            # Parse the email headers
            email_message = email.message_from_string(raw_email)
            # yyy-mm-dd hh:mm:ss+tz:tz
            datetime_obj = datetime.strptime(
                email_message["Date"], "%a, %d %b %Y %H:%M:%S %z"
            )
            sender_email_address = self._extract_text_within_tags(
                email_message["From"]
            )[0][1:-1]
            subject = email_message["Subject"]
            print(email_message["Body"])
            if "ATD" in subject:
                resulted_account_numbers += self._extract_digits(subject)
        # Close the connection
        self.mail.close()
        return resulted_account_numbers


if __name__ == "__main__":
    reader = EmailReader()
    print(reader.extract_ATD_email_account_numbers())
