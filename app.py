from CustomAgentAI import app, db, redirect, url_for, send_from_directory,request, jsonify,render_template,openai
from CustomAgentAI.ResponseChat import  ResponseChat, Menu, ButtonObject
from CustomAgentAI.Models import  Product,User,Session,Interaction
import logging
import json
import sys
import PyPDF2


@app.route("/")
def home():
    return render_template("index.html")

def evaluate_initial_response(scenario,question):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=scenario + question,
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return str(response["choices"][0]["text"])

def eval_conversation(messages):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages
    )
    return str(response["choices"][0]["message"]["content"])

def process_pdf(pdfFileObj):
    pdfReader = PyPDF2.PdfReader(pdfFileObj)
    buffer = ""
    for i in range(0, len(pdfReader.pages)):
        page = pdfReader.pages[i]
        buffer += "\n" + page.extract_text()
    pdfFileObj.close()
    return buffer.strip()


@app.route("/bot_interface",methods=['POST'])
def handle_request():
    r = ResponseChat()
    logging.basicConfig(filename='chat_builder.log', level=logging.INFO)
    logging.info('##################WHATSAPP REQUEST#####################')
    json_data = request.get_json()
    logging.info('Data: {}'.format(json.dumps(json_data)))
    number=json_data["caller"]["id"]
    user=User.query.filter_by(user_number=number).first()
    if user==None:
        usr=User(number)
        db.session.add(usr)
        db.session.commit()
    user=User.query.filter_by(user_number=number).first()
    ses_id=json_data["sid"]
    if json_data["data"]["type"] == "text" and json_data["data"]["body"]["data"]=="clear":
        r.send_text("Cleared Context")
        r.set_bot_state("")
    elif json_data["data"]["type"] == "text":
        if (json_data["bot_state"]=="Before_ProdSelection" or json_data["bot_state"] not in  [x.product_name for x in Product.query.all()]):
            chat_resp=json_data["data"]["body"]["data"]
            if ses_id not in [x.session_id for x in user.Sessions]:
                sess=Session(ses_id)
                db.session.add(sess)
                db.session.commit()
                user.Sessions.append(sess)
                db.session.commit()
                resp=evaluate_initial_response("Imagine you are a customer service bot name Oz.\
                    You are help to help the customer out on providing imforamtion or solving their problem.\
                        If the customer just introduces themselves, You need to respond with what you do and what you can do.\
                            If they say anything else, ask them to choose a product in the list.\n\n","cutomer: "+chat_resp+ "\n\nOz:")
                # Create a ButtonObject
                inter=Interaction("user","Imagine you are a customer service bot name Oz.\
                    You are help to help the customer out on providing imforamtion or solving their problem.\
                        If the customer just introduces themselves, You need to respond with what you do and what you can do.\n\n")
                db.session.add(inter)
                db.session.commit()
                sess.interactions.append(inter)
                inter3=Interaction("user",chat_resp)
                db.session.add(inter3)
                sess.interactions.append(inter3)
                interaction2=Interaction("assistant",resp)
                db.session.add(interaction2)
                sess.interactions.append(interaction2)
                db.session.commit()
                print(interaction2.interaction_data,file=sys.stderr)
                buttons = ButtonObject(resp)
                products=Product.query.all()
                for i in range(len(products)):
                    buttons.add_button(str(i+1), products[i].product_name)
                # Add the buttons to the response
                r.add_buttons(buttons)
                r.set_bot_state("Before_ProdSelection")
            else:
                sess=Session.query.filter_by(session_id=ses_id).first()
                if  sess!=None:
                    interactions=[ {"role": x.interaction_person, "content": x.interaction_data } for x in sess.interactions]
                    interactions.append({"role": "user", "content": chat_resp })
                    resp=eval_conversation(interactions)
                    inter3=Interaction("user",chat_resp)
                    db.session.add(inter3)
                    db.session.commit()
                    sess.interactions.append(inter3)
                    interaction2=Interaction("assistant",resp)
                    db.session.add(interaction2)
                    sess.interactions.append(interaction2)
                    db.session.commit()
                    print(interaction2.interaction_data,file=sys.stderr)
                    buttons = ButtonObject("Choose a Product for Mode detailed information")
                    products=Product.query.all()
                    for i in range(len(products)):
                        buttons.add_button(str(i+1), products[i].product_name)
                    r.set_bot_state("Before_ProdSelection")
                    r.send_text(resp)
                    r.add_buttons(buttons)
        else:
            sess=Session.query.filter_by(session_id=ses_id).first()
            if  sess!=None:
                prod_name=json_data["bot_state"]
                chat_resp=json_data["data"]["body"]["data"]
                prod=Product.query.filter_by(product_name=prod_name).first()
                interactions=[ {"role": x.interaction_person, "content": x.interaction_data } for x in sess.interactions]
                interactions.append({"role": "user", "content": chat_resp })
                resp=eval_conversation(interactions)
                inter3=Interaction("user",chat_resp)
                db.session.add(inter3)
                db.session.commit()
                sess.interactions.append(inter3)
                interaction2=Interaction("assistant",resp)
                db.session.add(interaction2)
                sess.interactions.append(interaction2)
                db.session.commit()
                print(interaction2.interaction_data,file=sys.stderr)
                r.send_text(resp)
                r.set_bot_state(prod.product_name)
    elif (json_data["data"]["type"] == "reply" and json_data["bot_state"] == "Before_ProdSelection"):
        sess=Session.query.filter_by(session_id=ses_id).first()
        prod_name = json_data["data"]["body"]["title"]
        prod=Product.query.filter_by(product_name=prod_name).first()
        interactions=[ {"role": x.interaction_person, "content": x.interaction_data } for x in sess.interactions]
        interactions.append({"role": "user", "content": "The Product Information is as follows: \n \
            Product Name: "+prod.product_name+".\n Product information: "+prod.product_description+". \n Product Data : "+prod.product_data+"." })
        interactions.append({"role": "user", "content": "Provide me 1 sentence of details of the product chosen."})
        resp=eval_conversation(interactions)
        interaction2=Interaction("user","The Product Information is as follows: \n \
            Product Name: "+prod.product_name+".\n Product information: "+prod.product_description+". \n Product Data : "+prod.product_data+".")
        db.session.add(interaction2)
        sess.interactions.append(interaction2)
        db.session.commit()
        print(interaction2.interaction_data,file=sys.stderr)
        r.send_text(resp)
        r.set_bot_state(prod.product_name)
    return jsonify(r.get_response())
    
@app.route("/create_product", methods=["GET","POST"])
def product_create():
    if request.method=="POST":
        product_name = request.form.get('product_name')
        product_description = request.form.get('product_description')
        product_tech_contact = request.form.get('product_tech_contact')
        product_data = request.files["product_data"]
        text_data=process_pdf(product_data)
        prod =Product(product_name,product_description,product_tech_contact,text_data)
        db.session.add(prod)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
