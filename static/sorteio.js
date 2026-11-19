// Animação do tambor: os nomes giram desfocados e o ganhador aparece no fim.
const botao = document.getElementById("sortear");
const nomeTambor = document.getElementById("nome-tambor");
const premioAtual = document.getElementById("premio-atual");
const listaGanhadores = document.getElementById("lista-ganhadores");
const DURACAO = 5000;

// Desfoque forte até 75% da animação, depois some aos poucos.
const desfoqueEm = (progresso) => (progresso < 0.75 ? 14 : Math.max(0, 14 * (1 - (progresso - 0.75) / 0.25)));

function girar(nomes, ganhador) {
  return new Promise((resolve) => {
    const inicio = performance.now();
    let ultimaTroca = 0;
    function quadro(agora) {
      const progresso = Math.min(1, (agora - inicio) / DURACAO);
      const intervalo = 40 + progresso * progresso * 260; // começa rápido e vai freando
      if (agora - ultimaTroca > intervalo) {
        nomeTambor.textContent = nomes[Math.floor(Math.random() * nomes.length)];
        ultimaTroca = agora;
      }
      nomeTambor.style.filter = `blur(${desfoqueEm(progresso)}px)`;
      if (progresso < 1) {
        requestAnimationFrame(quadro);
      } else {
        nomeTambor.textContent = ganhador;
        nomeTambor.style.filter = "none";
        resolve();
      }
    }
    requestAnimationFrame(quadro);
  });
}

async function onSortear() {
  botao.disabled = true;
  const resposta = await fetch(botao.dataset.url, { method: "POST" });
  const dados = await resposta.json();
  if (!resposta.ok) {
    nomeTambor.textContent = dados.erro;
    return;
  }
  const nomes = dados.nomes_tambor.length ? dados.nomes_tambor : JSON.parse(botao.dataset.nomes);
  await girar(nomes, dados.nome);
  document.getElementById("tambor").classList.add("vencedor");
  confete();

  const item = document.createElement("li");
  item.innerHTML = `<b></b>: <span></span> <small>(${dados.cupons} cupons)</small>`;
  item.querySelector("b").textContent = dados.premio;
  item.querySelector("span").textContent = dados.nome;
  listaGanhadores.appendChild(item);

  if (dados.restantes > 0) {
    premioAtual.textContent = `Parabéns! Ganhou: ${dados.premio}. Recarregue para o próximo prêmio.`;
    setTimeout(() => location.reload(), 6000);
  } else {
    premioAtual.textContent = `Parabéns! Ganhou: ${dados.premio}. Fim do sorteio!`;
  }
}

function confete() {
  const canvas = document.getElementById("confete");
  const ctx = canvas.getContext("2d");
  canvas.width = innerWidth;
  canvas.height = innerHeight;
  const cores = ["#ff7a00", "#1d4ed8", "#facc15", "#22c55e", "#ec4899", "#ffffff"];
  const pedacos = Array.from({ length: 200 }, () => ({
    x: Math.random() * canvas.width,
    y: -Math.random() * canvas.height * 0.4,
    r: Math.random() * 6 + 3,
    vy: Math.random() * 3 + 2,
    vx: (Math.random() - 0.5) * 2,
    cor: cores[Math.floor(Math.random() * cores.length)],
  }));
  const fim = performance.now() + 5000;
  (function desenhar(agora) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const p of pedacos) {
      p.y += p.vy;
      p.x += p.vx;
      ctx.fillStyle = p.cor;
      ctx.fillRect(p.x, p.y, p.r, p.r);
    }
    if (agora < fim) requestAnimationFrame(desenhar);
    else ctx.clearRect(0, 0, canvas.width, canvas.height);
  })(performance.now());
}

if (botao) botao.addEventListener("click", onSortear);

document.getElementById("mostrar")?.addEventListener("click", (e) => {
  const tabela = document.getElementById("tabela");
  tabela.classList.toggle("borrado");
  e.target.textContent = tabela.classList.contains("borrado") ? "mostrar" : "esconder";
});
