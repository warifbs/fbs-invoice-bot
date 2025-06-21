from flask import Flask, request, jsonify
from datetime import datetime
import random

app = Flask(__name__)
sessions = {}

@app.route('/whatsauto-reply', methods=['POST'])
def reply():
    data = request.get_json()
    message = data.get('message', '').strip().lower()
    user = data.get('phone', 'unknown_user')

    if user not in sessions:
        sessions[user] = {
            'step': 0,
            'invoice_number': f'INV{random.randint(1000, 9999)}',
            'date': datetime.now().strftime('%d-%m-%Y'),
            'mobile': '',
            'name': '',
            'items': []
        }

    session = sessions[user]

    if message == '.invoice' and session['step'] == 0:
        session['step'] = 1
        return jsonify({"reply": "📱 Please enter the *customer mobile number*:"})

    elif session['step'] == 1:
        session['mobile'] = message
        session['step'] = 2
        return jsonify({"reply": "👤 Please enter the *customer name*:"})

    elif session['step'] == 2:
        session['name'] = message
        session['step'] = 3
        return jsonify({"reply": "🎁 Enter *item name & price* (e.g. Netflix 450). Type 'done' when finished."})

    elif session['step'] == 3:
        if message == 'done':
            if not session['items']:
                return jsonify({"reply": "⚠️ No items entered yet. Please enter at least 1 item."})
            else:
                return jsonify({"reply": generate_invoice(session)})
        else:
            try:
                parts = message.split()
                price = int(parts[-1])
                name = " ".join(parts[:-1])
                session['items'].append({'name': name.title(), 'price': price})
                return jsonify({"reply": f"✅ Added: *{name.title()}* – Rs. {price}\nAdd next or type *done* to finish."})
            except:
                return jsonify({"reply": "⚠️ Invalid format. Please send as: `ItemName Price` (e.g. ChatGPT 599)"})

    else:
        return jsonify({"reply": "Type `.invoice` to start a new invoice."})

def generate_invoice(session):
    items_text = ""
    subtotal = sum(item['price'] for item in session['items'])

    for i, item in enumerate(session['items'], start=1):
        items_text += f"{i}️⃣ {item['name']} – Rs. {item['price']}\n"

    tax_percent = 1
    discount_percent = 10
    tax = round(subtotal * (tax_percent / 100), 2)
    discount = round(subtotal * (discount_percent / 100), 2)
    total = round(subtotal + tax - discount, 2)

    invoice = f"""📦 *FBS Digital Store – Invoice*

🧾 *Invoice #:* {session['invoice_number']}  
📅 *Date:* {session['date']}  

👤 *Customer:* {session['name'].title()}  
📱 *Mobile:* {session['mobile']}  

🎁 *Items Purchased:*
{items_text}
💸 *Payment Breakdown:*  
• Subtotal: Rs. {subtotal}  
• Tax ({tax_percent}%): Rs. {tax}  
• Discount ({discount_percent}%): Rs. {discount}  
✅ *Total Payable:* Rs. {total}  

🛍️ *FBS Digital Store (PVT) LTD*  
📞 For support, reply to this message."""
    
    del sessions[session['mobile']]
    return invoice

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
