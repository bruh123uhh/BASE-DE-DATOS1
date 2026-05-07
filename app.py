"""
===================================================
  SISTEMA DGT / INTERIOR - BASE DE DATOS FICTICIA
  USO EDUCATIVO - APRENDIZAJE DE PROGRAMACIÓN
===================================================
  Ejecutar: python app.py
  Abrir:    http://localhost:5000
  Admin:    http://localhost:5000/admin  (usuario: admin / pass: admin123)
"""

import sqlite3, random, string, json, os, hashlib
from datetime import date, datetime, timedelta
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, g

app = Flask(__name__)
app.secret_key = "dgt_educativo_2024"
DB_PATH = os.path.join(os.path.dirname(__file__), "dgt.db")

# ──────────────────────────────────────────────
#  UTILIDADES BASE DE DATOS
# ──────────────────────────────────────────────
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db: db.close()

def query(sql, params=(), one=False):
    cur = get_db().execute(sql, params)
    r = cur.fetchone() if one else cur.fetchall()
    return r

def execute(sql, params=()):
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur.lastrowid

# ──────────────────────────────────────────────
#  GENERADORES FICTICIOS
# ──────────────────────────────────────────────
LETS_MAT = "BCDFGHJKLMNPRSTUVWXYZ"   # 20 letras válidas DGT (sin vocales, Ñ, Q, U, V)
LETS_DNI  = "TRWAGMYFPDXBNJZSQVHLCKE"
PROVINCIAS = ["Madrid","Barcelona","Valencia","Sevilla","Zaragoza","Málaga","Murcia",
    "Palma","Las Palmas","Bilbao","Alicante","Córdoba","Valladolid","Vigo","Gijón",
    "Granada","La Coruña","Vitoria","Pamplona","Almería","Santander","Burgos",
    "Albacete","Salamanca","Toledo","Logroño","Badajoz","Huelva","Tarragona",
    "Lleida","Girona","Castellón","Jaén","Cádiz","León","Lugo","Pontevedra",
    "Ourense","Tenerife","Ibiza","Cuenca","Huesca","Teruel","Soria","Ávila",
    "Segovia","Zamora","Palencia","Ciudad Real","Guadalajara"]
NOMBRES_H = ["Alejandro","Carlos","David","Fernando","Javier","José","Juan","Luis",
    "Manuel","Miguel","Pablo","Rafael","Sergio","Alberto","Andrés","Óscar","Diego",
    "Eduardo","Iván","Marcos","Roberto","Tomás","Víctor","Adrián","Álvaro","Daniel",
    "Emilio","Felipe","Gonzalo","Héctor","Ignacio","Jorge","Kevin","Leonardo","Mateo"]
NOMBRES_M = ["Ana","Carmen","Elena","Isabel","Laura","Lucía","María","Marta","Nuria",
    "Patricia","Pilar","Rosa","Sandra","Sofía","Beatriz","Cristina","Esperanza",
    "Gloria","Inés","Irene","Julia","Leire","Mercedes","Miriam","Natalia","Olga",
    "Paula","Raquel","Silvia","Teresa","Úrsula","Valentina","Wendy","Yolanda","Zaida"]
APELLIDOS = ["García","Martínez","Fernández","López","González","Rodríguez","Sánchez",
    "Ramírez","Díaz","Torres","Muñoz","Álvarez","Romero","Alonso","Moreno","Gutiérrez",
    "Serrano","Ramos","Cruz","Reyes","Flores","Gómez","Iglesias","Cano","Ortiz",
    "Delgado","Castro","Vidal","Blanco","Morales","Peña","Vargas","Molina","Parra",
    "Lara","Jiménez","Rubio","Navarro","Ruiz","Gil","Herrera","Campos","Fuentes",
    "Ríos","Vera","Prado","Luna","Santos","Calvo","Prieto","Aguilar","Medina"]
CALLES = ["Calle Mayor","Avenida de la Constitución","Gran Vía","Paseo del Prado",
    "Calle Alcalá","Rambla de Catalunya","Calle Serrano","Avenida de América",
    "Calle Fuencarral","Paseo de Gracia","Calle Goya","Avenida Diagonal",
    "Calle Toledo","Ronda de Atocha","Calle Hortaleza","Paseo de la Castellana",
    "Calle Bravo Murillo","Calle Valencia","Calle Provença","Calle Muntaner",
    "Rambla del Poblenou","Calle Balmes","Avinguda Meridiana","Calle Colón",
    "Calle del Carmen","Avenida Libertad","Paseo Marítimo","Calle Real","Calle Nueva"]
MARCAS_TURISMO = ["SEAT","Volkswagen","Ford","Renault","Toyota","Peugeot","Opel",
    "Hyundai","Kia","Citroën","BMW","Mercedes","Audi","Skoda","Dacia","Nissan",
    "Mazda","Honda","Volvo","Jeep","Fiat","Alfa Romeo","Mitsubishi","Subaru"]
MARCAS_FURG = ["Ford","Renault","Mercedes","Volkswagen","Fiat","Peugeot","Citroën",
    "Nissan","Iveco","Opel","Toyota","Stellantis"]
MARCAS_MOTO = ["Honda","Yamaha","Kawasaki","Suzuki","BMW","Ducati","Aprilia","KTM",
    "Piaggio","Vespa","Triumph","Royal Enfield"]
MARCAS_CAMION = ["Scania","MAN","Volvo","DAF","Mercedes","Iveco","Renault Trucks"]
MARCAS_BUS = ["Mercedes","Volvo","Irizar","Iveco","Setra","MAN"]
MODELOS = {
    "SEAT":["León","Ibiza","Arona","Ateca","Tarraco","Toledo","Alhambra"],
    "Volkswagen":["Golf","Polo","Tiguan","Passat","T-Roc","Touareg","ID.4"],
    "Ford":["Focus","Fiesta","Kuga","Mondeo","Transit","Ranger","Mustang"],
    "Renault":["Clio","Megane","Captur","Kadjar","Trafic","Master","Zoe"],
    "Toyota":["Corolla","Yaris","RAV4","C-HR","Hilux","Land Cruiser","Prius"],
    "Peugeot":["208","308","3008","5008","Partner","Expert","e-208"],
    "Opel":["Corsa","Astra","Crossland","Mokka","Vivaro","Zafira"],
    "Hyundai":["i20","i30","Tucson","Santa Fe","Kona","Ioniq 5"],
    "Kia":["Ceed","Sportage","Stonic","Sorento","Picanto","EV6"],
    "Citroën":["C3","C4","Berlingo","Jumpy","SpaceTourer","C5 X"],
    "BMW":["Serie 1","Serie 3","Serie 5","X1","X3","X5","i3"],
    "Mercedes":["Clase A","Clase C","Clase E","GLA","GLC","Actros","Tourismo"],
    "Audi":["A1","A3","A4","A6","Q3","Q5","e-tron"],
    "Skoda":["Fabia","Octavia","Karoq","Kodiaq","Superb"],
    "Dacia":["Sandero","Duster","Logan","Jogger","Spring"],
    "Nissan":["Micra","Juke","Qashqai","X-Trail","Leaf"],
    "Mazda":["CX-5","Mazda3","CX-30","MX-5","MX-30"],
    "Honda":["Civic","CR-V","CB500F","PCX125","Forza 350"],
    "Volvo":["XC40","XC60","S60","FH16","FMX"],
    "Jeep":["Renegade","Compass","Grand Cherokee","Wrangler"],
    "Fiat":["Punto","Tipo","500","Doblò","Ducato"],
    "Kawasaki":["Z650","Z900","Ninja 650","Versys 650","H2"],
    "Suzuki":["GSX-S750","V-Strom 650","Bandit","Intruder"],
    "Ducati":["Monster","Panigale V4","Multistrada","Scrambler"],
    "Aprilia":["RS 660","Tuono","SX 125"],
    "KTM":["Duke 390","Duke 890","Adventure 1290"],
    "Yamaha":["MT-07","MT-09","R1","XMAX 300","Tracer 9"],
    "Scania":["R450","R580","G410","S500"],
    "MAN":["TGX 18.580","TGX 26.460","TGL 12.220"],
    "DAF":["XF 480","CF 440","LF 180"],
    "Iveco":["Daily","S-Way","Stralis","Eurocargo"],
    "Irizar":["i6S","i8","i3"],
    "Setra":["S 516 HD","S 431 DT"],
    "DEFAULT":["Modelo X","Modelo Y","Modelo Z"]
}
COMBUSTIBLES = ["Gasolina","Diésel","Híbrido","Eléctrico","GLP","GNC","Híbrido Enchufable"]
COLORES = ["Blanco","Negro","Gris","Rojo","Azul","Verde","Plata","Naranja","Marrón","Amarillo","Beige","Granate"]
USOS = ["Particular","Particular","Particular","Empresarial","Taxi","Alquiler","Transporte escolar"]
ESTADOS_MAT = ["Activa","Activa","Activa","Activa","Activa","Activa","Suspendida","Baja","Pendiente","Transferida"]
PROFESIONES = ["Médico/a","Enfermero/a","Maestro/a","Ingeniero/a","Abogado/a","Electricista",
    "Fontanero/a","Mecánico/a","Camionero/a","Informático/a","Comercial","Administrativo/a",
    "Hostelería","Agricultor/a","Policía","Bombero/a","Arquitecto/a","Economista",
    "Periodista","Chef","Carpintero/a","Albañil","Taxista","Pintor/a","Psicólogo/a",
    "Veterinario/a","Farmacéutico/a","Fisioterapeuta","Autónomo/a","Jubilado/a"]
ESTADO_CIVIL = ["Soltero/a","Casado/a","Divorciado/a","Viudo/a","Pareja de hecho"]
NACIONALIDADES = ["Española","Española","Española","Española","Española","Marroquí","Rumana",
    "Colombiana","Ecuatoriana","Venezolana","Argentina","Peruana","Italiana","Francesa",
    "Alemana","Británica","Portuguesa","China","Ucraniana","Boliviana"]
BANCOS = ["Santander","BBVA","CaixaBank","Bankinter","Sabadell","ING","Unicaja","Openbank"]
ESTUDIOS = ["Primaria","Secundaria","Bachillerato","FP Grado Medio","FP Grado Superior",
    "Grado Universitario","Máster","Doctorado"]
SITUACION_LAB = ["Empleado/a","Autónomo/a","Desempleado/a","Jubilado/a","Estudiante"]
TIPOS_ALERTA = ["Busca y Captura","Requisitoria Judicial","Vigilancia Especial","Multas Pendientes"]
MOTIVOS = {
    "Busca y Captura":["Robo con violencia","Tráfico de drogas","Estafa bancaria","Agresión grave",
        "Homicidio frustrado","Robo en domicilio","Fraude fiscal grave","Secuestro","Terrorismo"],
    "Requisitoria Judicial":["Impago pensión alimenticia","Delito informático","Falsedad documental",
        "Delito contra la propiedad","Incumplimiento condena","Fuga de prisión provisional"],
    "Vigilancia Especial":["Antecedentes reincidentes","Pertenencia a banda organizada",
        "Investigación en curso","Control judicial de alejamiento"],
    "Multas Pendientes":["Multas de tráfico impagadas","Multas administrativas","Sanciones pendientes"]
}
JUZGADOS = ["Juzg. Instrucción nº1 Madrid","Juzg. Instrucción nº3 Barcelona",
    "Juzg. Instrucción nº2 Valencia","Juzg. Instrucción nº1 Sevilla",
    "Juzg. Penal nº4 Madrid","Juzg. Penal nº2 Barcelona",
    "Juzg. Instrucción nº5 Málaga","Juzg. Instrucción nº1 Bilbao"]
EMISORES = ["Guardia Civil","Policía Nacional","Mossos d'Esquadra","Policía Local",
    "Interpol España","UDEV Central","Juzgado Central","Europol"]
DOMINIOS = ["gmail.com","hotmail.com","yahoo.es","outlook.es","telefonica.net","correo.es"]

def rnd_date(y1, y2):
    start = date(y1, 1, 1)
    end = date(y2, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def calcular_letra_dni(n):
    return LETS_DNI[n % 23]

def gen_dni(numero):
    return f"{numero:08d}{calcular_letra_dni(numero)}"

def gen_matricula(num, l1, l2, l3):
    return f"{num:04d} {l1}{l2}{l3}"

def get_marca_by_tipo(tipo):
    m = {"Turismo": MARCAS_TURISMO, "Furgoneta": MARCAS_FURG,
         "Motocicleta": MARCAS_MOTO, "Camión": MARCAS_CAMION,
         "Autobús": MARCAS_BUS, "Remolque": ["Schmitz","Krone","Kogel","Fliegl"]}
    return random.choice(m.get(tipo, MARCAS_TURISMO))

def get_modelo(marca):
    return random.choice(MODELOS.get(marca, MODELOS["DEFAULT"]))

def gen_bastidor():
    chars = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
    return ''.join(random.choices(chars, k=17))

def gen_cv(tipo):
    m = {"Camión":ri(280,600),"Autobús":ri(240,450),"Motocicleta":ri(14,200),
         "Furgoneta":ri(90,180),"Remolque":0}
    return m.get(tipo, ri(70,400))

def ri(a, b): return random.randint(a, b)

# ──────────────────────────────────────────────
#  INICIALIZAR BASE DE DATOS
# ──────────────────────────────────────────────
def init_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript("""
    PRAGMA journal_mode=WAL;

    CREATE TABLE IF NOT EXISTS ciudadanos (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        dni                  TEXT NOT NULL UNIQUE,
        nombre               TEXT NOT NULL,
        apellido1            TEXT NOT NULL,
        apellido2            TEXT,
        sexo                 TEXT,
        fecha_nac            TEXT,
        provincia_residencia TEXT,
        municipio            TEXT,
        direccion            TEXT,
        numero_via           TEXT,
        piso                 TEXT,
        codigo_postal        TEXT,
        telefono             TEXT,
        telefono2            TEXT,
        email                TEXT,
        nacionalidad         TEXT DEFAULT 'Española',
        estado_civil         TEXT,
        num_hijos            INTEGER DEFAULT 0,
        profesion            TEXT,
        situacion_laboral    TEXT,
        nivel_estudios       TEXT,
        ingresos_anuales     INTEGER,
        banco_ref            TEXT,
        num_cuenta           TEXT,
        licencia_conducir    TEXT DEFAULT 'No',
        tipo_licencia        TEXT,
        puntos_carnet        INTEGER DEFAULT 15,
        antecedentes_penales TEXT DEFAULT 'No',
        num_pasaporte        TEXT,
        fecha_exp_dni        TEXT,
        fecha_cad_dni        TEXT,
        alerta_policial      TEXT DEFAULT 'Sin alertas',
        notas_admin          TEXT,
        created_at           TEXT DEFAULT (datetime('now')),
        updated_at           TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS matriculas (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        matricula            TEXT NOT NULL UNIQUE,
        dni                  TEXT NOT NULL,
        tipo_vehiculo        TEXT,
        marca                TEXT,
        modelo               TEXT,
        año_fab              INTEGER,
        fecha_mat            TEXT,
        estado               TEXT DEFAULT 'Activa',
        combustible          TEXT,
        cv                   INTEGER,
        co2_grkg             INTEGER,
        bastidor             TEXT UNIQUE,
        fecha_itv            TEXT,
        color                TEXT,
        uso                  TEXT,
        km                   INTEGER DEFAULT 0,
        num_puertas          INTEGER,
        num_plazas           INTEGER,
        tara_kg              INTEGER,
        masa_max_kg          INTEGER,
        seguro_compañia      TEXT,
        seguro_poliza        TEXT,
        seguro_hasta         TEXT,
        num_infracciones     INTEGER DEFAULT 0,
        importe_multas       INTEGER DEFAULT 0,
        titular_anterior     TEXT,
        notas_admin          TEXT,
        created_at           TEXT DEFAULT (datetime('now')),
        updated_at           TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (dni) REFERENCES ciudadanos(dni) ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS alertas_policiales (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        dni              TEXT NOT NULL,
        tipo_alerta      TEXT,
        motivo           TEXT,
        emisor           TEXT,
        fecha_emision    TEXT,
        fecha_caducidad  TEXT,
        juzgado          TEXT,
        num_expediente   TEXT,
        peligrosidad     TEXT DEFAULT 'Media',
        observaciones    TEXT,
        activa           INTEGER DEFAULT 1,
        notas_admin      TEXT,
        created_at       TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (dni) REFERENCES ciudadanos(dni)
    );

    CREATE TABLE IF NOT EXISTS admin_users (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        username     TEXT UNIQUE NOT NULL,
        password     TEXT NOT NULL,
        rol          TEXT DEFAULT 'admin',
        created_at   TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario    TEXT,
        accion     TEXT,
        tabla      TEXT,
        registro_id TEXT,
        detalle    TEXT,
        fecha      TEXT DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_mat_dni    ON matriculas(dni);
    CREATE INDEX IF NOT EXISTS idx_mat_estado ON matriculas(estado);
    CREATE INDEX IF NOT EXISTS idx_cit_prov   ON ciudadanos(provincia_residencia);
    CREATE INDEX IF NOT EXISTS idx_alert_dni  ON alertas_policiales(dni);
    """)

    # Admin por defecto
    pw = hashlib.sha256("admin123".encode()).hexdigest()
    db.execute("INSERT OR IGNORE INTO admin_users (username, password, rol) VALUES (?,?,?)",
               ("admin", pw, "superadmin"))
    db.commit()

    # Poblar si vacío
    count = db.execute("SELECT COUNT(*) FROM ciudadanos").fetchone()[0]
    if count == 0:
        print("⚙  Generando base de datos ficticia (puede tardar unos segundos)...")
        generar_datos(db)
        print("✅ Base de datos generada correctamente.")
    db.close()

def generar_datos(db):
    """Genera ciudadanos con DNI del 00000001 al 99999999Z, matrículas 0001 BBB - 9999 NZZ"""
    # Seleccionamos ~600 DNIs distribuidos en todo el rango
    total = 600
    random.seed(42)
    numeros_dni = random.sample(range(1, 100_000_000), total)
    numeros_dni.sort()

    ciudadanos = []
    for num in numeros_dni:
        sexo = random.choice(["Hombre","Mujer"])
        nom = random.choice(NOMBRES_H if sexo=="Hombre" else NOMBRES_M)
        ap1, ap2 = random.choice(APELLIDOS), random.choice(APELLIDOS)
        prov = random.choice(PROVINCIAS)
        fn = rnd_date(1945, 2005)
        edad = (date(2025,6,1) - fn).days // 365
        alerta = "Sin alertas"
        p = random.random()
        if p < 0.08:   alerta = "Busca y Captura"
        elif p < 0.16: alerta = "Requisitoria Judicial"
        elif p < 0.22: alerta = "Vigilancia Especial"
        elif p < 0.32: alerta = "Multas Pendientes"
        calle = random.choice(CALLES)
        ciudadanos.append((
            gen_dni(num), nom, ap1, ap2, sexo, str(fn), prov,
            f"{prov} Capital",
            f"{calle} {ri(1,150)}", str(ri(1,150)),
            f"{ri(1,8)}º {random.choice(['A','B','C','D','Izq','Der'])}",
            f"{ri(1000,52999):05d}",
            f"+34 {ri(600,799)} {ri(100,999)} {ri(100,999)}",
            f"+34 {ri(600,799)} {ri(100,999)} {ri(100,999)}" if random.random()>0.5 else None,
            f"{nom.lower()}.{ap1.lower()}{ri(10,99)}@{random.choice(DOMINIOS)}",
            random.choice(NACIONALIDADES),
            random.choice(ESTADO_CIVIL),
            ri(0,4), random.choice(PROFESIONES),
            random.choice(SITUACION_LAB),
            random.choice(ESTUDIOS),
            ri(12000,85000),
            random.choice(BANCOS),
            f"ES{ri(10,99)} {ri(1000,9999)} {ri(1000,9999)} {ri(100000,999999):06d}",
            "Sí" if random.random()>0.12 else "No",
            random.choice(["B","B+E","C","C+E","A","AM"]) if random.random()>0.2 else "—",
            ri(0,15), "Sí" if alerta!="Sin alertas" and random.random()>0.4 else "No",
            f"AAB{ri(100000,999999)}" if random.random()>0.35 else None,
            str(rnd_date(2000,2022)), str(rnd_date(2023,2031)),
            alerta, None
        ))

    db.executemany("""INSERT OR IGNORE INTO ciudadanos
        (dni,nombre,apellido1,apellido2,sexo,fecha_nac,provincia_residencia,municipio,
         direccion,numero_via,piso,codigo_postal,telefono,telefono2,email,nacionalidad,
         estado_civil,num_hijos,profesion,situacion_laboral,nivel_estudios,ingresos_anuales,
         banco_ref,num_cuenta,licencia_conducir,tipo_licencia,puntos_carnet,antecedentes_penales,
         num_pasaporte,fecha_exp_dni,fecha_cad_dni,alerta_policial,notas_admin)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ciudadanos)
    db.commit()

    # Obtener DNIs insertados
    dnis = [r[0] for r in db.execute("SELECT dni FROM ciudadanos").fetchall()]

    # Generar matrículas: rango completo 0001 BBB → 9999 NZZ
    # Para educación: generamos 800 matrículas únicas con números y letras del rango real
    LETS = list(LETS_MAT)  # 20 letras
    # Rango real: 0000 AAA → 9999 ZZZ (solo letras válidas)
    # Generamos distribuidas
    mats_usadas = set()
    matriculas = []
    seguros = ["Mapfre","Axa","Allianz","Generali","Zurich","Mutua Madrileña","Santalucía","Liberty"]

    for i in range(800):
        tries = 0
        while tries < 100:
            num = ri(1, 9999)
            l1 = random.choice(LETS)
            l2 = random.choice(LETS)
            l3 = random.choice(LETS)
            mat = gen_matricula(num, l1, l2, l3)
            if mat not in mats_usadas:
                mats_usadas.add(mat)
                break
            tries += 1

        tipo = random.choice(["Turismo","Turismo","Turismo","Turismo","Furgoneta",
                               "Motocicleta","Camión","Autobús","Remolque"])
        marca = get_marca_by_tipo(tipo)
        modelo = get_modelo(marca)
        año = ri(1997, 2026)
        comb = random.choice(COMBUSTIBLES)
        cv = gen_cv(tipo)
        co2 = 0 if comb == "Eléctrico" else max(0, round(cv * 1.2 + ri(-20, 40)))
        fmat = rnd_date(max(año, 1997), min(año + 2, 2026))
        fitv = fmat.replace(year=fmat.year + ri(2, 4))
        seg_hasta = rnd_date(2024, 2027)
        dni_prop = random.choice(dnis)
        poliza = f"POL-{ri(1000000,9999999)}"
        matriculas.append((
            mat, dni_prop, tipo, marca, modelo, año, str(fmat),
            random.choice(ESTADOS_MAT), comb, cv, co2, gen_bastidor(),
            str(fitv), random.choice(COLORES), random.choice(USOS),
            ri(0, 350000),
            ri(3,5) if tipo=="Turismo" else None,
            ri(30,60) if tipo=="Autobús" else ri(2,9) if tipo!="Remolque" else 0,
            ri(800,20000), ri(1200,44000),
            random.choice(seguros), poliza, str(seg_hasta),
            ri(0,8), ri(0,5)*ri(50,600), None, None
        ))

    db.executemany("""INSERT OR IGNORE INTO matriculas
        (matricula,dni,tipo_vehiculo,marca,modelo,año_fab,fecha_mat,estado,combustible,
         cv,co2_grkg,bastidor,fecha_itv,color,uso,km,num_puertas,num_plazas,
         tara_kg,masa_max_kg,seguro_compañia,seguro_poliza,seguro_hasta,
         num_infracciones,importe_multas,titular_anterior,notas_admin)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        matriculas)
    db.commit()

    # Alertas
    alertas_cits = db.execute(
        "SELECT dni, alerta_policial FROM ciudadanos WHERE alerta_policial != 'Sin alertas'"
    ).fetchall()
    alertas = []
    for c in alertas_cits:
        tipo = c["alerta_policial"]
        motivos_list = MOTIVOS.get(tipo, ["Motivo desconocido"])
        femit = rnd_date(2018, 2025)
        fcad = femit.replace(year=femit.year + ri(1, 5))
        alertas.append((
            c["dni"], tipo, random.choice(motivos_list),
            random.choice(EMISORES), str(femit), str(fcad),
            random.choice(JUZGADOS) if tipo != "Multas Pendientes" else "—",
            f"{ri(100,999)}/{ri(2018,2025)}",
            "Alta" if tipo=="Busca y Captura" else "Media" if tipo in ["Requisitoria Judicial","Vigilancia Especial"] else "Baja",
            random.choice(["Puede estar armado","Menor de edad posible","Antecedentes en DD.PP.",
                "Investigación en curso","Paradero desconocido","Orden de alejamiento en vigor",
                "Colabora con la justicia","Última ubicación: "+random.choice(PROVINCIAS)]),
            1 if fcad > date(2025,1,1) else 0, None
        ))
    db.executemany("""INSERT INTO alertas_policiales
        (dni,tipo_alerta,motivo,emisor,fecha_emision,fecha_caducidad,juzgado,
         num_expediente,peligrosidad,observaciones,activa,notas_admin)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", alertas)
    db.commit()

# ──────────────────────────────────────────────
#  AUTENTICACIÓN ADMIN
# ──────────────────────────────────────────────
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def audit(accion, tabla, registro_id, detalle=""):
    try:
        execute("INSERT INTO audit_log (usuario,accion,tabla,registro_id,detalle) VALUES (?,?,?,?,?)",
                (session.get("admin","?"), accion, tabla, str(registro_id), detalle))
    except: pass

# ──────────────────────────────────────────────
#  RUTAS PÚBLICAS
# ──────────────────────────────────────────────
@app.route("/")
def index():
    stats = {
        "matriculas": query("SELECT COUNT(*) as n FROM matriculas", one=True)["n"],
        "ciudadanos": query("SELECT COUNT(*) as n FROM ciudadanos", one=True)["n"],
        "alertas":    query("SELECT COUNT(*) as n FROM alertas_policiales WHERE activa=1", one=True)["n"],
        "bc":         query("SELECT COUNT(*) as n FROM alertas_policiales WHERE tipo_alerta='Busca y Captura' AND activa=1", one=True)["n"],
        "activas":    query("SELECT COUNT(*) as n FROM matriculas WHERE estado='Activa'", one=True)["n"],
        "electricos": query("SELECT COUNT(*) as n FROM matriculas WHERE combustible='Eléctrico'", one=True)["n"],
        "antecedentes": query("SELECT COUNT(*) as n FROM ciudadanos WHERE antecedentes_penales='Sí'", one=True)["n"],
    }
    return render_template("index.html", stats=stats, admin=session.get("admin"))

# ── API MATRÍCULAS ──
@app.route("/api/matriculas")
def api_matriculas():
    q = request.args.get("q","").strip()
    prov = request.args.get("prov","")
    estado = request.args.get("estado","")
    tipo = request.args.get("tipo","")
    alerta = request.args.get("alerta","")
    combustible = request.args.get("combustible","")
    page = max(0, int(request.args.get("page",0)))
    per = 20
    sql = """SELECT m.*, c.nombre||' '||c.apellido1||' '||c.apellido2 as propietario_full,
                    c.telefono, c.email, c.alerta_policial
             FROM matriculas m
             LEFT JOIN ciudadanos c ON m.dni = c.dni
             WHERE 1=1"""
    params = []
    if q:
        sql += " AND (m.matricula LIKE ? OR m.dni LIKE ? OR m.bastidor LIKE ? OR m.marca LIKE ? OR m.modelo LIKE ? OR c.nombre LIKE ?)"
        params += [f"%{q}%"]*6
    if prov: sql += " AND c.provincia_residencia=?"; params.append(prov)
    if estado: sql += " AND m.estado=?"; params.append(estado)
    if tipo: sql += " AND m.tipo_vehiculo=?"; params.append(tipo)
    if combustible: sql += " AND m.combustible=?"; params.append(combustible)
    if alerta == "alert": sql += " AND c.alerta_policial != 'Sin alertas'"
    elif alerta == "clean": sql += " AND c.alerta_policial = 'Sin alertas'"
    total = get_db().execute(f"SELECT COUNT(*) FROM ({sql})", params).fetchone()[0]
    sql += f" ORDER BY m.id LIMIT {per} OFFSET {page*per}"
    rows = [dict(r) for r in query(sql, params)]
    return jsonify({"rows": rows, "total": total, "page": page, "per": per})

@app.route("/api/matricula/<int:mid>")
def api_matricula_detail(mid):
    r = query("""SELECT m.*, c.nombre, c.apellido1, c.apellido2, c.sexo, c.fecha_nac,
                        c.provincia_residencia, c.direccion, c.telefono, c.telefono2,
                        c.email, c.profesion, c.puntos_carnet, c.tipo_licencia,
                        c.alerta_policial, c.antecedentes_penales, c.situacion_laboral
                 FROM matriculas m LEFT JOIN ciudadanos c ON m.dni=c.dni
                 WHERE m.id=?""", (mid,), one=True)
    if not r: return jsonify({"error":"No encontrado"}), 404
    return jsonify(dict(r))

# ── API CIUDADANOS ──
@app.route("/api/ciudadanos")
def api_ciudadanos():
    q = request.args.get("q","").strip()
    prov = request.args.get("prov","")
    alerta = request.args.get("alerta","")
    sexo = request.args.get("sexo","")
    page = max(0, int(request.args.get("page",0)))
    per = 20
    sql = "SELECT * FROM ciudadanos WHERE 1=1"
    params = []
    if q:
        sql += " AND (dni LIKE ? OR nombre LIKE ? OR apellido1 LIKE ? OR apellido2 LIKE ? OR direccion LIKE ? OR telefono LIKE ? OR email LIKE ?)"
        params += [f"%{q}%"]*7
    if prov: sql += " AND provincia_residencia=?"; params.append(prov)
    if alerta: sql += " AND alerta_policial=?"; params.append(alerta)
    if sexo: sql += " AND sexo=?"; params.append(sexo)
    total = get_db().execute(f"SELECT COUNT(*) FROM ({sql})", params).fetchone()[0]
    sql += f" ORDER BY id LIMIT {per} OFFSET {page*per}"
    rows = [dict(r) for r in query(sql, params)]
    # Añadir num_vehiculos
    for row in rows:
        row["num_vehiculos"] = query("SELECT COUNT(*) as n FROM matriculas WHERE dni=?", (row["dni"],), one=True)["n"]
    return jsonify({"rows": rows, "total": total, "page": page, "per": per})

@app.route("/api/ciudadano/<dni>")
def api_ciudadano_detail(dni):
    c = query("SELECT * FROM ciudadanos WHERE dni=?", (dni,), one=True)
    if not c: return jsonify({"error":"No encontrado"}), 404
    mats = [dict(m) for m in query("SELECT * FROM matriculas WHERE dni=?", (dni,))]
    alertas = [dict(a) for a in query("SELECT * FROM alertas_policiales WHERE dni=?", (dni,))]
    return jsonify({"ciudadano": dict(c), "matriculas": mats, "alertas": alertas})

# ── API ALERTAS ──
@app.route("/api/alertas")
def api_alertas():
    q = request.args.get("q","").strip()
    tipo = request.args.get("tipo","")
    page = max(0, int(request.args.get("page",0)))
    per = 20
    sql = """SELECT a.*, c.nombre||' '||c.apellido1 as nombre_completo,
                    c.provincia_residencia, c.telefono, c.fecha_nac
             FROM alertas_policiales a
             LEFT JOIN ciudadanos c ON a.dni=c.dni
             WHERE 1=1"""
    params = []
    if q:
        sql += " AND (a.dni LIKE ? OR c.nombre LIKE ? OR c.apellido1 LIKE ? OR a.motivo LIKE ?)"
        params += [f"%{q}%"]*4
    if tipo: sql += " AND a.tipo_alerta=?"; params.append(tipo)
    total = get_db().execute(f"SELECT COUNT(*) FROM ({sql})", params).fetchone()[0]
    sql += f" ORDER BY a.id LIMIT {per} OFFSET {page*per}"
    rows = [dict(r) for r in query(sql, params)]
    return jsonify({"rows": rows, "total": total, "page": page, "per": per})

# ── API ESTADÍSTICAS ──
@app.route("/api/stats/graficas")
def api_stats():
    def group(sql): return {r[0]: r[1] for r in get_db().execute(sql).fetchall()}
    return jsonify({
        "por_tipo":     group("SELECT tipo_vehiculo, COUNT(*) FROM matriculas GROUP BY tipo_vehiculo ORDER BY 2 DESC"),
        "por_comb":     group("SELECT combustible, COUNT(*) FROM matriculas GROUP BY combustible ORDER BY 2 DESC"),
        "por_estado":   group("SELECT estado, COUNT(*) FROM matriculas GROUP BY estado ORDER BY 2 DESC"),
        "por_alerta":   group("SELECT alerta_policial, COUNT(*) FROM ciudadanos GROUP BY alerta_policial ORDER BY 2 DESC"),
        "por_prov_cit": group("SELECT provincia_residencia, COUNT(*) FROM ciudadanos GROUP BY provincia_residencia ORDER BY 2 DESC LIMIT 10"),
        "por_edad":     group("""SELECT CASE
            WHEN (strftime('%Y','now')-strftime('%Y',fecha_nac)) BETWEEN 18 AND 30 THEN '18-30'
            WHEN (strftime('%Y','now')-strftime('%Y',fecha_nac)) BETWEEN 31 AND 40 THEN '31-40'
            WHEN (strftime('%Y','now')-strftime('%Y',fecha_nac)) BETWEEN 41 AND 50 THEN '41-50'
            WHEN (strftime('%Y','now')-strftime('%Y',fecha_nac)) BETWEEN 51 AND 60 THEN '51-60'
            ELSE '61+' END as rango, COUNT(*) FROM ciudadanos GROUP BY rango"""),
        "por_marca":    group("SELECT marca, COUNT(*) FROM matriculas GROUP BY marca ORDER BY 2 DESC LIMIT 10"),
        "por_año":      group("SELECT año_fab, COUNT(*) FROM matriculas GROUP BY año_fab ORDER BY año_fab"),
    })

# ──────────────────────────────────────────────
#  PANEL ADMIN - LOGIN
# ──────────────────────────────────────────────
@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        user = request.form.get("username","")
        pw   = hashlib.sha256(request.form.get("password","").encode()).hexdigest()
        row  = query("SELECT * FROM admin_users WHERE username=? AND password=?", (user, pw), one=True)
        if row:
            session["admin"] = user
            session["rol"]   = row["rol"]
            audit("LOGIN", "admin_users", user, "Inicio de sesión")
            return redirect(url_for("admin"))
        error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ──────────────────────────────────────────────
#  PANEL ADMIN
# ──────────────────────────────────────────────
@app.route("/admin")
@admin_required
def admin():
    stats = {
        "matriculas": query("SELECT COUNT(*) as n FROM matriculas", one=True)["n"],
        "ciudadanos": query("SELECT COUNT(*) as n FROM ciudadanos", one=True)["n"],
        "alertas":    query("SELECT COUNT(*) as n FROM alertas_policiales WHERE activa=1", one=True)["n"],
        "bc":         query("SELECT COUNT(*) as n FROM alertas_policiales WHERE tipo_alerta='Busca y Captura' AND activa=1", one=True)["n"],
    }
    logs = [dict(r) for r in query("SELECT * FROM audit_log ORDER BY id DESC LIMIT 20")]
    return render_template("admin.html", stats=stats, logs=logs,
                           admin=session.get("admin"), rol=session.get("rol"),
                           provincias=PROVINCIAS, tipos_alerta=TIPOS_ALERTA,
                           combustibles=COMBUSTIBLES, tipos_mat=["Turismo","Furgoneta","Motocicleta","Camión","Autobús","Remolque"])

# ── ADMIN: CRUD CIUDADANOS ──
@app.route("/admin/ciudadano/nuevo", methods=["GET","POST"])
@admin_required
def admin_ciudadano_nuevo():
    if request.method == "POST":
        d = request.form
        num = int(d.get("dni_num","0"))
        dni = gen_dni(num)
        lid = execute("""INSERT INTO ciudadanos
            (dni,nombre,apellido1,apellido2,sexo,fecha_nac,provincia_residencia,municipio,
             direccion,numero_via,piso,codigo_postal,telefono,telefono2,email,nacionalidad,
             estado_civil,num_hijos,profesion,situacion_laboral,nivel_estudios,ingresos_anuales,
             banco_ref,licencia_conducir,tipo_licencia,puntos_carnet,antecedentes_penales,
             num_pasaporte,fecha_exp_dni,fecha_cad_dni,alerta_policial,notas_admin)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (dni, d["nombre"],d["apellido1"],d.get("apellido2"),d["sexo"],d["fecha_nac"],
             d["provincia_residencia"],d.get("municipio"),d.get("direccion"),d.get("numero_via"),
             d.get("piso"),d.get("codigo_postal"),d.get("telefono"),d.get("telefono2"),
             d.get("email"),d.get("nacionalidad","Española"),d.get("estado_civil"),
             int(d.get("num_hijos",0)),d.get("profesion"),d.get("situacion_laboral"),
             d.get("nivel_estudios"),int(d.get("ingresos_anuales",0) or 0),
             d.get("banco_ref"),d.get("licencia_conducir","No"),d.get("tipo_licencia"),
             int(d.get("puntos_carnet",15)),d.get("antecedentes_penales","No"),
             d.get("num_pasaporte"),d.get("fecha_exp_dni"),d.get("fecha_cad_dni"),
             d.get("alerta_policial","Sin alertas"),d.get("notas_admin")))
        audit("CREAR", "ciudadanos", dni, f"Nuevo ciudadano: {d['nombre']} {d['apellido1']}")
        return jsonify({"ok": True, "dni": dni, "id": lid})
    return render_template("admin.html", admin=session.get("admin"))

@app.route("/admin/ciudadano/<dni>/editar", methods=["POST"])
@admin_required
def admin_ciudadano_editar(dni):
    d = request.json or request.form
    campos = ["nombre","apellido1","apellido2","sexo","fecha_nac","provincia_residencia",
              "municipio","direccion","numero_via","piso","codigo_postal","telefono",
              "telefono2","email","nacionalidad","estado_civil","num_hijos","profesion",
              "situacion_laboral","nivel_estudios","ingresos_anuales","banco_ref",
              "licencia_conducir","tipo_licencia","puntos_carnet","antecedentes_penales",
              "num_pasaporte","fecha_exp_dni","fecha_cad_dni","alerta_policial","notas_admin"]
    sets = ", ".join(f"{c}=?" for c in campos if c in d)
    vals = [d[c] for c in campos if c in d]
    if sets:
        execute(f"UPDATE ciudadanos SET {sets}, updated_at=datetime('now') WHERE dni=?", vals + [dni])
        audit("EDITAR", "ciudadanos", dni, f"Campos: {sets}")
    return jsonify({"ok": True})

@app.route("/admin/ciudadano/<dni>/eliminar", methods=["POST"])
@admin_required
def admin_ciudadano_eliminar(dni):
    execute("DELETE FROM alertas_policiales WHERE dni=?", (dni,))
    execute("DELETE FROM matriculas WHERE dni=?", (dni,))
    execute("DELETE FROM ciudadanos WHERE dni=?", (dni,))
    audit("ELIMINAR", "ciudadanos", dni, "Ciudadano y registros asociados eliminados")
    return jsonify({"ok": True})

# ── ADMIN: CRUD MATRÍCULAS ──
@app.route("/admin/matricula/nueva", methods=["POST"])
@admin_required
def admin_matricula_nueva():
    d = request.json or request.form
    num = int(d.get("mat_num",1))
    l1,l2,l3 = d.get("l1","B"),d.get("l2","B"),d.get("l3","B")
    mat = gen_matricula(num, l1, l2, l3)
    lid = execute("""INSERT INTO matriculas
        (matricula,dni,tipo_vehiculo,marca,modelo,año_fab,fecha_mat,estado,combustible,
         cv,co2_grkg,bastidor,fecha_itv,color,uso,km,num_puertas,num_plazas,tara_kg,
         masa_max_kg,seguro_compañia,seguro_poliza,seguro_hasta,num_infracciones,importe_multas,notas_admin)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (mat, d["dni"],d.get("tipo_vehiculo","Turismo"),d.get("marca","SEAT"),
         d.get("modelo","León"),int(d.get("año_fab",2020)),d.get("fecha_mat"),
         d.get("estado","Activa"),d.get("combustible","Gasolina"),
         int(d.get("cv",100) or 0),int(d.get("co2_grkg",0) or 0),
         d.get("bastidor") or gen_bastidor(),
         d.get("fecha_itv"),d.get("color","Blanco"),d.get("uso","Particular"),
         int(d.get("km",0) or 0),d.get("num_puertas"),d.get("num_plazas"),
         d.get("tara_kg"),d.get("masa_max_kg"),d.get("seguro_compañia"),
         d.get("seguro_poliza"),d.get("seguro_hasta"),
         int(d.get("num_infracciones",0)),int(d.get("importe_multas",0)),d.get("notas_admin")))
    audit("CREAR", "matriculas", mat, f"Nueva matrícula {mat} para DNI {d['dni']}")
    return jsonify({"ok": True, "matricula": mat, "id": lid})

@app.route("/admin/matricula/<int:mid>/editar", methods=["POST"])
@admin_required
def admin_matricula_editar(mid):
    d = request.json or request.form
    campos = ["tipo_vehiculo","marca","modelo","año_fab","fecha_mat","estado","combustible",
              "cv","co2_grkg","bastidor","fecha_itv","color","uso","km","num_puertas",
              "num_plazas","tara_kg","masa_max_kg","seguro_compañia","seguro_poliza",
              "seguro_hasta","num_infracciones","importe_multas","notas_admin","dni"]
    sets = ", ".join(f"{c}=?" for c in campos if c in d)
    vals = [d[c] for c in campos if c in d]
    if sets:
        execute(f"UPDATE matriculas SET {sets}, updated_at=datetime('now') WHERE id=?", vals + [mid])
        audit("EDITAR", "matriculas", mid, f"Campos: {sets}")
    return jsonify({"ok": True})

@app.route("/admin/matricula/<int:mid>/eliminar", methods=["POST"])
@admin_required
def admin_matricula_eliminar(mid):
    execute("DELETE FROM matriculas WHERE id=?", (mid,))
    audit("ELIMINAR", "matriculas", mid, "Matrícula eliminada")
    return jsonify({"ok": True})

# ── ADMIN: CRUD ALERTAS ──
@app.route("/admin/alerta/nueva", methods=["POST"])
@admin_required
def admin_alerta_nueva():
    d = request.json or request.form
    lid = execute("""INSERT INTO alertas_policiales
        (dni,tipo_alerta,motivo,emisor,fecha_emision,fecha_caducidad,juzgado,
         num_expediente,peligrosidad,observaciones,activa,notas_admin)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d["dni"],d["tipo_alerta"],d.get("motivo"),d.get("emisor"),
         d.get("fecha_emision"),d.get("fecha_caducidad"),d.get("juzgado"),
         d.get("num_expediente"),d.get("peligrosidad","Media"),
         d.get("observaciones"),1,d.get("notas_admin")))
    execute("UPDATE ciudadanos SET alerta_policial=? WHERE dni=?", (d["tipo_alerta"], d["dni"]))
    audit("CREAR", "alertas_policiales", lid, f"Alerta {d['tipo_alerta']} para DNI {d['dni']}")
    return jsonify({"ok": True, "id": lid})

@app.route("/admin/alerta/<int:aid>/editar", methods=["POST"])
@admin_required
def admin_alerta_editar(aid):
    d = request.json or request.form
    campos = ["tipo_alerta","motivo","emisor","fecha_emision","fecha_caducidad",
              "juzgado","num_expediente","peligrosidad","observaciones","activa","notas_admin"]
    sets = ", ".join(f"{c}=?" for c in campos if c in d)
    vals = [d[c] for c in campos if c in d]
    if sets:
        execute(f"UPDATE alertas_policiales SET {sets} WHERE id=?", vals + [aid])
        audit("EDITAR", "alertas_policiales", aid, f"Campos: {sets}")
    return jsonify({"ok": True})

@app.route("/admin/alerta/<int:aid>/eliminar", methods=["POST"])
@admin_required
def admin_alerta_eliminar(aid):
    row = query("SELECT dni FROM alertas_policiales WHERE id=?", (aid,), one=True)
    execute("DELETE FROM alertas_policiales WHERE id=?", (aid,))
    if row:
        remaining = query("SELECT COUNT(*) as n FROM alertas_policiales WHERE dni=?", (row["dni"],), one=True)["n"]
        if remaining == 0:
            execute("UPDATE ciudadanos SET alerta_policial='Sin alertas' WHERE dni=?", (row["dni"],))
    audit("ELIMINAR", "alertas_policiales", aid)
    return jsonify({"ok": True})

# ── ADMIN: Usuarios ──
@app.route("/admin/usuario/nuevo", methods=["POST"])
@admin_required
def admin_usuario_nuevo():
    if session.get("rol") != "superadmin":
        return jsonify({"error":"Sin permisos"}), 403
    d = request.json or request.form
    pw = hashlib.sha256(d["password"].encode()).hexdigest()
    execute("INSERT OR IGNORE INTO admin_users (username,password,rol) VALUES (?,?,?)",
            (d["username"], pw, d.get("rol","admin")))
    audit("CREAR", "admin_users", d["username"], "Nuevo usuario admin")
    return jsonify({"ok": True})

# ── ADMIN: DNI lookup ──
@app.route("/api/dni/<dni>")
def api_dni(dni):
    r = query("SELECT * FROM ciudadanos WHERE dni=?", (dni,), one=True)
    if not r: return jsonify({"existe": False})
    return jsonify({"existe": True, **dict(r)})

# ── ADMIN: Generar matrícula ──
@app.route("/api/calcular_matricula")
def api_calcular_matricula():
    num = int(request.args.get("num",1))
    l1 = request.args.get("l1","B")
    l2 = request.args.get("l2","B")
    l3 = request.args.get("l3","B")
    mat = gen_matricula(num, l1, l2, l3)
    exists = query("SELECT id FROM matriculas WHERE matricula=?", (mat,), one=True)
    return jsonify({"matricula": mat, "existe": bool(exists)})

@app.route("/api/calcular_dni")
def api_calcular_dni():
    num = int(request.args.get("num",0))
    dni = gen_dni(num)
    exists = query("SELECT id FROM ciudadanos WHERE dni=?", (dni,), one=True)
    return jsonify({"dni": dni, "letra": LETS_DNI[num%23], "existe": bool(exists)})

# ── PROVINCIAS ──
@app.route("/api/provincias")
def api_provincias():
    return jsonify(sorted(PROVINCIAS))

# ──────────────────────────────────────────────
#  RESOLUCIÓN UNIVERSAL: cualquier DNI 00000001A→99999999Z
#  y cualquier matrícula 0001 BBB→9999 NZZ
#  Si NO está en la BD, genera datos ficticios al vuelo
# ──────────────────────────────────────────────

def _ficha_dni_universal(num: int) -> dict:
    """Devuelve ficha completa para cualquier número de DNI 1-99999999.
    Si existe en BD, devuelve los datos reales. Si no, los genera al vuelo."""
    dni = gen_dni(num)
    row = query("SELECT * FROM ciudadanos WHERE dni=?", (dni,), one=True)
    if row:
        r = dict(row)
        r["en_bd"] = True
        r["matriculas"] = [dict(m) for m in query("SELECT * FROM matriculas WHERE dni=?", (dni,))]
        r["alertas"]    = [dict(a) for a in query("SELECT * FROM alertas_policiales WHERE dni=?", (dni,))]
        return r
    # Generar al vuelo con semilla fija para que sea reproducible
    rng = random.Random(num)
    sexo  = rng.choice(["Hombre","Mujer"])
    nom   = rng.choice(NOMBRES_H if sexo=="Hombre" else NOMBRES_M)
    ap1, ap2 = rng.choice(APELLIDOS), rng.choice(APELLIDOS)
    prov  = rng.choice(PROVINCIAS)
    fn    = rnd_date(1945, 2005); fn = date(1945 + (num % 60), (num % 12)+1, (num % 28)+1)
    calle = rng.choice(CALLES)
    alerta_p = "Sin alertas"
    p = (num % 100) / 100
    if   p < 0.07: alerta_p = "Busca y Captura"
    elif p < 0.14: alerta_p = "Requisitoria Judicial"
    elif p < 0.20: alerta_p = "Vigilancia Especial"
    elif p < 0.30: alerta_p = "Multas Pendientes"
    return {
        "en_bd": False,
        "dni": dni, "nombre": nom, "apellido1": ap1, "apellido2": ap2,
        "sexo": sexo, "fecha_nac": str(fn),
        "edad": (date(2025,6,1)-fn).days//365,
        "provincia_residencia": prov, "municipio": f"{prov} Capital",
        "direccion": f"{calle} {rng.randint(1,150)}",
        "numero_via": str(rng.randint(1,150)),
        "piso": f"{rng.randint(1,8)}º {rng.choice(['A','B','C','D','Izq','Der'])}",
        "codigo_postal": f"{rng.randint(1000,52999):05d}",
        "telefono": f"+34 {rng.randint(600,799)} {rng.randint(100,999)} {rng.randint(100,999)}",
        "email": f"{nom.lower()}.{ap1.lower()}{rng.randint(10,99)}@{rng.choice(DOMINIOS)}",
        "nacionalidad": rng.choice(NACIONALIDADES),
        "estado_civil": rng.choice(ESTADO_CIVIL),
        "num_hijos": rng.randint(0,4),
        "profesion": rng.choice(PROFESIONES),
        "situacion_laboral": rng.choice(SITUACION_LAB),
        "nivel_estudios": rng.choice(ESTUDIOS),
        "ingresos_anuales": rng.randint(12000,85000),
        "banco_ref": rng.choice(BANCOS),
        "num_cuenta": f"ES{rng.randint(10,99)} {rng.randint(1000,9999)} {rng.randint(1000,9999)} {rng.randint(100000,999999):06d}",
        "licencia_conducir": rng.choice(["Sí","Sí","Sí","No"]),
        "tipo_licencia": rng.choice(["B","B","B","B+E","A","C","AM"]),
        "puntos_carnet": rng.randint(0,15),
        "antecedentes_penales": "Sí" if alerta_p != "Sin alertas" and rng.random()>0.5 else "No",
        "num_pasaporte": f"AAB{rng.randint(100000,999999)}" if rng.random()>0.4 else "—",
        "fecha_exp_dni": str(date(2000+(num%20), (num%12)+1, (num%28)+1)),
        "fecha_cad_dni": str(date(2023+(num%8),  (num%12)+1, (num%28)+1)),
        "alerta_policial": alerta_p,
        "notas_admin": None,
        "matriculas": [], "alertas": []
    }

def _ficha_matricula_universal(mat_str: str) -> dict:
    """Devuelve ficha para cualquier matrícula NNNN LLL.
    Si existe en BD la devuelve; si no, la genera al vuelo."""
    row = query("""SELECT m.*, c.nombre, c.apellido1, c.apellido2, c.sexo, c.fecha_nac,
                          c.provincia_residencia, c.direccion, c.telefono, c.email,
                          c.alerta_policial, c.profesion, c.puntos_carnet
                   FROM matriculas m LEFT JOIN ciudadanos c ON m.dni=c.dni
                   WHERE m.matricula=?""", (mat_str,), one=True)
    if row:
        r = dict(row); r["en_bd"] = True; return r
    # Generar al vuelo con semilla reproducible
    seed = sum(ord(c)*(i+1) for i,c in enumerate(mat_str.replace(" ","")))
    rng  = random.Random(seed)
    tipo = rng.choice(["Turismo","Turismo","Turismo","Furgoneta","Motocicleta","Camión"])
    marca = get_marca_by_tipo(tipo)
    modelo = get_modelo(marca)
    año  = rng.randint(1997, 2026)
    comb = rng.choice(COMBUSTIBLES)
    cv   = gen_cv(tipo)
    co2  = 0 if comb=="Eléctrico" else max(0, round(cv*1.2 + rng.randint(-20,40)))
    fmat = date(max(año,1997), rng.randint(1,12), rng.randint(1,28))
    fitv = date(min(fmat.year+rng.randint(2,4), 2030), fmat.month, fmat.day)
    # propietario ficticio
    sexo = rng.choice(["Hombre","Mujer"])
    nom  = rng.choice(NOMBRES_H if sexo=="Hombre" else NOMBRES_M)
    ap1  = rng.choice(APELLIDOS)
    prov = rng.choice(PROVINCIAS)
    dni_f= gen_dni(rng.randint(1,99999999))
    seguros=["Mapfre","Axa","Allianz","Generali","Zurich","Mutua Madrileña"]
    return {
        "en_bd": False,
        "matricula": mat_str, "dni": dni_f,
        "nombre": nom, "apellido1": ap1, "apellido2": rng.choice(APELLIDOS),
        "provincia_residencia": prov,
        "telefono": f"+34 {rng.randint(600,799)} {rng.randint(100,999)} {rng.randint(100,999)}",
        "email": f"{nom.lower()}{rng.randint(1,99)}@{rng.choice(DOMINIOS)}",
        "tipo_vehiculo": tipo, "marca": marca, "modelo": modelo,
        "año_fab": año, "fecha_mat": str(fmat), "estado": rng.choice(ESTADOS_MAT),
        "combustible": comb, "cv": cv, "co2_grkg": co2,
        "bastidor": gen_bastidor(),
        "fecha_itv": str(fitv), "color": rng.choice(COLORES),
        "uso": rng.choice(USOS), "km": rng.randint(0,350000),
        "num_puertas": rng.randint(3,5) if tipo=="Turismo" else None,
        "num_plazas": rng.randint(2,5), "tara_kg": rng.randint(800,3500),
        "masa_max_kg": rng.randint(1200,4500),
        "seguro_compañia": rng.choice(seguros),
        "seguro_poliza": f"POL-{rng.randint(1000000,9999999)}",
        "seguro_hasta": str(date(rng.randint(2024,2027), rng.randint(1,12), rng.randint(1,28))),
        "num_infracciones": rng.randint(0,5), "importe_multas": rng.randint(0,4)*rng.randint(50,400),
        "alerta_policial": "Sin alertas",
        "profesion": rng.choice(PROFESIONES), "puntos_carnet": rng.randint(0,15),
        "notas_admin": None,
    }

# ── API UNIVERSAL: resolver DNI ──
@app.route("/api/resolver/dni/<int:num>")
def api_resolver_dni(num):
    if num < 1 or num > 99_999_999:
        return jsonify({"error": "Número fuera de rango (1-99999999)"}), 400
    return jsonify(_ficha_dni_universal(num))

# ── API UNIVERSAL: resolver matrícula por texto ──
@app.route("/api/resolver/matricula/<path:mat>")
def api_resolver_matricula(mat):
    mat = mat.upper().strip()
    # normalizar: "1234BBB" → "1234 BBB"
    if " " not in mat and len(mat) == 7:
        mat = mat[:4] + " " + mat[4:]
    parts = mat.split()
    if len(parts) != 2 or not parts[0].isdigit() or len(parts[1]) != 3:
        return jsonify({"error": "Formato incorrecto. Usa: 1234BBB o 1234 BBB"}), 400
    num = int(parts[0])
    lets = parts[1]
    if num < 1 or num > 9999:
        return jsonify({"error": "Número fuera de rango (1-9999)"}), 400
    invalid = set(lets) - set(LETS_MAT)
    if invalid:
        return jsonify({"error": f"Letras inválidas: {invalid}. Válidas: {LETS_MAT}"}), 400
    return jsonify(_ficha_matricula_universal(mat))

# ── API UNIVERSAL: rango de DNIs ──
@app.route("/api/resolver/rango_dni")
def api_rango_dni():
    """Resuelve un rango de DNIs consecutivos. Max 200 por petición."""
    desde = max(1,     int(request.args.get("desde", 1)))
    hasta = min(99_999_999, int(request.args.get("hasta", 100)))
    if hasta - desde > 200: hasta = desde + 200
    return jsonify([_ficha_dni_universal(n) for n in range(desde, hasta+1)])

# ── PÁGINA: buscador universal ──
@app.route("/buscador")
def buscador():
    return render_template("buscador.html", admin=session.get("admin"))

# ──────────────────────────────────────────────
#  MÓDULO POLICIAL — verificación + multas
# ──────────────────────────────────────────────

# ──────────────────────────────────────────────
#  CATÁLOGO COMPLETO DE INFRACCIONES
# ──────────────────────────────────────────────
TIPOS_MULTA = [
    # (codigo, descripcion, articulo, importe_base, puntos_retirar, grave, categoria)
    # VELOCIDAD
    ("VEL-01","Exceso velocidad hasta 20 km/h en vía urbana",           "Art. 76 LSV",    100, 0,False,"VELOCIDAD"),
    ("VEL-02","Exceso velocidad 20-40 km/h en vía urbana",              "Art. 76 LSV",    300, 2,True, "VELOCIDAD"),
    ("VEL-03","Exceso velocidad +40 km/h en vía urbana",                "Art. 76 LSV",    600, 6,True, "VELOCIDAD"),
    ("VEL-04","Exceso velocidad hasta 30 km/h en autopista/autovía",    "Art. 76 LSV",    100, 0,False,"VELOCIDAD"),
    ("VEL-05","Exceso velocidad 30-50 km/h en autopista/autovía",       "Art. 76 LSV",    400, 4,True, "VELOCIDAD"),
    ("VEL-06","Exceso velocidad +50 km/h en autopista/autovía",         "Art. 76 LSV",    600, 6,True, "VELOCIDAD"),
    ("VEL-07","Exceso velocidad en zona escolar / hospital",             "Art. 76 LSV",    600, 6,True, "VELOCIDAD"),
    ("VEL-08","Exceso velocidad en obras / tramo reducido",              "Art. 76 LSV",    300, 4,True, "VELOCIDAD"),
    # ALCOHOL
    ("ALC-01","Tasa alcohol 0.25–0.50 mg/l en aire espirado",           "Art. 79 LSV",    500, 4,True, "ALCOHOL"),
    ("ALC-02","Tasa alcohol 0.50–0.70 mg/l en aire espirado",           "Art. 79 LSV",    800, 4,True, "ALCOHOL"),
    ("ALC-03","Tasa alcohol +0.70 mg/l en aire espirado",               "Art. 379.2 CP", 1000, 6,True, "ALCOHOL"),
    ("ALC-04","Tasa alcohol +1.00 mg/l (muy elevada)",                  "Art. 379.2 CP", 1000, 6,True, "ALCOHOL"),
    ("ALC-05","Negativa a prueba de alcoholemia",                       "Art. 383 CP",   1000, 6,True, "ALCOHOL"),
    ("ALC-06","Alcohol en conductor novel / profesional (0.15 mg/l)",   "Art. 79 LSV",    500, 4,True, "ALCOHOL"),
    # DROGAS
    ("DRG-01","Conducción bajo efectos de cannabis (THC)",              "Art. 379.2 CP", 1000, 6,True, "DROGAS"),
    ("DRG-02","Conducción bajo efectos de cocaína (COC)",               "Art. 379.2 CP", 1000, 6,True, "DROGAS"),
    ("DRG-03","Conducción bajo efectos de anfetaminas/speed (AMF)",     "Art. 379.2 CP", 1000, 6,True, "DROGAS"),
    ("DRG-04","Conducción bajo efectos de MDMA/éxtasis (MDMA)",        "Art. 379.2 CP", 1000, 6,True, "DROGAS"),
    ("DRG-05","Conducción bajo efectos de opiáceos/heroína (OPI)",      "Art. 379.2 CP", 1000, 6,True, "DROGAS"),
    ("DRG-06","Conducción bajo efectos de benzodiacepinas (BZD)",       "Art. 379.2 CP", 1000, 6,True, "DROGAS"),
    ("DRG-07","Conducción bajo efectos de ketamina (KET)",              "Art. 379.2 CP", 1000, 6,True, "DROGAS"),
    ("DRG-08","Negativa a prueba de detección de drogas",               "Art. 383 CP",   1000, 6,True, "DROGAS"),
    ("DRG-09","Policonsumo (alcohol + drogas)",                         "Art. 379.2 CP", 1000, 6,True, "DROGAS"),
    # DISTRACCIONES
    ("DIS-01","Uso de teléfono móvil al volante",                       "Art. 76.j LSV",  200, 3,True, "DISTRACCIONES"),
    ("DIS-02","Uso de auriculares / cascos en la conducción",           "Art. 76.k LSV",  200, 3,True, "DISTRACCIONES"),
    ("DIS-03","Conducción distraída (comer, maquillarse...)",           "Art. 76.m LSV",  200, 3,True, "DISTRACCIONES"),
    ("DIS-04","Fatiga / somnolencia al volante",                        "Art. 76.m LSV",  200, 3,True, "DISTRACCIONES"),
    ("DIS-05","Uso de pantalla / GPS no homologado al volante",         "Art. 76.j LSV",  200, 3,True, "DISTRACCIONES"),
    # CINTURÓN / CASCO / SRI
    ("CIN-01","No uso del cinturón de seguridad (conductor)",           "Art. 76.i LSV",  200, 3,True, "PROTECCIÓN"),
    ("CIN-02","No uso del cinturón de seguridad (pasajero)",            "Art. 76.i LSV",  200, 3,True, "PROTECCIÓN"),
    ("CAS-01","No uso del casco homologado en moto/ciclomotor",         "Art. 76.i LSV",  200, 3,True, "PROTECCIÓN"),
    ("SRI-01","Menor sin sistema de retención infantil homologado",     "Art. 76.i LSV",  200, 3,True, "PROTECCIÓN"),
    # SEMÁFOROS Y SEÑALES
    ("SEM-01","Saltarse semáforo en rojo",                              "Art. 76.b LSV",  200, 2,True, "SEÑALES"),
    ("SEM-02","No respetar señal de STOP",                              "Art. 76.b LSV",  200, 2,True, "SEÑALES"),
    ("SEM-03","No respetar señal de CEDA EL PASO",                     "Art. 76.b LSV",  200, 2,True, "SEÑALES"),
    ("SEM-04","Circular en dirección prohibida",                        "Art. 76.b LSV",  200, 2,True, "SEÑALES"),
    ("PRI-01","No ceder paso a vehículos con prioridad",                "Art. 68 LSV",    200, 2,True, "SEÑALES"),
    ("PRI-02","No ceder paso a peatones en paso de cebra",              "Art. 65 LSV",    200, 2,True, "SEÑALES"),
    # ESTACIONAMIENTO
    ("EST-01","Estacionamiento en zona prohibida",                      "Art. 90 LSV",     80, 0,False,"ESTACIONAMIENTO"),
    ("EST-02","Estacionamiento en plaza reservada discapacitados",      "Art. 94 LSV",    200, 0,True, "ESTACIONAMIENTO"),
    ("EST-03","Estacionamiento en carril bus/taxi/VTC",                 "Art. 90 LSV",    100, 0,False,"ESTACIONAMIENTO"),
    ("EST-04","Estacionamiento en salida emergencias/bomberos",         "Art. 94 LSV",    500, 0,True, "ESTACIONAMIENTO"),
    ("EST-05","Estacionamiento en doble fila",                          "Art. 90 LSV",    100, 0,False,"ESTACIONAMIENTO"),
    ("EST-06","Estacionamiento en paso de peatones / cebra",            "Art. 90 LSV",    200, 0,True, "ESTACIONAMIENTO"),
    ("EST-07","Estacionamiento bloqueando vado / garaje",               "Art. 90 LSV",    200, 0,True, "ESTACIONAMIENTO"),
    # DOCUMENTACIÓN
    ("CAR-01","Conducción sin seguro obligatorio",                      "Art. 1 LRCSCVM", 600, 0,True, "DOCUMENTACIÓN"),
    ("CAR-02","Conducción con ITV caducada o sin pasar",                "Art. 106 LSV",   200, 0,False,"DOCUMENTACIÓN"),
    ("CAR-03","Conducción sin permiso de conducir en vigor",            "Art. 77 LSV",    500, 0,True, "DOCUMENTACIÓN"),
    ("CAR-04","Conducción con permiso suspendido o retirado",           "Art. 383 CP",   1000, 0,True, "DOCUMENTACIÓN"),
    ("CAR-05","Matrícula ilegible, falsa o manipulada",                 "Art. 70 LSV",    200, 0,True, "DOCUMENTACIÓN"),
    ("CAR-06","No llevar documentación del vehículo",                   "Art. 109 LSV",   100, 0,False,"DOCUMENTACIÓN"),
    ("CAR-07","Conductor menor de edad sin carnet",                     "Art. 77 LSV",   1000, 0,True, "DOCUMENTACIÓN"),
    # ADELANTAMIENTO
    ("ADV-01","Adelantamiento antirreglamentario",                      "Art. 84 LSV",    200, 2,True, "ADELANTAMIENTO"),
    ("ADV-02","Adelantamiento en paso de peatones",                     "Art. 84 LSV",    200, 2,True, "ADELANTAMIENTO"),
    ("ADV-03","Adelantamiento en curva / cambio de rasante",            "Art. 84 LSV",    200, 4,True, "ADELANTAMIENTO"),
    ("ADV-04","Adelantamiento con línea continua",                      "Art. 84 LSV",    200, 4,True, "ADELANTAMIENTO"),
    # CARGA / TÉCNICA
    ("TEC-01","Carga mal sujeta o con exceso de peso",                  "Art. 105 LSV",   200, 0,True, "TÉCNICA/CARGA"),
    ("TEC-02","Vehículo con deficiencias técnicas graves",              "Art. 107 LSV",   200, 0,True, "TÉCNICA/CARGA"),
    ("TEC-03","Exceso de ocupantes (más plazas de las permitidas)",     "Art. 103 LSV",   200, 3,True, "TÉCNICA/CARGA"),
    ("TEC-04","Luces en mal estado o sin funcionar",                    "Art. 99 LSV",    100, 0,False,"TÉCNICA/CARGA"),
    # OTROS
    ("OTR-01","Abandono del lugar del accidente (fuga)",                "Art. 195 CP",    600, 0,True, "OTROS"),
    ("OTR-02","Conducción temeraria",                                   "Art. 380 CP",   1000, 6,True, "OTROS"),
    ("OTR-03","Carrera ilegal de vehículos",                            "Art. 76.g LSV",  600, 6,True, "OTROS"),
    ("OTR-04","Circular por el arcén indebidamente",                    "Art. 76.f LSV",  200, 0,False,"OTROS"),
    ("OTR-05","No respetar distancia de seguridad",                     "Art. 76.f LSV",  200, 3,True, "OTROS"),
    ("OTR-06","Conducción con gases de escape excesivos",               "Art. 107 LSV",   200, 0,False,"OTROS"),
]

AGENTES_TIPOS = [
    "Guardia Civil de Tráfico","Policía Local","Policía Nacional",
    "Mossos d'Esquadra","Ertzaintza","Policía Foral de Navarra",
    "Agente de Movilidad Urbana","Radar automático DGT",
]
MUNICIPIOS_MULTA = [
    "Madrid","Barcelona","Valencia","Sevilla","Málaga","Bilbao","Zaragoza",
    "Murcia","Palma","Alicante","Córdoba","Valladolid","Vigo","Granada",
    "La Coruña","Santander","Burgos","Pamplona","Almería","Castellón",
    "Toledo","Salamanca","León","Logroño","Cádiz","Jaén","Huelva",
    "Badajoz","Albacete","Lleida","Tarragona","Girona",
]
VIAS_MULTA = [
    "A-1 km 34","A-2 km 18","A-3 km 52","A-4 km 67","A-5 km 23",
    "A-6 km 41","A-7 km 230","A-8 km 15",
    "M-30 altura Vallecas","M-30 altura Coslada","M-40 km 12","M-50 km 8",
    "N-I km 12","N-II km 56","N-IV km 89","N-V km 44","N-VI km 33",
    "AP-7 km 145","AP-4 km 88","AP-68 km 22",
    "Calle Mayor 45","Gran Vía 102","Avenida Diagonal 350",
    "Paseo de la Castellana 200","Ronda de Atocha 12",
    "Avenida Meridiana 55","Calle Alcalá 300","Gran Vía 55",
]

# Dict de consulta rápida
MULTAS_DICT = {c: {"codigo":c,"descripcion":d,"articulo":a,"importe":i,
                    "puntos":p,"grave":g,"categoria":cat}
               for c,d,a,i,p,g,cat in TIPOS_MULTA}

# ──────────────────────────────────────────────
#  TABLA MULTAS (creación garantizada al inicio)
# ──────────────────────────────────────────────
def ensure_multas_table():
    """Crea la tabla si no existe y añade columnas nuevas si faltan."""
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS multas_registro (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        expediente            TEXT UNIQUE,
        matricula             TEXT,
        dni                   TEXT,
        nombre_denunciado     TEXT,
        codigo_infraccion     TEXT NOT NULL,
        descripcion           TEXT,
        articulo              TEXT,
        categoria             TEXT,
        importe               INTEGER NOT NULL DEFAULT 0,
        importe_reducido      INTEGER,
        puntos_retirados      INTEGER DEFAULT 0,
        lugar                 TEXT,
        via                   TEXT,
        municipio             TEXT,
        agente_tipo           TEXT,
        agente_num            TEXT,
        agente_nombre         TEXT,
        fecha_hora            TEXT,
        velocidad_detectada   INTEGER,
        velocidad_limite      TEXT,
        tasa_alcohol_aire     TEXT,
        tasa_alcohol_sangre   TEXT,
        droga_tipo            TEXT,
        droga_resultado       TEXT,
        num_pasajeros         INTEGER,
        condiciones_via       TEXT,
        condiciones_clima     TEXT,
        testigos              TEXT,
        observaciones         TEXT,
        pruebas               TEXT,
        estado                TEXT DEFAULT 'Pendiente pago',
        fecha_notificacion    TEXT,
        fecha_pago            TEXT,
        creado_por            TEXT,
        created_at            TEXT DEFAULT (datetime('now')),
        updated_at            TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_multa_mat ON multas_registro(matricula);
    CREATE INDEX IF NOT EXISTS idx_multa_dni ON multas_registro(dni);
    CREATE INDEX IF NOT EXISTS idx_multa_exp ON multas_registro(expediente);
    """)
    db.commit()
    db.close()

# ──────────────────────────────────────────────
#  API: verificación policial rápida
# ──────────────────────────────────────────────
@app.route("/api/policia/verificar")
def api_policia_verificar():
    q = request.args.get("q","").strip().upper().replace(" ","")
    if not q:
        return jsonify({"error": "Introduce un DNI o matrícula"}), 400

    # Normalizar matrícula (7 chars → insertar espacio)
    q_mat = q[:4]+" "+q[4:] if len(q)==7 and q[:4].isdigit() else q

    es_dni = len(q)==9 and q[:8].isdigit() and q[8].isalpha()
    es_mat = len(q)==7 and q[:4].isdigit() and q[4:].isalpha()

    resultado = {"query": q, "tipo": None, "encontrado": False,
                 "alertas":[], "multas_historial":[], "ciudadano":None, "matricula":None}

    if es_dni:
        resultado["tipo"] = "DNI"
        num  = int(q[:8])
        ficha= _ficha_dni_universal(num)
        resultado["ciudadano"]  = ficha
        resultado["encontrado"] = ficha.get("en_bd", False)
        resultado["alertas"]    = [dict(a) for a in query(
            "SELECT * FROM alertas_policiales WHERE dni=? AND activa=1", (q,))]
        resultado["puntos_carnet"] = ficha.get("puntos_carnet", 15)
        resultado["antecedentes"]  = ficha.get("antecedentes_penales","No")
        # Multas reales del DNI
        resultado["multas_historial"] = [dict(m) for m in query(
            "SELECT * FROM multas_registro WHERE dni=? ORDER BY id DESC LIMIT 20", (q,))]
        # Matrículas con multas pendientes
        mats = query("SELECT matricula,importe_multas,num_infracciones FROM matriculas WHERE dni=?", (q,))
        resultado["multas_pendientes"] = [dict(m) for m in mats if (m["importe_multas"] or 0)>0]

    elif es_mat:
        resultado["tipo"]     = "MATRICULA"
        ficha = _ficha_matricula_universal(q_mat)
        resultado["matricula"]  = ficha
        resultado["encontrado"] = ficha.get("en_bd", False)
        dni_prop = ficha.get("dni","")
        resultado["alertas"] = [dict(a) for a in query(
            "SELECT * FROM alertas_policiales WHERE dni=? AND activa=1", (dni_prop,))]
        resultado["multas_historial"] = [dict(m) for m in query(
            "SELECT * FROM multas_registro WHERE matricula=? ORDER BY id DESC LIMIT 20", (q_mat,))]
        resultado["multas_pendientes_importe"] = ficha.get("importe_multas", 0)
        resultado["num_infracciones"] = ficha.get("num_infracciones", 0)
        prop = query("SELECT * FROM ciudadanos WHERE dni=?", (dni_prop,), one=True)
        if prop:
            resultado["ciudadano"] = dict(prop)
    else:
        return jsonify({"error":"Formato no reconocido. Usa: 12345678Z o 1234BBB"}), 400

    return jsonify(resultado)

# ──────────────────────────────────────────────
#  API: registrar UNA o VARIAS multas
# ──────────────────────────────────────────────
@app.route("/api/policia/multa/nueva", methods=["POST"])
def api_nueva_multa():
    """Acepta JSON con una multa o lista de multas.
       No requiere login: el agente_num actúa como identificador."""
    try:
        payload = request.get_json(force=True, silent=True) or {}
    except Exception:
        payload = {}

    # Soporte para array de multas o multa individual
    multas_input = payload if isinstance(payload, list) else [payload]
    resultados   = []
    errores      = []

    for idx, d in enumerate(multas_input):
        try:
            mat_raw = str(d.get("matricula","")).upper().strip()
            # normalizar matrícula
            if len(mat_raw)==7 and mat_raw[:4].isdigit():
                mat_str = mat_raw[:4]+" "+mat_raw[4:]
            else:
                mat_str = mat_raw

            dni_str  = str(d.get("dni","")).upper().strip()
            codigo   = str(d.get("codigo_infraccion","")).upper().strip()

            if not codigo:
                errores.append({"idx":idx,"error":"Falta codigo_infraccion"})
                continue
            if codigo not in MULTAS_DICT:
                errores.append({"idx":idx,"error":f"Código {codigo} no válido"})
                continue
            if not mat_str and not dni_str:
                errores.append({"idx":idx,"error":"Falta matrícula y DNI"})
                continue

            inf = MULTAS_DICT[codigo]
            try:
                importe_final  = int(float(d.get("importe_final", inf["importe"])))
            except (ValueError, TypeError):
                importe_final  = inf["importe"]
            try:
                puntos_retirar = int(float(d.get("puntos_retirar", inf["puntos"])))
            except (ValueError, TypeError):
                puntos_retirar = inf["puntos"]

            importe_reducido = round(importe_final * 0.8)

            # Generar número de expediente único
            ts  = datetime.now().strftime("%Y%m%d%H%M%S")
            exp = f"MUL-{ts}-{idx:02d}-{abs(hash(mat_str+dni_str+codigo))%9999:04d}"

            # Si la matrícula está en BD: actualizar contadores
            if mat_str:
                mat_row = query("SELECT id,dni,importe_multas,num_infracciones FROM matriculas WHERE matricula=?",
                                (mat_str,), one=True)
                if mat_row:
                    execute("""UPDATE matriculas
                               SET importe_multas=?, num_infracciones=?, updated_at=datetime('now')
                               WHERE matricula=?""",
                            ((mat_row["importe_multas"] or 0)+importe_final,
                             (mat_row["num_infracciones"] or 0)+1,
                             mat_str))
                    if not dni_str:
                        dni_str = mat_row["dni"]

            # Retirar puntos si el ciudadano está en BD
            if dni_str and puntos_retirar > 0:
                cit = query("SELECT puntos_carnet FROM ciudadanos WHERE dni=?", (dni_str,), one=True)
                if cit:
                    nuevos = max(0, (cit["puntos_carnet"] or 15) - puntos_retirar)
                    execute("UPDATE ciudadanos SET puntos_carnet=?, updated_at=datetime('now') WHERE dni=?",
                            (nuevos, dni_str))

            # Nombre del denunciado
            nombre_den = ""
            if dni_str:
                cn = query("SELECT nombre,apellido1,apellido2 FROM ciudadanos WHERE dni=?", (dni_str,), one=True)
                if cn:
                    nombre_den = f"{cn['nombre']} {cn['apellido1']} {cn['apellido2'] or ''}".strip()

            # Insertar en tabla multas_registro
            db = get_db()
            cur = db.execute("""
                INSERT INTO multas_registro
                    (expediente, matricula, dni, nombre_denunciado,
                     codigo_infraccion, descripcion, articulo, categoria,
                     importe, importe_reducido, puntos_retirados,
                     lugar, via, municipio,
                     agente_tipo, agente_num, agente_nombre,
                     fecha_hora,
                     velocidad_detectada, velocidad_limite,
                     tasa_alcohol_aire, tasa_alcohol_sangre,
                     droga_tipo, droga_resultado,
                     num_pasajeros, condiciones_via, condiciones_clima,
                     testigos, observaciones, pruebas,
                     estado, fecha_notificacion, creado_por)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                exp, mat_str, dni_str, nombre_den,
                codigo, inf["descripcion"], inf["articulo"], inf["categoria"],
                importe_final, importe_reducido, puntos_retirar,
                str(d.get("lugar","")), str(d.get("via","")), str(d.get("municipio","")),
                str(d.get("agente_tipo","Policía Local")),
                str(d.get("agente_num","")), str(d.get("agente_nombre","")),
                str(d.get("fecha_hora", datetime.now().strftime("%Y-%m-%d %H:%M"))),
                d.get("velocidad_detectada") or None,
                str(d.get("velocidad_limite","")) or None,
                str(d.get("tasa_alcohol_aire","")) or None,
                str(d.get("tasa_alcohol_sangre","")) or None,
                str(d.get("droga_tipo","")) or None,
                str(d.get("droga_resultado","")) or None,
                d.get("num_pasajeros") or None,
                str(d.get("condiciones_via","")) or None,
                str(d.get("condiciones_clima","")) or None,
                str(d.get("testigos","")) or None,
                str(d.get("observaciones","")) or None,
                str(d.get("pruebas","")) or None,
                "Pendiente pago",
                datetime.now().strftime("%Y-%m-%d"),
                str(d.get("agente_num","sistema")),
            ))
            db.commit()
            lid = cur.lastrowid

            resultados.append({
                "ok": True, "id": lid, "expediente": exp,
                "codigo": codigo, "descripcion": inf["descripcion"],
                "importe": importe_final, "importe_reducido": importe_reducido,
                "puntos": puntos_retirar, "categoria": inf["categoria"],
            })

        except Exception as e:
            errores.append({"idx": idx, "error": str(e)})

    # Audit log
    for r in resultados:
        try:
            db2 = get_db()
            db2.execute("INSERT INTO audit_log (usuario,accion,tabla,registro_id,detalle) VALUES (?,?,?,?,?)",
                        (payload[0].get("agente_num","sistema") if isinstance(payload,list) else payload.get("agente_num","sistema"),
                         "MULTA", "multas_registro", str(r["id"]),
                         f"{r['codigo']} — {r['importe']}€"))
            db2.commit()
        except Exception:
            pass

    if not resultados and errores:
        return jsonify({"ok":False,"errores":errores}), 400

    return jsonify({
        "ok": True,
        "total_registradas": len(resultados),
        "multas": resultados,
        "errores": errores,
    })

# ── API: listar multas con paginación y filtros ──
@app.route("/api/policia/multas")
def api_multas_lista():
    q      = request.args.get("q","").strip()
    estado = request.args.get("estado","")
    cat    = request.args.get("categoria","")
    page   = max(0, int(request.args.get("page",0)))
    per    = int(request.args.get("per",20))
    sql    = "SELECT * FROM multas_registro WHERE 1=1"
    params = []
    if q:
        sql += """ AND (matricula LIKE ? OR dni LIKE ? OR descripcion LIKE ?
                        OR municipio LIKE ? OR expediente LIKE ?
                        OR nombre_denunciado LIKE ? OR codigo_infraccion LIKE ?)"""
        params += [f"%{q}%"]*7
    if estado:
        sql += " AND estado=?"; params.append(estado)
    if cat:
        sql += " AND categoria=?"; params.append(cat)
    total = get_db().execute(f"SELECT COUNT(*) FROM ({sql})", params).fetchone()[0]
    sql  += f" ORDER BY id DESC LIMIT {per} OFFSET {page*per}"
    rows  = [dict(r) for r in query(sql, params)]
    return jsonify({"rows":rows,"total":total,"page":page,"per":per})

# ── API: detalle de una multa ──
@app.route("/api/policia/multa/<int:mid>")
def api_multa_detalle(mid):
    r = query("SELECT * FROM multas_registro WHERE id=?", (mid,), one=True)
    if not r: return jsonify({"error":"No encontrada"}), 404
    return jsonify(dict(r))

# ── API: actualizar estado ──
@app.route("/api/policia/multa/<int:mid>/estado", methods=["POST"])
def api_multa_estado(mid):
    estado = (request.get_json(silent=True) or {}).get("estado","")
    if not estado:
        return jsonify({"error":"Falta estado"}), 400
    extra = ""
    vals  = [estado]
    if estado == "Pagada":
        extra = ", fecha_pago=datetime('now')"
    execute(f"UPDATE multas_registro SET estado=?, updated_at=datetime('now'){extra} WHERE id=?",
            vals+[mid])
    try:
        get_db().execute("INSERT INTO audit_log (usuario,accion,tabla,registro_id,detalle) VALUES (?,?,?,?,?)",
                        ("sistema","MULTA_ESTADO","multas_registro",str(mid),f"Estado → {estado}"))
        get_db().commit()
    except Exception:
        pass
    return jsonify({"ok":True})

# ── API: estadísticas de multas ──
@app.route("/api/policia/multas/stats")
def api_multas_stats():
    def g(sql): return get_db().execute(sql).fetchone()[0] or 0
    def gall(sql): return {r[0]:r[1] for r in get_db().execute(sql).fetchall()}
    return jsonify({
        "total":    g("SELECT COUNT(*) FROM multas_registro"),
        "pendiente":g("SELECT COUNT(*) FROM multas_registro WHERE estado='Pendiente pago'"),
        "pagada":   g("SELECT COUNT(*) FROM multas_registro WHERE estado='Pagada'"),
        "impugnada":g("SELECT COUNT(*) FROM multas_registro WHERE estado='Impugnada'"),
        "prescrita":g("SELECT COUNT(*) FROM multas_registro WHERE estado='Prescrita'"),
        "importe_total":   g("SELECT COALESCE(SUM(importe),0) FROM multas_registro"),
        "importe_pendiente":g("SELECT COALESCE(SUM(importe),0) FROM multas_registro WHERE estado='Pendiente pago'"),
        "importe_cobrado":  g("SELECT COALESCE(SUM(importe),0) FROM multas_registro WHERE estado='Pagada'"),
        "puntos_retirados": g("SELECT COALESCE(SUM(puntos_retirados),0) FROM multas_registro"),
        "por_categoria": gall("SELECT categoria,COUNT(*) FROM multas_registro GROUP BY categoria ORDER BY 2 DESC"),
        "por_municipio": gall("SELECT municipio,COUNT(*) FROM multas_registro WHERE municipio!='' GROUP BY municipio ORDER BY 2 DESC LIMIT 10"),
    })

# ── API: catálogo de infracciones ──
@app.route("/api/policia/infracciones")
def api_infracciones():
    return jsonify(list(MULTAS_DICT.values()))

# ── PÁGINA policial ──
@app.route("/policia")
def policia():
    cats = sorted(set(c for _,_,_,_,_,_,c in TIPOS_MULTA))
    return render_template("policia.html",
        admin=session.get("admin"),
        agentes_tipos=AGENTES_TIPOS,
        municipios=MUNICIPIOS_MULTA,
        vias=VIAS_MULTA,
        tipos_multa=TIPOS_MULTA,
        categorias=cats)

@app.before_request
def before_request():
    ensure_multas_table()

if __name__ == "__main__":
    print("="*52)
    print("  SISTEMA DGT / INTERIOR - USO EDUCATIVO")
    print("="*52)
    init_db()
    print(f"🌐 Servidor en http://localhost:5000")
    print(f"🔐 Admin:  http://localhost:5000/admin")
    print(f"   Usuario: admin  |  Contraseña: admin123")
    print("="*52)
    app.run(debug=True, port=5000)