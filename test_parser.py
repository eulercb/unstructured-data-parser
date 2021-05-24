from main import parse_unstructured_data, format_data
from faker import Faker


def test_always_pass():
    # Arrange
    faker = Faker()
    email = faker.email()
    senha_email = faker.password(special_chars=False)
    senha_fb = faker.password(special_chars=False)
    data_nascimento = faker.date('%d/%m/%Y')
    ano_criacao = faker.date('%Y')
    sexo = 'Masculino' if faker.pybool() else 'Feminino'
    usuario = faker.user_name()
    url = faker.url()

    unstructured_data = f"""
Email : {email}
Senha do email: {senha_email}
Senha facebook: {senha_fb}
Data de nascimento: {data_nascimento}
Ano de criação: {ano_criacao}
Sexo: {sexo}
Usuario:  {usuario}
Código de 2 fatores: {url}

CODE #1
{faker.pyint(1000)} {faker.pyint(1000)}
CODE #2
{faker.pyint(1000)} {faker.pyint(1000)}
CODE #3
{faker.pyint(1000)} {faker.pyint(1000)}
CODE #4
{faker.pyint(1000)} {faker.pyint(1000)}
CODE #5
{faker.pyint(1000)} {faker.pyint(1000)}
CODE #6
{faker.pyint(1000)} {faker.pyint(1000)}
CODE #7
{faker.pyint(1000)} {faker.pyint(1000)}
CODE #8
{faker.pyint(1000)} {faker.pyint(1000)}
CODE #9
{faker.pyint(1000)} {faker.pyint(1000)}
CODE #10
{faker.pyint(1000)} {faker.pyint(1000)}
"""

    # Act
    formatted_data = format_data(parse_unstructured_data(unstructured_data))

    # Assert
    assert formatted_data['login'] == email
    assert formatted_data['senha fb'] == senha_fb
    assert formatted_data['url'] == usuario
    assert formatted_data['data de nascimento'] == data_nascimento
    assert formatted_data['link com códigos para recuperação'] == url
    assert formatted_data['senha email'] == senha_email
