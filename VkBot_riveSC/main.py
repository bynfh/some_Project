from rivescript import RiveScript
import json

# def CreateTemplate():
#     Template = '''+ [*] меню [*]
# - {"msg":"Теперь Вы в разделе Меню!",
#     ^"photo":"test_photo",
#     ^"keyboard":"test_button"}'''
#     with open('Template.rive', 'w', encoding='utf-8') as file:
#         file.write(Template)
# CreateTemplate()
rs = RiveScript(utf8=True)
rs.load_directory("./eg/brain")
rs.sort_replies()



while True:
    msg = input("You> ")
    if msg == "/quit":
        quit()
    reply = rs.reply("localuser", msg)
    # print("Bot>", reply)
    try:
        reply = json.loads(reply)
        print(f'msg:{reply.get("msg", "")}')
        print(f'photo:{reply.get("photo", "")}')
        print(f'keyboard:{reply.get("keyboard", "")}')
    except:
        print(f'msg:{reply}')