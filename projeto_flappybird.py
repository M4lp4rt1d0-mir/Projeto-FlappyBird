"""
Modulo responsável por carregar recursos e gerenciar a lógica principal.
"""
from os import path, environ
from random import randrange
from sys import exit
import pygame


environ['SDL_VIDEO_WINDOW_POS'] = 'center, 100'

TELA_LARGURA = 500
TELA_ALTURA = 650

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(path.join("imgs", "pipe.png")))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(path.join("imgs", "base.png")))
IMAGEM_BACKGROUND = pygame.transform.scale(pygame.image.load(path.join("imgs", "bg.png")),
                                           (TELA_LARGURA, TELA_ALTURA))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(path.join("imgs", "bird3.png"))),
]

pygame.font.init()
pygame.mixer.init()
# Carrega a música (não esqueça de conferir o nome do arquivo)
fonte_pontos = pygame.font.SysFont("arial", 50)


class Passaro:
    # animações da rotação
    imgs = IMAGENS_PASSARO
    rotacao_maxima = 25
    velocidade_rotacao = 20
    tempo_animacao = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.imgs[0]

    def pular(self):
        # Define o pular
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo ** 2) + (self.velocidade * self.tempo)

        # restringir o deslocamente
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # O angulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo >= self.rotacao_maxima:
                return
            else:
                pass
            self.angulo = self.rotacao_maxima
        else:
            if self.angulo > -90:
                pass
            else:
                return
            self.angulo -= self.velocidade_rotacao

    def desenhar(self, tela):
        """
        :type tela: object
        """
        # Desenha o contador de canos
        self.contagem_imagem += 1

        # Define a ordem das imagens na animação (subindo e descendo a asa)
        ordem_animacao: list[int] = [0, 1, 2, 1]

        # Calcula qual índice da lista 'ordem_animacao' usar
        # O tempo total do ciclo é: tempo_cada_frame * total_de_frames
        ciclo_total = self.tempo_animacao * len(ordem_animacao)
        indice = (self.contagem_imagem // self.tempo_animacao) % len(ordem_animacao)

        self.imagem = self.imgs[ordem_animacao[indice]]

        # Reseta a contagem quando o ciclo acaba para evitar números gigantes
        if self.contagem_imagem >= ciclo_total:
            self.contagem_imagem = 0

        # se o passarp estiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.imgs[1]
            self.contagem_imagem = self.tempo_animacao * 2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    @property
    def get_mask(self):
        # Define o objeto do passaro
        return pygame.mask.from_surface(self.imagem)


class Cano:
    distancia: int = 200
    velocidade = 5

    def __init__(self, x):
        # Função que chama as classes
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.cano_topo = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.cano_base = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        # Define a altura do cano topo para o cano base
        self.altura = randrange(50, 300)
        self.pos_topo = self.altura - self.cano_topo.get_height()
        self.pos_base = self.altura + self.distancia

    def mover(self):
        # Define a velocidade do passaro
        self.x -= self.velocidade

    def desenhar(self, tela):
        # Desenha os canos
        tela.blit(self.cano_topo, (self.x, self.pos_topo))
        tela.blit(self.cano_base, (self.x, self.pos_base))

    def colidir(self, passaro):
        # Define o objeto fisico dos canos na imagem para a colisão do passaro
        passaro_mask = passaro.get_mask
        topo_mask = pygame.mask.from_surface(self.cano_topo)
        base_mask = pygame.mask.from_surface(self.cano_base)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        return bool(base_ponto or topo_ponto)

class Chao:
    velocidade = 5
    largura = IMAGEM_CHAO.get_width()
    imagem = IMAGEM_CHAO

    def __init__(self, y):
        # Função que inicia o game
        self.y = y
        self.x1 = 0
        self.x2 = self.largura

    def mover(self):
        # Move as coisas na tela
        self.x1 -= self.velocidade
        self.x2 -= self.velocidade

        if self.x1 + self.largura < 0:
            self.x1 = self.x2 + self.largura
        if self.x2 + self.largura < 0:
            self.x2 = self.x1 + self.largura

    def desenhar(self, tela):
        # Desenha na tela
        tela.blit(self.imagem, (self.x1, self.y))
        tela.blit(self.imagem, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    # Desenha na tela os Metodos
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)
    texto = fonte_pontos.render(f"Pontuação: {pontos}", 1, (0, 0, 0))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()


def main():
    # 1. Configurações Iniciais
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    relogio = pygame.time.Clock()

    # Criamos os objetos uma única vez para o Menu
    passaros = [Passaro(230, 250)]
    chao = Chao(TELA_ALTURA - 100)
    canos = [Cano(700)]
    pontos = 0

    estado_jogo = "MENU"  # Estados: MENU, JOGANDO, MORTE

    rodando = True
    while rodando:
        relogio.tick(30)

        # === PROCESSAMENTO DE EVENTOS (Teclado/Mouse) ===
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()

            if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                if estado_jogo == "MENU":
                    estado_jogo = "JOGANDO"
                elif estado_jogo == "JOGANDO":
                    for passaro in passaros:
                        passaro.pular()
                elif estado_jogo == "MORTE":
                    # Reinicia tudo e volta pro Menu
                    main()
                    return

        # === LÓGICA DE MOVIMENTO (Só acontece se estiver JOGANDO) ===
        if estado_jogo == "JOGANDO":
            for passaro in passaros:
                passaro.mover()
            chao.mover()

            adicionar_cano = False
            remover_canos = []
            for cano in canos:
                for i, passaro in enumerate(passaros):
                    if cano.colidir(passaro):
                        estado_jogo = "MORTE"  # Se bater, muda o estado
                    if not cano.passou and passaro.x > cano.x:
                        cano.passou = True
                        adicionar_cano = True
                cano.mover()
                if cano.x + cano.cano_topo.get_width() < 0:
                    remover_canos.append(cano)

            if adicionar_cano:
                pontos += 1
                canos.append(Cano(600))
            for cano in remover_canos:
                canos.remove(cano)

            for i, passaro in enumerate(passaros):
                if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                    estado_jogo = "MORTE"

        # === DESENHAR NA TELA ===
        tela.blit(IMAGEM_BACKGROUND, (0, 0))  # Fundo corrigido

        for passaro in passaros:
            passaro.desenhar(tela)

        for cano in canos:
            cano.desenhar(tela)

        chao.desenhar(tela)

        # Mostra os textos baseados no estado
        if estado_jogo == "MENU":
            fonte_m = pygame.font.SysFont('arial', 30, bold=True)
            txt = fonte_m.render("Aperte para Iniciar", 1, (255, 255, 255))
            tela.blit(txt, (TELA_LARGURA // 2 - txt.get_width() // 2, TELA_ALTURA // 2))

        elif estado_jogo == "MORTE":
            fonte_m = pygame.font.SysFont('arial', 40, bold=True)
            txt_morte = fonte_m.render("VOCÊ MORREU!", 1, (255, 0, 0))
            txt_reiniciar = pygame.font.SysFont('arial', 20).render("Clique para voltar ao Menu", 1, (255, 255, 255))
            tela.blit(txt_morte, (TELA_LARGURA // 2 - txt_morte.get_width() // 2, TELA_ALTURA // 2 - 50))
            tela.blit(txt_reiniciar, (TELA_LARGURA // 2 - txt_reiniciar.get_width() // 2, TELA_ALTURA // 2 + 20))

        # Pontuação sempre visível
        texto_pontos = fonte_pontos.render(f"Pontos: {pontos}", 1, (255, 255, 255))
        tela.blit(texto_pontos, (TELA_LARGURA - 10 - texto_pontos.get_width(), 10))

        pygame.display.update()


if __name__ == '__main__':
    main()
