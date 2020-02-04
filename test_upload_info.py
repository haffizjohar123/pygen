from firebase import firebase

firebase = firebase.FirebaseApplication('https://pygen-d1deb.firebaseio.com/',None)
gen_name_data={'name':'GEN_NAME',
               'value':'DS0448'}
info_base=firebase.put('/GENSET/INFO/','GEN_NAME',gen_name_data)
print(info_base)