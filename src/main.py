import Market

"""
Classe main qui gère le lancement du Mark
"""

if __name__ == "__main__":
    market = Market.Market(150, 5, 0.25)
    market.run()
