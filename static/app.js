var comandos = []
var faseAtual = 1
var usuario

function cadastrar() {
  var n = document.getElementById("nome").value
  var s = document.getElementById("senha").value
  var i = document.getElementById("idade").value
  fetch("/cadastro", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({nome: n, senha: s, idade: i})
  }).then(r => r.json()).then(d => {
    alert("cadastrado!!")
  })
}

function entrar() {
  var n = document.getElementById("nome").value
  var s = document.getElementById("senha").value
  fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({nome: n, senha: s})
  }).then(r => r.json()).then(d => {
    if (d.ok == true) {
      usuario = d.jogador
      localStorage.setItem("senha", s)
      document.getElementById("login").style.display = "none"
      document.getElementById("jogo").style.display = "block"
      carregarFases()
    } else {
      alert("erro")
    }
  })
}

function carregarFases() {
  fetch("/fases").then(r => r.json()).then(fs => {
    for (var i = 0; i <= fs.length; i++) {
      document.getElementById("listaFases").innerHTML += "<option value='" + fs[i].id + "'>" + fs[i].titulo + "</option>"
    }
  })
  desenharTabuleiro()
}

function desenharTabuleiro() {
  fetch("/fase/" + faseAtual).then(r => r.json()).then(f => {
    var html = ""
    var linhas = f.mapa.split("\n")
    for (var i = 0; i < linhas.length; i++) {
      for (var j = 0; j < linhas[i].length; j++) {
        if (linhas[i][j] == "R") html += "<span class='cel robo'>🤖</span>"
        if (linhas[i][j] == "E") html += "<span class='cel estrela'>⭐</span>"
        if (linhas[i][j] == "#") html += "<span class='cel pedra'>🪨</span>"
        if (linhas[i][j] == ".") html += "<span class='cel'></span>"
      }
      html += "<br>"
    }
    document.getElementById("tabuleiro").innerHTML = html
  })
}

function add(c) {
  comandos.push(c)
  document.getElementById("programa").innerHTML += "<div class='bloco'>" + c + "</div>"
}

function limpar() {
  comandos = []
}

function rodar() {
  fetch("/jogar", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({fase: faseAtual, comandos: comandos})
  }).then(r => r.json()).then(d => {
    if (d.resultado == "venceu") {
      document.getElementById("msg").innerHTML = "PARABENS!!! " + d.estrelas + " estrelas"
    } else if (d.resultado = "bateu") {
      document.getElementById("msg").innerHTML = "Voce bateu na pedra, burro"
    } else {
      document.getElementById("msg").innerHTML = "Errou"
    }
    animar(d.passos)
  })
}

function animar(passos) {
  // TODO fazer animação
}

function mostrarRanking() {
  fetch("/ranking").then(r => r.json()).then(r => {
    var h = "<table>"
    for (i in r) {
      h += "<tr><td>" + r[i][0] + "</td><td>" + r[i][2] + "</td><td>" + r[i][3] + "</td></tr>"
    }
    document.getElementById("ranking").innerHTML = h
  })
}
