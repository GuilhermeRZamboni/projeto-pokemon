import requests
import streamlit as st
import random
import time


if "pokemons_capturados" not in st.session_state:
    st.session_state.pokemons_capturados = {}

if "pagina_qtd" not in st.session_state:
    st.session_state.pagina_qtd = 1

if "pokebolas" not in st.session_state:
    st.session_state.pokebolas = 10

if "pc" not in st.session_state:
    st.session_state.pc = {}

if "moedas" not in st.session_state:
    st.session_state.moedas = 0

if "rolagem_restante" not in st.session_state:
    st.session_state.rolagem_restante = 5

if "ultimo_reset" not in st.session_state:
    st.session_state.ultimo_reset = time.time()

if "pokemon_rolado" not in st.session_state:
    st.session_state.pokemon_rolado = None

def resetar_rolagem():
    agora = time.time()

    if agora - st.session_state.ultimo_reset >= 3600:
        st.session_state.rolagem_restante = 5
        st.session_state.ultimo_reset = agora

pokemons_rolados = []


def roletar_pokemons():

    poke_id = random.randint(1, 1010)
    url = f"https://pokeapi.co/api/v2/pokemon/{poke_id}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        st.session_state.pokemon_rolado = {
            "name": dados["name"].capitalize(),
            "img": dados["sprites"]["front_default"]
        }

def buscar_pokemon(nome):
    url = f"https://pokeapi.co/api/v2/pokemon/{nome.lower()}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        info = {
            "nome": dados["name"].capitalize(),
            "id": dados["id"],
            "tipos": [t["type"]["name"].capitalize() for t in dados["types"]],
            "altura": dados["height"],
            "peso": dados["weight"],
            "img": dados["sprites"]["front_default"]
        }
        st.image(info["img"], width=120)
        st.write(f"- **Nome:** {info['nome']}")
        st.write(f"- **ID:** {info['id']}")
        st.write(f"- **Tipo:** {', '.join(info['tipos'])}")
        st.write(f"- **Altura:** {info['altura']}")
        st.write(f"- **Peso:** {info['peso']}")
        return info
    else:
        st.error("Pokémon não encontrado.")
        return None

st.title("Bem-vindo a sua Pokédex")
st.write(f"💰 Moedas: {st.session_state.moedas}$")

# Botão de resetar o game
if st.button("🔄 Resetar Jogo"):
    for key in [
        "pokemons_capturados",
        "pagina_qtd",
        "pokebolas",
        "pc",
        "moedas",
        "rolagem_restante",
        "ultimo_reset",
        "pokemon_rolado"
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Jogo resetado! Recarregue a página para começar do zero.")
    st.rerun()
aba1, aba2, aba3 = st.tabs(["Roletar & Capturar", "Pokédex", "PC/Shop"])


with aba1:
    resetar_rolagem()
    st.subheader("Roletar Pokémon")
    st.write(f"Você pode roletar mais {st.session_state.rolagem_restante} vez(es) nesta hora.")
    st.write(f"Pokébolas disponíveis: {st.session_state.pokebolas}")
    if st.button("Roletar 1 Pokémon"):
        resetar_rolagem()
        if st.session_state.rolagem_restante > 0:
            roletar_pokemons()
            st.session_state.rolagem_restante -= 1
        else:
            tempo_restante = int(3600 - (time.time() - st.session_state.ultimo_reset))
            minutos = tempo_restante // 60
            segundos = tempo_restante % 60
            st.error(f"Espere {minutos}m {segundos}s para roletar novamente.")



    if st.session_state.pokemon_rolado:
        poke = st.session_state.pokemon_rolado
        st.subheader("Pokémon Sorteado")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(poke["img"], width=80)
        with col2:
            st.write(f"**{poke['name']}**")
            if st.button(f"Capturar {poke['name']}", key=f"capturar_{poke['name']}"):
                if st.session_state.pokebolas > 0:
                    st.session_state.pokebolas -= 1
                    chance = random.randint(1, 10)
                    pegar = random.randint(1, 10)
                    if pegar <= chance:
                        info = buscar_pokemon(poke["name"])
                        if info:
                            st.session_state.pokemons_capturados[poke["name"]] = info
                            moedas_ganhas = random.randint(1, 150)
                            st.session_state.moedas += moedas_ganhas
                            st.success(f"Você capturou {poke['name']}! (+{moedas_ganhas} moedas)")
                            st.session_state.pokemon_rolado = None  # Limpa o Pokémon sorteado
                    else:
                        st.warning("O Pokémon escapou!")
                        st.session_state.pokemon_rolado = None
                else:
                    st.error("Você não tem mais Pokébolas! Compre mais no Shop!")

    if st.session_state.pokemons_capturados:
        st.markdown("---")
        st.subheader("Seus Pokémons Capturados")
        for nome, info in list(st.session_state.pokemons_capturados.items()):
            col, col2, col3 = st.columns([1, 3, 2])
            with col:
                st.image(info["img"], width=80)
            with col2:
                st.write(f"**{info['nome']}** | Tipo: {', '.join(info['tipos'])} | ID: {info['id']}")
                if st.button(f"Enviar para o PC: {nome}", key=f"pc_{nome}"):
                    st.session_state.pc[nome] = info
                    del st.session_state.pokemons_capturados[nome]
                    st.rerun()
            with col3:
                if st.button(f"Vender no Mercado Negro: {nome}", key=f"vender_{nome}"):
                    moedas_venda = random.randint(1, 150)
                    st.session_state.moedas += moedas_venda
                    del st.session_state.pokemons_capturados[nome]
                    st.success(f"Você vendeu {nome} por {moedas_venda} moedas!")


with aba2:
    st.subheader("Pokédex")
    st.info("Veja detalhes dos seus pokémons capturados ou no PC")
    todos = {**st.session_state.pokemons_capturados, **st.session_state.pc}
    if todos:
        nomes_pokemons = list(todos.keys())
        pokemon_buscado = st.selectbox("Escolha um Pokémon para ver detalhes", nomes_pokemons, key="busca_pokedex")
        info = todos[pokemon_buscado]
        st.image(info["img"], width=120)
        st.write(f"- **Nome:** {info['nome']}")
        st.write(f"- **ID:** {info['id']}")
        st.write(f"- **Tipo:** {', '.join(info['tipos'])}")
        st.write(f"- **Altura:** {info['altura']}")
        st.write(f"- **Peso:** {info['peso']}")
    else:
        st.warning("Você ainda não capturou nenhum Pokémon.")


with aba3:
    st.subheader("Seu PC")
    if st.session_state.pc:
        for nome, info in st.session_state.pc.items():
            col, col2 = st.columns([1, 4])
            with col:
                st.image(info["img"], width=80)
            with col2:
                st.write(f"**{info['nome']}** | Tipo: {', '.join(info['tipos'])} | ID: {info['id']}")
                if st.button(f"Retirar do PC: {nome}", key=f"retira_{nome}"):
                    st.session_state.pokemons_capturados[nome] = info
                    del st.session_state.pc[nome]
                    st.rerun()
    else:
        st.info("Seu PC está vazio.")

    st.markdown("---")
    st.subheader("Shop de Pokébolas")
    st.write(f"Pokébolas disponíveis: {st.session_state.pokebolas}")
    st.write(f"💰 Moedas: {st.session_state.moedas}")
    if st.button("Comprar 10 Pokébolas (500 moedas)", key="comprar_pokebolas"):
        if st.session_state.moedas >= 500:
            st.session_state.pokebolas += 10
            st.session_state.moedas -= 500
            st.success("Você comprou 10 Pokébolas!")
        else:
            st.error("Você não tem moedas suficientes para comprar Pokébolas!")