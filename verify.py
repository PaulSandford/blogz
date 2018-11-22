from flask import Flask, request, redirect




def create(username, password, v_pwd):
    pwd_error = verify_pwd(v_pwd, password)
    username_error = user_chk(username)
        
    return username_error, pwd_error

def user_chk(username):
    if username == "":
        return "Please choose a Username"
    else:
        return check(username)


def verify_pwd(v_pwd, password):

    if v_pwd != password:
        return "Passwords do not match."
    if password == "":
        return "Please enter a password"
    else:
        return check(password)
    
def check(entry):
    if len(entry) < 3 or len(entry) > 20:
        return "Must be 3-20 characters."
    for a in entry:
        if a == " ":
            return "Must contain no spaces"
    return ""
    
def email_check(email):
    if email == "":
        return ""
    if email != "":
        chck = check(email)
    if chck == "":
        for a in range(len(email)):
            if email[a] == "@":
                for b in range(a, len(email)-a-1, 1):
                    if email[b+a] == ".":
                        return ""
    if chck != "":
        return chck
    
    return "Please enter a valid email.(example@email.com)"
