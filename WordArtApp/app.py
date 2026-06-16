from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
import io
import os

app = Flask(__name__)

# Paletas de colores predefinidas (15 presets)
PRESETS = [
    # 0: Sunset Glow
    {"name": "Sunset Glow", "colors": [(186, 85, 211), (255, 127, 80), (255, 215, 0)]},
    # 1: Ocean Wave
    {"name": "Ocean Wave", "colors": [(10, 30, 80), (0, 150, 255), (150, 255, 200)]},
    # 2: Forest Mint
    {"name": "Forest Mint", "colors": [(10, 60, 30), (16, 185, 129), (167, 243, 208)]},
    # 3: Cyberpunk
    {"name": "Cyberpunk", "colors": [(100, 10, 150), (255, 0, 128), (255, 255, 0)]},
    # 4: Lavender Dream
    {"name": "Lavender Dream", "colors": [(75, 0, 130), (230, 190, 255), (255, 182, 193)]},
    # 5: Monochrome
    {"name": "Monochrome", "colors": [(30, 30, 30), (150, 150, 150), (255, 255, 255)]},
    # 6: Autumn Leaf
    {"name": "Autumn Leaf", "colors": [(80, 40, 20), (210, 105, 30), (255, 191, 0)]},
    # 7: Cherry Blossom
    {"name": "Cherry Blossom", "colors": [(150, 10, 40), (255, 100, 130), (255, 220, 230)]},
    # 8: Ice & Fire
    {"name": "Ice & Fire", "colors": [(30, 144, 255), (138, 43, 226), (255, 69, 0)]},
    # 9: Royal Gold
    {"name": "Royal Gold", "colors": [(10, 20, 60), (205, 127, 50), (255, 215, 0)]},
    # 10: Electric Lime
    {"name": "Electric Lime", "colors": [(0, 128, 128), (34, 139, 34), (50, 205, 50)]},
    # 11: Bubblegum
    {"name": "Bubblegum", "colors": [(255, 20, 147), (186, 85, 211), (135, 206, 250)]},
    # 12: Solar Flare
    {"name": "Solar Flare", "colors": [(180, 0, 0), (255, 140, 0), (255, 220, 0)]},
    # 13: Neon Matrix
    {"name": "Neon Matrix", "colors": [(0, 40, 0), (0, 140, 0), (0, 255, 0)]},
    # 14: Vintage Sepia
    {"name": "Vintage Sepia", "colors": [(44, 22, 8), (139, 90, 43), (244, 232, 205)]}
]

def get_preset_color(preset_id, x, width):
    """Interpola un color en base a un valor horizontal x dentro del width usando el preset_id"""
    try:
        preset = PRESETS[int(preset_id)]
    except (IndexError, ValueError):
        preset = PRESETS[0]
        
    colors = preset["colors"]
    t = x / width
    # Sujetar t entre 0 y 1
    t = max(0.0, min(1.0, t))
    
    if len(colors) == 2:
        c1, c2 = colors
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
    elif len(colors) == 3:
        c1, c2, c3 = colors
        if t < 0.5:
            factor = t * 2.0
            r = int(c1[0] * (1 - factor) + c2[0] * factor)
            g = int(c1[1] * (1 - factor) + c2[1] * factor)
            b = int(c1[2] * (1 - factor) + c2[2] * factor)
        else:
            factor = (t - 0.5) * 2.0
            r = int(c2[0] * (1 - factor) + c3[0] * factor)
            g = int(c2[1] * (1 - factor) + c3[1] * factor)
            b = int(c2[2] * (1 - factor) + c3[2] * factor)
    else:
        return colors[0]
        
    return (r, g, b)

def safe_load_font(font_name, size):
    """Carga de forma segura una fuente del sistema o recurre a la fuente por defecto"""
    try:
        return ImageFont.truetype(font_name, size)
    except OSError:
        try:
            return ImageFont.truetype(font_name.lower(), size)
        except OSError:
            # Fallback en Windows a Arial o Courier si no está la solicitada
            for alt in ["arial.ttf", "calibri.ttf", "cour.ttf"]:
                try:
                    return ImageFont.truetype(alt, size)
                except OSError:
                    continue
            return ImageFont.load_default()

@app.route('/')
def index():
    return render_template('index.html', presets=PRESETS)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Parámetros del formulario
        text = request.form.get('text', 'TB4B').strip().upper()
        quotes_raw = request.form.get('quotes', '').strip()
        preset_id = int(request.form.get('preset_id', 0))
        
        # Procesar frases de relleno
        if quotes_raw:
            quotes = [q.strip().upper() for q in quotes_raw.split('\n') if q.strip()]
        else:
            quotes = [
                "YOU BELIEVE IN YOURSELF",
                "MAKE UP YOUR MIND",
                "ACHIEVE YOUR GOALS",
                "REALIZE YOUR DREAMS",
                "IT IS WHO YOU ARE",
                "EVERY HUMAN BODY",
                "BE THE CHANGE"
            ]

        # Dimensiones del lienzo
        WIDTH = 2400
        HEIGHT = 1000
        BACKGROUND_COLOR = (10, 10, 15)  # Fondo oscuro elegante

        # Crear capa de relleno
        text_fill_fg = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
        draw_fg = ImageDraw.Draw(text_fill_fg)

        # Cargar diferentes variantes de fuentes
        fonts = [
            safe_load_font("arial.ttf", 20),
            safe_load_font("arial.ttf", 24),
            safe_load_font("arialbd.ttf", 20),
            safe_load_font("arialbd.ttf", 24),
        ]

        # Rellenar con frases y degradado
        for yy in range(0, HEIGHT, 28):
            xx = 0
            while xx < WIDTH:
                phrase = random.choice(quotes)
                font = random.choice(fonts)
                
                # Medir ancho de la frase de forma compatible
                try:
                    bbox_p = draw_fg.textbbox((0, 0), phrase, font=font)
                    phrase_w = bbox_p[2] - bbox_p[0]
                except AttributeError:
                    phrase_w, _ = draw_fg.textsize(phrase, font=font)
                
                fg_color = get_preset_color(preset_id, xx + phrase_w // 2, WIDTH)
                draw_fg.text((xx, yy), phrase, fill=fg_color, font=font)
                
                xx += phrase_w + random.randint(15, 30)

        # Crear máscara del texto principal
        mask = Image.new("L", (WIDTH, HEIGHT), 0)
        draw_mask = ImageDraw.Draw(mask)

        # Buscar tamaño óptimo del texto principal
        font_size = 600
        margin_x = 120
        margin_y = 120

        while font_size > 10:
            font_big = safe_load_font("arialbd.ttf", font_size)
            try:
                bbox = draw_mask.textbbox((0, 0), text, font=font_big)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except AttributeError:
                text_w, text_h = draw_mask.textsize(text, font=font_big)
                bbox = (0, 0, text_w, text_h)
            
            if text_w <= (WIDTH - 2 * margin_x) and text_h <= (HEIGHT - 2 * margin_y):
                break
            font_size -= 5

        # Centrar texto
        x = (WIDTH - (bbox[0] + bbox[2])) // 2
        y = (HEIGHT - (bbox[1] + bbox[3])) // 2

        # Dibujar máscara
        draw_mask.text((x, y), text, fill=255, font=font_big)

        # Crear imagen final combinando
        result = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
        result.paste(text_fill_fg, mask=mask)

        # Convertir a bytes para enviar al navegador
        img_io = io.BytesIO()
        result.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_from_image', methods=['POST'])
def generate_from_image():
    try:
        # Validar archivo
        if 'image' not in request.files:
            return jsonify({"error": "No se subió ninguna imagen"}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "Archivo de imagen inválido"}), 400

        # Cargar imagen original
        input_image = Image.open(file.stream).convert("RGB")
        
        # Parámetros adicionales
        quotes_raw = request.form.get('quotes', '').strip()
        mode = request.form.get('mode', 'mosaic') # 'mosaic' o 'silhouette'
        preset_id = int(request.form.get('preset_id', 0))
        threshold = int(request.form.get('threshold', 128)) # Para modo silueta

        # Procesar frases
        if quotes_raw:
            quotes = [q.strip().upper() for q in quotes_raw.split('\n') if q.strip()]
        else:
            quotes = [
                "YOU BELIEVE IN YOURSELF",
                "MAKE UP YOUR MIND",
                "ACHIEVE YOUR GOALS",
                "REALIZE YOUR DREAMS",
                "IT IS WHO YOU ARE",
                "EVERY HUMAN BODY",
                "BE THE CHANGE"
            ]

        # Dimensionar lienzo del mosaico basado en el aspecto original
        MAX_WIDTH = 1800
        orig_w, orig_h = input_image.size
        aspect = orig_h / orig_w
        
        WIDTH = MAX_WIDTH
        HEIGHT = int(MAX_WIDTH * aspect)
        
        # Redimensionar la imagen original de entrada para poder tomar los colores del pixel exacto
        source_image = input_image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        
        # Canvas final
        BACKGROUND_COLOR = (10, 10, 15)
        result = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
        draw_res = ImageDraw.Draw(result)

        # Cargar fuentes variadas
        fonts = [
            safe_load_font("arial.ttf", 15),
            safe_load_font("arial.ttf", 18),
            safe_load_font("arialbd.ttf", 15),
            safe_load_font("arialbd.ttf", 18),
        ]

        if mode == 'mosaic':
            # Mosaico de Color Fotográfico
            for yy in range(0, HEIGHT, 20):
                xx = 0
                while xx < WIDTH:
                    phrase = random.choice(quotes)
                    font = random.choice(fonts)
                    
                    try:
                        bbox_p = draw_res.textbbox((0, 0), phrase, font=font)
                        phrase_w = bbox_p[2] - bbox_p[0]
                    except AttributeError:
                        phrase_w, _ = draw_res.textsize(phrase, font=font)
                    
                    # Coordenada del píxel central para muestrear el color de la foto
                    sample_x = min(max(0, xx + phrase_w // 2), WIDTH - 1)
                    sample_y = min(max(0, yy), HEIGHT - 1)
                    
                    # Tomar color del píxel de la imagen original
                    pixel_color = source_image.getpixel((sample_x, sample_y))
                    
                    # Dibujar frase con el color de la foto original
                    draw_res.text((xx, yy), phrase, fill=pixel_color, font=font)
                    
                    xx += phrase_w + random.randint(10, 20)
                    
        else:
            # Modo Silueta de Imagen (Fondo oscuro con texto brillante solo donde la imagen tiene contraste)
            # Convertir imagen a escala de grises y aplicar umbral para máscara
            gray_img = ImageOps.grayscale(source_image)
            # Crear una máscara L (luminancia)
            # Invertir si se asume que las partes a dibujar son las oscuras, o conservar si son las claras.
            # Haremos que se dibuje texto donde la imagen sea más oscura que el umbral.
            mask = gray_img.point(lambda p: 255 if p < threshold else 0)
            
            # Crear capa del gradiente seleccionada
            text_fill_fg = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
            draw_fg = ImageDraw.Draw(text_fill_fg)
            
            for yy in range(0, HEIGHT, 20):
                xx = 0
                while xx < WIDTH:
                    phrase = random.choice(quotes)
                    font = random.choice(fonts)
                    
                    try:
                        bbox_p = draw_fg.textbbox((0, 0), phrase, font=font)
                        phrase_w = bbox_p[2] - bbox_p[0]
                    except AttributeError:
                        phrase_w, _ = draw_fg.textsize(phrase, font=font)
                    
                    fg_color = get_preset_color(preset_id, xx + phrase_w // 2, WIDTH)
                    draw_fg.text((xx, yy), phrase, fill=fg_color, font=font)
                    
                    xx += phrase_w + random.randint(10, 20)
            
            # Pegar texto a través de la máscara
            result.paste(text_fill_fg, mask=mask)

        # Convertir a bytes para enviar
        img_io = io.BytesIO()
        result.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
