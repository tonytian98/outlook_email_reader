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

        # Connect to the Outlook IMAP server
        self.mail = imaplib.IMAP4_SSL("outlook.office365.com")

        # Login to the email account
        self.mail.login(email_address, password)

    def _extract_text_within_tags(self, html_text):
        pattern = r"<[^>]+>"  # Regular expression pattern to match <any_char_inside>
        matches = re.findall(pattern, html_text)
        return matches

    def _extract_digits(self, text):
        return re.findall(r"\b\d{11}\b", text)

    def _isolated_ATD(self, text):
        return re.findall(r"\bATD\b", text)

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
            _, email_data = self.mail.uid("fetch", item, "(RFC822)")
            raw_email = email_data[0][1].decode("utf-8")
            email_message = email.message_from_string(raw_email)

            datetime_obj = datetime.strptime(
                email_message["Date"], "%a, %d %b %Y %H:%M:%S %z"
            )
            sender_email_address = self._extract_text_within_tags(
                email_message["From"]
            )[0][1:-1]
            subject = email_message["Subject"]
            for part in email_message.walk():
                # each part is a either non-multipart, or another multipart message
                # that contains further parts... Message is organized like a tree
                if part.get_content_type() == "text/plain":
                    email_content = part.get_payload()
                    if self._isolated_ATD(email_content):
                        resulted_account_numbers += self._extract_digits(email_content)

        self.mail.close()
        return resulted_account_numbers


if __name__ == "__main__":
    reader = EmailReader()
    print(reader.extract_ATD_email_account_numbers())
