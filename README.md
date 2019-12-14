# ASint

To Dos:<br/>
1- Web Application with Flask<br/>
2- Rooms Web Service

installs:<br/>
virtualenv flask<br/>
pip install flask<br/>
pip install flask-migrate<br/>
pip install flask-sqlalchemy<br/>
pip install flask-httpauth<br/>
pip install flask-wtf<br/>

Google Docs com o relatório:
https://docs.google.com/document/d/1xfKFOosCpsnncgoj6PvZY9dCy7BVxgD0Z0u8m-gYso8/edit?usp=sharing

Flask Mega Tutorial:
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxiii-application-programming-interfaces-apis

https://github.com/miguelgrinberg/microblog/tree/master/app

Funcionalidades já feitas:

- roomWS com integração com o fenix

- Backend com integração com o roomWS (Necessita Improvement)

- secretariatWS com BD e todos os endpoints (GET ALL, GET id, POST, PUT, DELETE)

- Backend com integração com o secretariatsWS

TO DOS:

Zé Cordeiro:

- Melhorar o Micro Serviço dos rooms e disponibilizar mais interaçoes com o backend (Zé Cordeiro)
- Verificar se o tipo de resposta do roomWS e BUILDING, FLOOR ou ROOM e mostrar o template de acordo
- Dar a opção de voltar ao edificio/floor/campus atras quando se esta na pagina a seguir: 
EX: Quando se está no room X dar a opção na pagina de voltar para o floor ou building ou campus onde esse room pertence

- Implementar os perfis disponiveis de acordo com o tipo de utilizador e dar autorizacao as paginas de acordo com esse perfil (LER ENUNCIADO)

- Criação do canteenWS

- Integração do backend com o canteenWS

Rui Silva:
- Autenticação com o fenix (Rui Silva)

- Implementar a autorização nos web services atraves de username e password definidos no documento .env apenas se estiverem autenticados no fenix

- Melhoria dos frontends - Bootstrap, responsive html, etc... (Rui Silva)

- Verificar quais necessitam de melhorias

Velez:
 
- Feature código de barras (Velez)

- Deploy dos varios serviços na GCloud
 
