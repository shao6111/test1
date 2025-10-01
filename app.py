from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = "mysecret"

# 租客資料 (記憶體模擬，可改資料庫)
tenants = []
next_id = 1

# 帳號密碼
USERNAME = "admin"
PASSWORD = "1234"

# 契約書存放資料夾
UPLOAD_FOLDER = "contracts"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 登入頁
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="帳號或密碼錯誤")
    return render_template("login.html")

# 登出
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# 首頁（資料管理）
@app.route("/index")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html", tenants=tenants)

# 新增租客
@app.route("/add", methods=["GET", "POST"])
def add():
    global next_id
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method == "POST":
        data = {
            "id": next_id,
            "name": request.form["name"],
            "room": request.form["room"],
            "mobile": request.form["mobile"],
            "id_number": request.form["id_number"],
            "address": request.form["address"],
            "move_in_date": request.form["move_in_date"],
            "rent": request.form["rent"],
            "deposit": request.form["deposit"],
            "electricity_start": request.form["electricity_start"],
            "contract": None
        }
        contract_file = request.files.get("contract")
        if contract_file and contract_file.filename:
            filename = f"{next_id}_{contract_file.filename}"
            contract_file.save(os.path.join(UPLOAD_FOLDER, filename))
            data["contract"] = filename

        tenants.append(data)
        next_id += 1
        return redirect(url_for("index"))
    return render_template("add.html")

# 編輯租客
@app.route("/edit/<int:tenant_id>", methods=["GET", "POST"])
def edit(tenant_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    tenant = next((t for t in tenants if t["id"] == tenant_id), None)
    if not tenant:
        return "租客不存在"
    if request.method == "POST":
        tenant.update({
            "name": request.form["name"],
            "room": request.form["room"],
            "mobile": request.form["mobile"],
            "id_number": request.form["id_number"],
            "address": request.form["address"],
            "move_in_date": request.form["move_in_date"],
            "rent": request.form["rent"],
            "deposit": request.form["deposit"],
            "electricity_start": request.form["electricity_start"]
        })
        contract_file = request.files.get("contract")
        if contract_file and contract_file.filename:
            filename = f"{tenant_id}_{contract_file.filename}"
            contract_file.save(os.path.join(UPLOAD_FOLDER, filename))
            tenant["contract"] = filename
        return redirect(url_for("index"))
    return render_template("edit.html", tenant=tenant)

# 刪除租客
@app.route("/delete/<int:tenant_id>", methods=["POST"])
def delete(tenant_id):
    global tenants
    tenants = [t for t in tenants if t["id"] != tenant_id]
    return redirect(url_for("index"))

# 下載契約書
@app.route("/contracts/<filename>")
def download_contract(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
