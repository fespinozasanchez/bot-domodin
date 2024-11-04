economic_limits = {
    "max_win_percentage_per_bet": 0.01,  # max percentage of total money in circulation that a player can win in a single bet (1%)
    "max_own_balance_bet_percentage": 0.20  # max percentage of a player's balance that can be bet in a single bet (20%)
}


gacha_limits = {
    "max_win_percentage_per_bet": 0.01,  # max percentage of total money in circulation that a player can win in a single bet (1%)
    "max_own_balance_bet_percentage": 0.005  # max percentage of a player's balance that can be bet in a single bet (20%)
}






taxes = {
    100_000:0.05,
    1_000_000:0.10,
    10_000_000:0.15,
    100_000_000:0.25,
    1_000_000_000:0.35,
    10_000_000_000:0.40,
    100_000_000_000:0.45,
    1_000_000_000_000:0.55
}



#A user can receive or lose up to 5% of their balance in any transaction.
#The total amount of money that can be introduced into the economy in a single transaction should not exceed 1-2% of the total money supply.

give_money_limits = {
    "max_percentage_win": 0.05,
    "max_percentage_loss": 0.10,
}




growth_limits = {
    1: 0.0001,  # 0.01%
    2: 0.0002,  # 0.02%
    3: 0.0003,  # 0.03%
    4: 0.0004,  # 0.04%
    5: 0.0005   # 0.05%
}