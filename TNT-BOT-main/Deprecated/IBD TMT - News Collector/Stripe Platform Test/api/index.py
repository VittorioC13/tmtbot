from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import stripe, requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.raxegckgsveacgflvwbd:wdsjkdmmhaq@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

API2D_KEY = "fk233911-VQhGLdF8yE88Kzii7miu7ZJSepM2WMhT"
API2D_URL = "https://oa.api2d.net/v1/chat/completions"

stripe.api_key = "sk_test_51Ri9SyFSHePhJarRDO1vrS4Ca8T8pRqsvkluFVE8sP4nc5qwiGal62fcWZAU9JeUbatWjzEZ6MQigXxOUvHwmXwJ00vr1eTfnk"
#YOUR_DOMAIN = "https://flask-hello-world-k5rd6inw8-xukun-cais-projects.vercel.app/"
YOUR_DOMAIN = "http://127.0.0.1:5000"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_paid = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('用户已存在')
            return redirect(url_for('login'))
        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    if current_user.is_paid:
        return jsonify({'error': '已完成支付，无需重复付款'}), 400
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': '付费服务',
                    },
                    'unit_amount': 100,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
            metadata={"user_id": current_user.id}
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = 'whsec_29a4674ae173cf9f65a762734b99ddb0f1667cfc1d4b2ff7e789044427d740ca'  # 在 Stripe 控制台生成
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # 无效payload
        return '', 400
    except stripe.error.SignatureVerificationError:
        # 签名验证失败
        return '', 400

    # 处理支付成功事件
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        # 在数据库中查找用户并更新支付状态s
        user = User.query.get(user_id)
        if user:
            user.is_paid = True
            db.session.commit()

    return '', 200
    
@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

@app.route('/about')
def about():
    return 'About'

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.form.get('question')

    headers = {
        "Authorization": f"Bearer {API2D_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_question}],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 500
    }

    response = requests.post(API2D_URL, headers=headers, json=data)

    if response.status_code == 200:
        content = response.json()["choices"][0]["message"]["content"]
        return jsonify({"response": content})
    else:
        return jsonify({"error": "API2D request failed"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)