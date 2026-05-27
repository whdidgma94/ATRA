from email_feature.process_report import generate_email_form
from ui.email_form_generator import EmailTemplateApp


def process_email_form(html_path):

    table_form = generate_email_form(html_path)
    app = EmailTemplateApp(table_form)
    app.mainloop()

    return