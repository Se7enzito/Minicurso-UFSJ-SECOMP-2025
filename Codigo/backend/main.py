from flask import Flask, flash, render_template, redirect, url_for, session, request
from flask_session import Session

from libs.dbAPI import Conexao
from libs.emailAPI import EmailAPI

app = Flask(__name__, template_folder="../frontend/templates")

app.static_folder = '../frontend/src'
app.static_url_path = '/static'

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

conn = Conexao()

# Páginas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    email = session.get('email')
    
    if (user is not None) and (email is not None):
        return render_template('dashboard.html')
    
    formUser = session.pop('formUser', '')
    formEmail = session.pop('formEmail', '')
    formSenha = session.pop('formSenha', '')
    
    return render_template('index.html', user=formUser, email=formEmail, senha=formSenha)

@app.route('/api/user/info', methods=['GET'])
def sessioninfo():
    email = session.get('email')
    user = session.get('user')
    id = session.get('id')
    
    return f'User: {user} / Email: {email} / ID: {id}'

# API
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        formEmail = request.form.get('email')
        formPass = request.form.get('senha')
        
        session['formEmail'] = formEmail
        session['formPass'] = formPass
        
        if formEmail is None or formPass is None or formEmail == "" or formPass == "":
            flash('Todos os campos do login precisam estar preenchidos', 'erro')
            
            return redirect(url_for('entrar'))
        
        if formEmail not in conn.listarEmails():
            flash('Este e-mail não foi encontrado em nosso banco de dados!', 'erro')
            
            return redirect(url_for('entrar'))
        
        loginOk = conn.confirmLogin(formEmail, formPass)
        
        if loginOk:
            session.clear()
            
            session['email'] = formEmail
            session['user'] = conn.getUser(formEmail)
            session['id'] = conn.getId(formEmail)
            
            print(f"Login bem-sucedido: {session['user']}, {session['email']}")
            
            return redirect(url_for('dashboard'))
        else:
            flash('Sua senha está incorreta.', 'erro')
            
            return redirect(url_for('entrar'))
    
    return redirect(url_for('entrar'))

@app.route('/registro', methods = ['POST'])
def registrar():
    if request.method == 'POST':
        formUser = request.form.get('user')
        formEmail = request.form.get('email')
        formPass = request.form.get('senha')
        formCheck = request.form.get('check')

        if formCheck != 'aceito':
            flash('Os termos não foram aceitos.', 'erro')
            
        elif formUser == None or formUser == "":
            flash('Por favor coloque um usuário válido.', 'erro')
            
        elif (formEmail == None or formEmail == "") and (EmailAPI.formato_valido(formEmail) and EmailAPI.dominio_tem_mx(formEmail)):
            flash('Por favor coloque um e-mail válido.', 'erro')
            
        elif formPass == None or formPass == "":
            flash('Por favor coloque uma senha válida.', 'erro')
            
        elif formEmail in conn.listarEmails():
            flash('Alguém já utiliza este e-mail!', 'erro')
            
        else:
            print(f'[DEBUG]: Email: {formEmail} | User: {formUser}')
            
            if (formEmail == '' or formUser == '' or formPass == '') and (formEmail in conn.listarEmails()):
                flash('Ocorreu algum erro criando sua conta!', 'erro')
                
                return redirect(url_for('entrar', form='register'))

            userCriado = conn.criarUser(formUser, formEmail, formPass)
            
            session.clear()
            
            if userCriado == "Utilizador criado com sucesso.":
                print('[DEBUG]: User criado com sucesso!')
                id = conn.getId(formEmail)
                
                session['email'] = formEmail
                session['user'] = formUser
                session['id'] = id
                
                print(f'Credenciais salvas: Email: {formEmail} | User: {formUser} | Id: {id}')
                
                return redirect(url_for('dashboard'))
            else:
                print(f'[DEBUG]: Erro {userCriado}')
                flash('Ocorreu algum erro criando sua conta!', 'erro')
                
                return redirect(url_for('entrar', form='register'))
                
        return redirect(url_for('entrar', form='register'))

@app.route('/api/user/logout')
def logout():
    session.clear()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    conn.criarTabelas()
    
    app.run(debug=True, port=8080)