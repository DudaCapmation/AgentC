def send_email(
        to_email: str,
        subject: str,
        body: str
):
    # Simulating email sending, no actual email sent
    return f"Simulated sending email to {to_email} with subject '{subject}'. Body length: {len(body)} characters."


FUNCTION_MAP = {
    "send_email": send_email,
}