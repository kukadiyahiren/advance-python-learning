from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
import psutil
from ml import predict_result
import os
import easyocr
import cv2
import yfinance as yf
from datetime import datetime
from nsepython import nse_get_index_quote, nse_quote
from deepface import DeepFace
from functools import wraps
from db import (init_db, save_gallery_item, get_gallery_items, get_gallery_count, 
                delete_gallery_item, create_user, get_all_users, get_user_by_id, 
                update_user, delete_user, get_categories, get_student_count, get_user_count)


app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for session

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

reader = easyocr.Reader(['en'])

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Static credentials
USERNAME = "admin"
PASSWORD = "123456"



# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function



# Initialize DB on start
with app.app_context():
    init_db()

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            message = "❌ Invalid Credentials"

    return render_template('login.html', message=message)


@app.route('/students')
@login_required
def students():
    return render_template('students.html')


@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    message = ""
    
    if request.method == 'POST':
        action = request.form.get('action', 'create')
        
        if action == 'create':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if name and email and password:
                user_id = create_user(name, email, password)
                if user_id:
                    message = "✅ User created successfully!"
                else:
                    message = "❌ Name or Email already exists!"
            else:
                message = "❌ Please fill all fields!"
    
    # Get all users for display
    all_users = get_all_users()
    return render_template('users.html', users=all_users, message=message)

def fetch_stock_data():
    stocks = []
    return stocks
    # --- 1. BSE SENSEX (via yfinance) ---
    try:
        bsesn = yf.Ticker("^BSESN")
        # Try 1m interval
        hist = bsesn.history(period="1d", interval="1m")
        if not hist.empty:
            close_price = hist['Close'].iloc[-1]
            open_price = hist['Open'].iloc[0] # Approx
            change = close_price - open_price
            pct = (change / open_price) * 100
            last_ts = hist.index[-1]
            last_updated = last_ts.strftime("%H:%M:%S")
        else:
            # Fallback to daily
            hist = bsesn.history(period="5d")
            if not hist.empty:
                close_price = hist['Close'].iloc[-1]
                open_price = hist['Open'].iloc[-1] # Prev close roughly
                # Better: change from prev close
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else open_price
                change = close_price - prev_close
                pct = (change / prev_close) * 100
                last_updated = hist.index[-1].strftime("%Y-%m-%d")
            else:
                 raise ValueError("Empty data")
        
        stocks.append({
            "name": "BSE SENSEX",
            "price": f"{close_price:,.2f}",
            "change": f"{change:+.2f}",
            "pct": f"{pct:+.2f}%",
            "is_up": bool(change >= 0),
            "last_updated": last_updated
        })
    except Exception as e:
        print(f"Sensex Error: {e}")
        stocks.append({"name": "BSE SENSEX", "price": "N/A", "change": "0.00", "pct": "0.00%", "is_up": True, "last_updated": "N/A"})

    # --- 2. NIFTY 50 (via nsepython) ---
    try:
        nifty = nse_get_index_quote("nifty 50")
        # Nifty dict: {'last': '...', 'percChange': '...', 'timeVal': '...'}
        price = float(nifty['last'].replace(',', ''))
        pct_change = float(nifty['percChange'])
        # Calculate raw change: price - (price / (1 + pct/100))
        # Or usually change is not explicitly in index quote, but let's check
        # Wait, index quote often has 'change' or 'absoluteChange'.
        # Based on test output: 'last', 'previousClose'.
        prev_close = float(nifty['previousClose'].replace(',', ''))
        change = price - prev_close
        
        last_updated = nifty['timeVal'].split(" ")[3] # 'Jan 16, 2026 13:28:03' -> 13:28:03
        
        stocks.append({
            "name": "NIFTY 50",
            "price": f"{price:,.2f}",
            "change": f"{change:+.2f}",
            "pct": f"{pct_change:+.2f}%",
            "is_up": bool(change >= 0),
            "last_updated": last_updated
        })
    except Exception as e:
        print(f"Nifty Error: {e}")
        stocks.append({"name": "NIFTY 50", "price": "N/A", "change": "0.00", "pct": "0.00%", "is_up": True, "last_updated": "N/A"})

    # --- 3. Individual Stocks (TRIDENT, VIKASECO) via nsepython ---
    for sym, name in [("TRIDENT", "Trident Ltd"), ("VIKASECO", "Vikas Ecotech")]:
        try:
            q = nse_quote(sym)
            # Structure: q['priceInfo']['lastPrice'], ['change'], ['pChange']
            # q['metadata']['lastUpdateTime'] '06-Feb-2026 12:49:27'
            p_info = q['priceInfo']
            price = p_info['lastPrice']
            change = p_info['change']
            pct = p_info['pChange']
            
            meta = q.get('metadata', {})
            t_str = meta.get('lastUpdateTime', "N/A")
            if " " in t_str:
                last_updated = t_str.split(" ")[1] # Get time part
            else:
                last_updated = t_str
            
            stocks.append({
                "name": name,
                "price": f"{price:,.2f}",
                "change": f"{change:+.2f}",
                "pct": f"{pct:+.2f}%",
                "is_up": bool(change >= 0),
                "last_updated": last_updated
            })
        except Exception as e:
            print(f"{name} Error: {e}")
            stocks.append({"name": name, "price": "N/A", "change": "0.00", "pct": "0.00%", "is_up": True, "last_updated": "N/A"})

    return stocks

@app.route('/api/stocks')
@login_required
def api_stocks():
    return jsonify(fetch_stock_data())

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = {
        "name": "Herry",
        "email": "admin@test.com",
        "skills": ["PHP", "Laravel", "Python"]
    }
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    study_hours = 2
    ml_result = predict_result(study_hours)
    # print(ml_result)

    s = "Python"
    rev = s[::-1]
    print(rev)
    
    gallery_count = get_gallery_count()
    student_count = get_student_count()
    user_count = get_user_count()

    
    stocks = fetch_stock_data()

    return render_template(
        "dashboard.html",
        user=session['user'],
        cpu=cpu,
        ram=ram,
        mlResult=ml_result,
        studyHours=study_hours,
        userData=user,
        galleryCount=gallery_count,
        studentCount=student_count,
        userCount=user_count,
        stocks=stocks
    )

# EasyOCR is used instead of pytesseract

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    text = ""

    if request.method == "POST":
        file = request.files["image"]
        category_id = request.form.get("category_id", default=1, type=int) 
        
        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)

        try:
            # Hair Style Category Processing
            if category_id == 2:
                
                # Analyze Face
                objs = DeepFace.analyze(img_path = path, actions = ['gender'], enforce_detection=False)
                gender = objs[0]['dominant_gender']
                
                # Generate 8 Variants (Simulated)
                # Generate Variants with Hair Overlays
                variants = []
                base_img = cv2.imread(path)
                
                # Detect face region for scaling hair
                # DeepFace analyze returns region in 'region': {'x':, 'y':, 'w':, 'h':}
                face_region = objs[0]['region']
                fx, fy, fw, fh = face_region['x'], face_region['y'], face_region['w'], face_region['h']
                
                # Select asset folder based on gender
                asset_folder = "male" if gender == "Man" else "female"
                asset_dir = os.path.join("static", "hair_assets", asset_folder)
                
                print(f"DEBUG: Gender detected: {gender}")
                print(f"DEBUG: Asset Directory: {os.path.abspath(asset_dir)}")

                # Ensure assets exist, if not use fallback or list available
                available_assets = []
                if os.path.exists(asset_dir):
                    available_assets = sorted([f for f in os.listdir(asset_dir) if f.endswith('.png')])
                    print(f"DEBUG: Found assets: {available_assets}")
                else:
                    print(f"DEBUG: Asset directory not found: {asset_dir}")
                
                # Generate 8 variants (cycling through available assets if fewer than 8)
                for i in range(1, 9):
                    variant_img = base_img.copy()
                    
                    if available_assets:
                        # Cycle through assets: 0, 1, 0, 1...
                        asset_name = available_assets[(i-1) % len(available_assets)]
                        asset_path = os.path.join(asset_dir, asset_name)
                        
                        # Load hair asset (uncached for simplicity)
                        hair_img = cv2.imread(asset_path, cv2.IMREAD_UNCHANGED) # Load with Alpha
                        
                        if hair_img is not None:
                            print(f"DEBUG: Applied asset {asset_name} for variant {i}")
                            # Resize hair to fit face width (plus some padding)
                            # Heuristic: Hair width = 1.2 * face width
                            scale_factor = 1.3
                            target_width = int(fw * scale_factor)
                            aspect_ratio = hair_img.shape[0] / hair_img.shape[1]
                            target_height = int(target_width * aspect_ratio)
                            
                            hair_resized = cv2.resize(hair_img, (target_width, target_height))
                            
                            # Calculate position: centered on face x, and sitting a bit above face y
                            # Heuristic: Hair bottom around eyebrows (y + h/3) or top of head (y)
                            # Let's align top of hair a bit above the face box
                            # x pos: center of hair = center of face
                            
                            face_center_x = fx + fw // 2
                            hair_x = face_center_x - target_width // 2
                            hair_y = fy - int(target_height * 0.45) # Shift up significantly
                            
                            # Overlay logic (handling boundaries and alpha)
                            y1, y2 = hair_y, hair_y + target_height
                            x1, x2 = hair_x, hair_x + target_width
                            
                            alpha_s = hair_resized[:, :, 3] / 255.0
                            alpha_l = 1.0 - alpha_s
                            
                            # Iterate channels
                            for c in range(0, 3):
                                # Define clipping for image boundaries
                                r_y1, r_y2 = max(0, y1), min(variant_img.shape[0], y2)
                                r_x1, r_x2 = max(0, x1), min(variant_img.shape[1], x2)
                                
                                # asset offsets if cropped
                                a_y1 = max(0, -y1)
                                a_y2 = a_y1 + (r_y2 - r_y1)
                                a_x1 = max(0, -x1)
                                a_x2 = a_x1 + (r_x2 - r_x1)
                                
                                if r_y2 > r_y1 and r_x2 > r_x1:
                                    variant_img[r_y1:r_y2, r_x1:r_x2, c] = (alpha_s[a_y1:a_y2, a_x1:a_x2] * hair_resized[a_y1:a_y2, a_x1:a_x2, c] +
                                                                            alpha_l[a_y1:a_y2, a_x1:a_x2] * variant_img[r_y1:r_y2, r_x1:r_x2, c])
                    else:
                         # Fallback if no assets found
                        variant_img = cv2.applyColorMap(variant_img, cv2.COLORMAP_AUTUMN if i%2==0 else cv2.COLORMAP_WINTER)

                        
                    variant_filename = f"variant_{i}_{file.filename}"
                    variant_path = os.path.join(app.config["UPLOAD_FOLDER"], variant_filename)
                    cv2.imwrite(variant_path, variant_img)
                    
                    variants.append({
                        "id": i,
                        "src": url_for('uploaded_file', filename=variant_filename),
                        "filename": variant_filename,
                        "style": f"Style {i} ({gender})"
                    })

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        "success": True, 
                        "type": "selection_required",
                        "variants": variants,
                        "original_filename": file.filename,
                        "gender": gender
                    })

            # General/OCR Processing
            # Read image
            img = cv2.imread(path)

            # EasyOCR reading
            results = reader.readtext(img)

            # Combine detected text
            lines = []
            for (bbox, detected_text, prob) in results:
                if prob > 0.4:  # confidence filter
                    lines.append(detected_text)

            text = "\n".join(lines)
            
            # Save to database
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_gallery_item(file.filename, text, timestamp, category_id)
            
            entry = {
                "filename": file.filename,
                "text": text,
                "timestamp": timestamp,
                "category_id": category_id
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": True, "entry": entry})

        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"success": False, "error": str(e)}), 500
            print(e)
            raise e

    return render_template("upload.html", text=text)

@app.route('/save_variant', methods=['POST'])
@login_required
def save_variant():
    try:
        data = request.json
        filename = data.get('filename')
        original_filename = data.get('original_filename')
        category_id = data.get('category_id', 2)
        style_name = data.get('style_name', 'Custom Style')
        
        # Cleanup unused variants
        if original_filename:
            for i in range(1, 9):
                variant_name = f"variant_{i}_{original_filename}"
                if variant_name != filename:
                    variant_path = os.path.join(app.config["UPLOAD_FOLDER"], variant_name)
                    if os.path.exists(variant_path):
                        os.remove(variant_path)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_gallery_item(filename, f"AI {style_name}", timestamp, category_id)
        
        entry = {
            "filename": filename,
            "text": f"AI {style_name}",
            "timestamp": timestamp,
            "category_id": category_id
        }
        return jsonify({"success": True, "entry": entry})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    try:
        filename = delete_gallery_item(item_id)
        
        if not filename:
            return jsonify({"success": False, "error": "Item not found"}), 404
        
        # Delete file from disk
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/edit_user/<int:user_id>', methods=['GET'])
def edit_user(user_id):
    """Render edit user page - actual data loading happens via FastAPI in the frontend"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('edit_user.html', user_id=user_id)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user_route(user_id):
    try:
        success = delete_user(user_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "User not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/gallery')
def gallery():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    categories = get_categories()
    data = get_gallery_items()
    
    return render_template('gallery.html', gallery_items=data, categories=categories)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
