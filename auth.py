from flask import request, redirect, url_for, render_template, flash, session

# 假设这是我们的用户数据库
users = {
    "admin": "password123"
}

def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            flash('登录成功！')
            return redirect(url_for('home'))
        else:
            flash('用户名或密码错误！')
    return render_template('login.html')

def logout():
    session.pop('username', None)
    flash('已注销！')
    return redirect(url_for('home'))

def is_logged_in():
    return 'username' in session