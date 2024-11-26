from flask import Flask, render_template, request, send_file
import pandas as pd
import qrcode
import socket
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import zipfile

app = Flask(__name__)
df = pd.read_excel("maquinas.xlsx")

def obter_ip_local():
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)
    return ip_local

def gerar_qr_code(id_maquina, url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="#001F4E", back_color="white").convert("RGBA")

    data = qr_img.getdata()
    new_data = []
    for item in data: 
        if item[:3] == (255, 255, 255):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    qr_img.putdata(new_data)

    caminho_arquivo = f"static/qr_codes/{id_maquina}.png"
    qr_img.save(caminho_arquivo)
    return caminho_arquivo

# def gerar_qr_code(id_maquina, url):
    # qr = qrcode.make(url)
    # caminho_arquivo = f"static/qr_codes/{id_maquina}.png"
    # qr.save(caminho_arquivo)
    # return caminho_arquivo

def gerar_zip_de_imagens(imagens):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i, img_io in enumerate(imagens):
            zip_file.writestr(f"etiqueta_{i+1}.png", img_io.getvalue())
    zip_buffer.seek(0)
    return zip_buffer


@app.route("/etiquetas", methods=["GET", "POST"])
def etiquetas():
    if request.method == "POST":
        id_maquina = request.form.get("id_maquina")
        return gerar_etiqueta(id_maquina) 
    return render_template("etiquetas.html")

def gerar_etiqueta(id_maquina):
    maquina = df[df["ID"] == id_maquina].to_dict(orient="records")
    
    if maquina:
        maquina = maquina[0]
        nome_maquina = maquina["Nome"]
        usuario = maquina["Usuario"]
        especificacoes = maquina["Especificacoes"]
        
        largura = 600
        altura = 200
        imagem = Image.new("RGBA", (largura, altura), (255,255,255,255))
        
        draw = ImageDraw.Draw(imagem)
        
        font = ImageFont.load_default()

        logo_path = "static/images/portobello_logo.png"
        logo = Image.open(logo_path).convert("RGBA") 
        logo = logo.resize((250, 60))
        imagem.paste(logo, (10, 120), logo)
        
        draw.text((10, 10), f"Máquina: {nome_maquina}", font=font, fill="black")
        draw.text((10, 30), f"Usuário: {usuario}", font=font, fill="black")
        draw.text((10, 50), f"Espec: {especificacoes}", font=font, fill="black")
        
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(f"ID: {id_maquina}")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill="black", back_color="white")
        qr_img = qr_img.resize((50, 50)) 
        imagem.paste(qr_img, (400, 10)) 

        img_io = BytesIO()
        imagem.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name="etiqueta.png")
    else:
        return "Máquina não encontrada", 404

@app.route("/etiquetas/massa", methods=["POST"])
def etiquetas_massa():
    imagens = []
    for index, maquina in df.iterrows():
        nome_maquina = maquina["Nome"]
        usuario = maquina["Usuario"]
        especificacoes = maquina["Especificacoes"]
        
        largura = 600
        altura = 200
        imagem = Image.new("RGBA", (largura, altura), (255,255,255,255))
        draw = ImageDraw.Draw(imagem)
        font = ImageFont.load_default()
        
        draw.text((10, 10), f"Máquina: {nome_maquina}", font=font, fill="black")
        draw.text((10, 30), f"Usuário: {usuario}", font=font, fill="black")
        draw.text((10, 50), f"Espec: {especificacoes}", font=font, fill="black")
        
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(f"ID: {maquina['ID']}")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill="black", back_color="white")
        qr_img = qr_img.resize((50, 50))
        imagem.paste(qr_img, (400, 10))
        
        logo_path = "static/images/portobello_logo.png" 
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((100, 40))
        imagem.paste(logo, (10, 120), logo)

        img_io = BytesIO()
        imagem.save(img_io, 'PNG')
        img_io.seek(0)
        imagens.append(img_io)

    return "Etiquetas em massa geradas com sucesso."

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        id_maquina = request.form.get("id_maquina")
        return pagina_maquina(id_maquina)
    return render_template("admin.html")

@app.route("/maquinas/<id_maquina>")
def pagina_maquina(id_maquina):
    print(f"Buscando máquina com ID: {id_maquina}") 
    maquina = df[df["ID"] == id_maquina].to_dict(orient="records")
    
    if maquina:
        print(f"Máquina encontrada: {maquina}") 
        maquina = maquina[0]
        ip_local = obter_ip_local()
        url = f"http://{ip_local}:5000/maquinas/{id_maquina}"
        caminho_qr = gerar_qr_code(id_maquina, url)
        return render_template("maquina.html", maquina=maquina, caminho_qr=caminho_qr)
    else:
        print("Máquina não encontrada") 
        return "Máquina não encontrada", 404
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)