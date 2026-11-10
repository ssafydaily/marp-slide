def check_signup(email, password):
    if "@" in email:
        return True
    if len(password) > 0:
        return True
    return False
