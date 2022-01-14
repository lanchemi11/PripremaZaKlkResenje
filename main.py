
from typing import Counter
from flask import Flask,render_template,request,url_for, redirect, session
import mysql.connector
from flask.templating import render_template_string
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY']= 'ogrbkrglbrlvperpoeveov'

mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="", # ako niste nista menjali u phpmyadminu ovo su standardni
    # username i password
	database="2s2login" # iz phpmyadmin 
    )

@app.route('/register', methods=['POST','GET'])	
def register():
	if request.method == 'GET':
		return render_template(
			'register.html'
		)
	username = request.form['username']
	password = request.form['password']
	confirm = request.form['confirm']
	jmbg = request.form['jmbg']
	email = request.form['email']
	godina_studija = request.form['godina_studija']

	cursor = mydb.cursor(prepared=True)
	sql = 'SELECT * FROM baza WHERE username=?'
	vrednost = (username,)
	cursor.execute(sql,vrednost)
	rez = cursor.fetchone()
	if rez != None:
		return render_template(
			'register.html',
			username_greska = 'Korisnik sa tim usernam-om vec postoji'
		)
	if confirm != password:
		return render_template(
			'register.html',
			pass_greska = 'Ne poklapaju se sifre'
		)
	duzina_jmbg = len(jmbg)
	if duzina_jmbg != 13:
		return render_template(
			'register.html',
			jmbg_greska = 'JMBG mora biti duzine tacno 13 karaktera'
		)

	cursor = mydb.cursor(prepared=True)
	sql_upit = 'INSERT INTO baza VALUES(null,?,?,?,?,?)'
	vrednosti = (username,email,password,godina_studija,jmbg)
	cursor.execute(sql_upit,vrednosti)
	mydb.commit()
	return render_template(
		'show_all.html'
	)
@app.route('/show_all')
def show_all():
	cursor = mydb.cursor(prepared=True)
	sql = 'SELECT * FROM baza'
	cursor.execute(sql)
	rez = cursor.fetchall()

	n = len(rez)
	m = len(rez[0])
	for i in range(n):
		rez[i] = list(rez[i])
		for j in range(m):
			if isinstance(rez[i][j], bytearray):
				rez[i][j] = rez[i][j].decode()
	return render_template(
		'show_all.html',
		rezultat = rez
	)

@app.route('/login', methods=['POST','GET'])
def login():
	if 'username' in session:
		return 'Vec ste registrovani'
	if request.method == 'GET':
		return render_template(
			'login.html'
		)
	username = request.form['username']
	password = request.form['password']

	cursor = mydb.cursor(prepared=True)
	sql = 'SELECT * FROM baza WHERE username=?'
	vrednosti = (username,)
	cursor.execute(sql,vrednosti)
	rez = cursor.fetchone()
	if rez == None:
		return render_template(
			'login.html',
			username_greska = "Ne postoji korisnik sa tim usernam-om"
		)
	rez = list(rez)
	n = len(rez)
	for i in range(n):
		if isinstance(rez[i], bytearray):
			rez[i] = rez[i].decode()

	if password != rez[3]:
		return render_template(
			'login.html',
			pass_greska = 'Ne poklapa se sifra sa sifrom iz baze'
		)

	session['username'] = username
	session['password'] = password
	return redirect(url_for('show_all'))

@app.route('/logout')
def logout():
	if 'username' not in session:
		return redirect(url_for('show_all'))
	if 'username' in session:
		session.pop('username')
		session.pop('password')
		return redirect(url_for('login'))

@app.route('/update/<username>', methods=['POST','GET'])
def update(username):
	cursor = mydb.cursor(prepared=True)
	sql = 'SELECT * FROM baza WHERE username=?'
	vrednost = (username,)
	cursor.execute(sql,vrednost)
	rez = cursor.fetchone()

	rez = konverzija(rez)

	if rez == None:
		return redirect(url_for('show_all'))

	if request.method == 'GET':
		return render_template(
			'update.html',
			korisnik = rez
		)
	username = request.form['username']
	password = request.form['password']
	confirm = request.form['confirm']
	jmbg = request.form['jmbg']
	email = request.form['email']
	godina_studija = request.form['godina_studija']

	cursor = mydb.cursor(prepared=True)
	sql = 'SELECT * FROM baza WHERE username=?'
	vrednosti = (username,)

	cursor.execute(sql,vrednosti)
	rez = cursor.fetchone()
	rez = konverzija(rez)

	if password != confirm:
		return render_template(
			'update.html',
			korisnik = rez,
			pass_greska = 'Sifre se ne poklapaju'
		)
	
	rez = konverzija(rez)
	
	if password != rez[3]:
		return render_template(
			'update.html',
			korisnik = rez,
			pass_greska = 'Nije dobra sifra'
		)

	cursor = mydb.cursor(prepared=True)
	sql_uslov = 'UPDATE baza SET email=?,GodinaStudija=? WHERE username=?'
	vrednosti = (email,godina_studija,username)
	cursor.execute(sql_uslov,vrednosti)
	mydb.commit()
	return redirect(url_for('show_all'))
	
	

@app.route('/delete/<username>')
def delete(username):

	if 'username' not in session:
		return redirect(url_for('login'))
	cursor = mydb.cursor(prepared=True)
	sql = 'DELETE FROM baza WHERE username=?'
	vrednost = (username,)
	cursor.execute(sql,vrednost)
	mydb.commit()
	return redirect(url_for('show_all'))


def konverzija(tupple):	
	tupple = list(tupple)
	n = len(tupple)
	for i in range(n):
		if isinstance(tupple[i], bytearray):
			tupple[i] = tupple[i].decode()
	return tupple

@app.route('/show_year/<year>')
def show_year(year):
	cursor = mydb.cursor(prepared=True)
	sql = 'SELECT * FROM baza WHERE godinaStudija=?'
	vrednost = (year,)
	cursor.execute(sql,vrednost)
	rez = cursor.fetchall()

	n = len(rez)
	for i in range(n):
		rez[i] = konverzija(rez[i])

	if len(rez) == 0:
		return 'Nema korisnika na toj godini studija'

	return render_template(
		'show_year.html',
		korisnik = rez
	)

app.run(debug=True)
