from CustomAgentAI.Models import Product, User,Session,Interaction


for i in Product.query.all():
    print(i.product_data)
    
for j in User.query.all():
    print(j.user_number)
    for k in j.Sessions:
        print("     ",k.session_id)
        for l in k.interactions:
            print(l.interaction_person,"                   ",l.interaction_data)