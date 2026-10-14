from otree.api import *
import random

doc = """
Willingness to pay for an appeal, elicited with the BDM mechanism.
"""


class C(BaseConstants):
    NAME_IN_URL = 'appeal_wtp'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ENDOWMENT = cu(10)
    PRIZE = cu(10)
    MAX_PRICE = 10


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    players = subsession.get_players()
    random.shuffle(players)
    for i, p in enumerate(players):
        # balanced random assignment
        p.reversal_pct = 30 if i % 2 == 0 else 70


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    reversal_pct = models.IntegerField()
    quiz_pay = models.IntegerField(
        label='Suppose you state 6 points and the computer draws a price of 4. How many points do you pay?'
    )
    bid = models.CurrencyField(
        min=0, max=C.MAX_PRICE,
        label='What is the most you are willing to pay for an appeal?'
    )
    price = models.CurrencyField()
    bought_appeal = models.BooleanField()
    appeal_won = models.BooleanField()


def quiz_pay_error_message(player: Player, value):
    if value != 4:
        return 'Not quite. You pay the price the computer draws, not the amount you state.'


def set_outcome(player: Player):
    player.price = random.randint(0, C.MAX_PRICE)
    player.bought_appeal = player.bid >= player.price
    if player.bought_appeal:
        player.appeal_won = random.random() < player.reversal_pct / 100
        prize = C.PRIZE if player.appeal_won else 0
        player.payoff = C.ENDOWMENT - player.price + prize
    else:
        player.appeal_won = False
        player.payoff = C.ENDOWMENT


# PAGES
class Instructions(Page):
    form_model = 'player'
    form_fields = ['quiz_pay']


class Bid(Page):
    form_model = 'player'
    form_fields = ['bid']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_outcome(player)


class Results(Page):
    pass


page_sequence = [Instructions, Bid, Results]