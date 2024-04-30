from flask import Flask,jsonify,request
from config import config
from flask_mysqldb import MySQL,MySQLdb

app =Flask(__name__)

connection = MySQL(app)

usersLogged = set()

@app.route('/faps',methods=['GET'])
def fapsList():
    try:
        cursor = connection.connection.cursor()
        sql = "SELECT * FROM fap LIMIT 100"
        cursor.execute(sql)
        fapData = cursor.fetchall()
        faps = []
        for data in fapData:
            fap = {'fapId':data[0],
                    'accountId':data[1],
                    'beginFap':data[2],
                    'endFap':data[3],
                    'fapDetail':data[4]}
            faps.append(fap)
        return jsonify({'faps':faps,'mensaje':'fapsListados'})

    except Exception as ex:
        return jsonify({'mensaje':'Error'})

@app.route('/account_data/<codigo>',methods=['GET'])
def fap_account(codigo):
    try:
        cursor = connection.connection.cursor()
        sql = f"SELECT * from account WHERE accountId = {codigo}"
        cursor.execute(sql)
        accountData = cursor.fetchone()
        if accountData != None:
            account_data = {
                'accountId':accountData[0],
                'username':accountData[1],
                'hashedPassword':accountData[2],
                'sex':accountData[3],
                'sexualPreference':[4],
                'birthdate':accountData[5]
            }
        return jsonify({'account_data':account_data,'mensaje':'cuenta encontrada'})

    except Exception as ex:
        return jsonify({'mensaje':'Error'})



@app.route('/faps/<codigo>',methods = ['GET'])
def leer_curso(codigo):
    try:
        cursor = connection.connection.cursor()
        sql = f"SELECT * FROM fap WHERE fapId = {codigo} LIMIT 100"
        cursor.execute(sql)
        data = cursor.fetchone()
        if data != None:
            fap = {'fapId':data[0],
                    'accountId':data[1],
                    'beginFap':data[2],
                    'endFap':data[3],
                    'fapDetail':data[4]}
            return jsonify({'fap':fap,'mensaje':'fap Encontrado'})
        return jsonify({'mensaje':'fap no Encontrado'})
    except Exception as ex:
        return '<h1>Error</h1>',500

def no_page(error):
    return '<h1>Pagina no encontrada</h1>',404

@app.route('/faps',methods=['POST'])
def register_account():
    try:
        cursor = connection.connection.cursor()
        sql ='INSERT INTO account(username,hashedPassword,sex,sexualPreference,birthdate) VALUES("{0}","{1}","{2}","{3}","{4}")'.format(
            request.json['username'],request.json['hashedPassword'],request.json['sex'],request.json['sexualPreference'],request.json['birthdate'])
        cursor.execute(sql)
        connection.connection.commit() #confirma la accion de inserccion
        return jsonify({'mensaje':'cuenta registrada'})
    except MySQLdb.IntegrityError as ex:
        return '<h1>este usuario ya existe</h1>',409
    except Exception as ex:

        return f'<h1>{ex}</h1>',500

@app.route('/faps-name/<codigo>',methods=['GET'])
def fap_account_by_name(codigo):
    try:
        cursor = connection.connection.cursor()
        sql = f'SELECT * FROM account WHERE username LIKE "{codigo.strip()}"'
        cursor.execute(sql)
        account_data = cursor.fetchone()
        if account_data != None:
            account_data = {
                'accountId':account_data[0],
                'username':account_data[1],
                'hashedPassword':account_data[2],
                'sex':account_data[3],
                'sexualPreference':[4],
                'birthdate':account_data[5]
            }
            return jsonify({'cuenta':account_data,'mensaje':'cuenta encontrada con exito'})
        return jsonify({'mensaje':'cuenta no encontrada'})

    except Exception as ex:
        print(ex)
        return jsonify({'mensaje':'Error'})

@app.route('/faps-name-filter/<codigo>',methods=['GET'])
def fap_account_by_name_filter(codigo):
    try:
        cursor = connection.connection.cursor()
        sql = f'SELECT * FROM account WHERE username LIKE "%{codigo.strip()}%"'
        cursor.execute(sql)
        accounts_data = cursor.fetchall()
        accounts = []
        if accounts_data != None:
            for account_data in accounts_data:
                account = {
                'accountId':account_data[0],
                'username':account_data[1],
                'hashedPassword':account_data[2],
                'sex':account_data[3],
                'sexualPreference':[4],
                'birthdate':account_data[5]
                }
                accounts.append(account)
            return jsonify({'cuentas':accounts,'mensaje':'cuenta encontrada con exito'})
        return jsonify({'mensaje':'cuenta no encontrada'})

    except Exception as ex:
        return jsonify({'mensaje':'Error'})

@app.route('/faps/<codigo>',methods = ['DELETE'])
def delete_account(codigo):
    try:
        cursor = connection.connection.cursor()
        sql =f'DELETE FROM account WHERE accountId = {codigo}'
        cursor.execute(sql)
        connection.connection.commit() #confirma la accion de inserccion
        return jsonify({'mensaje':'curso eliminado'})
    except Exception as ex:

        return f'<h1>{ex}</h1>',500

@app.route('/accounts-faps/<codigo>', methods=['GET'])
def get_fap_by_account_id(codigo):
    try:
        cursor = connection.connection.cursor()
        sql = f'SELECT f.* FROM fap f INNER JOIN account a ON a.accountId = f.accountId WHERE a.accountId = {codigo}'
        cursor.execute(sql)
        faps_data = cursor.fetchall()
        faps = []
        if faps_data:
            for fap_data in faps_data:
                fap = {
                    'fapId': fap_data[0],
                    'accountId': fap_data[1],
                    'beginFap': fap_data[2],
                    'endFap': fap_data[3],
                    'fapDetail': fap_data[4]
                }
                faps.append(fap)
            return jsonify({'faps': faps, 'mensaje': 'faps encontradas'})
        return jsonify({'mensaje': 'usuario sin faps'})
    except Exception as ex:
        return f'<h1>{ex}</h1>', 500

@app.route('/fall',methods=['POST'])
def caer():
    try:
        cursor = connection.connection.cursor()
        sql ='INSERT INTO fap(accountId,beginFap,endFap,fapDetail) VALUES("{0}","{1}","{2}","{3}")'.format(
            request.json['accountId'],request.json['beginFap'],request.json['fapDetail'],)
        cursor.execute(sql)
        connection.connection.commit() #confirma la accion de inserccion
        return jsonify({'mensaje':'caida registrada'})

    except Exception as ex:

        return f'<h1>{ex}</h1>',500

@app.route('/podium',methods = ['GET'])
def podium():
    try:
        cursor = connection.connection.cursor()
        sql = "SELECT f.*,a.username from fap f INNER JOIN account a ON a.accountId = f.accountId ORDER BY endFap LIMIT 50"
        cursor.execute(sql)
        podium_data = cursor.fetchall()
        faps_podium = []
        if podium_data:
            for fap_data in podium_data:
                fap = {
                      'fapId':fap_data[0],
                      'accounId':fap_data[1],
                      'beginFap':fap_data[2],
                      'endFap':fap_data[3],
                      'fapDetail':fap_data[4],
                      'username':fap_data[5],
                }
                faps_podium.append(fap)
            return jsonify({'podio':faps_podium,'mensaje':'elementos del podio'})
        return jsonify({'mensaje':'sin datos'})
    except Exception as ex:
        return f'<h1>{ex}</h1>',500

@app.route('/login',methods = ['POST'])
def login():
    try:
        user = request.json['username']
        password = request.json['password']
        
        if user in usersLogged:
            return jsonify({"mensaje":"usuario ya logeado"})
        
        cursor = connection.connection.cursor()
        sql = f"SELECT * FROM account WHERE username = '{user}'"
        cursor.execute(sql)
        
        data = cursor.fetchone()
        
        if data != None:
            sql = f"SELECT * FROM account WHERE hashedPassword = PASSWORD('{password}')"
            cursor.execute(sql)
            data_password = cursor.fetchone()
        
            if data_password != None:
                usersLogged.add(user)
                print(usersLogged)
                return jsonify({"mensaje":"logeado"})   
           
            return jsonify({"mensaje":"contraseña incorrecta"})
        
        return jsonify({"mensaje":"no se encuentra el usuario"}) 
   
    except Exception as ex:
        return f'<h1>{ex}</h1>',500

@app.route('/logout',methods = ['POST'])
def logout():
    try:
        user = request.json['username']
        if user in usersLogged:
            usersLogged.discard(user)
            print(usersLogged)
        return jsonify({"mensaje":"salida de sesion completada"})
    except Exception as ex:
        return f'<h1>{ex}</h1>',500



if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404,no_page)
    app.run()